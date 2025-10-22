from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..dependencies import ensure_role, get_current_user
from ..db import get_session
from ..models import AgencySettings, AgencyTier, ClientOrganization, DomainConfiguration, DomainStatus, MembershipRole, User, UserAgencyMembership
from ..schemas import DomainCreate, DomainRead, DomainVerificationRequest
from ..services.acme import acme_client
from ..services.dns import dns_verifier

router = APIRouter(prefix="", tags=["domains"])


@router.post("/clients/{client_id}/domains", response_model=DomainRead, status_code=status.HTTP_201_CREATED)
def create_domain_configuration(
    client_id: uuid.UUID,
    payload: DomainCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> DomainRead:
    client = session.get(ClientOrganization, client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    membership = session.exec(
        select(UserAgencyMembership).where(
            UserAgencyMembership.agency_id == client.agency_id,
            UserAgencyMembership.user_id == current_user.id,
        )
    ).first()
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this agency")
    ensure_role(membership, MembershipRole.owner, MembershipRole.manager)

    agency = session.get(AgencySettings, client.agency_id)
    if not agency:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agency not found")
    if agency.tier != AgencyTier.agency:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agency tier does not support custom domains")

    domain_value = payload.domain.lower()
    existing = session.exec(
        select(DomainConfiguration).where(DomainConfiguration.domain == domain_value)
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Domain already configured")

    verification_token = uuid.uuid4().hex
    domain_cfg = DomainConfiguration(
        client_id=client_id,
        domain=domain_value,
        status=DomainStatus.pending,
        verification_token=verification_token,
    )
    session.add(domain_cfg)
    session.commit()
    session.refresh(domain_cfg)
    return DomainRead.model_validate(domain_cfg)


@router.post("/domains/{domain_id}/verify", response_model=DomainRead)
def verify_domain_configuration(
    domain_id: uuid.UUID,
    payload: DomainVerificationRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> DomainRead:
    domain_cfg = session.get(DomainConfiguration, domain_id)
    if not domain_cfg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain configuration not found")

    client = session.get(ClientOrganization, domain_cfg.client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found for domain configuration")

    membership = session.exec(
        select(UserAgencyMembership).where(
            UserAgencyMembership.agency_id == client.agency_id,
            UserAgencyMembership.user_id == current_user.id,
        )
    ).first()
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this agency")
    ensure_role(membership, MembershipRole.owner, MembershipRole.manager)

    domain_cfg.last_verification_attempt = datetime.utcnow()

    verification = dns_verifier.verify(domain_cfg.verification_token, payload.dns_record_value)
    if not verification.success:
        domain_cfg.status = DomainStatus.pending
        session.add(domain_cfg)
        session.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=verification.message)

    domain_cfg.status = DomainStatus.verified
    domain_cfg.verified_at = datetime.utcnow()

    certificate = acme_client.issue_certificate(domain_cfg.domain)
    domain_cfg.certificate_pem = certificate.pem
    domain_cfg.status = DomainStatus.active
    domain_cfg.activated_at = certificate.issued_at

    session.add(domain_cfg)
    session.commit()
    session.refresh(domain_cfg)
    return DomainRead.model_validate(domain_cfg)

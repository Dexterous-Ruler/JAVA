from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..dependencies import ensure_role, get_agency_membership, get_current_user
from ..db import get_session
from ..models import BrandingAsset, ClientOrganization, DomainConfiguration, DomainStatus, MembershipRole, User, UserAgencyMembership
from ..schemas import BrandingRead, BrandingUpdate

router = APIRouter(prefix="", tags=["branding"])


def _upsert_branding(
    session: Session,
    agency_id: uuid.UUID,
    client_id: uuid.UUID | None,
    payload: BrandingUpdate,
) -> BrandingAsset:
    branding = session.exec(
        select(BrandingAsset).where(
            BrandingAsset.agency_id == agency_id,
            BrandingAsset.client_id == client_id,
        )
    ).first()
    data = payload.model_dump(exclude_unset=True)
    if not branding:
        branding = BrandingAsset(agency_id=agency_id, client_id=client_id, **data)
        session.add(branding)
    else:
        for field, value in data.items():
            setattr(branding, field, value)
    session.commit()
    session.refresh(branding)
    return branding


@router.put("/agencies/{agency_id}/branding", response_model=BrandingRead)
def update_agency_branding(
    agency_id: uuid.UUID,
    payload: BrandingUpdate,
    session: Session = Depends(get_session),
    membership=Depends(get_agency_membership),
) -> BrandingRead:
    ensure_role(membership, MembershipRole.owner, MembershipRole.manager)
    branding = _upsert_branding(session, agency_id, None, payload)
    return BrandingRead(scope=f"agency:{agency_id}", **branding.model_dump(exclude={"id", "agency_id", "client_id", "created_at", "updated_at"}))


@router.put("/clients/{client_id}/branding", response_model=BrandingRead)
def update_client_branding(
    client_id: uuid.UUID,
    payload: BrandingUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> BrandingRead:
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

    branding = _upsert_branding(session, client.agency_id, client_id, payload)
    return BrandingRead(scope=f"client:{client_id}", **branding.model_dump(exclude={"id", "agency_id", "client_id", "created_at", "updated_at"}))


def _compose_branding(
    session: Session,
    agency_id: uuid.UUID,
    client_id: uuid.UUID | None,
) -> BrandingRead:
    agency_branding = session.exec(
        select(BrandingAsset).where(
            BrandingAsset.agency_id == agency_id,
            BrandingAsset.client_id.is_(None),
        )
    ).first()
    client_branding = None
    if client_id:
        client_branding = session.exec(
            select(BrandingAsset).where(
                BrandingAsset.agency_id == agency_id,
                BrandingAsset.client_id == client_id,
            )
        ).first()

    base = {
        "company_name": None,
        "logo_url": None,
        "primary_color": None,
        "secondary_color": None,
        "accent_color": None,
    }
    if agency_branding:
        base.update(
            {
                "company_name": agency_branding.company_name,
                "logo_url": agency_branding.logo_url,
                "primary_color": agency_branding.primary_color,
                "secondary_color": agency_branding.secondary_color,
                "accent_color": agency_branding.accent_color,
            }
        )
    if client_branding:
        overrides = {
            key: getattr(client_branding, key)
            for key in base.keys()
            if getattr(client_branding, key) is not None
        }
        base.update(overrides)

    scope = f"client:{client_id}" if client_id else f"agency:{agency_id}"
    return BrandingRead(scope=scope, **base)


@router.get("/branding/by-client/{client_id}", response_model=BrandingRead)
def get_branding_by_client(
    client_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> BrandingRead:
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

    return _compose_branding(session, client.agency_id, client_id)


@router.get("/branding/by-domain/{domain}", response_model=BrandingRead)
def get_branding_by_domain(
    domain: str,
    session: Session = Depends(get_session),
) -> BrandingRead:
    domain_cfg = session.exec(
        select(DomainConfiguration).where(
            DomainConfiguration.domain == domain,
            DomainConfiguration.status.in_([DomainStatus.verified, DomainStatus.active]),
        )
    ).first()
    if not domain_cfg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not configured")

    client = session.get(ClientOrganization, domain_cfg.client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found for domain")

    branding = _compose_branding(session, client.agency_id, client.id)
    return BrandingRead(scope=f"domain:{domain}", **branding.model_dump(exclude={"scope"}))

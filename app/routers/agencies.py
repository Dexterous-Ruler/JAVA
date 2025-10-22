from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..dependencies import get_agency_membership, get_current_user
from ..db import get_session
from ..models import AgencySettings, BrandingAsset, ClientOrganization, MembershipRole, User, UserAgencyMembership
from ..schemas import AgencyCreate, AgencyRead
from ..services.utils import slugify

router = APIRouter(prefix="/agencies", tags=["agencies"])


def _ensure_default_branding(session: Session, agency: AgencySettings) -> None:
    existing = session.exec(
        select(BrandingAsset).where(
            BrandingAsset.agency_id == agency.id,
            BrandingAsset.client_id.is_(None),
        )
    ).first()
    if not existing:
        branding = BrandingAsset(agency_id=agency.id, company_name=agency.name)
        session.add(branding)


def _hydrate_agency_response(agency: AgencySettings, default_client_id: uuid.UUID) -> AgencyRead:
    return AgencyRead(
        id=agency.id,
        name=agency.name,
        tier=agency.tier,
        owner_id=agency.owner_id,
        created_at=agency.created_at,
        updated_at=agency.updated_at,
        default_client_id=default_client_id,
    )


@router.post("", response_model=AgencyRead, status_code=status.HTTP_201_CREATED)
def create_agency(
    payload: AgencyCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> AgencyRead:
    agency = AgencySettings(name=payload.name, owner_id=current_user.id, tier=payload.tier)
    session.add(agency)
    session.flush()

    client_name = payload.primary_client_name or f"{payload.name} Client"
    slug_candidate = slugify(client_name)
    suffix = 1

    slug = slug_candidate
    while session.exec(
        select(ClientOrganization).where(
            ClientOrganization.agency_id == agency.id,
            ClientOrganization.slug == slug,
        )
    ).first():
        suffix += 1
        slug = f"{slug_candidate}-{suffix}"

    client = ClientOrganization(agency_id=agency.id, name=client_name, slug=slug)
    session.add(client)
    session.flush()

    membership = UserAgencyMembership(
        user_id=current_user.id,
        agency_id=agency.id,
        role=MembershipRole.owner,
        current_client_id=client.id,
    )
    session.add(membership)

    _ensure_default_branding(session, agency)

    session.commit()
    session.refresh(agency)
    return _hydrate_agency_response(agency, default_client_id=client.id)


@router.get("/{agency_id}", response_model=AgencyRead)
def get_agency(
    agency_id: uuid.UUID,
    membership: UserAgencyMembership = Depends(get_agency_membership),
    session: Session = Depends(get_session),
) -> AgencyRead:
    agency = session.get(AgencySettings, agency_id)
    if not agency:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agency not found")

    default_client = session.exec(
        select(ClientOrganization)
        .where(ClientOrganization.agency_id == agency_id)
        .order_by(ClientOrganization.created_at)
    ).first()
    if not default_client:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Agency has no clients configured")

    return _hydrate_agency_response(agency, default_client_id=default_client.id)

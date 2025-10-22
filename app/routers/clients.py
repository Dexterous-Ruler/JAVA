from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..dependencies import ensure_role, get_agency_membership
from ..db import get_session
from ..models import AgencySettings, AgencyTier, ClientOrganization, MembershipRole
from ..schemas import ClientCreate, ClientRead
from ..services.utils import slugify

router = APIRouter(prefix="/agencies/{agency_id}/clients", tags=["clients"])


@router.get("", response_model=list[ClientRead])
def list_clients(
    agency_id: uuid.UUID,
    session: Session = Depends(get_session),
    membership=Depends(get_agency_membership),
) -> list[ClientOrganization]:
    clients = session.exec(
        select(ClientOrganization).where(ClientOrganization.agency_id == agency_id)
    ).all()
    return clients


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(
    agency_id: uuid.UUID,
    payload: ClientCreate,
    session: Session = Depends(get_session),
    membership=Depends(get_agency_membership),
) -> ClientOrganization:
    ensure_role(membership, MembershipRole.owner, MembershipRole.manager)
    agency = session.get(AgencySettings, agency_id)
    if not agency:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agency not found")

    existing_client_count = len(
        session.exec(select(ClientOrganization).where(ClientOrganization.agency_id == agency_id)).all()
    )
    if agency.tier != AgencyTier.agency and existing_client_count >= 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agency tier does not support multiple clients")

    desired_slug = payload.slug or slugify(payload.name)
    slug = desired_slug
    suffix = 1
    while session.exec(
        select(ClientOrganization).where(
            ClientOrganization.agency_id == agency_id,
            ClientOrganization.slug == slug,
        )
    ).first():
        suffix += 1
        slug = f"{desired_slug}-{suffix}"

    client = ClientOrganization(agency_id=agency_id, name=payload.name, slug=slug)
    session.add(client)

    session.commit()
    session.refresh(client)
    return client

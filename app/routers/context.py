from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..dependencies import get_agency_membership
from ..db import get_session
from ..models import ClientOrganization, UserAgencyMembership
from ..schemas import AgencyContext, ClientSwitchRequest, MembershipRead

router = APIRouter(prefix="/agencies/{agency_id}", tags=["context"])


@router.get("/context", response_model=AgencyContext)
def get_agency_context(
    agency_id: uuid.UUID,
    membership: UserAgencyMembership = Depends(get_agency_membership),
) -> AgencyContext:
    return AgencyContext(
        agency_id=agency_id,
        user_id=membership.user_id,
        role=membership.role,
        current_client_id=membership.current_client_id,
    )


@router.post("/switch-client", response_model=MembershipRead)
def switch_client(
    agency_id: uuid.UUID,
    payload: ClientSwitchRequest,
    membership: UserAgencyMembership = Depends(get_agency_membership),
    session: Session = Depends(get_session),
) -> MembershipRead:
    client = session.get(ClientOrganization, payload.client_id)
    if not client or client.agency_id != agency_id:
        raise HTTPException(status_code=400, detail="Client not part of this agency")

    persisted_membership = session.exec(
        select(UserAgencyMembership).where(UserAgencyMembership.id == membership.id)
    ).first()
    if not persisted_membership:
        raise HTTPException(status_code=400, detail="Membership not found")

    persisted_membership.current_client_id = payload.client_id
    session.add(persisted_membership)
    session.commit()
    session.refresh(persisted_membership)
    return MembershipRead.model_validate(persisted_membership)

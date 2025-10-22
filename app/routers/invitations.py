from __future__ import annotations

from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..dependencies import ensure_role, get_agency_membership, get_current_user
from ..db import get_session
from ..models import AgencySettings, AgencyTier, ClientOrganization, Invitation, InvitationStatus, MembershipRole, User, UserAgencyMembership
from ..schemas import AcceptInvitationRequest, InvitationCreate, InvitationRead, MembershipRead

router = APIRouter(prefix="", tags=["invitations"])


@router.post("/agencies/{agency_id}/invitations", response_model=InvitationRead, status_code=status.HTTP_201_CREATED)
def create_invitation(
    agency_id: uuid.UUID,
    payload: InvitationCreate,
    membership=Depends(get_agency_membership),
    session: Session = Depends(get_session),
) -> Invitation:
    ensure_role(membership, MembershipRole.owner, MembershipRole.manager)

    agency = session.get(AgencySettings, agency_id)
    if not agency:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agency not found")
    if agency.tier != AgencyTier.agency:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agency tier does not support invitations")

    if payload.client_id:
        client = session.get(ClientOrganization, payload.client_id)
        if not client or client.agency_id != agency_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client does not belong to this agency")

    invitation = Invitation(
        agency_id=agency_id,
        email=payload.email,
        role=payload.role,
        invited_by_user_id=membership.user_id,
        client_id=payload.client_id,
    )
    session.add(invitation)
    session.commit()
    session.refresh(invitation)
    return InvitationRead.model_validate(invitation)


@router.post("/invitations/{token}/accept", response_model=MembershipRead)
def accept_invitation(
    token: str,
    payload: AcceptInvitationRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> MembershipRead:
    invitation = session.exec(select(Invitation).where(Invitation.token == token)).first()
    if not invitation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")

    if invitation.status != InvitationStatus.pending:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation already processed")

    if invitation.expires_at < datetime.utcnow():
        invitation.status = InvitationStatus.expired
        session.add(invitation)
        session.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation expired")

    if payload.email.lower() != invitation.email.lower():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation email does not match")

    if current_user.email.lower() != invitation.email.lower():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Authenticated user does not match invitation")

    membership = session.exec(
        select(UserAgencyMembership).where(
            UserAgencyMembership.agency_id == invitation.agency_id,
            UserAgencyMembership.user_id == current_user.id,
        )
    ).first()
    if membership:
        membership.role = invitation.role
        if invitation.client_id:
            membership.current_client_id = invitation.client_id
    else:
        membership = UserAgencyMembership(
            agency_id=invitation.agency_id,
            user_id=current_user.id,
            role=invitation.role,
            current_client_id=invitation.client_id,
        )
        session.add(membership)

    invitation.status = InvitationStatus.accepted
    invitation.accepted_at = datetime.utcnow()

    session.add(invitation)
    session.commit()
    session.refresh(membership)

    return MembershipRead.model_validate(membership)

from __future__ import annotations

import uuid

from fastapi import Depends, Header, HTTPException, status
from sqlmodel import Session, select

from .db import get_session
from .models import MembershipRole, User, UserAgencyMembership


def get_current_user(
    x_user_id: str = Header(..., alias="X-User-Id"),
    session: Session = Depends(get_session),
) -> User:
    try:
        user_id = uuid.UUID(x_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user identifier") from exc

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown user")
    return user


def get_agency_membership(
    agency_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UserAgencyMembership:
    membership = session.exec(
        select(UserAgencyMembership).where(
            UserAgencyMembership.agency_id == agency_id,
            UserAgencyMembership.user_id == current_user.id,
        )
    ).first()
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this agency")
    return membership


def ensure_role(
    membership: UserAgencyMembership,
    *allowed_roles: MembershipRole,
) -> None:
    if membership.role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role permissions")


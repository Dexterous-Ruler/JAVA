from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from .models import AgencyTier, DomainStatus, InvitationStatus, MembershipRole


class UserCreate(BaseModel):
    email: EmailStr
    name: str


class UserRead(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str

    class Config:
        from_attributes = True


class AgencyCreate(BaseModel):
    name: str
    tier: AgencyTier = AgencyTier.basic
    primary_client_name: Optional[str] = None


class AgencyRead(BaseModel):
    id: uuid.UUID
    name: str
    tier: AgencyTier
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    default_client_id: uuid.UUID

    class Config:
        from_attributes = True


class ClientCreate(BaseModel):
    name: str
    slug: Optional[str] = None


class ClientRead(BaseModel):
    id: uuid.UUID
    agency_id: uuid.UUID
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BrandingUpdate(BaseModel):
    company_name: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None


class BrandingRead(BaseModel):
    scope: str
    company_name: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None


class DomainCreate(BaseModel):
    domain: str


class DomainRead(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    domain: str
    status: DomainStatus
    verification_token: str
    certificate_pem: Optional[str]

    class Config:
        from_attributes = True


class DomainVerificationRequest(BaseModel):
    dns_record_value: str


class InvitationCreate(BaseModel):
    email: EmailStr
    role: MembershipRole
    client_id: Optional[uuid.UUID] = None


class InvitationRead(BaseModel):
    id: uuid.UUID
    agency_id: uuid.UUID
    email: EmailStr
    role: MembershipRole
    client_id: Optional[uuid.UUID]
    token: str
    status: InvitationStatus
    expires_at: datetime

    class Config:
        from_attributes = True


class AcceptInvitationRequest(BaseModel):
    email: EmailStr


class MembershipRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    agency_id: uuid.UUID
    role: MembershipRole
    current_client_id: Optional[uuid.UUID]

    class Config:
        from_attributes = True


class ClientSwitchRequest(BaseModel):
    client_id: uuid.UUID


class AgencyContext(BaseModel):
    agency_id: uuid.UUID
    user_id: uuid.UUID
    role: MembershipRole
    current_client_id: Optional[uuid.UUID]

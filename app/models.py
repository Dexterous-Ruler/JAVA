from __future__ import annotations

import enum
import uuid
from datetime import datetime, timedelta
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel, UniqueConstraint


class AgencyTier(str, enum.Enum):
    basic = "basic"
    agency = "agency"


class MembershipRole(str, enum.Enum):
    owner = "owner"
    manager = "manager"
    analyst = "analyst"


class DomainStatus(str, enum.Enum):
    pending = "pending"
    verified = "verified"
    active = "active"
    failed = "failed"


class InvitationStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    expired = "expired"
    revoked = "revoked"


class TimestampedModel(SQLModel):
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    updated_at: datetime = Field(default_factory=lambda: datetime.utcnow(), sa_column_kwargs={"onupdate": datetime.utcnow})


class User(TimestampedModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    email: EmailStr = Field(index=True, unique=True)
    name: str = Field(max_length=255)


class AgencySettings(TimestampedModel, table=True):
    __tablename__ = "agency_settings"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(foreign_key="users.id")
    tier: AgencyTier = Field(default=AgencyTier.basic)


class ClientOrganization(TimestampedModel, table=True):
    __tablename__ = "client_organizations"

    __table_args__ = (
        UniqueConstraint("agency_id", "slug", name="uq_client_slug_per_agency"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    agency_id: uuid.UUID = Field(foreign_key="agency_settings.id")
    name: str = Field(max_length=255)
    slug: str = Field(max_length=255)


class BrandingAsset(TimestampedModel, table=True):
    __tablename__ = "branding_assets"

    __table_args__ = (
        UniqueConstraint("agency_id", "client_id", name="uq_branding_per_scope"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    agency_id: uuid.UUID = Field(foreign_key="agency_settings.id")
    client_id: Optional[uuid.UUID] = Field(default=None, foreign_key="client_organizations.id", index=True)
    company_name: Optional[str] = Field(default=None, max_length=255)
    logo_url: Optional[str] = Field(default=None, max_length=2048)
    primary_color: Optional[str] = Field(default=None, max_length=32)
    secondary_color: Optional[str] = Field(default=None, max_length=32)
    accent_color: Optional[str] = Field(default=None, max_length=32)


class DomainConfiguration(TimestampedModel, table=True):
    __tablename__ = "domain_configurations"

    __table_args__ = (
        UniqueConstraint("client_id", "domain", name="uq_client_domain"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    client_id: uuid.UUID = Field(foreign_key="client_organizations.id")
    domain: str = Field(max_length=255, index=True)
    status: DomainStatus = Field(default=DomainStatus.pending)
    verification_token: str = Field(max_length=255)
    certificate_pem: Optional[str] = Field(default=None)
    verified_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    last_verification_attempt: Optional[datetime] = None


class UserAgencyMembership(TimestampedModel, table=True):
    __tablename__ = "user_agency_memberships"

    __table_args__ = (
        UniqueConstraint("user_id", "agency_id", name="uq_user_agency_membership"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    agency_id: uuid.UUID = Field(foreign_key="agency_settings.id", index=True)
    role: MembershipRole = Field()
    current_client_id: Optional[uuid.UUID] = Field(default=None, foreign_key="client_organizations.id")


class Invitation(TimestampedModel, table=True):
    __tablename__ = "invitations"

    __table_args__ = (
        UniqueConstraint("token", name="uq_invitation_token"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    agency_id: uuid.UUID = Field(foreign_key="agency_settings.id", index=True)
    email: EmailStr = Field(index=True)
    role: MembershipRole = Field()
    token: str = Field(max_length=255, default_factory=lambda: uuid.uuid4().hex)
    invited_by_user_id: uuid.UUID = Field(foreign_key="users.id")
    client_id: Optional[uuid.UUID] = Field(default=None, foreign_key="client_organizations.id")
    status: InvitationStatus = Field(default=InvitationStatus.pending)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=3))
    accepted_at: Optional[datetime] = None

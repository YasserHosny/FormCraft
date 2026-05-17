from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import Language, Role

class Organization(BaseModel):
    id: UUID
    name_ar: str
    name_en: str
    logo_url: str | None = None
    primary_color: str | None = None
    default_language: Language = Language.AR
    default_country: str = "EG"
    default_currency: str = "EGP"
    custom_domain: str | None = None
    settings: dict = {}
    subscription_tier: str = "starter"
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class Department(BaseModel):
    id: UUID
    org_id: UUID
    name_ar: str
    name_en: str
    is_active: bool = True
    created_at: datetime


class Branch(BaseModel):
    id: UUID
    department_id: UUID
    org_id: UUID
    name_ar: str
    name_en: str
    location: str | None = None
    is_active: bool = True
    created_at: datetime


class UserInvitation(BaseModel):
    id: UUID
    email: str
    token: UUID
    role: Role
    org_id: UUID
    department_id: UUID | None = None
    branch_id: UUID | None = None
    invited_by: UUID
    status: str = "pending"
    expires_at: datetime
    accepted_at: datetime | None = None
    created_at: datetime

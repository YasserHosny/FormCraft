from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import Country, Language, Role


class OrgCreate(BaseModel):
    name_ar: str = Field(..., min_length=1, max_length=200)
    name_en: str = Field(..., min_length=1, max_length=200)
    logo_url: str | None = None
    primary_color: str | None = None
    default_language: Language = Language.AR
    default_country: Country = Country.EG
    default_currency: str = Field(default="EGP", max_length=10)
    custom_domain: str | None = None
    subscription_tier: str = Field(
        default="starter", pattern=r"^(starter|professional|enterprise)$"
    )


class OrgUpdate(BaseModel):
    name_ar: str | None = Field(default=None, min_length=1, max_length=200)
    name_en: str | None = Field(default=None, min_length=1, max_length=200)
    logo_url: str | None = None
    primary_color: str | None = None
    default_language: Language | None = None
    default_country: Country | None = None
    default_currency: str | None = None
    custom_domain: str | None = None
    subscription_tier: str | None = Field(
        default=None, pattern=r"^(starter|professional|enterprise)$"
    )
    is_active: bool | None = None


class OrgSettingsUpdate(BaseModel):
    primary_color: str | None = None
    settings: dict | None = None
    approval_workflow_enabled: bool | None = None
    draft_expiry_days: int | None = None
    data_retention_months: int | None = None
    allowed_file_types: list[str] | None = None
    max_batch_size: int | None = None
    customer_profiles_enabled: bool | None = None
    hijri_date_support: bool | None = None
    notification_preferences: dict | None = None


class OrgResponse(BaseModel):
    id: UUID
    name_ar: str
    name_en: str
    logo_url: str | None = None
    primary_color: str | None = None
    default_language: str
    default_country: str
    default_currency: str
    custom_domain: str | None = None
    settings: dict
    subscription_tier: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class DepartmentCreate(BaseModel):
    name_ar: str = Field(..., min_length=1, max_length=200)
    name_en: str = Field(..., min_length=1, max_length=200)


class DepartmentUpdate(BaseModel):
    name_ar: str | None = Field(default=None, min_length=1, max_length=200)
    name_en: str | None = Field(default=None, min_length=1, max_length=200)


class DepartmentResponse(BaseModel):
    id: UUID
    org_id: UUID
    name_ar: str
    name_en: str
    is_active: bool
    created_at: datetime
    branch_count: int = 0
    user_count: int = 0


class BranchCreate(BaseModel):
    department_id: UUID
    name_ar: str = Field(..., min_length=1, max_length=200)
    name_en: str = Field(..., min_length=1, max_length=200)
    location: str | None = None


class BranchUpdate(BaseModel):
    name_ar: str | None = Field(default=None, min_length=1, max_length=200)
    name_en: str | None = Field(default=None, min_length=1, max_length=200)
    location: str | None = None


class BranchResponse(BaseModel):
    id: UUID
    department_id: UUID
    org_id: UUID
    name_ar: str
    name_en: str
    location: str | None = None
    is_active: bool
    created_at: datetime
    user_count: int = 0


class InvitationCreate(BaseModel):
    email: EmailStr
    role: Role = Role.VIEWER
    department_id: UUID | None = None
    branch_id: UUID | None = None


class InvitationResponse(BaseModel):
    id: UUID
    email: str
    token: UUID
    role: str
    org_id: UUID
    department_id: UUID | None = None
    branch_id: UUID | None = None
    invited_by: UUID
    status: str
    expires_at: datetime
    accepted_at: datetime | None = None
    created_at: datetime


class InvitationAcceptRequest(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=200)
    password: str = Field(..., min_length=8, max_length=128)


class OrgBrandingResponse(BaseModel):
    name_ar: str
    name_en: str
    logo_url: str | None
    primary_color: str | None
    default_language: str


class UserRoleAssignment(BaseModel):
    department_id: UUID | None = None
    branch_id: UUID | None = None
    role: Role | None = None

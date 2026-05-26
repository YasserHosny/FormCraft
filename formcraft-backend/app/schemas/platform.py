"""Platform admin DTOs (F039)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import Country, Currency, Language


class OrganizationSummary(BaseModel):
    id: UUID
    name_ar: str
    name_en: str | None = None
    subscription_tier: str
    status: str
    active_users_count: int = 0
    templates_count: int = 0
    submissions_this_month: int = 0
    created_at: datetime


class OrganizationCreate(BaseModel):
    name_ar: str = Field(..., min_length=1, max_length=200)
    name_en: str | None = Field(default=None, min_length=1, max_length=200)
    default_language: Language = Language.AR
    default_country: Country = Country.SA
    default_currency: Currency = Currency.SAR
    subscription_tier: str = Field(
        default="starter", pattern=r"^(starter|professional|enterprise|platform)$"
    )
    domain: str | None = Field(default=None, max_length=255)


class OrganizationUpdate(BaseModel):
    name_ar: str | None = Field(default=None, min_length=1, max_length=200)
    name_en: str | None = Field(default=None, min_length=1, max_length=200)
    default_language: Language | None = None
    default_country: Country | None = None
    default_currency: Currency | None = None
    subscription_tier: str | None = Field(
        default=None, pattern=r"^(starter|professional|enterprise|platform)$"
    )
    domain: str | None = Field(default=None, max_length=255)
    logo_url: str | None = None
    branding: dict | None = None


class OrganizationDetail(BaseModel):
    id: UUID
    name_ar: str
    name_en: str | None = None
    default_language: str
    default_country: str
    default_currency: str
    subscription_tier: str
    status: str
    domain: str | None = None
    logo_url: str | None = None
    branding: dict | None = None
    active_users_count: int = 0
    templates_count: int = 0
    submissions_this_month: int = 0
    total_submissions: int = 0
    storage_usage: str | None = None
    created_at: datetime
    updated_at: datetime


class FirstAdminInvite(BaseModel):
    email: EmailStr


class TierLimitAlert(BaseModel):
    org_id: UUID
    org_name: str
    tier: str
    limit_type: str
    current_usage: int
    limit_value: int
    threshold_pct: float


class SubmissionVolumePoint(BaseModel):
    month: str
    count: int


class PlatformMetrics(BaseModel):
    total_orgs: int
    total_users: int
    total_submissions: int
    orgs_by_tier: dict[str, int]
    submission_volume_trend: list[SubmissionVolumePoint]
    recently_created_orgs: list[OrganizationSummary]
    tier_limit_alerts: list[TierLimitAlert]

"""Retention policy Pydantic models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class RetentionPolicyBase(BaseModel):
    name: dict[str, str] = Field(..., description="i18n object: {ar: ..., en: ...}")
    data_class: Literal[
        "submission",
        "customer_profile",
        "audit_log",
        "generated_pdf",
        "export_file",
        "portal_session",
        "report_archive",
    ]
    scope_json: dict = Field(default_factory=dict)
    action: Literal["archive", "purge", "mask", "retain"]
    period_days: int = Field(..., ge=1)
    legal_basis: str | None = None
    approval_required: bool = True
    effective_date: datetime


class RetentionPolicyCreate(RetentionPolicyBase):
    pass


class RetentionPolicyUpdate(BaseModel):
    name: dict[str, str] | None = None
    data_class: str | None = None
    scope_json: dict | None = None
    action: str | None = None
    period_days: int | None = Field(None, ge=1)
    legal_basis: str | None = None
    approval_required: bool | None = None
    effective_date: datetime | None = None


class RetentionPolicyResponse(RetentionPolicyBase):
    id: UUID
    org_id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

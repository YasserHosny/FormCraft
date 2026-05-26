"""Retention Pydantic schemas for API request/response validation."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


# ------------------------------------------------------------------
# Retention Policy
# ------------------------------------------------------------------

class PolicyCreate(BaseModel):
    name: dict[str, str]
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


class PolicyUpdate(BaseModel):
    name: dict[str, str] | None = None
    data_class: str | None = None
    scope_json: dict | None = None
    action: str | None = None
    period_days: int | None = Field(None, ge=1)
    legal_basis: str | None = None
    approval_required: bool | None = None
    effective_date: datetime | None = None


class PolicyResponse(BaseModel):
    id: UUID
    org_id: UUID
    name: dict[str, str]
    data_class: str
    scope_json: dict
    action: str
    period_days: int
    legal_basis: str | None
    approval_required: bool
    effective_date: datetime
    created_by: UUID
    created_at: datetime
    updated_at: datetime


# ------------------------------------------------------------------
# Retention Job
# ------------------------------------------------------------------

class JobCreate(BaseModel):
    policy_id: UUID
    batch_size: int = Field(default=1000, ge=1, le=10000)


class JobResponse(BaseModel):
    id: UUID
    policy_id: UUID
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    batch_size: int
    checkpoint_cursor: str | None
    evaluated_count: int
    actioned_count: int
    error_count: int
    error_log: list[dict]
    skipped_records: list[dict]
    manifest_id: UUID | None
    resumed_from_job_id: UUID | None
    created_at: datetime
    updated_at: datetime


# ------------------------------------------------------------------
# Legal Hold
# ------------------------------------------------------------------

class HoldCreate(BaseModel):
    hold_type: Literal["investigation", "dispute", "regulatory"]
    scope_type: Literal["submission", "customer", "template", "export", "audit_evidence"]
    scope_id: UUID
    reason: str
    expiry_date: datetime | None = None


class HoldResponse(BaseModel):
    id: UUID
    org_id: UUID
    hold_type: str
    scope_type: str
    scope_id: UUID
    reason: str
    expiry_date: datetime | None
    created_by: UUID
    created_at: datetime
    updated_at: datetime


# ------------------------------------------------------------------
# Archive Manifest
# ------------------------------------------------------------------

class ManifestResponse(BaseModel):
    id: UUID
    job_id: UUID
    record_count: int
    schema_location: str
    cold_storage_uri: str | None
    sha256_hash: str
    integrity_status: str
    restore_conditions: dict
    created_at: datetime


# ------------------------------------------------------------------
# Privacy Request
# ------------------------------------------------------------------

class PrivacyRequestCreate(BaseModel):
    request_type: Literal["export", "delete", "mask", "restrict"]
    scope_type: Literal["customer", "submission"]
    scope_id: UUID


class PrivacyRequestResolve(BaseModel):
    status: Literal["approved", "rejected"]
    resolution: dict | None = None


class PrivacyRequestResponse(BaseModel):
    id: UUID
    org_id: UUID
    request_type: str
    scope_type: str
    scope_id: UUID
    status: str
    conflict_hold_id: UUID | None
    resolution: dict | None
    created_by: UUID
    created_at: datetime
    updated_at: datetime


# ------------------------------------------------------------------
# Preview
# ------------------------------------------------------------------

class PreviewResponse(BaseModel):
    affected_count: int
    date_range: dict[str, str]
    affected_forms: list[str]
    blocked_records: int
    blocked_reason: str
    downstream_references: dict[str, int]

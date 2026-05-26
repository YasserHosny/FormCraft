"""Privacy request Pydantic models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class PrivacyRequestBase(BaseModel):
    request_type: Literal["export", "delete", "mask", "restrict"]
    scope_type: Literal["customer", "submission"]
    scope_id: UUID
    status: Literal["pending", "approved", "rejected", "completed", "failed"] = "pending"
    conflict_hold_id: UUID | None = None
    resolution: dict | None = None


class PrivacyRequestCreate(PrivacyRequestBase):
    pass


class PrivacyRequestResolve(BaseModel):
    status: Literal["approved", "rejected"]
    resolution: dict | None = None


class PrivacyRequestResponse(PrivacyRequestBase):
    id: UUID
    org_id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

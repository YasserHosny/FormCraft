"""Legal hold Pydantic models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class LegalHoldBase(BaseModel):
    hold_type: Literal["investigation", "dispute", "regulatory"]
    scope_type: Literal["submission", "customer", "template", "export", "audit_evidence"]
    scope_id: UUID
    reason: str
    expiry_date: datetime | None = None


class LegalHoldCreate(LegalHoldBase):
    pass


class LegalHoldResponse(LegalHoldBase):
    id: UUID
    org_id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

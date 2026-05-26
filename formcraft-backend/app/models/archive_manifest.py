"""Archive manifest Pydantic models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ArchiveManifestBase(BaseModel):
    job_id: UUID
    record_count: int = Field(..., ge=0)
    schema_location: str
    cold_storage_uri: str | None = None
    sha256_hash: str
    integrity_status: Literal["verified", "failed", "pending"] = "verified"
    restore_conditions: dict = Field(default_factory=dict)


class ArchiveManifestCreate(ArchiveManifestBase):
    pass


class ArchiveManifestResponse(ArchiveManifestBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

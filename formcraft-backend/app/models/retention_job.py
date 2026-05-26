"""Retention job Pydantic models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class RetentionJobBase(BaseModel):
    policy_id: UUID
    status: Literal["pending", "running", "paused", "completed", "failed"] = "pending"
    batch_size: int = Field(default=1000, ge=1, le=10000)
    checkpoint_cursor: str | None = None
    evaluated_count: int = 0
    actioned_count: int = 0
    error_count: int = 0
    error_log: list[dict] = Field(default_factory=list)
    skipped_records: list[dict] = Field(default_factory=list)
    manifest_id: UUID | None = None
    resumed_from_job_id: UUID | None = None


class RetentionJobCreate(RetentionJobBase):
    pass


class RetentionJobResponse(RetentionJobBase):
    id: UUID
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

"""Retention job-specific schemas."""

from __future__ import annotations

from pydantic import BaseModel


class JobPauseRequest(BaseModel):
    reason: str | None = None


class JobResumeRequest(BaseModel):
    pass


class RestoreRequest(BaseModel):
    reason: str
    approval_override: bool = False


class RestoreResponse(BaseModel):
    restore_job_id: str
    status: str

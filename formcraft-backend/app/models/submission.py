from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Submission(BaseModel):
    id: UUID
    template_id: UUID
    template_version: int
    operator_id: UUID
    org_id: UUID
    field_values: dict = {}
    reference_number: str
    status: str = "printed"
    created_at: datetime


class Draft(BaseModel):
    id: UUID
    template_id: UUID
    template_version: int
    operator_id: UUID
    org_id: UUID
    field_values: dict = {}
    completion_percent: int = 0
    name: str | None = None
    expires_at: datetime
    created_at: datetime
    updated_at: datetime
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class OperatorPin(BaseModel):
    id: UUID
    operator_id: UUID
    template_id: UUID
    org_id: UUID
    created_at: datetime


class NotificationDismissal(BaseModel):
    id: UUID
    operator_id: UUID
    template_id: UUID
    dismissed_version: int
    org_id: UUID
    created_at: datetime
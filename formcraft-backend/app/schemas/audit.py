from uuid import UUID

from pydantic import BaseModel


class AuditLogEntry(BaseModel):
    id: UUID
    user_id: UUID
    action: str
    resource_type: str
    resource_id: str | None
    metadata: dict
    ip_address: str | None
    created_at: str


class AuditLogQueryParams(BaseModel):
    user_id: UUID | None = None
    action: str | None = None
    resource_type: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    page: int = 1
    limit: int = 50

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class OrgCategory(BaseModel):
    id: UUID
    org_id: UUID
    name: str
    is_system_default: bool = False
    sort_order: int = 0
    created_at: datetime
    updated_at: datetime

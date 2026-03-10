from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import Language, Role


class UserProfile(BaseModel):
    id: UUID
    role: Role = Role.VIEWER
    language: Language = Language.AR
    display_name: str | None = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None = None

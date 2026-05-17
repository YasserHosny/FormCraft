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
    org_id: UUID | None = None
    department_id: UUID | None = None
    branch_id: UUID | None = None
    is_platform_admin: bool = False
    invited_by: UUID | None = None
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import Language, Role


class UserProfileResponse(BaseModel):
    id: UUID
    email: str | None = None
    role: Role
    language: Language
    display_name: str | None
    is_active: bool
    org_id: UUID | None = None
    department_id: UUID | None = None
    branch_id: UUID | None = None
    is_platform_admin: bool = False


class UpdateProfileRequest(BaseModel):
    language: Language | None = None
    display_name: str | None = None


class UpdateRoleRequest(BaseModel):
    role: Role


class UserListQuery(BaseModel):
    page: int = 1
    limit: int = 20
    department_id: UUID | None = None
    branch_id: UUID | None = None
    role: Role | None = None
    is_active: bool | None = None
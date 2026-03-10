from uuid import UUID

from pydantic import BaseModel

from app.models.enums import Language, Role


class UserProfileResponse(BaseModel):
    id: UUID
    email: str
    role: Role
    language: Language
    display_name: str | None
    is_active: bool


class UpdateProfileRequest(BaseModel):
    language: Language | None = None
    display_name: str | None = None


class UpdateRoleRequest(BaseModel):
    role: Role

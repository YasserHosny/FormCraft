from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.models.enums import Language, Role
from app.models.user import UserProfile


class UserService:
    """User profile CRUD operations via Supabase."""

    def __init__(self, client: Client):
        self.client = client

    async def get_profile(self, user_id: UUID) -> UserProfile:
        result = (
            self.client.table("profiles")
            .select("*")
            .eq("id", str(user_id))
            .single()
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User profile not found")
        return UserProfile(**result.data)

    async def update_profile(
        self,
        user_id: UUID,
        language: Language | None = None,
        display_name: str | None = None,
    ) -> UserProfile:
        updates = {}
        if language is not None:
            updates["language"] = language.value
        if display_name is not None:
            updates["display_name"] = display_name
        if not updates:
            return await self.get_profile(user_id)

        result = (
            self.client.table("profiles")
            .update(updates)
            .eq("id", str(user_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User profile not found")
        return UserProfile(**result.data[0])

    async def create_user(
        self,
        email: str,
        password: str,
        role: Role = Role.VIEWER,
        display_name: str | None = None,
    ) -> UserProfile:
        # Create auth user via Supabase Admin API
        auth_response = self.client.auth.admin.create_user(
            {"email": email, "password": password, "email_confirm": True}
        )
        user_id = auth_response.user.id

        # Create profile
        profile_data = {
            "id": str(user_id),
            "role": role.value,
            "language": Language.AR.value,
            "display_name": display_name,
            "is_active": True,
        }
        result = self.client.table("profiles").insert(profile_data).execute()
        return UserProfile(**result.data[0])

    async def list_users(
        self, page: int = 1, limit: int = 20
    ) -> tuple[list[UserProfile], int]:
        offset = (page - 1) * limit
        result = (
            self.client.table("profiles")
            .select("*", count="exact")
            .range(offset, offset + limit - 1)
            .order("created_at", desc=True)
            .execute()
        )
        profiles = [UserProfile(**row) for row in result.data]
        return profiles, result.count or 0

    async def update_role(self, user_id: UUID, role: Role) -> UserProfile:
        result = (
            self.client.table("profiles")
            .update({"role": role.value})
            .eq("id", str(user_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User profile not found")
        return UserProfile(**result.data[0])

    async def deactivate_user(self, user_id: UUID) -> UserProfile:
        result = (
            self.client.table("profiles")
            .update({"is_active": False})
            .eq("id", str(user_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User profile not found")
        return UserProfile(**result.data[0])

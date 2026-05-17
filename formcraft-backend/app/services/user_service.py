from datetime import datetime, timezone
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
        org_id: UUID | None = None,
        department_id: UUID | None = None,
        branch_id: UUID | None = None,
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
        if org_id is not None:
            profile_data["org_id"] = str(org_id)
        if department_id is not None:
            profile_data["department_id"] = str(department_id)
        if branch_id is not None:
            profile_data["branch_id"] = str(branch_id)

        result = self.client.table("profiles").insert(profile_data).execute()
        return UserProfile(**result.data[0])

    async def list_users(
        self,
        page: int = 1,
        limit: int = 20,
        org_id: UUID | None = None,
        department_id: UUID | None = None,
        branch_id: UUID | None = None,
        role: str | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> tuple[list[UserProfile], int]:
        offset = (page - 1) * limit
        query = self.client.table("profiles").select("*", count="exact")

        if org_id is not None:
            query = query.eq("org_id", str(org_id))
        if department_id is not None:
            query = query.eq("department_id", str(department_id))
        if branch_id is not None:
            query = query.eq("branch_id", str(branch_id))
        if role is not None:
            query = query.eq("role", role)
        if is_active is not None:
            query = query.eq("is_active", is_active)
        if search:
            query = query.ilike("display_name", f"%{search}%")

        result = (
            query.range(offset, offset + limit - 1)
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

    async def update_user_assignment(
        self,
        user_id: UUID,
        org_id: UUID,
        department_id: UUID | None = None,
        branch_id: UUID | None = None,
        role: str | None = None,
    ) -> UserProfile:
        """Update a user's department, branch, and/or role assignment within an org."""
        updates: dict = {}
        if department_id is not None:
            updates["department_id"] = str(department_id)
        if branch_id is not None:
            updates["branch_id"] = str(branch_id)
        if role is not None:
            updates["role"] = role
        if not updates:
            return await self.get_profile(user_id)

        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        result = (
            self.client.table("profiles")
            .update(updates)
            .eq("id", str(user_id))
            .eq("org_id", str(org_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "User profile not found in this organization",
            )
        return UserProfile(**result.data[0])

    async def deactivate_user(
        self, user_id: UUID, org_id: UUID | None = None
    ) -> UserProfile:
        query = (
            self.client.table("profiles")
            .update({"is_active": False, "updated_at": datetime.now(timezone.utc).isoformat()})
            .eq("id", str(user_id))
        )
        if org_id is not None:
            query = query.eq("org_id", str(org_id))
        result = query.execute()
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User profile not found")
        return UserProfile(**result.data[0])

    async def activate_user(
        self, user_id: UUID, org_id: UUID | None = None
    ) -> UserProfile:
        query = (
            self.client.table("profiles")
            .update({"is_active": True, "updated_at": datetime.now(timezone.utc).isoformat()})
            .eq("id", str(user_id))
        )
        if org_id is not None:
            query = query.eq("org_id", str(org_id))
        result = query.execute()
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User profile not found")
        return UserProfile(**result.data[0])

    async def update_last_login(self, user_id: UUID) -> None:
        """Update the last_login_at timestamp (fire-and-forget from login flow)."""
        self.client.table("profiles").update(
            {"last_login_at": datetime.now(timezone.utc).isoformat()}
        ).eq("id", str(user_id)).execute()

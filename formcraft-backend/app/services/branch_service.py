"""Branch CRUD service (T016)."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.core.audit import AuditLogger


class BranchService:
    """Handles branch lifecycle within a department / organisation."""

    def __init__(self, client: Client):
        self.client = client
        self.audit = AuditLogger(client)

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------

    async def create_branch(
        self, dept_id: UUID, org_id: UUID, data: dict, created_by: UUID
    ) -> dict:
        # Verify department belongs to the organisation
        dept = (
            self.client.table("departments")
            .select("id")
            .eq("id", str(dept_id))
            .eq("org_id", str(org_id))
            .execute()
        )
        if not dept.data:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Department does not belong to this organization",
            )

        row = {**data, "department_id": str(dept_id), "org_id": str(org_id)}
        result = self.client.table("branches").insert(row).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create branch",
            )
        branch = result.data[0]
        await self.audit.log_event(
            user_id=str(created_by),
            action="branch_created",
            resource_type="branch",
            resource_id=branch["id"],
            metadata={
                "name_en": branch.get("name_en"),
                "department_id": str(dept_id),
            },
        )
        return branch

    # ------------------------------------------------------------------
    # LIST (scoped to a department)
    # ------------------------------------------------------------------

    async def list_branches(
        self, dept_id: UUID, org_id: UUID, include_inactive: bool = False
    ) -> list[dict]:
        query = (
            self.client.table("branches")
            .select("*")
            .eq("department_id", str(dept_id))
            .eq("org_id", str(org_id))
        )
        if not include_inactive:
            query = query.eq("is_active", True)
        result = query.order("name_en").execute()
        branches = result.data or []

        for b in branches:
            uc = (
                self.client.table("profiles")
                .select("id", count="exact")
                .eq("branch_id", b["id"])
                .eq("is_active", True)
                .execute()
            )
            b["user_count"] = uc.count or 0

        return branches

    # ------------------------------------------------------------------
    # LIST ALL (flat list for whole org, includes department info)
    # ------------------------------------------------------------------

    async def list_all_branches(self, org_id: UUID) -> list[dict]:
        result = (
            self.client.table("branches")
            .select("*, departments(name_en, name_ar)")
            .eq("org_id", str(org_id))
            .eq("is_active", True)
            .order("name_en")
            .execute()
        )
        return result.data or []

    # ------------------------------------------------------------------
    # GET
    # ------------------------------------------------------------------

    async def get_branch(self, branch_id: UUID, org_id: UUID) -> dict:
        result = (
            self.client.table("branches")
            .select("*")
            .eq("id", str(branch_id))
            .eq("org_id", str(org_id))
            .single()
            .execute()
        )
        raw = result.data
        if isinstance(raw, list):
            raw = raw[0] if raw else None
        if not raw:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Branch not found",
            )
        return raw

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    async def update_branch(
        self, branch_id: UUID, org_id: UUID, data: dict, updated_by: UUID
    ) -> dict:
        result = (
            self.client.table("branches")
            .update(data)
            .eq("id", str(branch_id))
            .eq("org_id", str(org_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Branch not found",
            )
        await self.audit.log_event(
            user_id=str(updated_by),
            action="branch_updated",
            resource_type="branch",
            resource_id=str(branch_id),
            metadata=data,
        )
        return result.data[0]

    # ------------------------------------------------------------------
    # DEACTIVATE
    # ------------------------------------------------------------------

    async def deactivate_branch(
        self, branch_id: UUID, org_id: UUID, updated_by: UUID
    ) -> dict:
        uc = (
            self.client.table("profiles")
            .select("id", count="exact")
            .eq("branch_id", str(branch_id))
            .eq("is_active", True)
            .execute()
        )
        if (uc.count or 0) > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Branch has active users — reassign them before deactivating",
            )

        result = (
            self.client.table("branches")
            .update({"is_active": False})
            .eq("id", str(branch_id))
            .eq("org_id", str(org_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Branch not found",
            )
        await self.audit.log_event(
            user_id=str(updated_by),
            action="branch_deactivated",
            resource_type="branch",
            resource_id=str(branch_id),
        )
        return result.data[0]

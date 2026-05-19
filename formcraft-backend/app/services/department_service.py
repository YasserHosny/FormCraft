"""Department CRUD service (T015)."""

from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.core.audit import AuditLogger


class DepartmentService:
    """Handles department lifecycle within an organisation."""

    def __init__(self, client: Client):
        self.client = client
        self.audit = AuditLogger(client)

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------

    async def create_department(
        self, org_id: UUID, data: dict, created_by: UUID
    ) -> dict:
        row = {**data, "org_id": str(org_id)}
        result = self.client.table("departments").insert(row).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create department",
            )
        dept = result.data[0]
        await self.audit.log_event(
            user_id=str(created_by),
            action="department_created",
            resource_type="department",
            resource_id=dept["id"],
            metadata={"name_en": dept.get("name_en"), "org_id": str(org_id)},
        )
        return dept

    # ------------------------------------------------------------------
    # LIST
    # ------------------------------------------------------------------

    async def list_departments(
        self, org_id: UUID, include_inactive: bool = False
    ) -> list[dict]:
        query = (
            self.client.table("departments")
            .select("*")
            .eq("org_id", str(org_id))
        )
        if not include_inactive:
            query = query.eq("is_active", True)
        result = query.order("name_en").execute()
        depts = result.data or []

        for dept in depts:
            bc = (
                self.client.table("branches")
                .select("id", count="exact")
                .eq("department_id", dept["id"])
                .execute()
            )
            dept["branch_count"] = bc.count or 0

            uc = (
                self.client.table("profiles")
                .select("id", count="exact")
                .eq("department_id", dept["id"])
                .eq("is_active", True)
                .execute()
            )
            dept["user_count"] = uc.count or 0

        return depts

    # ------------------------------------------------------------------
    # GET
    # ------------------------------------------------------------------

    async def get_department(self, dept_id: UUID, org_id: UUID) -> dict:
        result = (
            self.client.table("departments")
            .select("*")
            .eq("id", str(dept_id))
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
                detail="Department not found",
            )
        return raw

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    async def update_department(
        self, dept_id: UUID, org_id: UUID, data: dict, updated_by: UUID
    ) -> dict:
        result = (
            self.client.table("departments")
            .update(data)
            .eq("id", str(dept_id))
            .eq("org_id", str(org_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found",
            )
        await self.audit.log_event(
            user_id=str(updated_by),
            action="department_updated",
            resource_type="department",
            resource_id=str(dept_id),
            metadata=data,
        )
        return result.data[0]

    # ------------------------------------------------------------------
    # DEACTIVATE
    # ------------------------------------------------------------------

    async def deactivate_department(
        self, dept_id: UUID, org_id: UUID, updated_by: UUID
    ) -> dict:
        uc = (
            self.client.table("profiles")
            .select("id", count="exact")
            .eq("department_id", str(dept_id))
            .eq("is_active", True)
            .execute()
        )
        if (uc.count or 0) > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department has active users — reassign them before deactivating",
            )

        result = (
            self.client.table("departments")
            .update({"is_active": False})
            .eq("id", str(dept_id))
            .eq("org_id", str(org_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found",
            )
        await self.audit.log_event(
            user_id=str(updated_by),
            action="department_deactivated",
            resource_type="department",
            resource_id=str(dept_id),
        )
        return result.data[0]

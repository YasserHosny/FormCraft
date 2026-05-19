"""Organisation CRUD service (T014)."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.core.audit import AuditLogger


class OrganizationService:
    """Handles organisation lifecycle operations."""

    def __init__(self, client: Client):
        self.client = client
        self.audit = AuditLogger(client)

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------

    async def create_org(self, data: dict, created_by: UUID) -> dict:
        result = self.client.table("organizations").insert(data).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create organization",
            )
        org = result.data[0]
        await self.audit.log_event(
            user_id=str(created_by),
            action="org_created",
            resource_type="organization",
            resource_id=org["id"],
            metadata={"name_en": org.get("name_en")},
        )
        return org

    # ------------------------------------------------------------------
    # LIST (platform-admin level — all orgs)
    # ------------------------------------------------------------------

    async def list_orgs(
        self,
        page: int = 1,
        limit: int = 20,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[dict], int]:
        offset = (page - 1) * limit
        query = self.client.table("organizations").select("*", count="exact")
        if is_active is not None:
            query = query.eq("is_active", is_active)
        if search:
            query = query.or_(f"name_en.ilike.%{search}%,name_ar.ilike.%{search}%")
        result = (
            query.order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return result.data or [], result.count or 0

    # ------------------------------------------------------------------
    # GET
    # ------------------------------------------------------------------

    async def get_org(self, org_id: UUID) -> dict:
        result = (
            self.client.table("organizations")
            .select("*")
            .eq("id", str(org_id))
            .single()
            .execute()
        )
        raw = result.data
        if isinstance(raw, list):
            raw = raw[0] if raw else None
        if not raw:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
        return raw

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    async def update_org(self, org_id: UUID, data: dict, updated_by: UUID) -> dict:
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        result = (
            self.client.table("organizations")
            .update(data)
            .eq("id", str(org_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
        await self.audit.log_event(
            user_id=str(updated_by),
            action="org_updated",
            resource_type="organization",
            resource_id=str(org_id),
            metadata=data,
        )
        return result.data[0]

    # ------------------------------------------------------------------
    # SETTINGS
    # ------------------------------------------------------------------

    async def get_org_settings(self, org_id: UUID) -> dict:
        return await self.get_org(org_id)

    async def update_org_settings(
        self, org_id: UUID, data: dict, updated_by: UUID
    ) -> dict:
        updates: dict = {}
        if "primary_color" in data and data["primary_color"] is not None:
            updates["primary_color"] = data["primary_color"]
        if "settings" in data and data["settings"] is not None:
            org = await self.get_org(org_id)
            merged = {**(org.get("settings") or {}), **data["settings"]}
            updates["settings"] = merged
        if not updates:
            return await self.get_org(org_id)

        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        result = (
            self.client.table("organizations")
            .update(updates)
            .eq("id", str(org_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
        await self.audit.log_event(
            user_id=str(updated_by),
            action="org_settings_updated",
            resource_type="organization",
            resource_id=str(org_id),
            metadata=updates,
        )
        return result.data[0]

    # ------------------------------------------------------------------
    # LOGO
    # ------------------------------------------------------------------

    async def upload_logo(
        self,
        org_id: UUID,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        updated_by: UUID,
    ) -> str:
        path = f"org-logos/{org_id}/{filename}"
        self.client.storage.from_("assets").upload(
            path, file_bytes, {"content-type": content_type}
        )
        logo_url = self.client.storage.from_("assets").get_public_url(path)
        self.client.table("organizations").update(
            {"logo_url": logo_url, "updated_at": datetime.now(timezone.utc).isoformat()}
        ).eq("id", str(org_id)).execute()
        await self.audit.log_event(
            user_id=str(updated_by),
            action="org_logo_uploaded",
            resource_type="organization",
            resource_id=str(org_id),
            metadata={"filename": filename},
        )
        return logo_url

    # ------------------------------------------------------------------
    # BRANDING (public — by custom domain)
    # ------------------------------------------------------------------

    async def get_branding_by_domain(self, domain: str) -> dict | None:
        result = (
            self.client.table("organizations")
            .select("id,name_ar,name_en,logo_url,primary_color,default_language")
            .eq("custom_domain", domain)
            .eq("is_active", True)
            .execute()
        )
        data = result.data
        if not data:
            return None
        return data[0]

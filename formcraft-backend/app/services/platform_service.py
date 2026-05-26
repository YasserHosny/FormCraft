"""Platform admin service (F039)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.core.audit import AuditLogger


class PlatformService:
    """Handles platform-level organization management."""

    def __init__(self, client: Client):
        self.client = client
        self.audit = AuditLogger(client)

    # ------------------------------------------------------------------
    # LIST
    # ------------------------------------------------------------------

    async def list_organizations(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        tier: str | None = None,
        status: str | None = None,
        country: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[dict], int]:
        offset = (page - 1) * page_size
        query = self.client.table("organizations").select("*", count="exact")

        if tier:
            query = query.eq("subscription_tier", tier)
        if status:
            query = query.eq("status", status)
        if country:
            query = query.eq("default_country", country)
        if search:
            query = query.or_(f"name_ar.ilike.%{search}%,name_en.ilike.%{search}%")

        order = {"asc": True, "desc": False}.get(sort_order, False)
        query = query.order(sort_by, desc=order)

        result = query.range(offset, offset + page_size - 1).execute()
        total = result.count if result.count is not None else 0
        orgs = result.data or []

        # Enrich with computed counts
        for org in orgs:
            org["active_users_count"] = await self._count_users(org["id"])
            org["templates_count"] = await self._count_templates(org["id"])
            org["submissions_this_month"] = await self._count_submissions_this_month(org["id"])

        return orgs, total

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------

    async def create_organization(
        self, data: dict, created_by: UUID
    ) -> dict:
        # Rate limit check
        await self._check_creation_rate_limit(created_by)

        # Domain uniqueness check
        domain = data.get("domain")
        if domain:
            existing = (
                self.client.table("organizations")
                .select("id")
                .eq("domain", domain)
                .execute()
            )
            if existing.data:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Domain already assigned to another organization.",
                )

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
            metadata={
                "name_ar": org.get("name_ar"),
                "subscription_tier": org.get("subscription_tier"),
            },
        )
        return org

    async def _check_creation_rate_limit(self, user_id: UUID) -> None:
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        result = (
            self.client.table("audit_logs")
            .select("id", count="exact")
            .eq("user_id", str(user_id))
            .eq("action", "org_created")
            .gte("created_at", one_hour_ago.isoformat())
            .execute()
        )
        count = result.count or 0
        if count >= 10:
            await self.audit.log_event(
                user_id=str(user_id),
                action="org_creation_rate_limited",
                resource_type="platform",
                metadata={"attempted_count": count + 1},
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Organization creation rate limit exceeded (10 per hour).",
            )

    # ------------------------------------------------------------------
    # GET DETAIL
    # ------------------------------------------------------------------

    async def get_organization_detail(self, org_id: UUID) -> dict:
        result = (
            self.client.table("organizations")
            .select("*")
            .eq("id", str(org_id))
            .single()
            .execute()
        )
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
        org = result.data
        org["active_users_count"] = await self._count_users(org_id)
        org["templates_count"] = await self._count_templates(org_id)
        org["submissions_this_month"] = await self._count_submissions_this_month(org_id)
        org["total_submissions"] = await self._count_total_submissions(org_id)
        return org

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    async def update_organization(
        self, org_id: UUID, data: dict, updated_by: UUID
    ) -> dict:
        domain = data.get("domain")
        if domain:
            existing = (
                self.client.table("organizations")
                .select("id")
                .eq("domain", domain)
                .neq("id", str(org_id))
                .execute()
            )
            if existing.data:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Domain already assigned to another organization.",
                )

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
        org = result.data[0]
        await self.audit.log_event(
            user_id=str(updated_by),
            action="org_updated",
            resource_type="organization",
            resource_id=str(org_id),
            metadata={"fields": list(data.keys())},
        )
        return org

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------

    async def delete_organization(self, org_id: UUID, deleted_by: UUID) -> None:
        # Check for submissions
        subs = (
            self.client.table("submissions")
            .select("id", count="exact")
            .eq("org_id", str(org_id))
            .execute()
        )
        if subs.count and subs.count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete organization with active submissions. Suspend instead.",
            )

        self.client.table("organizations").delete().eq("id", str(org_id)).execute()
        await self.audit.log_event(
            user_id=str(deleted_by),
            action="org_deleted",
            resource_type="organization",
            resource_id=str(org_id),
        )

    # ------------------------------------------------------------------
    # SUSPEND / REACTIVATE
    # ------------------------------------------------------------------

    async def suspend_organization(self, org_id: UUID, admin_id: UUID) -> dict:
        # Revoke all active sessions for users in this org
        users = (
            self.client.table("profiles")
            .select("id")
            .eq("org_id", str(org_id))
            .execute()
        )
        for user in users.data or []:
            try:
                self.client.auth.admin.sign_out(user["id"])
            except Exception:
                # Best-effort session revocation; log but don't fail
                pass

        result = (
            self.client.table("organizations")
            .update({"status": "suspended"})
            .eq("id", str(org_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
        org = result.data[0]
        await self.audit.log_event(
            user_id=str(admin_id),
            action="org_suspended",
            resource_type="organization",
            resource_id=str(org_id),
        )
        return org

    async def reactivate_organization(self, org_id: UUID, admin_id: UUID) -> dict:
        result = (
            self.client.table("organizations")
            .update({"status": "active"})
            .eq("id", str(org_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
        org = result.data[0]
        await self.audit.log_event(
            user_id=str(admin_id),
            action="org_reactivated",
            resource_type="organization",
            resource_id=str(org_id),
        )
        return org

    # ------------------------------------------------------------------
    # INVITE FIRST ADMIN
    # ------------------------------------------------------------------

    async def invite_first_admin(
        self, org_id: UUID, email: str, invited_by: UUID
    ) -> dict:
        # Use existing invitation service or infrastructure
        from app.services.invitation_service import InvitationService

        invite_service = InvitationService(self.client)
        invite = await invite_service.create_invitation(
            org_id=org_id,
            email=email,
            role="admin",
            invited_by=invited_by,
        )
        await self.audit.log_event(
            user_id=str(invited_by),
            action="first_admin_invited",
            resource_type="organization",
            resource_id=str(org_id),
            metadata={"email": email},
        )
        return invite

    # ------------------------------------------------------------------
    # COMPUTED COUNT HELPERS
    # ------------------------------------------------------------------

    async def _count_users(self, org_id: UUID) -> int:
        result = (
            self.client.table("profiles")
            .select("id", count="exact")
            .eq("org_id", str(org_id))
            .execute()
        )
        return result.count or 0

    async def _count_templates(self, org_id: UUID) -> int:
        result = (
            self.client.table("templates")
            .select("id", count="exact")
            .eq("org_id", str(org_id))
            .execute()
        )
        return result.count or 0

    async def _count_submissions_this_month(self, org_id: UUID) -> int:
        start_of_month = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        result = (
            self.client.table("submissions")
            .select("id", count="exact")
            .eq("org_id", str(org_id))
            .gte("created_at", start_of_month.isoformat())
            .execute()
        )
        return result.count or 0

    async def _count_total_submissions(self, org_id: UUID) -> int:
        result = (
            self.client.table("submissions")
            .select("id", count="exact")
            .eq("org_id", str(org_id))
            .execute()
        )
        return result.count or 0

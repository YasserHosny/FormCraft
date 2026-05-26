"""Platform metrics service (F039)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from dateutil.relativedelta import relativedelta
from supabase import Client


class PlatformMetricsService:
    """Reads from the materialized view and computes derived metrics."""

    def __init__(self, client: Client):
        self.client = client

    async def get_metrics(self) -> dict:
        mv_result = (
            self.client.table("platform_metrics_mv")
            .select("*")
            .limit(1)
            .single()
            .execute()
        )
        mv = mv_result.data or {}

        # Compute submission volume trend for last 12 months
        trend = await self._submission_volume_trend()

        # Recently created orgs (last 30 days)
        recent_orgs = await self._recently_created_orgs()

        # Tier limit alerts
        alerts = await self._tier_limit_alerts()

        return {
            "total_orgs": mv.get("total_orgs", 0),
            "total_users": mv.get("total_users", 0),
            "total_submissions": mv.get("total_submissions", 0),
            "orgs_by_tier": mv.get("orgs_by_tier", {}),
            "submission_volume_trend": trend,
            "recently_created_orgs": recent_orgs,
            "tier_limit_alerts": alerts,
        }

    async def refresh_materialized_view(self) -> None:
        # Execute raw SQL to refresh the materialized view
        self.client.rpc("refresh_platform_metrics_mv", {}).execute()

    async def _submission_volume_trend(self) -> list[dict]:
        now = datetime.now(timezone.utc)
        points = []
        for i in range(11, -1, -1):
            month_start = now.replace(day=1) - relativedelta(months=i)
            month_end = month_start + relativedelta(months=1)
            result = (
                self.client.table("submissions")
                .select("id", count="exact")
                .gte("created_at", month_start.isoformat())
                .lt("created_at", month_end.isoformat())
                .execute()
            )
            points.append({
                "month": month_start.strftime("%Y-%m"),
                "count": result.count or 0,
            })
        return points

    async def _recently_created_orgs(self) -> list[dict]:
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        result = (
            self.client.table("organizations")
            .select("*")
            .gte("created_at", thirty_days_ago.isoformat())
            .order("created_at", desc=True)
            .limit(10)
            .execute()
        )
        orgs = result.data or []
        for org in orgs:
            org["active_users_count"] = await self._count_users(org["id"])
            org["templates_count"] = await self._count_templates(org["id"])
            org["submissions_this_month"] = await self._count_submissions_this_month(org["id"])
        return orgs

    async def _tier_limit_alerts(self) -> list[dict]:
        # Query orgs approaching tier limits
        result = self.client.rpc("get_tier_limit_alerts", {}).execute()
        return result.data or []

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

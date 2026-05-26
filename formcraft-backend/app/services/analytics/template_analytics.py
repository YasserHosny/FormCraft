"""Template usage analytics service."""

import logging
from datetime import date, datetime
from uuid import UUID

from supabase import Client

from app.schemas.analytics import (
    DepartmentUsageItem,
    FunnelData,
    TemplateUsageResponse,
    VersionAdoptionItem,
    VersionAdoptionResponse,
)
from app.services.analytics.base_analytics import apply_org_scope

logger = logging.getLogger(__name__)


class TemplateAnalyticsService:
    """Aggregate and retrieve template usage analytics."""

    def __init__(self, client: Client):
        self.client = client

    async def get_template_usage(
        self,
        org_id: UUID,
        template_id: UUID | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        group_by: str | None = None,
    ) -> TemplateUsageResponse:
        """Return template usage funnel and optional department breakdown."""
        # Query materialized view
        query = apply_org_scope(self.client, "mv_template_usage_funnel", org_id)
        if template_id:
            query = query.eq("template_id", str(template_id))
        if from_date:
            query = query.gte("day", from_date.isoformat())
        if to_date:
            query = query.lte("day", to_date.isoformat())

        response = query.execute()
        rows = response.data or []

        started = sum(r.get("started_count", 0) for r in rows)
        draft = sum(r.get("draft_count", 0) for r in rows)
        submitted = sum(r.get("submitted_count", 0) for r in rows)
        printed = sum(r.get("printed_count", 0) for r in rows)

        conversion_rates = {}
        if started > 0:
            conversion_rates["started_to_submitted"] = round(submitted / started, 3)
        if submitted > 0:
            conversion_rates["submitted_to_printed"] = round(printed / submitted, 3)

        # Department breakdown
        by_department: list[DepartmentUsageItem] | None = None
        if group_by == "department" and template_id:
            by_department = await self._get_department_breakdown(org_id, template_id, from_date, to_date)

        # Template metadata
        template_name = None
        if template_id:
            tpl_resp = (
                self.client.table("templates")
                .select("name")
                .eq("id", str(template_id))
                .single()
                .execute()
            )
            template_name = tpl_resp.data.get("name") if tpl_resp.data else None

        return TemplateUsageResponse(
            template_id=template_id,
            template_name=template_name,
            funnel=FunnelData(
                started_count=started,
                draft_count=draft,
                submitted_count=submitted,
                printed_count=printed,
                conversion_rates=conversion_rates,
            ),
            avg_fill_time_ms=None,  # Would aggregate from field_analytics or submissions telemetry
            by_department=by_department,
            computed_at=datetime.utcnow(),
        )

    async def get_version_adoption(
        self,
        org_id: UUID,
        template_id: UUID,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> VersionAdoptionResponse:
        """Return version adoption timeline for a template."""
        query = (
            apply_org_scope(self.client, "submissions", org_id)
            .select("template_version, created_at")
            .eq("template_id", str(template_id))
        )
        if from_date:
            query = query.gte("created_at", from_date.isoformat())
        if to_date:
            query = query.lte("created_at", to_date.isoformat())

        response = query.execute()
        rows = response.data or []

        # Aggregate counts per version per day
        counts: dict[tuple[int, date], int] = {}
        for row in rows:
            version = row.get("template_version", 0)
            created = row.get("created_at")
            if not created:
                continue
            dt = datetime.fromisoformat(created.replace("Z", "+00:00")).date()
            counts[(version, dt)] = counts.get((version, dt), 0) + 1

        # Compute daily totals for percentage
        daily_totals: dict[date, int] = {}
        for (version, day), cnt in counts.items():
            daily_totals[day] = daily_totals.get(day, 0) + cnt

        adoption = []
        for (version, day), cnt in sorted(counts.items()):
            total = daily_totals.get(day, 1)
            adoption.append(
                VersionAdoptionItem(
                    version=version,
                    day=day,
                    count=cnt,
                    pct_of_total=round(cnt / total, 3),
                )
            )

        template_name = None
        tpl_resp = (
            self.client.table("templates")
            .select("name")
            .eq("id", str(template_id))
            .single()
            .execute()
        )
        template_name = tpl_resp.data.get("name") if tpl_resp.data else None

        return VersionAdoptionResponse(
            template_id=template_id,
            template_name=template_name,
            adoption=adoption,
        )

    async def _get_department_breakdown(
        self,
        org_id: UUID,
        template_id: UUID,
        from_date: date | None,
        to_date: date | None,
    ) -> list[DepartmentUsageItem]:
        """Return usage breakdown by department."""
        query = (
            apply_org_scope(self.client, "submissions", org_id)
            .select("department_id, departments(name), count")
            .eq("template_id", str(template_id))
            .not_.is_("department_id", "null")
            .group("department_id, departments(name)")
        )
        if from_date:
            query = query.gte("created_at", from_date.isoformat())
        if to_date:
            query = query.lte("created_at", to_date.isoformat())

        response = query.execute()
        rows = response.data or []

        return [
            DepartmentUsageItem(
                department_id=r.get("department_id"),
                department_name=r.get("departments", {}).get("name", ""),
                submitted_count=r.get("count", 0),
            )
            for r in rows
        ]

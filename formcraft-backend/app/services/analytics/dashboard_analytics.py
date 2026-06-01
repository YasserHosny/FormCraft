"""Dashboard analytics service for real-time admin console KPIs and charts."""

import logging
from datetime import date, datetime, timedelta
from uuid import UUID

from cachetools import TTLCache
from supabase import Client

from app.schemas.analytics import (
    DashboardSummaryResponse,
    DepartmentDistributionResponse,
    DepartmentShareItem,
    SubmissionsOverTimeResponse,
    TimeSeriesPoint,
    TopTemplateItem,
    TopTemplatesResponse,
)
from app.services.analytics.base_analytics import apply_branch_scope, apply_org_scope, _period_to_dates

logger = logging.getLogger(__name__)


class DashboardAnalyticsService:
    """Aggregate and retrieve dashboard analytics for the admin console."""

    _cache: TTLCache = TTLCache(maxsize=1024, ttl=300)

    def __init__(self, client: Client):
        self.client = client

    @classmethod
    def _cache_key(cls, org_id: UUID | str, period: str, department_id: UUID | str | None, branch_id: UUID | str | None) -> tuple:
        return (str(org_id), period, str(department_id) if department_id else None, str(branch_id) if branch_id else None)

    def _build_submissions_query(
        self,
        org_id: UUID,
        from_date: date,
        to_date: date,
        department_id: UUID | None = None,
        branch_id: UUID | None = None,
    ):
        query = apply_branch_scope(self.client, "submissions", org_id, branch_id)
        query = query.gte("created_at", from_date.isoformat()).lte("created_at", to_date.isoformat())
        if department_id:
            query = query.eq("department_id", str(department_id))
        return query

    async def get_summary(
        self,
        org_id: UUID,
        period: str,
        department_id: UUID | None = None,
        branch_id: UUID | None = None,
    ) -> DashboardSummaryResponse:
        """Return dashboard summary KPIs for the org."""
        cache_key = ("summary",) + self._cache_key(org_id, period, department_id, branch_id)
        cached = self._cache.get(cache_key)
        if cached:
            return cached

        current_from, current_to, prev_from, prev_to = _period_to_dates(period)

        # Current period submissions
        current_query = self._build_submissions_query(org_id, current_from, current_to, department_id, branch_id)
        current_rows = current_query.execute().data or []
        total_forms_filled = len(current_rows)

        # Previous period submissions
        prev_query = self._build_submissions_query(org_id, prev_from, prev_to, department_id, branch_id)
        prev_rows = prev_query.execute().data or []
        total_forms_filled_prev = len(prev_rows)

        delta_pct = None
        if total_forms_filled_prev > 0:
            delta_pct = round(((total_forms_filled - total_forms_filled_prev) / total_forms_filled_prev) * 100, 2)

        # Unique customers
        unique_customers = len({r["customer_id"] for r in current_rows if r.get("customer_id")})

        # New customers this week (first submission within last 7 days)
        week_ago = date.today() - timedelta(days=7)
        week_query = apply_branch_scope(self.client, "submissions", org_id, branch_id)
        week_query = week_query.gte("created_at", week_ago.isoformat())
        if department_id:
            week_query = week_query.eq("department_id", str(department_id))
        week_rows = week_query.execute().data or []
        new_customers_this_week = len({r["customer_id"] for r in week_rows if r.get("customer_id")})

        # Templates count
        templates_query = apply_org_scope(self.client, "templates", org_id)
        all_templates = templates_query.execute().data or []
        active_templates = sum(1 for t in all_templates if t.get("status") == "published")
        total_templates = len(all_templates)

        # Avg fill time (submitted_at - started_at in ms)
        def _avg_fill_time(rows):
            times = []
            for r in rows:
                started = r.get("started_at")
                submitted = r.get("submitted_at")
                if started and submitted:
                    try:
                        s = datetime.fromisoformat(str(started).replace("Z", "+00:00"))
                        e = datetime.fromisoformat(str(submitted).replace("Z", "+00:00"))
                        times.append(int((e - s).total_seconds() * 1000))
                    except Exception:
                        pass
            return int(sum(times) / len(times)) if times else None

        avg_fill_time_ms = _avg_fill_time(current_rows)
        avg_fill_time_prev_ms = _avg_fill_time(prev_rows)

        fill_time_delta_pct = None
        if avg_fill_time_prev_ms and avg_fill_time_prev_ms > 0:
            fill_time_delta_pct = round(((avg_fill_time_ms - avg_fill_time_prev_ms) / avg_fill_time_prev_ms) * 100, 2)

        result = DashboardSummaryResponse(
            total_forms_filled=total_forms_filled,
            total_forms_filled_prev=total_forms_filled_prev,
            delta_pct=delta_pct,
            active_templates=active_templates,
            total_templates=total_templates,
            avg_fill_time_ms=avg_fill_time_ms,
            avg_fill_time_prev_ms=avg_fill_time_prev_ms,
            fill_time_delta_pct=fill_time_delta_pct,
            unique_customers=unique_customers,
            new_customers_this_week=new_customers_this_week,
            period=period,
            cache_expires_at=datetime.utcnow() + timedelta(seconds=300),
        )
        self._cache[cache_key] = result
        return result

    async def get_submissions_over_time(
        self,
        org_id: UUID,
        period: str,
        department_id: UUID | None = None,
        branch_id: UUID | None = None,
    ) -> SubmissionsOverTimeResponse:
        """Return daily or monthly submission counts for the trend line chart."""
        cache_key = ("submissions_over_time",) + self._cache_key(org_id, period, department_id, branch_id)
        cached = self._cache.get(cache_key)
        if cached:
            return cached

        current_from, current_to, _, _ = _period_to_dates(period)
        is_yearly = period == "yearly"
        granularity = "monthly" if is_yearly else "daily"

        query = self._build_submissions_query(org_id, current_from, current_to, department_id, branch_id)
        rows = query.execute().data or []

        # Group by date/month
        counts: dict[date, int] = {}
        for r in rows:
            created = r.get("created_at")
            if not created:
                continue
            try:
                dt = datetime.fromisoformat(str(created).replace("Z", "+00:00"))
                key = date(dt.year, dt.month, 1) if is_yearly else dt.date()
                counts[key] = counts.get(key, 0) + 1
            except Exception:
                pass

        # Zero-fill missing days/months
        points: list[TimeSeriesPoint] = []
        if is_yearly:
            key = current_from
            for _ in range(12):
                points.append(TimeSeriesPoint(date=key, count=counts.get(key, 0)))
                if key.month == 12:
                    key = date(key.year + 1, 1, 1)
                else:
                    key = date(key.year, key.month + 1, 1)
        else:
            delta = (current_to - current_from).days
            for i in range(delta + 1):
                key = current_from + timedelta(days=i)
                points.append(TimeSeriesPoint(date=key, count=counts.get(key, 0)))

        peak_count = max((p.count for p in points), default=0)
        peak_date = next((p.date for p in points if p.count == peak_count), None) if peak_count > 0 else None

        result = SubmissionsOverTimeResponse(
            points=points,
            peak_date=peak_date,
            peak_count=peak_count,
            granularity=granularity,
            cache_expires_at=datetime.utcnow() + timedelta(seconds=300),
        )
        self._cache[cache_key] = result
        return result

    async def get_department_distribution(
        self,
        org_id: UUID,
        period: str,
        branch_id: UUID | None = None,
    ) -> DepartmentDistributionResponse:
        """Return submission share by department for the donut chart."""
        cache_key = ("department_distribution",) + self._cache_key(org_id, period, None, branch_id)
        cached = self._cache.get(cache_key)
        if cached:
            return cached

        current_from, current_to, _, _ = _period_to_dates(period)
        query = self._build_submissions_query(org_id, current_from, current_to, None, branch_id)
        rows = query.execute().data or []

        # Count per department (exclude null department_id)
        dept_counts: dict[str, int] = {}
        for r in rows:
            dept_id = r.get("department_id")
            if dept_id:
                dept_counts[str(dept_id)] = dept_counts.get(str(dept_id), 0) + 1

        total = sum(dept_counts.values())

        # Fetch department names
        departments = []
        if dept_counts:
            dept_query = apply_org_scope(self.client, "departments", org_id)
            dept_rows = dept_query.execute().data or []
            dept_names = {str(d["id"]): d.get("name", "Unknown") for d in dept_rows}

            for dept_id, count in sorted(dept_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = round((count / total) * 100, 1) if total > 0 else 0.0
                departments.append(
                    DepartmentShareItem(
                        department_id=dept_id,
                        department_name=dept_names.get(dept_id, "Unknown"),
                        count=count,
                        percentage=percentage,
                    )
                )

        result = DepartmentDistributionResponse(
            departments=departments,
            total=total,
            cache_expires_at=datetime.utcnow() + timedelta(seconds=300),
        )
        self._cache[cache_key] = result
        return result

    async def get_top_templates(
        self,
        org_id: UUID,
        period: str,
        department_id: UUID | None = None,
        branch_id: UUID | None = None,
        limit: int = 7,
    ) -> TopTemplatesResponse:
        """Return the most-used templates for the bar chart."""
        cache_key = ("top_templates",) + self._cache_key(org_id, period, department_id, branch_id)
        cached = self._cache.get(cache_key)
        if cached:
            return cached

        current_from, current_to, _, _ = _period_to_dates(period)
        query = self._build_submissions_query(org_id, current_from, current_to, department_id, branch_id)
        rows = query.execute().data or []

        # Count per template
        template_counts: dict[str, int] = {}
        for r in rows:
            tid = r.get("template_id")
            if tid:
                template_counts[str(tid)] = template_counts.get(str(tid), 0) + 1

        # Fetch template names
        templates = []
        if template_counts:
            template_query = apply_org_scope(self.client, "templates", org_id)
            template_rows = template_query.execute().data or []
            template_info = {str(t["id"]): (t.get("name", "Unknown"), t.get("code", "")) for t in template_rows}

            for tid, count in sorted(template_counts.items(), key=lambda x: x[1], reverse=True)[:limit]:
                name, code = template_info.get(tid, ("Unknown", ""))
                templates.append(
                    TopTemplateItem(
                        template_id=tid,
                        template_name=name,
                        template_code=code,
                        count=count,
                    )
                )

        result = TopTemplatesResponse(
            templates=templates,
            cache_expires_at=datetime.utcnow() + timedelta(seconds=300),
        )
        self._cache[cache_key] = result
        return result

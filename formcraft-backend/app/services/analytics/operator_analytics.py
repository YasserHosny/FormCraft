"""Operator performance analytics service."""

import logging
from datetime import date, datetime
from uuid import UUID

from supabase import Client

from app.schemas.analytics import BusiestHoursResponse, HeatmapItem, OperatorAnalyticsItem, OperatorAnalyticsResponse
from app.services.analytics.base_analytics import apply_org_scope

logger = logging.getLogger(__name__)

COACHING_MULTIPLIER = 1.5


class OperatorAnalyticsService:
    """Aggregate and retrieve operator performance analytics."""

    def __init__(self, client: Client):
        self.client = client

    async def get_operator_analytics(
        self,
        org_id: UUID,
        period_type: str = "week",
        from_date: date | None = None,
        to_date: date | None = None,
        branch_id: UUID | None = None,
    ) -> OperatorAnalyticsResponse:
        """Return operator analytics for the org."""
        query = (
            apply_org_scope(self.client, "operator_analytics", org_id)
            .eq("period_type", period_type)
            .order("operator_id")
        )

        if from_date:
            query = query.gte("period_start", from_date.isoformat())
        if to_date:
            query = query.lte("period_start", to_date.isoformat())

        response = query.execute()
        rows = response.data or []

        # Compute org average error rate
        error_rates = [r["error_rate"] for r in rows if r.get("error_rate")]
        org_avg_error_rate = sum(error_rates) / len(error_rates) if error_rates else 0.0

        operators: list[OperatorAnalyticsItem] = []
        for row in rows:
            op_error_rate = row.get("error_rate", 0.0)
            coaching = org_avg_error_rate > 0 and op_error_rate > (org_avg_error_rate * COACHING_MULTIPLIER)
            operators.append(
                OperatorAnalyticsItem(
                    operator_id=row["operator_id"],
                    operator_name=row.get("operator_name", ""),
                    forms_filled=row.get("forms_filled", 0),
                    avg_fill_time_ms=row.get("avg_fill_time_ms"),
                    error_rate=op_error_rate,
                    coaching_flag=coaching,
                )
            )

        return OperatorAnalyticsResponse(
            period_type=period_type,
            period={"from": from_date.isoformat() if from_date else None, "to": to_date.isoformat() if to_date else None},
            operators=operators,
            org_average_error_rate=org_avg_error_rate,
            computed_at=datetime.utcnow(),
        )

    async def get_busiest_hours(
        self,
        org_id: UUID,
        from_date: date | None = None,
        to_date: date | None = None,
        branch_id: UUID | None = None,
    ) -> BusiestHoursResponse:
        """Return submission volume heatmap by hour and day of week."""
        # Aggregate from submissions table since operator_analytics.busiest_hours
        # may be pre-aggregated per operator; we want org-wide heatmap
        query = (
            apply_org_scope(self.client, "submissions", org_id)
            .select("created_at")
        )
        if from_date:
            query = query.gte("created_at", from_date.isoformat())
        if to_date:
            query = query.lte("created_at", to_date.isoformat())

        response = query.execute()
        rows = response.data or []

        # Build heatmap: hour (0-23) x day_of_week (0-6)
        heatmap_data: dict[tuple[int, int], int] = {}
        for row in rows:
            created = row.get("created_at")
            if not created:
                continue
            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            key = (dt.hour, dt.weekday())
            heatmap_data[key] = heatmap_data.get(key, 0) + 1

        heatmap = [
            HeatmapItem(hour=h, day_of_week=d, submission_count=c)
            for (h, d), c in heatmap_data.items()
        ]

        peak = max(heatmap_data.items(), key=lambda x: x[1]) if heatmap_data else ((0, 0), 0)

        return BusiestHoursResponse(
            heatmap=heatmap,
            peak_hour=peak[0][0],
            peak_day=peak[0][1],
            computed_at=datetime.utcnow(),
        )

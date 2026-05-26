"""Field-level analytics service."""

import logging
from datetime import date, datetime
from uuid import UUID

from supabase import Client

from app.schemas.analytics import FieldAnalyticsItem, FieldAnalyticsResponse, TopErrorItem
from app.services.analytics.base_analytics import apply_org_scope

logger = logging.getLogger(__name__)

WARNING_THRESHOLD = 0.20


class FieldAnalyticsService:
    """Aggregate and retrieve field-level analytics per template."""

    def __init__(self, client: Client):
        self.client = client

    async def get_field_analytics(
        self,
        org_id: UUID,
        template_id: UUID,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> FieldAnalyticsResponse:
        """Return field-level analytics for a template."""
        # Fetch pre-aggregated field_analytics rows
        query = (
            apply_org_scope(self.client, "field_analytics", org_id)
            .eq("template_id", str(template_id))
            .order("field_key")
        )

        if from_date:
            query = query.gte("period_start", from_date.isoformat())
        if to_date:
            query = query.lte("period_end", to_date.isoformat())

        response = query.execute()
        rows = response.data or []

        # Fetch template metadata for display
        template_resp = (
            self.client.table("templates")
            .select("name, version")
            .eq("id", str(template_id))
            .single()
            .execute()
        )
        template = template_resp.data or {}

        fields: list[FieldAnalyticsItem] = []
        for row in rows:
            error_rate = row.get("total_submissions", 0) and (
                row.get("error_count", 0) / row.get("total_submissions", 1)
            )
            empty_rate = row.get("total_submissions", 0) and (
                row.get("empty_count", 0) / row.get("total_submissions", 1)
            )
            top_errors = self._extract_top_errors(row.get("error_types", {}))
            fields.append(
                FieldAnalyticsItem(
                    field_key=row["field_key"],
                    error_rate=error_rate,
                    top_errors=top_errors,
                    empty_rate=empty_rate,
                    avg_fill_time_ms=row.get("avg_fill_time_ms"),
                    warning=error_rate > WARNING_THRESHOLD,
                )
            )

        return FieldAnalyticsResponse(
            template_id=template_id,
            template_name=template.get("name", ""),
            template_version=template.get("version", 0),
            period={"from": from_date.isoformat() if from_date else None, "to": to_date.isoformat() if to_date else None},
            fields=fields,
            computed_at=datetime.utcnow(),
        )

    def _extract_top_errors(self, error_types: dict) -> list[TopErrorItem]:
        """Extract top 3 errors by count."""
        sorted_errors = sorted(error_types.items(), key=lambda x: x[1], reverse=True)
        return [TopErrorItem(message=msg, count=cnt) for msg, cnt in sorted_errors[:3]]

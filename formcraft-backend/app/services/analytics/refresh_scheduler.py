"""Scheduled refresh for analytics materialized views."""

import logging
from datetime import datetime

from supabase import Client


logger = logging.getLogger(__name__)

REFRESH_INTERVAL_MINUTES = 15


class AnalyticsRefreshScheduler:
    """Refresh materialized views and log outcomes."""

    def __init__(self, client: Client):
        self.client = client

    async def refresh_all(self) -> None:
        """Refresh all analytics materialized views."""
        await self._refresh_view("mv_template_usage_funnel")

    async def _refresh_view(self, view_name: str) -> None:
        """Refresh a single materialized view and log the result."""
        started_at = datetime.utcnow()
        log_entry = {
            "view_name": view_name,
            "refresh_type": "full",
            "started_at": started_at.isoformat(),
            "status": "running",
        }
        log_resp = self.client.table("analytics_aggregation_log").insert(log_entry).execute()
        log_id = log_resp.data[0]["id"] if log_resp.data else None

        try:
            # Execute raw SQL for concurrent refresh
            self.client.rpc("refresh_materialized_view_concurrently", {"view_name": view_name}).execute()

            completed_at = datetime.utcnow()
            duration_ms = int((completed_at - started_at).total_seconds() * 1000)

            # Count rows in view
            count_resp = self.client.table(view_name).select("*", count="exact").limit(0).execute()
            row_count = count_resp.count or 0

            if log_id:
                self.client.table("analytics_aggregation_log").update({
                    "completed_at": completed_at.isoformat(),
                    "duration_ms": duration_ms,
                    "row_count": row_count,
                    "status": "success",
                }).eq("id", log_id).execute()

            logger.info(f"Refreshed {view_name} in {duration_ms}ms ({row_count} rows)")
        except Exception as exc:
            if log_id:
                self.client.table("analytics_aggregation_log").update({
                    "completed_at": datetime.utcnow().isoformat(),
                    "status": "failed",
                    "error_message": str(exc),
                }).eq("id", log_id).execute()
            logger.exception(f"Failed to refresh {view_name}")

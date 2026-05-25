"""Compliance: quality scores, staleness detection, regulatory impact."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from supabase import Client


class ComplianceService:
    def __init__(self, client: Client):
        self.client = client

    async def compute_quality_score(self, template_id: UUID) -> dict:
        """Compute quality score for a single template from element metadata."""
        # Fetch pages and elements
        pages_result = (
            self.client.table("pages")
            .select("id")
            .eq("template_id", str(template_id))
            .execute()
        )
        page_ids = [p["id"] for p in (pages_result.data or [])]

        if not page_ids:
            return {
                "validator_coverage_pct": 0.0,
                "bilingual_label_pct": 0.0,
                "help_text_coverage_pct": 0.0,
                "tab_order_defined": False,
                "quality_score": 0,
            }

        elements_result = (
            self.client.table("elements")
            .select("validation, label_ar, label_en, help_text, tab_order")
            .in_("page_id", page_ids)
            .execute()
        )
        elements = elements_result.data or []

        total = len(elements)
        if total == 0:
            return {
                "validator_coverage_pct": 0.0,
                "bilingual_label_pct": 0.0,
                "help_text_coverage_pct": 0.0,
                "tab_order_defined": False,
                "quality_score": 0,
            }

        with_validator = sum(1 for e in elements if e.get("validation"))
        with_bilingual = sum(
            1 for e in elements if e.get("label_ar") and e.get("label_en")
        )
        with_help = sum(1 for e in elements if e.get("help_text"))
        with_tab_order = sum(1 for e in elements if e.get("tab_order") is not None)

        validator_pct = (with_validator / total) * 100
        bilingual_pct = (with_bilingual / total) * 100
        help_pct = (with_help / total) * 100
        tab_order_pct = (with_tab_order / total) * 100

        # Weighted score
        quality_score = int(
            (validator_pct * 0.40)
            + (bilingual_pct * 0.30)
            + (help_pct * 0.20)
            + (tab_order_pct * 0.10)
        )

        return {
            "validator_coverage_pct": round(validator_pct, 1),
            "bilingual_label_pct": round(bilingual_pct, 1),
            "help_text_coverage_pct": round(help_pct, 1),
            "tab_order_defined": with_tab_order > 0,
            "quality_score": quality_score,
        }

    async def get_compliance_dashboard(self, org_id: UUID) -> dict:
        """Aggregated compliance metrics for all templates in an org."""
        # Fetch all templates
        templates_result = (
            self.client.table("templates")
            .select("id, name, updated_at")
            .eq("org_id", str(org_id))
            .execute()
        )
        templates = templates_result.data or []

        total = len(templates)
        if total == 0:
            return {
                "avg_quality_score": 0.0,
                "total_templates": 0,
                "validator_coverage_pct": 0.0,
                "bilingual_coverage_pct": 0.0,
                "stale_count": 0,
                "templates": [],
            }

        stale_threshold = datetime.now(timezone.utc) - timedelta(days=180)
        stale_count = 0
        template_metrics = []
        total_validator_pct = 0.0
        total_bilingual_pct = 0.0
        total_quality = 0

        for t in templates:
            quality = await self.compute_quality_score(UUID(t["id"]))
            updated = datetime.fromisoformat(t["updated_at"].replace("Z", "+00:00"))
            is_stale = updated < stale_threshold
            if is_stale:
                stale_count += 1

            template_metrics.append(
                {
                    "template_id": t["id"],
                    "template_name": t["name"],
                    **quality,
                    "is_stale": is_stale,
                    "last_modified": t["updated_at"],
                }
            )

            total_validator_pct += quality["validator_coverage_pct"]
            total_bilingual_pct += quality["bilingual_label_pct"]
            total_quality += quality["quality_score"]

        return {
            "avg_quality_score": round(total_quality / total, 1),
            "total_templates": total,
            "validator_coverage_pct": round(total_validator_pct / total, 1),
            "bilingual_coverage_pct": round(total_bilingual_pct / total, 1),
            "stale_count": stale_count,
            "templates": template_metrics,
        }

    async def get_regulatory_alerts(self, org_id: UUID) -> list[dict]:
        """Recent validator change events affecting the org."""
        result = (
            self.client.table("validator_change_events")
            .select("*")
            .or_(f"org_id.eq.{str(org_id)},org_id.is.null")
            .order("created_at", desc=True)
            .limit(20)
            .execute()
        )

        alerts = []
        for row in result.data or []:
            alerts.append(
                {
                    "event_id": row["id"],
                    "validator_key": row["validator_key"],
                    "change_summary": row["change_summary"],
                    "effective_date": row["effective_date"],
                    "affected_template_count": row.get("affected_template_count", 0),
                }
            )

        return alerts

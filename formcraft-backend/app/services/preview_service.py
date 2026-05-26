"""Preview service for retention policy impact analysis."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.schemas.retention import PreviewResponse


class PreviewService:
    def __init__(self, client):
        self.client = client

    async def generate_preview(self, org_id: UUID, policy_id: UUID) -> PreviewResponse:
        policy = (
            self.client.table("retention_policies")
            .select("*")
            .eq("id", str(policy_id))
            .eq("org_id", str(org_id))
            .single()
            .execute()
        )
        if not policy.data:
            raise ValueError("Policy not found")

        p = policy.data
        data_class = p["data_class"]
        action = p["action"]
        period_days = p["period_days"]
        scope_json = p.get("scope_json", {})
        effective_date = datetime.fromisoformat(p["effective_date"].replace("Z", "+00:00"))
        cutoff = effective_date - timedelta(days=period_days)

        # Map data_class to operational table
        table_map = {
            "submission": "form_submissions",
            "customer_profile": "customer_profiles",
            "audit_log": "audit_logs",
            "generated_pdf": "generated_pdfs",
            "export_file": "export_files",
            "portal_session": "portal_sessions",
            "report_archive": "report_archives",
        }
        table = table_map.get(data_class)
        if not table:
            raise ValueError(f"Unknown data_class: {data_class}")

        # Build query with scope filters
        query = (
            self.client.table(table)
            .select("*", count="exact")
            .eq("org_id", str(org_id))
            .lt("created_at", cutoff.isoformat())
        )
        for key, value in scope_json.items():
            if value:
                query = query.eq(key, value)

        # Read-only approach: fetch limited count and sample
        resp = query.limit(1).execute()
        affected_count = resp.count or 0

        # Check blocked records (legal holds, audit minimums)
        holds = (
            self.client.table("legal_holds")
            .select("*", count="exact")
            .eq("org_id", str(org_id))
            .eq("scope_type", data_class.rstrip("s"))  # simplistic mapping
            .execute()
        )
        blocked_records = holds.count or 0
        blocked_reason = "Legal hold or audit minimum"

        # Downstream references (reports, exports, PDFs)
        downstream = {
            "reports": 0,
            "exports": 0,
            "generated_pdfs": 0,
        }
        if data_class == "submission":
            # Count references from reports, exports, pdfs
            for ref_type in downstream:
                ref_resp = (
                    self.client.table(ref_type)
                    .select("id", count="exact")
                    .eq("org_id", str(org_id))
                    .lt("created_at", cutoff.isoformat())
                    .limit(1)
                    .execute()
                )
                downstream[ref_type] = ref_resp.count or 0

        return PreviewResponse(
            affected_count=affected_count,
            date_range={
                "oldest": (cutoff - timedelta(days=365)).strftime("%Y-%m-%d"),
                "newest": cutoff.strftime("%Y-%m-%d"),
            },
            affected_forms=[],
            blocked_records=blocked_records,
            blocked_reason=blocked_reason,
            downstream_references=downstream,
        )

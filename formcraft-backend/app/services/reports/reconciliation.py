class ReconciliationService:
    """Builds daily reconciliation reports."""

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    async def generate(self, org_id: str, report_date: str, branch_id: str | None = None):
        # Placeholder: implement aggregation queries
        return {
            "date": report_date,
            "branch": {"id": branch_id, "name": "Branch", "name_ar": "الفرع"},
            "summary": {"total_submissions": 0, "total_amount": 0.0, "template_breakdown": []},
            "operators": [],
        }

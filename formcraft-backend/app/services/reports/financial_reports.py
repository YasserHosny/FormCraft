class FinancialReportsService:
    """Builds beneficiary, void-reprint, and signatory usage reports."""

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    async def beneficiary_report(self, org_id: str, date_from: str, date_to: str, beneficiary_query: str | None = None, template_id: str | None = None):
        return {"data": [], "total_count": 0}

    async def void_reprint_report(self, org_id: str, date_from: str, date_to: str, branch_id: str | None = None, min_reprint_count: int = 1):
        return {"data": [], "total_count": 0}

    async def signatory_usage_report(self, org_id: str, date_from: str, date_to: str, signatory_id: str | None = None):
        return {"data": [], "total_count": 0}

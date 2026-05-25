class PeriodSummaryService:
    """Builds period summary reports with comparisons."""

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    async def generate(self, org_id: str, period: str, group_by: str, date_from: str | None = None, compare: bool = True):
        # Placeholder: implement period aggregation and comparison
        return {
            "period": period,
            "current": {"from": "", "to": ""},
            "previous": {"from": "", "to": ""},
            "groups": [],
        }

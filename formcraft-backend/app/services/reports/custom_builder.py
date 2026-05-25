class CustomBuilderService:
    """Builds dynamic custom reports across templates."""

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    async def preview(self, org_id: str, config: dict):
        return {
            "columns": [{"key": "branch_name", "label": "Branch", "type": "text"}],
            "rows": [],
            "total_matching": 0,
            "preview_limited": True,
        }

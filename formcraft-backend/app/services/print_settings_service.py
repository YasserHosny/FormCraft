"""Service for template print settings."""

from uuid import UUID

from supabase import Client


class PrintSettingsService:
    def __init__(self, client: Client):
        self.client = client

    async def get_settings(self, template_id: UUID) -> dict | None:
        result = (
            self.client.table("template_print_settings")
            .select("template_id, print_mode, updated_at")
            .eq("template_id", str(template_id))
            .maybe_single()
            .execute()
        )
        return result.data if result and result.data else None

    async def upsert_settings(self, template_id: UUID, print_mode: str, org_id: UUID) -> dict:
        data = {
            "template_id": str(template_id),
            "print_mode": print_mode,
            "org_id": str(org_id),
            "updated_at": "now()",
        }
        result = (
            self.client.table("template_print_settings")
            .upsert(data, on_conflict="template_id")
            .execute()
        )
        return result.data[0] if result.data else data

"""Legal hold service."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from app.models.legal_hold import LegalHoldCreate
from app.schemas.retention import HoldResponse


class LegalHoldService:
    def __init__(self, client):
        self.client = client
        self.table = "legal_holds"

    async def create_hold(self, org_id: UUID, data: LegalHoldCreate, created_by: UUID) -> HoldResponse:
        # Duplicate guard
        existing = (
            self.client.table(self.table)
            .select("id")
            .eq("org_id", str(org_id))
            .eq("scope_type", data.scope_type)
            .eq("scope_id", str(data.scope_id))
            .execute()
        )
        if existing.data:
            raise ValueError("LEGAL_HOLD_EXISTS")

        payload = data.model_dump()
        payload["org_id"] = str(org_id)
        payload["created_by"] = str(created_by)
        resp = self.client.table(self.table).insert(payload).execute()

        # Audit log
        self.client.table("audit_logs").insert(
            {
                "table_name": "legal_holds",
                "record_id": resp.data[0]["id"],
                "action": "legal_hold_applied",
                "new_values": payload,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        ).execute()

        return HoldResponse(**resp.data[0])

    async def release_hold(self, org_id: UUID, hold_id: UUID) -> None:
        self.client.table(self.table).delete().eq("id", str(hold_id)).eq(
            "org_id", str(org_id)
        ).execute()

        # Audit log
        self.client.table("audit_logs").insert(
            {
                "table_name": "legal_holds",
                "record_id": str(hold_id),
                "action": "legal_hold_released",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        ).execute()

    async def list_holds(
        self, org_id: UUID, scope_type: str | None = None, hold_type: str | None = None
    ) -> list[HoldResponse]:
        query = self.client.table(self.table).select("*").eq("org_id", str(org_id))
        if scope_type:
            query = query.eq("scope_type", scope_type)
        if hold_type:
            query = query.eq("hold_type", hold_type)
        resp = query.execute()
        return [HoldResponse(**row) for row in resp.data]

    async def get_hold(self, org_id: UUID, hold_id: UUID) -> HoldResponse:
        resp = (
            self.client.table(self.table)
            .select("*")
            .eq("id", str(hold_id))
            .eq("org_id", str(org_id))
            .single()
            .execute()
        )
        return HoldResponse(**resp.data)

"""Privacy request service."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from app.models.privacy_request import PrivacyRequestCreate, PrivacyRequestResolve
from app.schemas.retention import PrivacyRequestResponse


class PrivacyRequestService:
    def __init__(self, client):
        self.client = client
        self.table = "privacy_requests"

    async def create_request(
        self, org_id: UUID, data: PrivacyRequestCreate, created_by: UUID
    ) -> PrivacyRequestResponse:
        payload = data.model_dump()
        payload["org_id"] = str(org_id)
        payload["created_by"] = str(created_by)

        # Conflict detection
        hold = (
            self.client.table("legal_holds")
            .select("id")
            .eq("org_id", str(org_id))
            .eq("scope_type", data.scope_type)
            .eq("scope_id", str(data.scope_id))
            .execute()
        )
        if hold.data:
            payload["conflict_hold_id"] = hold.data[0]["id"]

        resp = self.client.table(self.table).insert(payload).execute()
        return PrivacyRequestResponse(**resp.data[0])

    async def resolve_request(
        self, org_id: UUID, request_id: UUID, data: PrivacyRequestResolve
    ) -> PrivacyRequestResponse:
        payload = {
            "status": data.status,
            "resolution": data.resolution,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        resp = (
            self.client.table(self.table)
            .update(payload)
            .eq("id", str(request_id))
            .eq("org_id", str(org_id))
            .execute()
        )
        return PrivacyRequestResponse(**resp.data[0])

    async def list_requests(
        self, org_id: UUID, status: str | None = None, request_type: str | None = None
    ) -> list[PrivacyRequestResponse]:
        query = self.client.table(self.table).select("*").eq("org_id", str(org_id))
        if status:
            query = query.eq("status", status)
        if request_type:
            query = query.eq("request_type", request_type)
        resp = query.execute()
        return [PrivacyRequestResponse(**row) for row in resp.data]

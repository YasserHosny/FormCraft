"""Retention policy service."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import UUID

from app.models.retention_policy import RetentionPolicyCreate, RetentionPolicyUpdate
from app.schemas.retention import PolicyResponse


class RetentionPolicyService:
    def __init__(self, client):
        self.client = client
        self.table = "retention_policies"

    async def create_policy(
        self, org_id: UUID, data: RetentionPolicyCreate, created_by: UUID
    ) -> PolicyResponse:
        payload = data.model_dump()
        payload["org_id"] = str(org_id)
        payload["created_by"] = str(created_by)
        payload["scope_json"] = json.dumps(payload.get("scope_json", {}))
        payload["name"] = json.dumps(payload["name"])

        # Conflict detection: org + data_class + scope
        existing = (
            self.client.table(self.table)
            .select("id")
            .eq("org_id", str(org_id))
            .eq("data_class", payload["data_class"])
            .eq("scope_json", payload["scope_json"])
            .execute()
        )
        if existing.data:
            raise ValueError("RETENTION_POLICY_CONFLICT")

        resp = self.client.table(self.table).insert(payload).execute()
        return PolicyResponse(**resp.data[0])

    async def update_policy(
        self, org_id: UUID, policy_id: UUID, data: RetentionPolicyUpdate
    ) -> PolicyResponse:
        # Guard: no active jobs referencing this policy
        jobs = (
            self.client.table("retention_jobs")
            .select("id")
            .eq("policy_id", str(policy_id))
            .in_("status", ["pending", "running", "paused"])
            .execute()
        )
        if jobs.data:
            raise ValueError("RETENTION_JOB_ACTIVE")

        payload = {k: v for k, v in data.model_dump().items() if v is not None}
        if "scope_json" in payload:
            payload["scope_json"] = json.dumps(payload["scope_json"])
        if "name" in payload:
            payload["name"] = json.dumps(payload["name"])
        payload["updated_at"] = datetime.now(timezone.utc).isoformat()

        resp = (
            self.client.table(self.table)
            .update(payload)
            .eq("id", str(policy_id))
            .eq("org_id", str(org_id))
            .execute()
        )
        if not resp.data:
            raise ValueError("Policy not found")
        return PolicyResponse(**resp.data[0])

    async def delete_policy(self, org_id: UUID, policy_id: UUID) -> None:
        # Guard: no jobs exist for this policy
        jobs = (
            self.client.table("retention_jobs")
            .select("id")
            .eq("policy_id", str(policy_id))
            .execute()
        )
        if jobs.data:
            raise ValueError("RETENTION_JOB_ACTIVE")

        self.client.table(self.table).delete().eq("id", str(policy_id)).eq(
            "org_id", str(org_id)
        ).execute()

    async def list_policies(
        self,
        org_id: UUID,
        data_class: str | None = None,
        action: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        query = (
            self.client.table(self.table)
            .select("*", count="exact")
            .eq("org_id", str(org_id))
        )
        if data_class:
            query = query.eq("data_class", data_class)
        if action:
            query = query.eq("action", action)

        start = (page - 1) * page_size
        resp = query.order("created_at", desc=True).range(start, start + page_size - 1).execute()

        return {
            "items": [PolicyResponse(**row) for row in resp.data],
            "total": resp.count,
            "page": page,
            "page_size": page_size,
        }

    async def get_policy(self, org_id: UUID, policy_id: UUID) -> PolicyResponse:
        resp = (
            self.client.table(self.table)
            .select("*")
            .eq("id", str(policy_id))
            .eq("org_id", str(org_id))
            .single()
            .execute()
        )
        return PolicyResponse(**resp.data)

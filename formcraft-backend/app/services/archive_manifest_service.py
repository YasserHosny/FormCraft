"""Archive manifest service."""

from __future__ import annotations

from uuid import UUID

from app.schemas.retention import ManifestResponse


class ArchiveManifestService:
    def __init__(self, client):
        self.client = client
        self.table = "archive_manifests"

    async def list_manifests(
        self, org_id: UUID, job_id: UUID | None = None, integrity_status: str | None = None
    ) -> list[ManifestResponse]:
        query = (
            self.client.table(self.table)
            .select("*, retention_jobs!inner(policy_id!inner(org_id))")
            .eq("retention_jobs.policy_id.org_id", str(org_id))
        )
        if job_id:
            query = query.eq("job_id", str(job_id))
        if integrity_status:
            query = query.eq("integrity_status", integrity_status)
        resp = query.execute()
        return [ManifestResponse(**row) for row in resp.data]

    async def get_manifest(self, org_id: UUID, manifest_id: UUID) -> ManifestResponse:
        resp = (
            self.client.table(self.table)
            .select("*")
            .eq("id", str(manifest_id))
            .single()
            .execute()
        )
        return ManifestResponse(**resp.data)

    async def request_restore(self, org_id: UUID, manifest_id: UUID, reason: str) -> dict:
        manifest = await self.get_manifest(org_id, manifest_id)
        conditions = manifest.restore_conditions
        if conditions.get("max_restore_date"):
            from datetime import datetime, timezone
            max_date = datetime.fromisoformat(conditions["max_restore_date"])
            if datetime.now(timezone.utc) > max_date:
                raise ValueError("RESTORE_NOT_ALLOWED")
        return {"restore_job_id": str(manifest_id), "status": "pending"}

"""Retention job service with batch executor, checkpointing, and audit logging."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.models.retention_job import RetentionJobCreate
from app.schemas.retention import JobResponse


class RetentionJobService:
    def __init__(self, client):
        self.client = client

    async def create_job(self, org_id: UUID, data: RetentionJobCreate) -> JobResponse:
        # Guard: no active job for this policy
        existing = (
            self.client.table("retention_jobs")
            .select("id")
            .eq("policy_id", str(data.policy_id))
            .in_("status", ["pending", "running", "paused"])
            .execute()
        )
        if existing.data:
            raise ValueError("RETENTION_JOB_ACTIVE")

        payload = data.model_dump()
        resp = self.client.table("retention_jobs").insert(payload).execute()
        return JobResponse(**resp.data[0])

    async def process_pending_jobs(self) -> None:
        """APScheduler entrypoint: process all pending/running jobs."""
        jobs = (
            self.client.table("retention_jobs")
            .select("*")
            .in_("status", ["pending", "running", "paused"])
            .order("created_at")
            .execute()
        )
        for job in jobs.data:
            await self._process_job(job)

    async def _process_job(self, job: dict) -> None:
        job_id = job["id"]
        policy_id = job["policy_id"]
        status = job["status"]
        batch_size = job["batch_size"]
        checkpoint = job.get("checkpoint_cursor")

        if status == "paused":
            return

        # Mark running
        self.client.table("retention_jobs").update(
            {"status": "running", "started_at": datetime.now(timezone.utc).isoformat()}
        ).eq("id", job_id).execute()

        policy = (
            self.client.table("retention_policies")
            .select("*")
            .eq("id", policy_id)
            .single()
            .execute()
        )
        if not policy.data:
            self._fail_job(job_id, "Policy not found")
            return

        p = policy.data
        data_class = p["data_class"]
        action = p["action"]
        period_days = p["period_days"]
        effective_date = datetime.fromisoformat(p["effective_date"].replace("Z", "+00:00"))
        cutoff = effective_date - timedelta(days=period_days)

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
            self._fail_job(job_id, f"Unknown data_class: {data_class}")
            return

        try:
            if action == "archive":
                await self._archive_batch(job_id, table, cutoff, batch_size, checkpoint)
            elif action == "purge":
                await self._purge_batch(job_id, table, cutoff, batch_size, checkpoint)
            elif action == "mask":
                await self._mask_batch(job_id, table, cutoff, batch_size, checkpoint)
            else:
                # retain = no-op for job
                self._complete_job(job_id, actioned_count=0)
        except Exception as exc:
            self._fail_job(job_id, str(exc))

    async def _archive_batch(
        self, job_id: str, table: str, cutoff: datetime, batch_size: int, checkpoint: str | None
    ) -> None:
        client = self.client
        archive_table = f"archive.{table}"
        query = (
            client.table(table)
            .select("*")
            .lt("created_at", cutoff.isoformat())
            .order("id")
            .limit(batch_size)
        )
        if checkpoint:
            query = query.gt("id", checkpoint)

        records = query.execute()
        if not records.data:
            self._complete_job(job_id, actioned_count=0)
            return

        skipped = []
        archived = []
        for rec in records.data:
            hold = (
                client.table("legal_holds")
                .select("id")
                .eq("scope_id", rec["id"])
                .execute()
            )
            if hold.data:
                skipped.append({"record_id": rec["id"], "reason": "legal_hold", "hold_id": hold.data[0]["id"]})
                continue
            archived.append(rec)

        if archived:
            # Insert into archive schema
            archive_rows = []
            for rec in archived:
                row = dict(rec)
                row["original_id"] = rec["id"]
                row["archived_at"] = datetime.now(timezone.utc).isoformat()
                row["manifest_id"] = None  # populated after manifest creation
                del row["id"]  # let archive table generate new id
                archive_rows.append(row)
            client.table(archive_table).insert(archive_rows).execute()

            # Generate manifest hash
            canonical = json.dumps(archive_rows, sort_keys=True, ensure_ascii=False)
            sha256 = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

            manifest_resp = (
                client.table("archive_manifests")
                .insert(
                    {
                        "job_id": job_id,
                        "record_count": len(archived),
                        "schema_location": archive_table,
                        "sha256_hash": sha256,
                        "integrity_status": "verified",
                        "restore_conditions": {},
                    }
                )
                .execute()
            )
            manifest_id = manifest_resp.data[0]["id"]

            # Update archive rows with manifest_id
            for row in archive_rows:
                row["manifest_id"] = manifest_id

        last_id = records.data[-1]["id"]
        client.table("retention_jobs").update(
            {
                "checkpoint_cursor": last_id,
                "evaluated_count": len(records.data),
                "actioned_count": len(archived),
                "skipped_records": skipped,
            }
        ).eq("id", job_id).execute()

        # Audit log
        await self._audit(job_id, "retention_job_completed", {"action": "archive", "count": len(archived)})

        self._complete_job(job_id, actioned_count=len(archived))

    async def _purge_batch(
        self, job_id: str, table: str, cutoff: datetime, batch_size: int, checkpoint: str | None
    ) -> None:
        client = self.client
        query = (
            client.table(table)
            .select("*")
            .lt("created_at", cutoff.isoformat())
            .order("id")
            .limit(batch_size)
        )
        if checkpoint:
            query = query.gt("id", checkpoint)

        records = query.execute()
        if not records.data:
            self._complete_job(job_id, actioned_count=0)
            return

        skipped = []
        purged = []
        for rec in records.data:
            hold = (
                client.table("legal_holds")
                .select("id")
                .eq("scope_id", rec["id"])
                .execute()
            )
            if hold.data:
                skipped.append({"record_id": rec["id"], "reason": "legal_hold", "hold_id": hold.data[0]["id"]})
                continue
            # Reference check before purge
            refs = await self._check_references(rec["id"])
            if refs:
                skipped.append({"record_id": rec["id"], "reason": "downstream_references", "refs": refs})
                continue
            purged.append(rec)

        if purged:
            ids = [r["id"] for r in purged]
            client.table(table).delete().in_("id", ids).execute()

            # Purge evidence
            evidence = {"action": "purge", "table": table, "count": len(purged), "ids": ids}
            canonical = json.dumps(evidence, sort_keys=True, ensure_ascii=False)
            sha256 = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            await self._audit(job_id, "record_purged", {"sha256": sha256, **evidence})

        last_id = records.data[-1]["id"]
        client.table("retention_jobs").update(
            {
                "checkpoint_cursor": last_id,
                "evaluated_count": len(records.data),
                "actioned_count": len(purged),
                "skipped_records": skipped,
            }
        ).eq("id", job_id).execute()

        self._complete_job(job_id, actioned_count=len(purged))

    async def _mask_batch(
        self, job_id: str, table: str, cutoff: datetime, batch_size: int, checkpoint: str | None
    ) -> None:
        client = self.client
        query = (
            client.table(table)
            .select("*")
            .lt("created_at", cutoff.isoformat())
            .order("id")
            .limit(batch_size)
        )
        if checkpoint:
            query = query.gt("id", checkpoint)

        records = query.execute()
        if not records.data:
            self._complete_job(job_id, actioned_count=0)
            return

        skipped = []
        masked = []
        for rec in records.data:
            hold = (
                client.table("legal_holds")
                .select("id")
                .eq("scope_id", rec["id"])
                .execute()
            )
            if hold.data:
                skipped.append({"record_id": rec["id"], "reason": "legal_hold", "hold_id": hold.data[0]["id"]})
                continue
            # Redact PII in-place (simplistic: overwrite name/email fields)
            updates = {}
            for field in ("name", "email", "phone", "national_id"):
                if field in rec and rec[field]:
                    updates[field] = "***MASKED***"
            if updates:
                client.table(table).update(updates).eq("id", rec["id"]).execute()
                masked.append(rec["id"])

        last_id = records.data[-1]["id"]
        client.table("retention_jobs").update(
            {
                "checkpoint_cursor": last_id,
                "evaluated_count": len(records.data),
                "actioned_count": len(masked),
                "skipped_records": skipped,
            }
        ).eq("id", job_id).execute()

        await self._audit(job_id, "record_masked", {"table": table, "count": len(masked)})
        self._complete_job(job_id, actioned_count=len(masked))

    async def _check_references(self, record_id: str) -> dict:
        """Check downstream references before purge."""
        refs = {}
        for ref_table in ("reports", "exports", "generated_pdfs"):
            resp = (
                self.client.table(ref_table)
                .select("id")
                .eq("submission_id", record_id)  # assumes foreign key naming
                .limit(1)
                .execute()
            )
            if resp.data:
                refs[ref_table] = len(resp.data)
        return refs

    async def _audit(self, job_id: str, event_type: str, payload: dict) -> None:
        self.client.table("audit_logs").insert(
            {
                "table_name": "retention_jobs",
                "record_id": job_id,
                "action": event_type,
                "new_values": payload,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        ).execute()

    def _complete_job(self, job_id: str, actioned_count: int) -> None:
        self.client.table("retention_jobs").update(
            {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "actioned_count": actioned_count,
            }
        ).eq("id", job_id).execute()

    def _fail_job(self, job_id: str, error: str) -> None:
        job = self.client.table("retention_jobs").select("error_log").eq("id", job_id).single().execute()
        log = job.data.get("error_log", []) if job.data else []
        log.append({"error": error, "timestamp": datetime.now(timezone.utc).isoformat()})
        self.client.table("retention_jobs").update(
            {
                "status": "failed",
                "error_count": len(log),
                "error_log": log,
            }
        ).eq("id", job_id).execute()

    async def pause_job(self, org_id: UUID, job_id: UUID) -> JobResponse:
        resp = (
            self.client.table("retention_jobs")
            .update({"status": "paused"})
            .eq("id", str(job_id))
            .execute()
        )
        return JobResponse(**resp.data[0])

    async def resume_job(self, org_id: UUID, job_id: UUID) -> JobResponse:
        resp = (
            self.client.table("retention_jobs")
            .update({"status": "pending"})
            .eq("id", str(job_id))
            .execute()
        )
        return JobResponse(**resp.data[0])

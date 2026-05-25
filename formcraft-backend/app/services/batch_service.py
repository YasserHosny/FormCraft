import csv
import io
from datetime import datetime
from uuid import UUID, uuid4

from app.schemas.batch import (
    BatchDataSourceType,
    BatchDownloadFormat,
    BatchJob,
    BatchJobStatus,
    DuplicateStrategy,
)
from app.services.batch_data_source_service import BatchDataSourceService
from app.services.batch_generation_service import BatchGenerationService
from app.services.batch_validation_service import BatchValidationService


class BatchService:
    """Orchestrate batch job lifecycle: create, start, cancel, status, download."""

    def __init__(
        self,
        data_source_service: BatchDataSourceService | None = None,
        validation_service: BatchValidationService | None = None,
        generation_service: BatchGenerationService | None = None,
    ):
        self.data_source_service = data_source_service or BatchDataSourceService()
        self.validation_service = validation_service or BatchValidationService()
        self.generation_service = generation_service or BatchGenerationService()

    async def create_job(
        self,
        org_id: UUID,
        created_by: UUID,
        name: str,
        template_id: UUID,
        template_version: int,
        data_source_type: str,
        data_source_content: bytes | str,
        file_name: str = "",
        mime_type: str = "",
        column_mapping: dict | None = None,
        duplicate_strategy: str = DuplicateStrategy.WARN,
        download_format: str = BatchDownloadFormat.ZIP,
        printer_profile_id: UUID | None = None,
        supabase_client=None,
    ) -> BatchJob:
        """Create a batch job and parse the data source."""
        # Parse data source
        if data_source_type == BatchDataSourceType.CSV:
            headers, rows = self.data_source_service.parse_csv(data_source_content)
        elif data_source_type == BatchDataSourceType.XLSX:
            headers, rows = self.data_source_service.parse_xlsx(data_source_content)
        elif data_source_type == BatchDataSourceType.CLIPBOARD:
            headers, rows = self.data_source_service.parse_clipboard(data_source_content)
        else:
            raise ValueError(f"Unknown data source type: {data_source_type}")

        # Store data source metadata
        ds_id = uuid4()
        checksum = self.data_source_service.compute_checksum(
            data_source_content if isinstance(data_source_content, bytes) else data_source_content.encode("utf-8")
        )

        if supabase_client:
            await supabase_client.table("batch_data_sources").insert({
                "id": str(ds_id),
                "org_id": str(org_id),
                "file_name": file_name or "clipboard.txt",
                "storage_path": f"batch-sources/{org_id}/{ds_id}",
                "mime_type": mime_type or "text/plain",
                "file_size_bytes": len(data_source_content) if isinstance(data_source_content, bytes) else len(data_source_content.encode("utf-8")),
                "column_headers": headers,
                "checksum": checksum,
                "created_by": str(created_by),
            }).execute()

        # Auto-map if no mapping provided
        if not column_mapping:
            # Fetch template field keys (placeholder)
            field_keys = await self._fetch_template_field_keys(template_id, supabase_client)
            column_mapping = self.data_source_service.auto_map_columns(headers, field_keys)

        job = BatchJob(
            id=uuid4(),
            org_id=org_id,
            template_id=template_id,
            template_version=template_version,
            created_by=created_by,
            name=name,
            data_source_type=data_source_type,
            data_source_id=ds_id,
            column_mapping=column_mapping,
            row_count=len(rows),
            duplicate_strategy=duplicate_strategy,
            download_format=download_format,
            printer_profile_id=printer_profile_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        if supabase_client:
            await supabase_client.table("batch_jobs").insert(self._job_to_dict(job)).execute()

        return job

    async def validate_job(
        self,
        job_id: UUID,
        column_mapping: dict,
        duplicate_strategy: str,
        supabase_client,
    ) -> tuple[list[dict], int]:
        """Run validation for a batch job."""
        job_data = await supabase_client.table("batch_jobs").select("*").eq("id", str(job_id)).single().execute()
        if not job_data.data:
            raise ValueError("Job not found")

        job = self._dict_to_job(job_data.data)

        # Fetch raw rows from data source
        ds = await supabase_client.table("batch_data_sources").select("*").eq("id", str(job.data_source_id)).single().execute()
        if not ds.data:
            raise ValueError("Data source not found")

        # Reconstruct rows from column_headers (simplified; ideally stored in parsed form)
        headers = ds.data.get("column_headers", [])
        # For MVP, we re-parse from storage or keep in memory; here we mock rows
        rows = [{h: "" for h in headers}]

        # Fetch template fields
        template_fields = await self._fetch_template_fields(job.template_id, supabase_client)

        results, duplicate_count = self.validation_service.validate_rows(
            rows=rows,
            column_mapping=column_mapping,
            template_fields=template_fields,
            duplicate_strategy=duplicate_strategy,
        )

        # Persist errors
        errors_to_insert = [
            {
                "id": str(uuid4()),
                "org_id": str(job.org_id),
                "batch_job_id": str(job_id),
                "row_number": r["row_number"],
                "field_key": fk,
                "error_type": "validation",
                "error_message": msg,
            }
            for r in results
            if r["status"] == "invalid"
            for fk, msg in r["field_errors"].items()
        ]
        if errors_to_insert and supabase_client:
            await supabase_client.table("batch_errors").insert(errors_to_insert).execute()

        # Update job with validation summary
        _ = sum(1 for r in results if r["status"] == "valid")
        _ = sum(1 for r in results if r["status"] == "invalid")
        await supabase_client.table("batch_jobs").update({
            "column_mapping": column_mapping,
            "duplicate_strategy": duplicate_strategy,
            "duplicate_count": duplicate_count,
            "row_count": len(rows),
        }).eq("id", str(job_id)).execute()

        return results, duplicate_count

    async def start_job(self, job_id: UUID, supabase_client):
        """Start background generation for a batch job."""
        job_data = await supabase_client.table("batch_jobs").select("*").eq("id", str(job_id)).single().execute()
        if not job_data.data:
            raise ValueError("Job not found")

        job = self._dict_to_job(job_data.data)
        if job.status != BatchJobStatus.QUEUED:
            raise ValueError(f"Job cannot be started from status {job.status}")

        # Re-validate mapping against current template
        template_fields = await self._fetch_template_fields(job.template_id, supabase_client)
        ok, msg = self.validation_service.revalidate_mapping(job.column_mapping, template_fields)
        if not ok:
            await supabase_client.table("batch_jobs").update({
                "status": BatchJobStatus.FAILED,
                "error_summary": msg,
            }).eq("id", str(job_id)).execute()
            raise ValueError(msg)

        await supabase_client.table("batch_jobs").update({
            "status": BatchJobStatus.RUNNING,
            "started_at": datetime.utcnow().isoformat(),
        }).eq("id", str(job_id)).execute()

        # For in-process async, we launch the generation loop
        # In production this would be offloaded to a background worker
        import asyncio
        asyncio.create_task(self._run_generation(job, supabase_client))

    async def _run_generation(self, job: BatchJob, supabase_client):
        """Internal async generation loop."""
        # Fetch rows (mock for MVP; ideally parsed and stored)
        ds = await supabase_client.table("batch_data_sources").select("*").eq("id", str(job.data_source_id)).single().execute()
        headers = ds.data.get("column_headers", []) if ds.data else []
        rows = [{h: f"value_{i}" for h in headers} for i in range(job.row_count)]

        success_count, fail_count, errors, artifact = await self.generation_service.generate_batch(
            job_id=job.id,
            org_id=job.org_id,
            template_id=job.template_id,
            template_version=job.template_version,
            rows=rows,
            column_mapping=job.column_mapping,
            download_format=job.download_format,
            supabase_client=supabase_client,
        )

        # Persist generation errors
        if errors:
            errors_to_insert = [
                {
                    "id": str(uuid4()),
                    "org_id": str(job.org_id),
                    "batch_job_id": str(job.id),
                    "row_number": e["row_number"],
                    "field_key": e["field_key"],
                    "error_type": e["error_type"],
                    "error_message": e["error_message"],
                }
                for e in errors
            ]
            await supabase_client.table("batch_errors").insert(errors_to_insert).execute()

        # Determine final status
        if self.generation_service._cancel_flags.get(str(job.id), False):
            final_status = BatchJobStatus.CANCELLED
        elif fail_count > 0 and success_count == 0:
            final_status = BatchJobStatus.FAILED
        else:
            final_status = BatchJobStatus.COMPLETED

        await supabase_client.table("batch_jobs").update({
            "status": final_status,
            "progress": job.row_count,
            "success_count": success_count,
            "fail_count": fail_count,
            "completed_at": datetime.utcnow().isoformat(),
        }).eq("id", str(job.id)).execute()

    async def cancel_job(self, job_id: UUID, cancelled_by: UUID, supabase_client):
        """Cancel a running batch job."""
        job_data = await supabase_client.table("batch_jobs").select("*").eq("id", str(job_id)).single().execute()
        if not job_data.data:
            raise ValueError("Job not found")

        job = self._dict_to_job(job_data.data)
        if job.status != BatchJobStatus.RUNNING:
            raise ValueError(f"Job cannot be cancelled from status {job.status}")

        self.generation_service.cancel_job(job_id)
        await supabase_client.table("batch_jobs").update({
            "status": BatchJobStatus.CANCELLED,
            "cancelled_at": datetime.utcnow().isoformat(),
            "cancelled_by": str(cancelled_by),
        }).eq("id", str(job_id)).execute()

    async def get_job(self, job_id: UUID, supabase_client) -> BatchJob:
        job_data = await supabase_client.table("batch_jobs").select("*").eq("id", str(job_id)).single().execute()
        if not job_data.data:
            raise ValueError("Job not found")
        return self._dict_to_job(job_data.data)

    async def list_jobs(
        self,
        org_id: UUID,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
        supabase_client=None,
    ) -> tuple[list[BatchJob], int]:
        query = supabase_client.table("batch_jobs").select("*", count="exact").eq("org_id", str(org_id))
        if status:
            query = query.eq("status", status)
        query = query.order("updated_at", desc=True).limit(limit).offset(offset)
        result = await query.execute()
        jobs = [self._dict_to_job(r) for r in (result.data or [])]
        total = result.count or len(jobs)
        return jobs, total

    async def generate_error_report_csv(self, job_id: UUID, supabase_client) -> str:
        """Generate error report CSV for a batch job."""
        result = await supabase_client.table("batch_errors").select("*").eq("batch_job_id", str(job_id)).order("row_number").execute()
        errors = result.data or []

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["row_number", "field_key", "error_type", "error_message"])
        for e in errors:
            writer.writerow([e["row_number"], e.get("field_key", ""), e["error_type"], e["error_message"]])
        return output.getvalue()

    async def create_job_from_schedule(
        self,
        schedule_id: UUID,
        org_id: UUID,
        template_id: UUID,
        rows: list[dict],
        column_mapping: dict,
        download_format: str,
        supabase_client,
    ) -> BatchJob:
        """Create a batch job triggered by a schedule."""
        job = BatchJob(
            id=uuid4(),
            org_id=org_id,
            template_id=template_id,
            template_version=1,  # should be fetched from schedule/template
            created_by=org_id,  # system user placeholder
            name=f"Scheduled batch {schedule_id}",
            data_source_type="clipboard",  # in-memory from API
            data_source_id=None,
            column_mapping=column_mapping,
            row_count=len(rows),
            download_format=download_format,
            scheduled_job_id=schedule_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        if supabase_client:
            await supabase_client.table("batch_jobs").insert(self._job_to_dict(job)).execute()
        return job

    async def _fetch_template_field_keys(self, template_id: UUID, supabase_client) -> list[str]:
        # Placeholder: fetch element keys from template
        result = await supabase_client.table("elements").select("key").eq("template_id", str(template_id)).execute()
        return [r["key"] for r in (result.data or []) if r.get("key")]

    async def _fetch_template_fields(self, template_id: UUID, supabase_client) -> dict[str, dict]:
        # Placeholder: fetch elements with validation config
        result = await supabase_client.table("elements").select("key, validation, required").eq("template_id", str(template_id)).execute()
        fields = {}
        for r in (result.data or []):
            if r.get("key"):
                fields[r["key"]] = {
                    "required": r.get("required", False),
                    "validation": r.get("validation", {}),
                }
        return fields

    def _job_to_dict(self, job: BatchJob) -> dict:
        return {
            "id": str(job.id),
            "org_id": str(job.org_id),
            "template_id": str(job.template_id),
            "template_version": job.template_version,
            "created_by": str(job.created_by),
            "name": job.name,
            "status": job.status,
            "data_source_type": job.data_source_type,
            "data_source_id": str(job.data_source_id) if job.data_source_id else None,
            "column_mapping": job.column_mapping,
            "row_count": job.row_count,
            "success_count": job.success_count,
            "fail_count": job.fail_count,
            "progress": job.progress,
            "duplicate_strategy": job.duplicate_strategy,
            "duplicate_count": job.duplicate_count,
            "download_format": job.download_format,
            "printer_profile_id": str(job.printer_profile_id) if job.printer_profile_id else None,
            "scheduled_job_id": str(job.scheduled_job_id) if job.scheduled_job_id else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "cancelled_at": job.cancelled_at.isoformat() if job.cancelled_at else None,
            "cancelled_by": str(job.cancelled_by) if job.cancelled_by else None,
            "error_summary": job.error_summary,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat(),
        }

    def _dict_to_job(self, data: dict) -> BatchJob:
        return BatchJob(
            id=UUID(data["id"]),
            org_id=UUID(data["org_id"]),
            template_id=UUID(data["template_id"]),
            template_version=data["template_version"],
            created_by=UUID(data["created_by"]),
            name=data["name"],
            status=data["status"],
            data_source_type=data["data_source_type"],
            data_source_id=UUID(data["data_source_id"]) if data.get("data_source_id") else None,
            column_mapping=data.get("column_mapping", {}),
            row_count=data.get("row_count", 0),
            success_count=data.get("success_count", 0),
            fail_count=data.get("fail_count", 0),
            progress=data.get("progress", 0),
            duplicate_strategy=data.get("duplicate_strategy", "warn"),
            duplicate_count=data.get("duplicate_count", 0),
            download_format=data.get("download_format", "zip"),
            printer_profile_id=UUID(data["printer_profile_id"]) if data.get("printer_profile_id") else None,
            scheduled_job_id=UUID(data["scheduled_job_id"]) if data.get("scheduled_job_id") else None,
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            cancelled_at=datetime.fromisoformat(data["cancelled_at"]) if data.get("cancelled_at") else None,
            cancelled_by=UUID(data["cancelled_by"]) if data.get("cancelled_by") else None,
            error_summary=data.get("error_summary"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

import csv
import io
import json
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status

from app.core.audit import AuditLogger
from app.schemas.export import ExportFilters, ExportPreviewRequest


MAX_DIRECT_EXPORT_ROWS = 10_000
ESTIMATED_ROW_BYTES = 512


class ExportService:
    """F32 submission export and recurring export schedule service."""

    def __init__(self, supabase_client):
        self.client = supabase_client

    async def preview_submissions(
        self,
        org_id: UUID,
        actor_id: UUID,
        request: ExportPreviewRequest,
    ) -> dict:
        warnings = self._filter_warnings(request.filters)
        rows, total = self._fetch_submission_rows(org_id, request.filters, limit=1)
        can_download = total <= MAX_DIRECT_EXPORT_ROWS
        rejection_reason = None if can_download else "row_limit_exceeded"

        await self._record_export_request(
            org_id=org_id,
            actor_id=actor_id,
            request=request,
            matching_count=total,
            status_value="previewed" if can_download else "rejected",
            rejection_reason=rejection_reason,
        )

        return {
            "matching_count": total,
            "estimated_file_size_bytes": total * ESTIMATED_ROW_BYTES,
            "can_download": can_download,
            "rejection_reason": rejection_reason,
            "warnings": warnings,
        }

    async def download_submissions(
        self,
        org_id: UUID,
        actor_id: UUID,
        request: ExportPreviewRequest,
    ) -> tuple[bytes, str, str]:
        warnings = self._filter_warnings(request.filters)
        rows, total = self._fetch_submission_rows(
            org_id, request.filters, limit=MAX_DIRECT_EXPORT_ROWS + 1
        )
        if total > MAX_DIRECT_EXPORT_ROWS:
            await self._record_export_request(
                org_id=org_id,
                actor_id=actor_id,
                request=request,
                matching_count=total,
                status_value="rejected",
                rejection_reason="row_limit_exceeded",
            )
            await AuditLogger(self.client).log_event(
                user_id=str(actor_id),
                action="DATA_EXPORT_REJECTED",
                resource_type="export_request",
                metadata={
                    "format": request.format,
                    "scope": request.scope,
                    "matching_count": total,
                    "warnings": warnings,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail={
                    "message": "Export exceeds direct download limit",
                    "matching_count": total,
                    "limit": MAX_DIRECT_EXPORT_ROWS,
                },
            )

        content, media_type, suffix = self._render_export(rows, request)
        file_name = f"submissions-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.{suffix}"
        record = await self._record_export_request(
            org_id=org_id,
            actor_id=actor_id,
            request=request,
            matching_count=total,
            status_value="completed",
            file_name=file_name,
            file_size_bytes=len(content),
            completed_at=datetime.now(timezone.utc),
        )
        await AuditLogger(self.client).log_event(
            user_id=str(actor_id),
            action="DATA_EXPORTED",
            resource_type="export_request",
            resource_id=str(record.get("id")) if record else None,
            metadata={
                "format": request.format,
                "scope": request.scope,
                "matching_count": total,
                "file_name": file_name,
            },
        )
        return content, media_type, file_name

    async def list_history(
        self,
        org_id: UUID,
        page: int = 1,
        page_size: int = 25,
    ) -> tuple[list[dict], int]:
        offset = (page - 1) * page_size
        result = (
            self.client.table("export_requests")
            .select(
                "id, dataset, format, scope, status, matching_count, rejection_reason, created_at",
                count="exact",
            )
            .eq("org_id", str(org_id))
            .order("created_at", desc=True)
            .range(offset, offset + page_size - 1)
            .execute()
        )
        return result.data or [], result.count or len(result.data or [])

    def _fetch_submission_rows(
        self,
        org_id: UUID,
        filters: ExportFilters,
        limit: int,
    ) -> tuple[list[dict], int]:
        query = self.client.table("submissions").select(
            (
                "id, reference_number, template_id, template_version, status, "
                "field_values, operator_id, branch_id, org_id, created_at, templates(name)"
            ),
            count="exact",
        )
        query = query.eq("org_id", str(org_id))

        if filters.template_id:
            query = query.eq("template_id", str(filters.template_id))
        if filters.date_from:
            query = query.gte("created_at", filters.date_from)
        if filters.date_to:
            query = query.lte("created_at", filters.date_to)
        if filters.branch_id:
            query = query.eq("branch_id", str(filters.branch_id))
        if filters.operator_id:
            query = query.eq("operator_id", str(filters.operator_id))
        if filters.status:
            query = query.eq("status", filters.status)

        result = query.order("created_at", desc=True).range(0, limit - 1).execute()
        return result.data or [], result.count or len(result.data or [])

    @staticmethod
    def _filter_warnings(filters: ExportFilters) -> list[str]:
        warnings = []
        if filters.department_id:
            warnings.append("department_filter_unavailable_for_submissions")
        return warnings

    def _render_export(
        self,
        rows: list[dict],
        request: ExportPreviewRequest,
    ) -> tuple[bytes, str, str]:
        if request.format == "json":
            payload = (
                self._structured_rows(rows)
                if request.scope == "structured"
                else self._flat_rows(rows)
            )
            return (
                json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8"),
                "application/json; charset=utf-8",
                "json",
            )
        if request.format == "csv":
            return (
                self._csv_bytes(self._flat_rows(rows)),
                "text/csv; charset=utf-8",
                "csv",
            )
        return (
            self._xlsx_bytes(self._flat_rows(rows)),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "xlsx",
        )

    @staticmethod
    def _template_name(row: dict) -> str:
        templates = row.get("templates") or {}
        if isinstance(templates, dict):
            return templates.get("name", "")
        if isinstance(templates, list) and templates:
            return templates[0].get("name", "")
        return ""

    def _structured_rows(self, rows: list[dict]) -> list[dict]:
        return [
            {
                "id": row["id"],
                "reference_number": row.get("reference_number"),
                "template_id": row.get("template_id"),
                "template_name": self._template_name(row),
                "template_version": row.get("template_version"),
                "status": row.get("status"),
                "operator_id": row.get("operator_id"),
                "branch_id": row.get("branch_id"),
                "created_at": row.get("created_at"),
                "field_values": row.get("field_values") or {},
            }
            for row in rows
        ]

    def _flat_rows(self, rows: list[dict]) -> list[dict]:
        flattened = []
        for row in rows:
            output = {
                "id": row["id"],
                "reference_number": row.get("reference_number"),
                "template_id": row.get("template_id"),
                "template_name": self._template_name(row),
                "template_version": row.get("template_version"),
                "status": row.get("status"),
                "operator_id": row.get("operator_id"),
                "branch_id": row.get("branch_id"),
                "created_at": row.get("created_at"),
            }
            for key, value in (row.get("field_values") or {}).items():
                output[key] = self._escape_spreadsheet_formula(value)
            flattened.append(output)
        return flattened

    @staticmethod
    def _escape_spreadsheet_formula(value):
        if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
            return f"'{value}"
        return value

    @staticmethod
    def _csv_bytes(rows: list[dict]) -> bytes:
        output = io.StringIO()
        output.write("\ufeff")
        headers = sorted({key for row in rows for key in row.keys()})
        writer = csv.DictWriter(output, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        return output.getvalue().encode("utf-8")

    @staticmethod
    def _xlsx_bytes(rows: list[dict]) -> bytes:
        from openpyxl import Workbook

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "submissions"
        headers = sorted({key for row in rows for key in row.keys()})
        sheet.append(headers)
        for row in rows:
            sheet.append([row.get(header) for header in headers])

        output = io.BytesIO()
        workbook.save(output)
        return output.getvalue()

    async def _record_export_request(
        self,
        org_id: UUID,
        actor_id: UUID,
        request: ExportPreviewRequest,
        matching_count: int,
        status_value: str,
        rejection_reason: str | None = None,
        file_name: str | None = None,
        file_size_bytes: int | None = None,
        completed_at: datetime | None = None,
    ) -> dict | None:
        row = {
            "org_id": str(org_id),
            "requested_by": str(actor_id),
            "dataset": "submissions",
            "filters": request.filters.model_dump(mode="json", exclude_none=True),
            "format": request.format,
            "scope": request.scope,
            "matching_count": matching_count,
            "status": status_value,
            "rejection_reason": rejection_reason,
            "file_name": file_name,
            "file_size_bytes": file_size_bytes,
            "completed_at": completed_at.isoformat() if completed_at else None,
            "created_by": str(actor_id),
        }
        result = self.client.table("export_requests").insert(row).execute()
        if result.data:
            return result.data[0]
        return None

    # --- Export Schedule Methods ---

    async def create_schedule(
        self,
        org_id: UUID,
        actor_id: UUID,
        request: dict,
    ) -> dict:
        """Create a new export schedule."""
        row = {
            "org_id": str(org_id),
            "created_by": str(actor_id),
            "updated_by": str(actor_id),
            "name": request["name"],
            "dataset": "submissions",
            "filters": request.get("filters", {}),
            "format": request["format"],
            "scope": request["scope"],
            "frequency": request["frequency"],
            "email_recipients": request["email_recipients"],
            "no_data_behavior": request.get("no_data_behavior", "send_empty_file"),
            "next_run_at": request["next_run_at"],
            "status": "active",
        }
        result = self.client.table("export_schedules").insert(row).execute()
        if result.data:
            return result.data[0]
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create schedule",
        )

    async def list_schedules(
        self,
        org_id: UUID,
    ) -> list[dict]:
        """List all export schedules for an org."""
        result = (
            self.client.table("export_schedules")
            .select("*")
            .eq("org_id", str(org_id))
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []

    async def update_schedule(
        self,
        org_id: UUID,
        schedule_id: UUID,
        actor_id: UUID,
        updates: dict,
    ) -> dict:
        """Update an export schedule."""
        row = {"updated_by": str(actor_id), "updated_at": datetime.now(timezone.utc).isoformat()}
        if "name" in updates:
            row["name"] = updates["name"]
        if "filters" in updates:
            row["filters"] = updates["filters"]
        if "frequency" in updates:
            row["frequency"] = updates["frequency"]
        if "email_recipients" in updates:
            row["email_recipients"] = updates["email_recipients"]
        if "status" in updates:
            row["status"] = updates["status"]
        if "next_run_at" in updates:
            row["next_run_at"] = updates["next_run_at"]

        result = (
            self.client.table("export_schedules")
            .update(row)
            .eq("id", str(schedule_id))
            .eq("org_id", str(org_id))
            .execute()
        )
        if result.data:
            return result.data[0]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    async def run_schedule_now(
        self,
        org_id: UUID,
        schedule_id: UUID,
        actor_id: UUID,
    ) -> dict:
        """Execute a schedule immediately and record delivery."""
        # Fetch schedule
        schedule_result = (
            self.client.table("export_schedules")
            .select("*")
            .eq("id", str(schedule_id))
            .eq("org_id", str(org_id))
            .single()
            .execute()
        )
        if not schedule_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found",
            )

        schedule = schedule_result.data

        # Create delivery record
        delivery_row = {
            "schedule_id": str(schedule_id),
            "org_id": str(org_id),
            "status": "queued",
            "attempt_count": 0,
            "created_by": str(actor_id),
        }
        delivery_result = self.client.table("export_deliveries").insert(delivery_row).execute()
        delivery = delivery_result.data[0] if delivery_result.data else None

        # Generate export using schedule filters
        from app.schemas.export import ExportFilters
        filters = ExportFilters(**(schedule.get("filters") or {}))
        ExportPreviewRequest(filters=filters, format=schedule["format"], scope=schedule["scope"])

        rows, total = self._fetch_submission_rows(org_id, filters, limit=MAX_DIRECT_EXPORT_ROWS + 1)

        if total == 0 and schedule.get("no_data_behavior") == "send_notice":
            # Update delivery to sent with no-data notice
            if delivery:
                self.client.table("export_deliveries").update({
                    "status": "sent",
                    "sent_at": datetime.now(timezone.utc).isoformat(),
                }).eq("id", delivery["id"]).execute()
            return {"status": "sent", "message": "No data to export", "matching_count": 0}

        if total > MAX_DIRECT_EXPORT_ROWS:
            if delivery:
                self.client.table("export_deliveries").update({
                    "status": "failed",
                    "failure_reason": "row_limit_exceeded",
                    "attempt_count": 1,
                }).eq("id", delivery["id"]).execute()
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Export exceeds direct download limit",
            )

        # Update delivery to sent
        if delivery:
            self.client.table("export_deliveries").update({
                "status": "sent",
                "sent_at": datetime.now(timezone.utc).isoformat(),
                "attempt_count": 1,
            }).eq("id", delivery["id"]).execute()

        # Update schedule last_run_at
        self.client.table("export_schedules").update({
            "last_run_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", str(schedule_id)).execute()

        await AuditLogger(self.client).log_event(
            user_id=str(actor_id),
            action="EXPORT_SCHEDULE_EXECUTED",
            resource_type="export_schedule",
            resource_id=str(schedule_id),
            metadata={"matching_count": total, "format": schedule["format"]},
        )

        return {"status": "sent", "matching_count": total, "delivery_id": delivery["id"] if delivery else None}

    async def list_deliveries(
        self,
        org_id: UUID,
        schedule_id: UUID | None = None,
    ) -> list[dict]:
        """List export deliveries for an org."""
        query = self.client.table("export_deliveries").select("*").eq("org_id", str(org_id))
        if schedule_id:
            query = query.eq("schedule_id", str(schedule_id))
        result = query.order("created_at", desc=True).execute()
        return result.data or []

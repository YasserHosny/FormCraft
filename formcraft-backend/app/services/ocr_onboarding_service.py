"""Service layer for batch OCR onboarding."""

from __future__ import annotations

import hashlib
import inspect
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.audit import AuditLogger
from app.schemas.ocr_onboarding import (
    OCRBulkAcceptResponse,
    OCRDuplicateCandidateResponse,
    OCRImportBatchDetailResponse,
    OCRImportBatchResponse,
    OCRImportItemResponse,
)
from app.services.template_service import TemplateService


SUPPORTED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
}
MAX_BATCH_ITEMS = 200


class OCRBatchValidationError(ValueError):
    """Raised when an OCR onboarding batch is invalid before persistence."""


class OCROnboardingService:
    """Manage OCR onboarding batch lifecycle and review decisions."""

    def __init__(self, supabase_client):
        self.client = supabase_client

    async def create_batch(
        self,
        *,
        org_id: UUID,
        created_by: UUID,
        name: str,
        confidence_threshold: float,
        files: list[UploadFile],
    ) -> OCRImportBatchResponse:
        if not files:
            raise OCRBatchValidationError("At least one file is required")
        if len(files) > MAX_BATCH_ITEMS:
            raise OCRBatchValidationError("A batch can contain at most 200 files")

        now = self._now()
        valid_items = []
        invalid_count = 0
        batch_id = uuid4()

        for upload in files:
            content = await upload.read()
            checksum = hashlib.sha256(content).hexdigest()
            mime_type = upload.content_type or "application/octet-stream"
            if mime_type not in SUPPORTED_MIME_TYPES:
                invalid_count += 1
                continue
            valid_items.append(
                {
                    "id": str(uuid4()),
                    "batch_id": str(batch_id),
                    "org_id": str(org_id),
                    "file_name": upload.filename or "upload",
                    "storage_path": None,
                    "mime_type": mime_type,
                    "file_size_bytes": len(content),
                    "checksum": checksum,
                    "status": "queued",
                    "page_count": 1,
                    "retry_count": 0,
                    "created_at": now,
                    "updated_at": now,
                }
            )

        if not valid_items:
            raise OCRBatchValidationError("No supported files were uploaded")

        batch_data = {
            "id": str(batch_id),
            "org_id": str(org_id),
            "name": name,
            "status": "queued",
            "confidence_threshold": confidence_threshold,
            "total_items": len(valid_items),
            "processed_items": 0,
            "accepted_items": 0,
            "failed_items": invalid_count,
            "duplicate_items": 0,
            "created_by": str(created_by),
            "created_at": now,
            "updated_at": now,
        }
        batch_result = await self._execute(self.client.table("ocr_import_batches").insert(batch_data))
        await self._execute(self.client.table("ocr_import_items").insert(valid_items))
        await self._audit(created_by, "ocr_onboarding_batch_create", "ocr_import_batch", str(batch_id), {
            "total_items": len(valid_items),
            "invalid_items": invalid_count,
        })

        return self._batch_response((batch_result.data or [batch_data])[0])

    async def list_batches(
        self,
        *,
        org_id: UUID,
        status_filter: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[OCRImportBatchResponse], int]:
        query = (
            self.client.table("ocr_import_batches")
            .select("*", count="exact")
            .eq("org_id", str(org_id))
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
        )
        if status_filter:
            query = query.eq("status", status_filter)
        result = await self._execute(query)
        return [self._batch_response(row) for row in (result.data or [])], result.count or 0

    async def get_batch(self, *, batch_id: UUID, org_id: UUID) -> OCRImportBatchDetailResponse:
        batch = await self._get_batch_row(batch_id, org_id)
        items_result = await self._execute(
            self.client.table("ocr_import_items")
            .select("*")
            .eq("batch_id", str(batch_id))
            .order("created_at")
        )
        response = OCRImportBatchDetailResponse(
            **self._batch_response(batch).model_dump(),
            items=[self._item_response(row) for row in (items_result.data or [])],
        )
        return response

    async def record_decision(
        self,
        *,
        batch_id: UUID,
        item_id: UUID,
        org_id: UUID,
        decided_by: UUID,
        action: str,
        payload: dict | None = None,
    ) -> OCRImportItemResponse:
        await self._get_batch_row(batch_id, org_id)
        item = await self._get_item_row(batch_id, item_id, org_id)
        payload = payload or {}
        await self._insert_decision(batch_id, item_id, decided_by, action, payload)

        status_by_action = {
            "accept": "accepted",
            "reject": "rejected",
            "defer": "needs_review",
            "edit": "needs_review",
            "merge": "duplicate",
        }
        next_status = status_by_action.get(action, item["status"])
        update_data = {"status": next_status, "updated_at": self._now()}
        if action == "accept":
            template_id = await self._create_draft_template(item, decided_by, org_id)
            update_data.update({"status": "converted", "converted_template_id": str(template_id)})

        result = await self._execute(
            self.client.table("ocr_import_items").update(update_data).eq("id", str(item_id))
        )
        await self._refresh_batch_counts(batch_id)
        await self._audit(decided_by, f"ocr_onboarding_{action}", "ocr_import_item", str(item_id), payload)
        return self._item_response((result.data or [{**item, **update_data}])[0])

    async def bulk_accept(
        self,
        *,
        batch_id: UUID,
        org_id: UUID,
        decided_by: UUID,
        item_ids: list[UUID],
    ) -> OCRBulkAcceptResponse:
        batch = await self._get_batch_row(batch_id, org_id)
        accepted_count = 0
        skipped = []
        for item_id in item_ids:
            item = await self._get_item_row(batch_id, item_id, org_id)
            confidence = item.get("confidence")
            if item.get("status") != "needs_review" or confidence is None:
                skipped.append({"item_id": str(item_id), "reason": "not_eligible"})
                continue
            if float(confidence) < float(batch["confidence_threshold"]):
                skipped.append({"item_id": str(item_id), "reason": "below_threshold"})
                continue
            await self.record_decision(
                batch_id=batch_id,
                item_id=item_id,
                org_id=org_id,
                decided_by=decided_by,
                action="accept",
                payload={"bulk": True},
            )
            accepted_count += 1

        await self._insert_decision(batch_id, None, decided_by, "bulk_accept", {"item_ids": [str(i) for i in item_ids]})
        await self._audit(decided_by, "ocr_onboarding_bulk_accept", "ocr_import_batch", str(batch_id), {
            "accepted_count": accepted_count,
            "skipped": skipped,
        })
        return OCRBulkAcceptResponse(accepted_count=accepted_count, skipped=skipped)

    async def retry_item(
        self,
        *,
        batch_id: UUID,
        item_id: UUID,
        org_id: UUID,
        decided_by: UUID,
    ) -> OCRImportItemResponse:
        item = await self._get_item_row(batch_id, item_id, org_id)
        if item["status"] not in {"failed", "queued"}:
            raise HTTPException(status.HTTP_409_CONFLICT, "Only failed or queued items can be retried")
        update_data = {
            "status": "queued",
            "retry_count": int(item.get("retry_count") or 0) + 1,
            "last_error": None,
            "updated_at": self._now(),
        }
        result = await self._execute(
            self.client.table("ocr_import_items").update(update_data).eq("id", str(item_id))
        )
        await self._insert_decision(batch_id, item_id, decided_by, "retry", {})
        await self._refresh_batch_counts(batch_id)
        await self._audit(decided_by, "ocr_onboarding_retry", "ocr_import_item", str(item_id), {})
        return self._item_response((result.data or [{**item, **update_data}])[0])

    async def resolve_duplicate(
        self,
        *,
        candidate_id: UUID,
        batch_id: UUID,
        org_id: UUID,
        decided_by: UUID,
        decision: str,
    ) -> OCRDuplicateCandidateResponse:
        await self._get_batch_row(batch_id, org_id)
        result = await self._execute(
            self.client.table("ocr_duplicate_candidates")
            .update({"decision": decision, "updated_at": self._now()})
            .eq("id", str(candidate_id))
            .eq("batch_id", str(batch_id))
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Duplicate candidate not found")
        await self._audit(decided_by, "ocr_onboarding_duplicate_resolve", "ocr_duplicate_candidate", str(candidate_id), {
            "decision": decision,
        })
        return OCRDuplicateCandidateResponse(**result.data[0])

    async def _get_batch_row(self, batch_id: UUID, org_id: UUID) -> dict:
        result = await self._execute(
            self.client.table("ocr_import_batches")
            .select("*")
            .eq("id", str(batch_id))
            .eq("org_id", str(org_id))
            .single()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "OCR onboarding batch not found")
        return result.data

    async def _get_item_row(self, batch_id: UUID, item_id: UUID, org_id: UUID) -> dict:
        result = await self._execute(
            self.client.table("ocr_import_items")
            .select("*")
            .eq("id", str(item_id))
            .eq("batch_id", str(batch_id))
            .eq("org_id", str(org_id))
            .single()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "OCR onboarding item not found")
        return result.data

    async def _create_draft_template(self, item: dict, decided_by: UUID, org_id: UUID) -> UUID:
        template = await TemplateService(self.client).create_template(
            {
                "name": item.get("likely_type") or item.get("file_name") or "OCR draft",
                "description": "Created from batch OCR onboarding",
                "category": item.get("category") or "ocr-onboarding",
                "language": item.get("language") or "ar",
                "country": "EG",
                "currency": "EGP",
                "tags": ["ocr-onboarding"],
            },
            user_id=decided_by,
            org_id=org_id,
        )
        return UUID(str(template["id"]))

    async def _insert_decision(
        self,
        batch_id: UUID,
        item_id: UUID | None,
        decided_by: UUID,
        action: str,
        payload: dict,
    ) -> None:
        await self._execute(
            self.client.table("ocr_review_decisions").insert({
                "id": str(uuid4()),
                "batch_id": str(batch_id),
                "item_id": str(item_id) if item_id else None,
                "decided_by": str(decided_by),
                "action": action,
                "payload": payload,
                "created_at": self._now(),
            })
        )

    async def _refresh_batch_counts(self, batch_id: UUID) -> None:
        result = await self._execute(
            self.client.table("ocr_import_items").select("status").eq("batch_id", str(batch_id))
        )
        items = result.data or []
        total = len(items)
        accepted = sum(1 for row in items if row["status"] in {"accepted", "converted"})
        failed = sum(1 for row in items if row["status"] == "failed")
        duplicate = sum(1 for row in items if row["status"] == "duplicate")
        processed = sum(1 for row in items if row["status"] not in {"queued", "processing"})
        batch_status = "completed" if total and processed == total and not failed else "needs_review"
        await self._execute(
            self.client.table("ocr_import_batches")
            .update({
                "status": batch_status,
                "total_items": total,
                "processed_items": processed,
                "accepted_items": accepted,
                "failed_items": failed,
                "duplicate_items": duplicate,
                "updated_at": self._now(),
            })
            .eq("id", str(batch_id))
        )

    async def _audit(
        self,
        user_id: UUID,
        action: str,
        resource_type: str,
        resource_id: str,
        metadata: dict,
    ) -> None:
        await AuditLogger(self.client).log_event(
            user_id=str(user_id),
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata,
        )

    @staticmethod
    async def _execute(query):
        result = query.execute()
        if inspect.isawaitable(result):
            return await result
        return result

    @staticmethod
    def _batch_response(row: dict) -> OCRImportBatchResponse:
        return OCRImportBatchResponse(**row)

    @staticmethod
    def _item_response(row: dict) -> OCRImportItemResponse:
        return OCRImportItemResponse(**row)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

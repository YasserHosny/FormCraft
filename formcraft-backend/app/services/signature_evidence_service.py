import hashlib
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status


class SignatureEvidenceService:
    """Handles evidence package creation, hash verification, and PDF sealing orchestration."""

    def __init__(self, client, pdf_service=None):
        self.client = client
        self.pdf_service = pdf_service

    def compute_document_hash(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    async def create_evidence_package(
        self,
        request_id: UUID,
        original_pdf_path: str | None,
        sealed_pdf_path: str,
        signer_snapshot: list[dict],
        event_summary: list[dict],
    ) -> dict:
        document_hash = ""
        if self.pdf_service and original_pdf_path:
            try:
                pdf_data = await self.pdf_service.download_pdf(original_pdf_path)
                document_hash = self.compute_document_hash(pdf_data)
            except Exception:
                document_hash = ""

        evidence = {
            "request_id": str(request_id),
            "document_hash": document_hash or "unknown",
            "hash_algorithm": "sha256",
            "original_pdf_path": original_pdf_path,
            "sealed_pdf_path": sealed_pdf_path,
            "signer_snapshot": signer_snapshot,
            "event_summary": event_summary,
            "integrity_status": "valid",
            "verified_at": datetime.now(timezone.utc).isoformat(),
        }

        result = (
            self.client.table("signed_evidence_packages")
            .insert(evidence)
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create evidence package")
        return result.data[0]

    async def verify_integrity(self, evidence_id: UUID) -> dict:
        result = (
            self.client.table("signed_evidence_packages")
            .select("*")
            .eq("id", str(evidence_id))
            .single()
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Evidence package not found")

        evidence = result.data
        original_path = evidence.get("original_pdf_path")
        stored_hash = evidence.get("document_hash")

        if not original_path or not stored_hash or stored_hash == "unknown":
            evidence["integrity_status"] = "unknown"
            evidence["verified_at"] = datetime.now(timezone.utc).isoformat()
            self._update_evidence(evidence["id"], evidence)
            return {
                "integrity_status": "unknown",
                "verified_at": evidence["verified_at"],
                "message": "Original document or hash unavailable for verification.",
            }

        if self.pdf_service:
            try:
                pdf_data = await self.pdf_service.download_pdf(original_path)
                current_hash = self.compute_document_hash(pdf_data)
            except Exception:
                current_hash = ""
        else:
            current_hash = ""

        if current_hash and current_hash == stored_hash:
            status_val = "valid"
            message = "Document hash matches expected value."
        else:
            status_val = "invalid"
            message = "Document hash does not match. The document may have been modified."

        evidence["integrity_status"] = status_val
        evidence["verified_at"] = datetime.now(timezone.utc).isoformat()
        self._update_evidence(evidence["id"], evidence)

        return {
            "integrity_status": status_val,
            "verified_at": evidence["verified_at"],
            "message": message,
        }

    def _update_evidence(self, evidence_id: str, data: dict) -> None:
        self.client.table("signed_evidence_packages").update({
            "integrity_status": data["integrity_status"],
            "verified_at": data["verified_at"],
        }).eq("id", evidence_id).execute()

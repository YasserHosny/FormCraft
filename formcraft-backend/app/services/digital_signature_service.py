import logging
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status

from app.services.signature_evidence_service import SignatureEvidenceService
from app.services.signature_token_service import SignatureTokenService
from app.services.signer_identity_service import SignerIdentityService

logger = logging.getLogger(__name__)


class DigitalSignatureService:
    def __init__(
        self,
        client,
        token_service: SignatureTokenService | None = None,
        identity_service: SignerIdentityService | None = None,
        evidence_service: SignatureEvidenceService | None = None,
        email_service=None,
    ):
        self.client = client
        self.token_service = token_service or SignatureTokenService(client)
        self.identity_service = identity_service or SignerIdentityService(client, email_service)
        self.evidence_service = evidence_service or SignatureEvidenceService(client)
        self.email_service = email_service

    # ============================================================
    # Workflow management
    # ============================================================

    async def list_workflows(
        self,
        org_id: UUID,
        *,
        template_id: UUID | None = None,
        is_active: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict], int]:
        offset = (page - 1) * page_size
        query = self.client.table("signature_workflows").select("*", count="exact").eq("org_id", str(org_id))
        if template_id:
            query = query.eq("template_id", str(template_id))
        if is_active is not None:
            query = query.eq("is_active", is_active)
        result = query.order("created_at", desc=True).range(offset, offset + page_size - 1).execute()
        return result.data or [], result.count or len(result.data or [])

    async def create_workflow(self, org_id: UUID, actor_id: UUID, data: dict) -> dict:
        row = {
            "org_id": str(org_id),
            "created_by": str(actor_id),
            "name": data["name"],
            "template_id": str(data["template_id"]) if data.get("template_id") else None,
            "approval_step_id": str(data["approval_step_id"]) if data.get("approval_step_id") else None,
            "is_ordered": data.get("is_ordered", False),
            "expiration_days": data.get("expiration_days", 7),
            "decline_policy": data.get("decline_policy", "stop"),
            "require_all_signers": data.get("require_all_signers", True),
            "is_active": data.get("is_active", True),
        }
        result = self.client.table("signature_workflows").insert(row).execute()
        if not result.data:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create workflow")
        return result.data[0]

    async def update_workflow(self, workflow_id: UUID, org_id: UUID, data: dict) -> dict:
        existing = (
            self.client.table("signature_workflows")
            .select("*")
            .eq("id", str(workflow_id))
            .eq("org_id", str(org_id))
            .single()
            .execute()
        )
        if not existing.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Workflow not found")

        updates = {k: v for k, v in data.items() if v is not None and k in {"name", "expiration_days", "decline_policy", "is_active"}}
        if not updates:
            return existing.data

        result = self.client.table("signature_workflows").update(updates).eq("id", str(workflow_id)).execute()
        return result.data[0]

    # ============================================================
    # Request management
    # ============================================================

    async def create_request(self, org_id: UUID, actor_id: UUID, data: dict) -> dict:
        workflow_id = UUID(str(data["workflow_id"]))
        workflow = (
            self.client.table("signature_workflows")
            .select("*")
            .eq("id", str(workflow_id))
            .eq("org_id", str(org_id))
            .eq("is_active", True)
            .single()
            .execute()
        )
        if not workflow.data:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Workflow not found or inactive")

        wf = workflow.data
        expiration_days = wf.get("expiration_days", 7)
        expires_at = datetime.now(timezone.utc) + timedelta(days=expiration_days)

        row = {
            "workflow_id": str(workflow_id),
            "org_id": str(org_id),
            "created_by": str(actor_id),
            "submission_id": str(data["submission_id"]) if data.get("submission_id") else None,
            "approval_id": str(data["approval_id"]) if data.get("approval_id") else None,
            "status": "draft",
            "expires_at": expires_at.isoformat(),
        }
        req_result = self.client.table("signature_requests").insert(row).execute()
        if not req_result.data:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create signature request")
        request = req_result.data[0]
        request_id = UUID(request["id"])

        # Create recipients
        signers = data.get("signers", [])
        if len(signers) > 10:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Maximum 10 signers allowed")

        for signer in signers:
            rec_row = {
                "request_id": str(request_id),
                "signer_type": signer["signer_type"],
                "profile_id": str(signer["profile_id"]) if signer.get("profile_id") else None,
                "email": signer.get("email"),
                "name": signer["name"],
                "phone": signer.get("phone"),
                "order_index": signer.get("order_index", 0),
                "status": "pending",
            }
            self.client.table("signature_recipients").insert(rec_row).execute()

        await self._log_event(request_id, event_type="created", actor_type="operator", actor_id=actor_id)
        return await self.get_request(request_id)

    async def send_request(self, request_id: UUID, org_id: UUID, actor_id: UUID) -> dict:
        request = await self._get_request_or_404(request_id, org_id)
        if request["status"] != "draft":
            raise HTTPException(status.HTTP_409_CONFLICT, "Request is not in draft state")

        recipients = (
            self.client.table("signature_recipients")
            .select("*")
            .eq("request_id", str(request_id))
            .execute()
        )
        if not recipients.data:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "No signers configured")

        wf = (
            self.client.table("signature_workflows")
            .select("*")
            .eq("id", request["workflow_id"])
            .single()
            .execute()
        )
        is_ordered = wf.data.get("is_ordered", False) if wf.data else False

        for rec in recipients.data:
            rec_id = UUID(rec["id"])
            if is_ordered and rec["order_index"] != 0:
                # Skip non-first signers in ordered workflow
                continue
            await self._invite_recipient(rec_id, rec)

        self.client.table("signature_requests").update({"status": "sent"}).eq("id", str(request_id)).execute()
        await self._log_event(request_id, event_type="invited", actor_type="operator", actor_id=actor_id)
        return await self.get_request(request_id)

    async def _invite_recipient(self, recipient_id: UUID, rec_data: dict) -> None:
        token = await self.token_service.create_signer_token(recipient_id)
        self.client.table("signature_recipients").update({"status": "invited"}).eq("id", str(recipient_id)).execute()
        if self.email_service and rec_data.get("email"):
            await self.email_service.send(
                to=rec_data["email"],
                subject="Signature Request",
                body=f"You have been requested to sign a document. Use this link: /sign/{token}",
            )

    async def cancel_request(self, request_id: UUID, org_id: UUID, actor_id: UUID, reason: str | None = None) -> dict:
        request = await self._get_request_or_404(request_id, org_id)
        if request["status"] in ("canceled", "expired", "sealed", "failed"):
            raise HTTPException(status.HTTP_409_CONFLICT, "Request cannot be canceled")

        self.client.table("signature_requests").update({"status": "canceled"}).eq("id", str(request_id)).execute()
        self.client.table("signature_recipients").update({"status": "canceled"}).eq("request_id", str(request_id)).execute()
        await self._log_event(
            request_id, event_type="canceled", actor_type="operator", actor_id=actor_id,
            event_data={"reason": reason or ""},
        )
        return await self.get_request(request_id)

    async def resend_invitation(self, request_id: UUID, recipient_id: UUID, org_id: UUID, actor_id: UUID) -> dict:
        request = await self._get_request_or_404(request_id, org_id)
        rec = (
            self.client.table("signature_recipients")
            .select("*")
            .eq("id", str(recipient_id))
            .eq("request_id", str(request_id))
            .single()
            .execute()
        )
        if not rec.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Recipient not found")

        await self._invite_recipient(recipient_id, rec.data)
        await self._log_event(request_id, event_type="resend", actor_type="operator", actor_id=actor_id)
        return rec.data

    async def get_request(self, request_id: UUID) -> dict:
        req = (
            self.client.table("signature_requests")
            .select("*")
            .eq("id", str(request_id))
            .single()
            .execute()
        )
        if not req.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Request not found")

        recipients = (
            self.client.table("signature_recipients")
            .select("*")
            .eq("request_id", str(request_id))
            .execute()
        )
        events = (
            self.client.table("signature_events")
            .select("*")
            .eq("request_id", str(request_id))
            .order("created_at", desc=False)
            .execute()
        )

        result = req.data
        result["recipients"] = recipients.data or []
        result["events"] = events.data or []
        return result

    async def list_requests(
        self,
        org_id: UUID,
        *,
        status: str | None = None,
        submission_id: UUID | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict], int]:
        offset = (page - 1) * page_size
        query = self.client.table("signature_requests").select("*", count="exact").eq("org_id", str(org_id))
        if status:
            query = query.eq("status", status)
        if submission_id:
            query = query.eq("submission_id", str(submission_id))
        result = query.order("created_at", desc=True).range(offset, offset + page_size - 1).execute()
        return result.data or [], result.count or len(result.data or [])

    # ============================================================
    # Signer actions
    # ============================================================

    async def record_signer_view(self, recipient_id: UUID, request_id: UUID) -> None:
        self.client.table("signature_recipients").update({"status": "viewed"}).eq("id", str(recipient_id)).execute()
        await self._log_event(request_id, event_type="viewed", actor_type="signer", recipient_id=recipient_id)

    async def record_signature(self, recipient_id: UUID, request_id: UUID, payload: dict) -> dict:
        rec = (
            self.client.table("signature_recipients")
            .select("*")
            .eq("id", str(recipient_id))
            .single()
            .execute()
        )
        if not rec.data or rec.data.get("status") != "verified":
            raise HTTPException(status.HTTP_409_CONFLICT, "Signer must be verified before signing")

        now = datetime.now(timezone.utc).isoformat()
        self.client.table("signature_recipients").update({"status": "signed", "signed_at": now}).eq("id", str(recipient_id)).execute()
        await self._log_event(
            request_id,
            event_type="signed",
            actor_type="signer",
            recipient_id=recipient_id,
            event_data={"ip": payload.get("ip_address"), "ua": payload.get("user_agent")},
        )

        # Check if request is complete
        await self._advance_request(request_id)
        return await self.get_request(request_id)

    async def record_decline(self, recipient_id: UUID, request_id: UUID, reason: str | None = None) -> dict:
        self.client.table("signature_recipients").update({"status": "declined", "decline_reason": reason or ""}).eq("id", str(recipient_id)).execute()
        await self._log_event(
            request_id,
            event_type="declined",
            actor_type="signer",
            recipient_id=recipient_id,
            event_data={"reason": reason or ""},
        )

        request = await self.get_request(request_id)
        wf = (
            self.client.table("signature_workflows")
            .select("decline_policy")
            .eq("id", request["workflow_id"])
            .single()
            .execute()
        )
        policy = wf.data.get("decline_policy", "stop") if wf.data else "stop"

        if policy == "stop":
            self.client.table("signature_requests").update({"status": "declined"}).eq("id", str(request_id)).execute()
        elif policy == "continue_next":
            await self._advance_request(request_id)
        # route_to_admin is handled by notifications elsewhere

        return await self.get_request(request_id)

    async def _advance_request(self, request_id: UUID) -> None:
        request = await self.get_request(request_id)
        wf = (
            self.client.table("signature_workflows")
            .select("is_ordered", "require_all_signers")
            .eq("id", request["workflow_id"])
            .single()
            .execute()
        )
        wf_data = wf.data or {}
        is_ordered = wf_data.get("is_ordered", False)
        require_all = wf_data.get("require_all_signers", True)
        recipients = request.get("recipients", [])

        if is_ordered:
            current = request.get("current_signer_index", 0)
            # Find next signer
            next_signer = None
            for r in recipients:
                if r["order_index"] == current + 1 and r["status"] not in ("declined", "canceled", "expired"):
                    next_signer = r
                    break
            if next_signer:
                self.client.table("signature_requests").update({"current_signer_index": current + 1}).eq("id", str(request_id)).execute()
                await self._invite_recipient(UUID(next_signer["id"]), next_signer)
            else:
                # No more signers; check completion
                await self._check_completion(request_id, recipients, require_all)
        else:
            await self._check_completion(request_id, recipients, require_all)

    async def _check_completion(self, request_id: UUID, recipients: list[dict], require_all: bool) -> None:
        signed_count = sum(1 for r in recipients if r["status"] == "signed")
        total = len(recipients)

        if require_all and signed_count == total:
            await self._seal_request(request_id)
        elif not require_all and signed_count > 0:
            await self._seal_request(request_id)

    async def _seal_request(self, request_id: UUID) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self.client.table("signature_requests").update({"status": "signed", "completed_at": now}).eq("id", str(request_id)).execute()

        # Create evidence package
        request = await self.get_request(request_id)
        signer_snapshot = [
            {"name": r["name"], "email": r.get("email"), "signed_at": r.get("signed_at"), "type": r["signer_type"]}
            for r in request.get("recipients", [])
            if r["status"] == "signed"
        ]
        event_summary = [
            {"type": e["event_type"], "at": e["created_at"]} for e in request.get("events", [])
        ]

        # In a real implementation, sealed_pdf_path would be generated by calling the PDF service
        sealed_path = f"signed/sealed-{request_id}.pdf"
        await self.evidence_service.create_evidence_package(
            request_id=request_id,
            original_pdf_path=request.get("document_hash") and f"submissions/{request['submission_id']}.pdf",
            sealed_pdf_path=sealed_path,
            signer_snapshot=signer_snapshot,
            event_summary=event_summary,
        )

        self.client.table("signature_requests").update({"status": "sealed", "sealed_pdf_path": sealed_path}).eq("id", str(request_id)).execute()
        await self._log_event(request_id, event_type="sealed", actor_type="system")

    # ============================================================
    # Helpers
    # ============================================================

    async def _get_request_or_404(self, request_id: UUID, org_id: UUID) -> dict:
        result = (
            self.client.table("signature_requests")
            .select("*")
            .eq("id", str(request_id))
            .eq("org_id", str(org_id))
            .single()
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Request not found")
        return result.data

    async def _log_event(
        self,
        request_id: UUID,
        event_type: str,
        actor_type: str,
        actor_id: UUID | None = None,
        recipient_id: UUID | None = None,
        event_data: dict | None = None,
    ) -> None:
        row = {
            "request_id": str(request_id),
            "event_type": event_type,
            "actor_type": actor_type,
            "actor_id": str(actor_id) if actor_id else None,
            "recipient_id": str(recipient_id) if recipient_id else None,
            "event_data": event_data or {},
        }
        self.client.table("signature_events").insert(row).execute()

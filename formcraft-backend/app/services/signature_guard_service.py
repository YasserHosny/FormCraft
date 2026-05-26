from uuid import UUID

from fastapi import HTTPException, status


class SignatureGuardService:
    """Enforces FR-007: prevents silent modification of submissions with pending or completed signatures."""

    def __init__(self, client):
        self.client = client

    async def assert_modification_allowed(self, submission_id: UUID) -> None:
        """Raise 409 if the submission has any non-canceled/non-failed signature requests."""
        result = (
            self.client.table("signature_requests")
            .select("id, status")
            .eq("submission_id", str(submission_id))
            .execute()
        )
        if not result.data:
            return

        blocked_statuses = {"draft", "sent", "in_progress", "signed", "sealed"}
        for req in result.data:
            if req.get("status") in blocked_statuses:
                raise HTTPException(
                    status.HTTP_409_CONFLICT,
                    f"Submission has an active signature request ({req['status']}). "
                    "Cancel or invalidate the signature before modifying.",
                )

    async def assert_template_modification_allowed(self, template_id: UUID) -> None:
        """Raise 409 if the template has active signature workflows."""
        result = (
            self.client.table("signature_workflows")
            .select("id")
            .eq("template_id", str(template_id))
            .eq("is_active", True)
            .execute()
        )
        if result.data:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Template has active signature workflows. Deactivate them before modifying.",
            )

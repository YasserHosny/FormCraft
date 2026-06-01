import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.core.audit import AuditLogger
from app.models.submission import Draft

logger = logging.getLogger(__name__)


class DraftService:
    """Draft CRUD with completion tracking and audit logging."""

    def __init__(self, client: Client):
        self.client = client

    async def create_draft(
        self,
        template_id: UUID,
        template_version: int,
        field_values: dict,
        operator_id: UUID,
        org_id: UUID,
        name: str | None = None,
        completion_percent: int | None = None,
    ) -> Draft:
        data = {
            "template_id": str(template_id),
            "template_version": template_version,
            "operator_id": str(operator_id),
            "org_id": str(org_id),
            "field_values": field_values,
            "name": name,
            "completion_percent": completion_percent if completion_percent is not None else 0,
        }

        result = self.client.table("drafts").insert(data).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create draft",
            )

        draft = Draft(**result.data[0])

        audit = AuditLogger(self.client)
        await audit.log_event(
            user_id=str(operator_id),
            action="DRAFT_SAVED",
            resource_type="draft",
            resource_id=str(draft.id),
            metadata={"template_id": str(template_id), "name": name},
            ip_address=None,
        )

        return draft

    async def update_draft(
        self,
        draft_id: UUID,
        operator_id: UUID,
        field_values: dict | None = None,
        name: str | None = None,
        completion_percent: int | None = None,
    ) -> Draft:
        updates = {"updated_at": datetime.now(timezone.utc).isoformat()}
        if field_values is not None:
            updates["field_values"] = field_values
        if name is not None:
            updates["name"] = name
        if completion_percent is not None:
            updates["completion_percent"] = completion_percent

        result = (
            self.client.table("drafts")
            .update(updates)
            .eq("id", str(draft_id))
            .eq("operator_id", str(operator_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found",
            )

        draft = Draft(**result.data[0])

        audit = AuditLogger(self.client)
        await audit.log_event(
            user_id=str(operator_id),
            action="DRAFT_SAVED",
            resource_type="draft",
            resource_id=str(draft_id),
            metadata={"field_count": len(field_values) if field_values else 0},
            ip_address=None,
        )

        return draft

    async def get_draft(self, draft_id: UUID, operator_id: UUID) -> Draft:
        result = (
            self.client.table("drafts")
            .select("*")
            .eq("id", str(draft_id))
            .eq("operator_id", str(operator_id))
            .single()
            .execute()
        )
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found",
            )

        draft = Draft(**result.data)

        if draft.expires_at and draft.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Draft expired",
            )

        return draft

    async def list_drafts(self, operator_id: UUID) -> list[Draft]:
        result = (
            self.client.table("drafts")
            .select("*")
            .eq("operator_id", str(operator_id))
            .order("updated_at", desc=True)
            .execute()
        )
        return [Draft(**row) for row in (result.data or [])]

    async def delete_draft(self, draft_id: UUID, operator_id: UUID) -> None:
        result = (
            self.client.table("drafts")
            .delete()
            .eq("id", str(draft_id))
            .eq("operator_id", str(operator_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found",
            )

        audit = AuditLogger(self.client)
        await audit.log_event(
            user_id=str(operator_id),
            action="DRAFT_DELETED",
            resource_type="draft",
            resource_id=str(draft_id),
            metadata={},
            ip_address=None,
        )

    def compute_completion_percent(self, field_values: dict, required_keys: list[str]) -> int:
        if not required_keys:
            return 0
        filled = sum(1 for key in required_keys if key in field_values and field_values[key] not in (None, ""))
        return int((filled / len(required_keys)) * 100)

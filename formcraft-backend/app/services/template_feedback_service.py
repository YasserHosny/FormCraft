"""Template feedback service — operator/designer feedback on template elements."""

import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

logger = logging.getLogger(__name__)

VALID_CATEGORIES = {"layout", "readability", "logical", "other"}
VALID_STATUSES = {"new", "acknowledged", "resolved"}


class TemplateFeedbackService:
    """CRUD and admin overview for template_feedback rows."""

    def __init__(self, client: Client):
        self.client = client

    def submit_feedback(
        self,
        template_id: UUID,
        user_id: UUID,
        category: str,
        comment: str,
        page_number: int | None = None,
        element_key: str | None = None,
        screenshot_path: str | None = None,
    ) -> dict:
        if category not in VALID_CATEGORIES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category. Must be one of: {', '.join(sorted(VALID_CATEGORIES))}",
            )

        row = {
            "template_id": str(template_id),
            "created_by": str(user_id),
            "category": category,
            "comment": comment,
            "page_number": page_number,
            "element_key": element_key,
            "screenshot_path": screenshot_path,
            "status": "new",
        }
        result = self.client.table("template_feedback").insert(row).execute()
        fb = result.data[0]

        creator = self.client.table("profiles").select("full_name").eq("id", str(user_id)).single().execute()
        fb["created_by_name"] = creator.data.get("full_name") if creator.data else None

        return fb

    def list_feedback(
        self,
        template_id: UUID,
        status_filter: str | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> dict:
        query = (
            self.client.table("template_feedback")
            .select("*, profiles!template_feedback_created_by_fkey(full_name)", count="exact")
            .eq("template_id", str(template_id))
            .order("created_at", desc=True)
        )
        if status_filter and status_filter in VALID_STATUSES:
            query = query.eq("status", status_filter)

        offset = (page - 1) * limit
        result = query.range(offset, offset + limit - 1).execute()

        items = []
        for row in result.data:
            profile = row.pop("profiles", None)
            row["created_by_name"] = profile.get("full_name") if profile else None
            items.append(row)

        return {"items": items, "total": result.count}

    def update_feedback_status(
        self,
        feedback_id: UUID,
        new_status: str,
        user_id: UUID,
    ) -> dict:
        if new_status not in VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(sorted(VALID_STATUSES))}",
            )

        update: dict = {"status": new_status, "updated_at": datetime.now(timezone.utc).isoformat()}
        if new_status == "resolved":
            update["resolved_by"] = str(user_id)
            update["resolved_at"] = datetime.now(timezone.utc).isoformat()

        result = (
            self.client.table("template_feedback")
            .update(update)
            .eq("id", str(feedback_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

        fb = result.data[0]
        creator = self.client.table("profiles").select("full_name").eq("id", str(fb["created_by"])).single().execute()
        fb["created_by_name"] = creator.data.get("full_name") if creator.data else None

        return fb

    def get_admin_overview(self, org_id: UUID | None = None) -> list[dict]:
        query = (
            self.client.table("template_feedback")
            .select("template_id, status, templates!template_feedback_template_id_fkey(name)")
        )
        if org_id:
            query = query.eq("templates.org_id", str(org_id))

        result = query.execute()

        summary: dict[tuple, dict] = {}
        for row in result.data:
            tid = row["template_id"]
            tname = row.get("templates", {}).get("name", "Unknown") if row.get("templates") else "Unknown"
            key = (tid, tname)
            if key not in summary:
                summary[key] = {"template_id": tid, "template_name": tname, "total_feedback": 0, "new_count": 0, "acknowledged_count": 0, "resolved_count": 0}
            summary[key]["total_feedback"] += 1
            s = row.get("status", "new")
            if s == "new":
                summary[key]["new_count"] += 1
            elif s == "acknowledged":
                summary[key]["acknowledged_count"] += 1
            elif s == "resolved":
                summary[key]["resolved_count"] += 1

        return list(summary.values())
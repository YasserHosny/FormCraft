"""Template governance: all-status oversight, bulk actions, and compliance."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.schemas.admin_templates import BulkActionRequest


class TemplateGovernanceService:
    def __init__(self, client: Client):
        self.client = client

    async def list_templates(
        self,
        org_id: UUID,
        page: int = 1,
        page_size: int = 25,
        status_filter: str | None = None,
        department_id: UUID | None = None,
        designer_id: UUID | None = None,
        category: str | None = None,
        search: str | None = None,
        sort_by: str = "updated_at",
        sort_dir: str = "desc",
    ) -> tuple[list[dict], int]:
        """Query all templates for an org with filters, sorting, pagination."""
        query = (
            self.client.table("templates")
            .select(
                "id, name, category, status, version, created_by, department_id, updated_at, created_at, "
                "profiles!templates_created_by_fkey(display_name), "
                "departments!templates_department_id_fkey(name_en)"
            )
            .eq("org_id", str(org_id))
        )

        if status_filter and status_filter != "all":
            query = query.eq("status", status_filter)
        if department_id:
            query = query.eq("department_id", str(department_id))
        if designer_id:
            query = query.eq("created_by", str(designer_id))
        if category:
            query = query.eq("category", category)
        if search:
            pattern = f"%{search}%"
            query = query.or_(f"name.ilike.{pattern},category.ilike.{pattern}")

        # Validate sort
        allowed_sort = {
            "name",
            "status",
            "category",
            "version",
            "updated_at",
            "created_at",
        }
        if sort_by not in allowed_sort:
            sort_by = "updated_at"

        sort_desc = sort_dir.lower() == "desc"
        query = query.order(sort_by, desc=sort_desc)

        start = (page - 1) * page_size
        result = query.range(start, start + page_size - 1).execute()

        items = []
        for t in result.data or []:
            profile = t.get("profiles") or {}
            dept = t.get("departments") or {}
            items.append(
                {
                    "id": t["id"],
                    "name": t["name"],
                    "category": t.get("category", "general"),
                    "status": t["status"],
                    "version": t.get("version", 1),
                    "designer_id": t["created_by"],
                    "designer_name": profile.get("display_name")
                    if isinstance(profile, dict)
                    else None,
                    "department_id": t.get("department_id"),
                    "department_name": dept.get("name_en")
                    if isinstance(dept, dict)
                    else None,
                    "quality_score": None,  # Computed later
                    "updated_at": t["updated_at"],
                    "created_at": t["created_at"],
                }
            )

        return items, len(result.data or [])

    async def preview_bulk_action(
        self, org_id: UUID, request: BulkActionRequest
    ) -> dict:
        """Preview a bulk action without executing."""
        template_ids = [str(tid) for tid in request.template_ids]

        # Fetch selected templates
        result = (
            self.client.table("templates")
            .select("id, name, status, created_by")
            .in_("id", template_ids)
            .eq("org_id", str(org_id))
            .execute()
        )

        templates = result.data or []
        warnings = []
        items = []

        published_count = sum(1 for t in templates if t["status"] == "published")

        if request.action == "archive" and published_count > 0:
            # Count current-month usage
            month_start = datetime.now(timezone.utc).replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            usage_result = (
                self.client.table("form_submissions")
                .select("operator_id", count="exact")
                .in_("template_id", template_ids)
                .gte("created_at", month_start.isoformat())
                .execute()
            )
            distinct_operators = len(
                {r["operator_id"] for r in (usage_result.data or [])}
            )
            warnings.append(
                f"{published_count} published templates selected — {distinct_operators} operators used them this month."
            )

        for t in templates:
            items.append(
                {
                    "template_id": t["id"],
                    "template_name": t["name"],
                    "current_status": t["status"],
                    "warning": None,
                }
            )

        return {
            "action": request.action,
            "dry_run": True,
            "affected_count": len(templates),
            "warnings": warnings,
            "items": items,
        }

    async def execute_bulk_action(
        self, org_id: UUID, request: BulkActionRequest, actor_id: UUID
    ) -> dict:
        """Execute a bulk action with audit logging."""
        if request.dry_run:
            return await self.preview_bulk_action(org_id, request)

        template_ids = [str(tid) for tid in request.template_ids]

        # Fetch templates
        result = (
            self.client.table("templates")
            .select("id, name, status")
            .in_("id", template_ids)
            .eq("org_id", str(org_id))
            .execute()
        )
        templates = result.data or []

        if request.action == "archive":
            for t in templates:
                self.client.table("templates").update({"status": "archived"}).eq(
                    "id", t["id"]
                ).execute()
            action_name = "TEMPLATE_BULK_ARCHIVED"
        elif request.action == "reassign":
            if not request.new_designer_id:
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY, "new_designer_id required"
                )
            for t in templates:
                self.client.table("templates").update(
                    {"created_by": str(request.new_designer_id)}
                ).eq("id", t["id"]).execute()
            action_name = "TEMPLATE_REASSIGNED"
        elif request.action == "change_category":
            if not request.new_category:
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY, "new_category required"
                )
            for t in templates:
                self.client.table("templates").update(
                    {"category": request.new_category}
                ).eq("id", t["id"]).execute()
            action_name = "TEMPLATE_CATEGORY_CHANGED"
        else:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"Unknown action: {request.action}",
            )

        # Audit log
        from app.core.audit import AuditLogger

        await AuditLogger(self.client).log_event(
            user_id=str(actor_id),
            action=action_name,
            resource_type="template",
            resource_id=",".join(template_ids),
            metadata={
                "action": request.action,
                "count": len(templates),
                "template_ids": template_ids,
            },
        )

        return {
            "action": request.action,
            "dry_run": False,
            "affected_count": len(templates),
            "warnings": [],
            "items": [],
        }

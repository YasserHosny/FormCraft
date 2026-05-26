import logging
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.models.desk import OperatorPin
from app.schemas.desk import (
    DashboardResponse,
    NotificationResponse,
    PinnedTemplateResponse,
    RecentTemplateResponse,
    TemplateCardResponse,
    TemplatesPageResponse,
)

logger = logging.getLogger(__name__)

PIN_LIMIT = 20


class DeskService:
    """Dashboard aggregation, pin CRUD, and notification dismissal."""

    def __init__(self, client: Client):
        self.client = client

    async def get_dashboard(
        self,
        operator_id: UUID,
        org_id: UUID | None,
        search: str | None = None,
        category: str | None = None,
        country: str | None = None,
        language: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> DashboardResponse:
        offset = (page - 1) * limit

        templates_data = self._get_templates(
            operator_id=operator_id,
            org_id=org_id,
            search=search,
            category=category,
            country=country,
            language=language,
            offset=offset,
            limit=limit,
        )
        recent = self._get_recent(operator_id=operator_id, org_id=org_id, limit=10)
        pinned = self._get_pinned(operator_id=operator_id, org_id=org_id)
        notifications = self._get_notifications(operator_id=operator_id, org_id=org_id)

        return DashboardResponse(
            templates=templates_data,
            recent=recent,
            pinned=pinned,
            drafts=[],
            notifications=notifications,
        )

    def _get_templates(
        self,
        operator_id: UUID,
        org_id: UUID | None,
        search: str | None,
        category: str | None,
        country: str | None,
        language: str | None,
        offset: int,
        limit: int,
    ) -> TemplatesPageResponse:
        query = (
            self.client.table("templates")
            .select("*, operator_pins!left(id, operator_id)", count="exact")
            .in_("status", ("published", "deprecated"))
        )

        if org_id:
            query = query.eq("org_id", str(org_id))
        if search:
            query = query.ilike("name", f"%{search}%")
        if category:
            query = query.eq("category", category)
        if country:
            query = query.eq("country", country)
        if language:
            query = query.eq("language", language)

        fetch_window = max(limit * 5, limit)
        start = offset
        end = start + fetch_window - 1

        result = (
            query.order("updated_at", desc=True)
            .range(start, end)
            .execute()
        )

        seen_lineages: set[str] = set()
        deduped = []
        for row in result.data or []:
            lineage = str(row.get("lineage_id", row["id"]))
            if lineage in seen_lineages:
                continue
            seen_lineages.add(lineage)
            deduped.append(row)
            if len(deduped) >= limit:
                break

        total_count = result.count or 0

        pin_ids = set()
        try:
            pins_result = (
                self.client.table("operator_pins")
                .select("template_id")
                .eq("operator_id", str(operator_id))
                .execute()
            )
            pin_ids = {str(row["template_id"]) for row in pins_result.data}
        except Exception:
            pass

        items = []
        for row in deduped:
            items.append(
                TemplateCardResponse(
                    id=row["id"],
                    name=row.get("name", ""),
                    description=row.get("description"),
                    category=row.get("category"),
                    status=row.get("status", "published"),
                    version=row.get("version", 1),
                    lineage_id=row.get("lineage_id"),
                    is_deprecated=row.get("status") == "deprecated",
                    language=row.get("language"),
                    country=row.get("country"),
                    updated_at=row.get("updated_at", ""),
                    is_pinned=str(row["id"]) in pin_ids,
                )
            )

        return TemplatesPageResponse(
            items=items,
            total=total_count,
            page=(offset // limit) + 1,
            limit=limit,
        )

    def _get_recent(
        self, operator_id: UUID, org_id: UUID | None, limit: int = 10
    ) -> list[RecentTemplateResponse]:
        try:
            query = (
                self.client.table("submissions")
                .select("template_id, created_at, templates(id, name, category, version)")
                .eq("operator_id", str(operator_id))
                .order("created_at", desc=True)
                .limit(limit * 3)
                .execute()
            )
        except Exception:
            return []

        seen = set()
        recent = []
        for row in query.data:
            tid = row.get("template_id")
            if tid and str(tid) not in seen:
                seen.add(str(tid))
                tpl = row.get("templates")
                if tpl and isinstance(tpl, dict):
                    recent.append(
                        RecentTemplateResponse(
                            template_id=tid,
                            template_name=tpl.get("name", ""),
                            category=tpl.get("category"),
                            version=tpl.get("version", 1),
                            last_used_at=row.get("created_at", ""),
                        )
                    )
                if len(recent) >= limit:
                    break
        return recent

    def _get_pinned(
        self, operator_id: UUID, org_id: UUID | None
    ) -> list[PinnedTemplateResponse]:
        try:
            query = (
                self.client.table("operator_pins")
                .select("template_id, created_at, templates(id, name, category, version, status)")
                .eq("operator_id", str(operator_id))
                .order("created_at", desc=True)
                .execute()
            )
        except Exception:
            return []

        pinned = []
        for row in query.data:
            tpl = row.get("templates")
            if tpl and isinstance(tpl, dict):
                pinned.append(
                    PinnedTemplateResponse(
                        template_id=tpl["id"],
                        template_name=tpl.get("name", ""),
                        category=tpl.get("category"),
                        version=tpl.get("version", 1),
                        is_published=tpl.get("status") == "published",
                        pinned_at=row.get("created_at", ""),
                    )
                )
        return pinned

    def _get_notifications(
        self, operator_id: UUID, org_id: UUID | None
    ) -> list[NotificationResponse]:
        try:
            recent_submissions = (
                self.client.table("submissions")
                .select("template_id, MAX(created_at)")
                .eq("operator_id", str(operator_id))
                .group("template_id")
                .execute()
            )
        except Exception:
            return []

        try:
            dismissed = (
                self.client.table("notification_dismissals")
                .select("template_id, dismissed_version")
                .eq("operator_id", str(operator_id))
                .execute()
            )
            dismissed_map: dict[str, set[int]] = {}
            for d in dismissed.data:
                key = str(d["template_id"])
                dismissed_map.setdefault(key, set()).add(d["dismissed_version"])
        except Exception:
            dismissed_map = {}

        notifications = []
        template_ids = [str(r["template_id"]) for r in recent_submissions.data] if recent_submissions.data else []

        if not template_ids:
            return notifications

        try:
            templates_result = (
                self.client.table("templates")
                .select("id, name, version, updated_at")
                .in_("id", template_ids)
                .execute()
            )
        except Exception:
            return notifications

        for tpl in templates_result.data:
            tpl_id_str = str(tpl["id"])
            current_version = tpl.get("version", 1)
            old_version = max(current_version - 1, 1)

            if old_version >= current_version:
                continue

            notification_id = f"{tpl_id_str}:{current_version}"
            if tpl_id_str in dismissed_map and current_version in dismissed_map[tpl_id_str]:
                continue

            notifications.append(
                NotificationResponse(
                    id=notification_id,
                    template_id=tpl["id"],
                    template_name=tpl.get("name", ""),
                    old_version=old_version,
                    new_version=current_version,
                    updated_at=tpl.get("updated_at", ""),
                )
            )

        return notifications

    async def pin_template(
        self, operator_id: UUID, template_id: UUID, org_id: UUID
    ) -> OperatorPin:
        count_result = (
            self.client.table("operator_pins")
            .select("id", count="exact")
            .eq("operator_id", str(operator_id))
            .execute()
        )
        if (count_result.count or 0) >= PIN_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Maximum 20 pinned templates allowed",
            )

        try:
            template_exists = (
                self.client.table("templates")
                .select("id, status")
                .eq("id", str(template_id))
                .single()
                .execute()
            )
            if not template_exists.data or template_exists.data.get("status") != "published":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Template not found",
                )
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found",
            )

        try:
            result = (
                self.client.table("operator_pins")
                .insert(
                    {
                        "operator_id": str(operator_id),
                        "template_id": str(template_id),
                        "org_id": str(org_id),
                    }
                )
                .execute()
            )
            return OperatorPin(**result.data[0])
        except Exception as e:
            error_msg = str(e).lower()
            if "unique" in error_msg or "duplicate" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Template already pinned",
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to pin template",
            )

    async def unpin_template(self, operator_id: UUID, template_id: UUID) -> None:
        result = (
            self.client.table("operator_pins")
            .delete()
            .eq("operator_id", str(operator_id))
            .eq("template_id", str(template_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pin not found",
            )

    async def dismiss_notification(
        self, operator_id: UUID, template_id: UUID, version: int, org_id: UUID
    ) -> None:
        self.client.table("notification_dismissals").upsert(
            {
                "operator_id": str(operator_id),
                "template_id": str(template_id),
                "dismissed_version": version,
                "org_id": str(org_id),
            },
            on_conflict="operator_id,template_id,dismissed_version",
        ).execute()
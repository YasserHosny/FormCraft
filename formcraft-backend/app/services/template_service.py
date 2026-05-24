"""Template, Page, and Element CRUD operations via Supabase."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from supabase import Client

TRANSITION_MAP: dict[str, list[str]] = {
    "draft": ["submitted_for_review", "published"],
    "submitted_for_review": ["approved", "rejected", "draft"],
    "approved": ["published"],
    "rejected": ["draft", "submitted_for_review"],
    "published": ["archived", "deprecated"],
    "archived": ["published"],
    "deprecated": ["archived"],
}

ROLE_TRANSITIONS: dict[str, list[str]] = {
    "draft->submitted_for_review": ["designer", "admin"],
    "draft->published": ["designer", "admin"],
    "submitted_for_review->approved": ["admin", "branch_manager"],
    "submitted_for_review->rejected": ["admin", "branch_manager"],
    "submitted_for_review->draft": ["designer", "admin"],
    "approved->published": ["admin"],
    "rejected->draft": ["designer", "admin"],
    "rejected->submitted_for_review": ["designer", "admin"],
    "published->archived": ["admin"],
    "published->deprecated": ["admin"],
    "archived->published": ["admin"],
    "deprecated->archived": ["admin"],
}

EDITABLE_STATUSES = {"draft", "rejected"}


class TemplateService:
    """Template domain model CRUD with optimistic concurrency."""

    def __init__(self, client: Client):
        self.client = client

    def _check_editable(self, template: dict) -> None:
        if template.get("status") not in EDITABLE_STATUSES:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail={
                    "detail": "Template is not editable in current status",
                    "status": template.get("status"),
                    "hint": "Create a new version to make changes",
                },
            )

    # --- Lifecycle ---

    async def transition_status(
        self,
        template_id: UUID,
        new_status: str,
        actor_id: UUID,
        comment: str | None = None,
        element_comments: list[dict] | None = None,
    ) -> dict:
        template = await self.get_template(template_id)
        current_status = template.get("status")

        if current_status not in TRANSITION_MAP:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"Unknown current status: {current_status}",
            )

        allowed = TRANSITION_MAP.get(current_status, [])
        if new_status not in allowed:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"Cannot transition from '{current_status}' to '{new_status}'",
            )

        # Approval-disabled shortcut: draft -> published when approval is disabled
        if current_status == "draft" and new_status == "published":
            org_settings = await self._get_org_settings(template.get("org_id"))
            if org_settings.get("approval_workflow_enabled", True):
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "Approval workflow requires review before publishing",
                )

        transition_key = f"{current_status}->{new_status}"
        allowed_roles = ROLE_TRANSITIONS.get(transition_key, [])
        actor_profile = (
            self.client.table("profiles")
            .select("role")
            .eq("id", str(actor_id))
            .single()
            .execute()
        )
        actor_role = actor_profile.data.get("role", "") if actor_profile.data else ""
        if allowed_roles and actor_role not in allowed_roles:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"Only {', '.join(allowed_roles)} can perform this transition",
            )

        # Self-review prevention: actor cannot approve/reject their own template
        if new_status in ("approved", "rejected") and str(
            template.get("created_by")
        ) == str(actor_id):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "Cannot review your own template",
            )

        if new_status == "rejected" and not comment:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "Comment required when rejecting",
            )

        result = (
            self.client.table("templates")
            .update({"status": new_status})
            .eq("id", str(template_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Template not found")

        from app.core.audit import AuditLogger

        action_name = f"TEMPLATE_{new_status.upper()}"
        if new_status == "draft" and current_status == "submitted_for_review":
            action_name = "TEMPLATE_WITHDRAWN"

        await AuditLogger(self.client).log_event(
            user_id=str(actor_id),
            action=action_name,
            resource_type="template",
            resource_id=str(template_id),
            metadata={
                "from_status": current_status,
                "to_status": new_status,
                "comment": comment,
            },
        )

        if new_status in ("approved", "rejected"):
            review_data = {
                "template_id": str(template_id),
                "reviewer_id": str(actor_id),
                "action": new_status,
                "comment": comment,
                "element_comments": element_comments,
                "org_id": template.get("org_id"),
            }
            self.client.table("template_reviews").insert(review_data).execute()

        return result.data[0]

    async def _get_org_settings(self, org_id: UUID | None) -> dict:
        if not org_id:
            return {}
        try:
            result = (
                self.client.table("organizations")
                .select("settings")
                .eq("id", str(org_id))
                .single()
                .execute()
            )
            if result.data and result.data.get("settings"):
                return result.data["settings"]
        except Exception:
            pass
        return {}

    # --- Templates ---

    async def create_template(self, data: dict, user_id: UUID) -> dict:
        new_id = str(uuid4())
        template_data = {
            **data,
            "id": new_id,
            "created_by": str(user_id),
            "status": "draft",
            "version": 1,
            "lineage_id": new_id,
        }
        result = self.client.table("templates").insert(template_data).execute()
        template = result.data[0]

        page_data = {
            "template_id": template["id"],
            "width_mm": 210,
            "height_mm": 297,
            "sort_order": 0,
        }
        self.client.table("pages").insert(page_data).execute()

        return await self.get_template(UUID(template["id"]))

    async def get_template(self, template_id: UUID) -> dict:
        result = (
            self.client.table("templates")
            .select("*")
            .eq("id", str(template_id))
            .single()
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Template not found")

        template = result.data
        pages_result = (
            self.client.table("pages")
            .select("*")
            .eq("template_id", str(template_id))
            .order("sort_order")
            .execute()
        )
        template["pages"] = pages_result.data or []

        for page in template["pages"]:
            elements_result = (
                self.client.table("elements")
                .select("*")
                .eq("page_id", page["id"])
                .order("sort_order")
                .execute()
            )
            page["elements"] = elements_result.data or []

        return template

    async def list_templates(
        self,
        page: int = 1,
        limit: int = 20,
        status_filter: str | None = None,
        category: str | None = None,
        country: str | None = None,
        search: str | None = None,
        department_id: str | None = None,
        user_role: str | None = None,
    ) -> tuple[list[dict], int]:
        offset = (page - 1) * limit
        query = self.client.table("templates").select("*", count="exact")

        if status_filter:
            query = query.eq("status", status_filter)
        if category:
            query = query.eq("category", category)
        if country:
            query = query.eq("country", country)
        if search:
            query = query.ilike("name", f"%{search}%")
        if department_id and user_role not in ("admin", "branch_manager"):
            query = query.or_(f"department_id.is.null,department_id.eq.{department_id}")

        result = (
            query.range(offset, offset + limit - 1)
            .order("updated_at", desc=True)
            .execute()
        )
        return result.data or [], result.count or 0

    async def update_template(
        self,
        template_id: UUID,
        data: dict,
        expected_updated_at: str,
    ) -> dict:
        template = await self.get_template(template_id)
        self._check_editable(template)
        result = (
            self.client.table("templates")
            .update(data)
            .eq("id", str(template_id))
            .eq("updated_at", expected_updated_at)
            .execute()
        )
        if not result.data:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Template was modified by another user. Please refresh.",
            )
        return result.data[0]

    async def delete_template(self, template_id: UUID) -> None:
        template = await self.get_template(template_id)
        self._check_editable(template)
        self.client.table("templates").delete().eq("id", str(template_id)).execute()

    async def publish_template(self, template_id: UUID) -> dict:
        result = (
            self.client.table("templates")
            .update({"status": "published"})
            .eq("id", str(template_id))
            .eq("status", "draft")
            .execute()
        )
        if not result.data:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Template is not in draft status or not found.",
            )
        return result.data[0]

    # --- Pages ---

    async def add_page(self, template_id: UUID, data: dict) -> dict:
        template = await self.get_template(template_id)
        self._check_editable(template)
        existing = (
            self.client.table("pages")
            .select("sort_order")
            .eq("template_id", str(template_id))
            .order("sort_order", desc=True)
            .limit(1)
            .execute()
        )
        next_order = (existing.data[0]["sort_order"] + 1) if existing.data else 0
        page_data = {
            **data,
            "template_id": str(template_id),
            "sort_order": next_order,
        }
        result = self.client.table("pages").insert(page_data).execute()
        return result.data[0]

    async def update_page(self, page_id: UUID, data: dict) -> dict:
        page = (
            self.client.table("pages")
            .select("template_id")
            .eq("id", str(page_id))
            .single()
            .execute()
        )
        if not page.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Page not found")
        template = await self.get_template(UUID(page.data["template_id"]))
        self._check_editable(template)
        result = (
            self.client.table("pages").update(data).eq("id", str(page_id)).execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Page not found")
        return result.data[0]

    async def delete_page(self, page_id: UUID) -> None:
        page = (
            self.client.table("pages")
            .select("template_id")
            .eq("id", str(page_id))
            .single()
            .execute()
        )
        if not page.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Page not found")
        template = await self.get_template(UUID(page.data["template_id"]))
        self._check_editable(template)

        count_result = (
            self.client.table("pages")
            .select("id", count="exact")
            .eq("template_id", page.data["template_id"])
            .execute()
        )
        if (count_result.count or 0) <= 1:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Cannot delete the last page of a template.",
            )

        self.client.table("pages").delete().eq("id", str(page_id)).execute()

    # --- Elements ---

    async def add_element(self, page_id: UUID, data: dict) -> dict:
        import uuid as uuid_mod

        page = (
            self.client.table("pages")
            .select("template_id")
            .eq("id", str(page_id))
            .single()
            .execute()
        )
        if not page.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Page not found")
        template = await self.get_template(UUID(page.data["template_id"]))
        self._check_editable(template)

        key = f"{data.get('type', 'field')}_{uuid_mod.uuid4().hex[:8]}"

        existing = (
            self.client.table("elements")
            .select("sort_order")
            .eq("page_id", str(page_id))
            .order("sort_order", desc=True)
            .limit(1)
            .execute()
        )
        next_order = (existing.data[0]["sort_order"] + 1) if existing.data else 0

        element_data = {
            **data,
            "page_id": str(page_id),
            "key": key,
            "sort_order": next_order,
        }
        # Try full insert first; on schema error, strip columns that may
        # not exist yet (migrations 023/024 add extra element columns).
        try:
            result = self.client.table("elements").insert(element_data).execute()
        except Exception as exc:
            if "PGRST204" in str(exc) or "schema cache" in str(exc):
                _BASE_ELEMENT_COLS = {
                    "page_id",
                    "type",
                    "key",
                    "label_ar",
                    "label_en",
                    "x_mm",
                    "y_mm",
                    "width_mm",
                    "height_mm",
                    "validation",
                    "formatting",
                    "required",
                    "direction",
                    "sort_order",
                }
                element_data = {
                    k: v for k, v in element_data.items() if k in _BASE_ELEMENT_COLS
                }
                result = self.client.table("elements").insert(element_data).execute()
            else:
                raise
        return result.data[0]

    async def update_element(self, element_id: UUID, data: dict) -> dict:
        element = (
            self.client.table("elements")
            .select("page_id")
            .eq("id", str(element_id))
            .single()
            .execute()
        )
        if not element.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Element not found")
        page = (
            self.client.table("pages")
            .select("template_id")
            .eq("id", element.data["page_id"])
            .single()
            .execute()
        )
        if page.data:
            template = await self.get_template(UUID(page.data["template_id"]))
            self._check_editable(template)
        try:
            result = (
                self.client.table("elements")
                .update(data)
                .eq("id", str(element_id))
                .execute()
            )
        except Exception as exc:
            if "PGRST204" in str(exc) or "schema cache" in str(exc):
                _BASE_ELEMENT_COLS = {
                    "type",
                    "key",
                    "label_ar",
                    "label_en",
                    "x_mm",
                    "y_mm",
                    "width_mm",
                    "height_mm",
                    "validation",
                    "formatting",
                    "required",
                    "direction",
                    "sort_order",
                }
                data = {k: v for k, v in data.items() if k in _BASE_ELEMENT_COLS}
                result = (
                    self.client.table("elements")
                    .update(data)
                    .eq("id", str(element_id))
                    .execute()
                )
            else:
                raise
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Element not found")
        return result.data[0]

    async def delete_element(self, element_id: UUID) -> None:
        element = (
            self.client.table("elements")
            .select("page_id")
            .eq("id", str(element_id))
            .single()
            .execute()
        )
        if element.data:
            page = (
                self.client.table("pages")
                .select("template_id")
                .eq("id", element.data["page_id"])
                .single()
                .execute()
            )
            if page.data:
                template = await self.get_template(UUID(page.data["template_id"]))
                self._check_editable(template)
        self.client.table("elements").delete().eq("id", str(element_id)).execute()

    async def reorder_pages(self, template_id: UUID, page_ids: list[UUID]) -> None:
        template = await self.get_template(template_id)
        self._check_editable(template)
        existing_page_ids = {page["id"] for page in template.get("pages", [])}
        requested_page_ids = [str(pid) for pid in page_ids]

        if len(existing_page_ids) != len(requested_page_ids):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Page reorder must include all existing pages exactly once",
            )

        if set(existing_page_ids) != set(requested_page_ids):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Page reorder must include all existing pages exactly once",
            )

        if len(requested_page_ids) != len(set(requested_page_ids)):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Page reorder cannot contain duplicate page IDs",
            )

        self.client.table("pages").update({"sort_order": 999}).eq(
            "template_id", str(template_id)
        ).execute()

        for order, page_id in enumerate(page_ids):
            self.client.table("pages").update({"sort_order": order}).eq(
                "id", str(page_id)
            ).eq("template_id", str(template_id)).execute()

    async def reorder_elements(self, page_id: UUID, element_ids: list[UUID]) -> None:
        page = (
            self.client.table("pages")
            .select("template_id")
            .eq("id", str(page_id))
            .single()
            .execute()
        )
        if page.data:
            template = await self.get_template(UUID(page.data["template_id"]))
            self._check_editable(template)
        for order, element_id in enumerate(element_ids):
            self.client.table("elements").update({"sort_order": order}).eq(
                "id", str(element_id)
            ).eq("page_id", str(page_id)).execute()

    async def create_new_version(self, template_id: UUID, user_id: UUID) -> dict:
        source = await self.get_template(template_id)
        if source.get("status") != "published":
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Only published templates can be versioned.",
            )
        new_version = source["version"] + 1
        new_template_data = {
            "name": source["name"],
            "description": source.get("description", ""),
            "category": source.get("category", ""),
            "language": source.get("language", "ar"),
            "country": source.get("country", "EG"),
            "status": "draft",
            "version": new_version,
            "created_by": str(user_id),
            "org_id": source.get("org_id"),
        }
        # Add versioning columns only if they exist in schema (migration 020)
        if "lineage_id" in source:
            new_template_data["lineage_id"] = source.get("lineage_id", source["id"])
            new_template_data["parent_version_id"] = str(template_id)
        result = self.client.table("templates").insert(new_template_data).execute()
        new_template = result.data[0]

        for page in source.get("pages", []):
            page_data = {
                "template_id": new_template["id"],
                "width_mm": page["width_mm"],
                "height_mm": page["height_mm"],
                "background_asset": page.get("background_asset"),
                "sort_order": page["sort_order"],
            }
            page_result = self.client.table("pages").insert(page_data).execute()
            new_page = page_result.data[0]

            for element in page.get("elements", []):
                element_data = {
                    "page_id": new_page["id"],
                    "type": element["type"],
                    "key": element["key"],
                    "label_ar": element["label_ar"],
                    "label_en": element["label_en"],
                    "x_mm": element["x_mm"],
                    "y_mm": element["y_mm"],
                    "width_mm": element["width_mm"],
                    "height_mm": element["height_mm"],
                    "validation": element.get("validation", {}),
                    "formatting": element.get("formatting", {}),
                    "required": element.get("required", False),
                    "direction": element.get("direction", "auto"),
                    "sort_order": element["sort_order"],
                }
                self.client.table("elements").insert(element_data).execute()

        from app.core.audit import AuditLogger

        await AuditLogger(self.client).log_event(
            user_id=str(user_id),
            action="TEMPLATE_VERSIONED",
            resource_type="template",
            resource_id=str(template_id),
            metadata={
                "new_template_id": new_template["id"],
                "new_version": new_version,
            },
        )

        return await self.get_template(UUID(new_template["id"]))

    async def clone_template(
        self, template_id: UUID, name: str | None, user_id: UUID
    ) -> dict:
        source = await self.get_template(template_id)
        clone_name = name or f"{source['name']} (Copy)"
        new_id = str(uuid4())
        new_template_data = {
            "id": new_id,
            "name": clone_name,
            "description": source.get("description", ""),
            "category": source.get("category", ""),
            "language": source.get("language", "ar"),
            "country": source.get("country", "EG"),
            "status": "draft",
            "version": 1,
            "created_by": str(user_id),
            "org_id": source.get("org_id"),
            "lineage_id": new_id,
        }
        result = self.client.table("templates").insert(new_template_data).execute()
        new_template = result.data[0]

        for page in source.get("pages", []):
            page_data = {
                "template_id": new_template["id"],
                "width_mm": page["width_mm"],
                "height_mm": page["height_mm"],
                "background_asset": page.get("background_asset"),
                "sort_order": page["sort_order"],
            }
            page_result = self.client.table("pages").insert(page_data).execute()
            new_page = page_result.data[0]

            for element in page.get("elements", []):
                element_data = {
                    "page_id": new_page["id"],
                    "type": element["type"],
                    "key": element["key"],
                    "label_ar": element["label_ar"],
                    "label_en": element["label_en"],
                    "x_mm": element["x_mm"],
                    "y_mm": element["y_mm"],
                    "width_mm": element["width_mm"],
                    "height_mm": element["height_mm"],
                    "validation": element.get("validation", {}),
                    "formatting": element.get("formatting", {}),
                    "required": element.get("required", False),
                    "direction": element.get("direction", "auto"),
                    "sort_order": element["sort_order"],
                }
                self.client.table("elements").insert(element_data).execute()

        from app.core.audit import AuditLogger

        await AuditLogger(self.client).log_event(
            user_id=str(user_id),
            action="TEMPLATE_CLONED",
            resource_type="template",
            resource_id=new_template["id"],
            metadata={
                "source_template_id": str(template_id),
                "source_version": source.get("version", 1),
            },
        )

        return await self.get_template(UUID(new_template["id"]))

    async def get_version_history(self, template_id: UUID) -> dict:
        template = await self.get_template(template_id)
        lineage_id = template.get("lineage_id", template["id"])

        versions_result = (
            self.client.table("templates")
            .select("id, version, status, created_by, created_at, updated_at, name")
            .eq("lineage_id", str(lineage_id))
            .order("version", desc=True)
            .execute()
        )

        versions = []
        for v in versions_result.data or []:
            pages_result = (
                self.client.table("pages")
                .select("id")
                .eq("template_id", v["id"])
                .execute()
            )
            page_count = len(pages_result.data or [])
            element_count = 0
            for p in pages_result.data or []:
                elems = (
                    self.client.table("elements")
                    .select("id")
                    .eq("page_id", p["id"])
                    .execute()
                )
                element_count += len(elems.data or [])

            creator_result = (
                self.client.table("profiles")
                .select("id, display_name")
                .eq("id", v["created_by"])
                .single()
                .execute()
            )
            creator_name = None
            if creator_result.data:
                creator_name = creator_result.data.get(
                    "display_name"
                ) or creator_result.data.get("id")

            published_at = None
            if v.get("status") == "published":
                reviews = (
                    self.client.table("template_reviews")
                    .select("created_at")
                    .eq("template_id", v["id"])
                    .eq("action", "approved")
                    .order("created_at")
                    .limit(1)
                    .execute()
                )
                if reviews.data:
                    published_at = reviews.data[0]["created_at"]

            versions.append(
                {
                    "id": v["id"],
                    "version": v["version"],
                    "status": v["status"],
                    "created_by": v["created_by"],
                    "created_by_name": creator_name,
                    "created_at": v["created_at"],
                    "published_at": published_at,
                    "element_count": element_count,
                    "page_count": page_count,
                }
            )

        return {"lineage_id": str(lineage_id), "versions": versions}

    async def compute_diff(self, template_id_a: UUID, template_id_b: UUID) -> dict:
        template_a = await self.get_template(template_id_a)
        template_b = await self.get_template(template_id_b)

        lineage_a = template_a.get("lineage_id", template_a["id"])
        lineage_b = template_b.get("lineage_id", template_b["id"])
        if str(lineage_a) != str(lineage_b):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Can only compare versions within the same lineage",
            )

        def collect_elements(template: dict) -> dict[str, dict]:
            elements = {}
            for page in template.get("pages", []):
                for elem in page.get("elements", []):
                    elements[elem["key"]] = elem
            return elements

        def collect_pages(template: dict) -> dict[int, dict]:
            pages = {}
            for page in template.get("pages", []):
                pages[page["sort_order"]] = page
            return pages

        elems_a = collect_elements(template_a)
        elems_b = collect_elements(template_b)

        added_keys = set(elems_b.keys()) - set(elems_a.keys())
        removed_keys = set(elems_a.keys()) - set(elems_b.keys())
        common_keys = set(elems_a.keys()) & set(elems_b.keys())

        added = [
            {
                "key": k,
                "type": elems_b[k]["type"],
                "label_ar": elems_b[k].get("label_ar", ""),
                "label_en": elems_b[k].get("label_en", ""),
                "page_sort_order": _find_page_sort_order(template_b, elems_b[k]),
            }
            for k in sorted(added_keys)
        ]
        removed = [{"key": k, "type": elems_a[k]["type"]} for k in sorted(removed_keys)]

        comparable_props = [
            "x_mm",
            "y_mm",
            "width_mm",
            "height_mm",
            "label_ar",
            "label_en",
            "required",
            "direction",
        ]

        modified = []
        for key in sorted(common_keys):
            changes = []
            ea, eb = elems_a[key], elems_b[key]
            for prop in comparable_props:
                val_a = ea.get(prop)
                val_b = eb.get(prop)
                if val_a != val_b:
                    changes.append({"property": prop, "from": val_a, "to": val_b})
            if ea.get("validation", {}) != eb.get("validation", {}):
                changes.append(
                    {
                        "property": "validation",
                        "from": ea.get("validation"),
                        "to": eb.get("validation"),
                    }
                )
            if ea.get("formatting", {}) != eb.get("formatting", {}):
                changes.append(
                    {
                        "property": "formatting",
                        "from": ea.get("formatting"),
                        "to": eb.get("formatting"),
                    }
                )
            if changes:
                modified.append({"key": key, "changes": changes})

        pages_a = collect_pages(template_a)
        pages_b = collect_pages(template_b)
        page_added = sorted(set(pages_b.keys()) - set(pages_a.keys()))
        page_removed = sorted(set(pages_a.keys()) - set(pages_b.keys()))
        page_modified = []
        for sort_order in sorted(set(pages_a.keys()) & set(pages_b.keys())):
            pa, pb = pages_a[sort_order], pages_b[sort_order]
            page_changes = []
            for prop in ["width_mm", "height_mm"]:
                if pa.get(prop) != pb.get(prop):
                    page_changes.append(
                        {"property": prop, "from": pa.get(prop), "to": pb.get(prop)}
                    )
            if pa.get("background_asset") != pb.get("background_asset"):
                page_changes.append(
                    {
                        "property": "background_asset",
                        "from": pa.get("background_asset"),
                        "to": pb.get("background_asset"),
                    }
                )
            if page_changes:
                page_modified.append(
                    {"sort_order": sort_order, "changes": page_changes}
                )

        return {
            "base_version": {
                "id": str(template_id_a),
                "version": template_a["version"],
            },
            "compare_version": {
                "id": str(template_id_b),
                "version": template_b["version"],
            },
            "summary": {
                "elements_added": len(added),
                "elements_removed": len(removed),
                "elements_modified": len(modified),
                "pages_added": len(page_added),
                "pages_removed": len(page_removed),
            },
            "changes": {
                "added": added,
                "removed": removed,
                "modified": modified,
                "pages": {
                    "added": page_added,
                    "removed": page_removed,
                    "modified": page_modified,
                },
            },
        }

    async def get_reviews(self, template_id: UUID) -> list[dict]:
        template = await self.get_template(template_id)

        reviews_result = (
            self.client.table("template_reviews")
            .select("*")
            .eq("template_id", str(template_id))
            .order("created_at", desc=True)
            .execute()
        )

        reviews = []
        for r in reviews_result.data or []:
            reviewer_result = (
                self.client.table("profiles")
                .select("id, display_name")
                .eq("id", r["reviewer_id"])
                .single()
                .execute()
            )
            reviewer_name = None
            if reviewer_result.data:
                reviewer_name = reviewer_result.data.get(
                    "display_name"
                ) or reviewer_result.data.get("id")
            reviews.append(
                {
                    "id": r["id"],
                    "template_id": r["template_id"],
                    "reviewer_id": r["reviewer_id"],
                    "reviewer_name": reviewer_name,
                    "action": r["action"],
                    "comment": r.get("comment"),
                    "element_comments": r.get("element_comments"),
                    "created_at": r["created_at"],
                }
            )

        return reviews


def _find_page_sort_order(template: dict, element: dict) -> int:
    for page in template.get("pages", []):
        for e in page.get("elements", []):
            if e["id"] == element.get("id"):
                return page.get("sort_order", 0)
    return 0

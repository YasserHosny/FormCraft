"""Template, Page, and Element CRUD operations via Supabase."""

from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client


class TemplateService:
    """Template domain model CRUD with optimistic concurrency."""

    def __init__(self, client: Client):
        self.client = client

    # --- Templates ---

    async def create_template(self, data: dict, user_id: UUID) -> dict:
        template_data = {
            **data,
            "created_by": str(user_id),
            "status": "draft",
            "version": 1,
        }
        result = self.client.table("templates").insert(template_data).execute()
        template = result.data[0]

        # Create default A4 page
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
        self.client.table("templates").delete().eq(
            "id", str(template_id)
        ).execute()

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
        # Get max sort_order for this template
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
        result = (
            self.client.table("pages")
            .update(data)
            .eq("id", str(page_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Page not found")
        return result.data[0]

    async def delete_page(self, page_id: UUID) -> None:
        # Prevent deleting the last page
        page = (
            self.client.table("pages")
            .select("template_id")
            .eq("id", str(page_id))
            .single()
            .execute()
        )
        if not page.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Page not found")

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
        # Generate unique key
        import uuid as uuid_mod

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
        result = self.client.table("elements").insert(element_data).execute()
        return result.data[0]

    async def update_element(self, element_id: UUID, data: dict) -> dict:
        result = (
            self.client.table("elements")
            .update(data)
            .eq("id", str(element_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Element not found")
        return result.data[0]

    async def delete_element(self, element_id: UUID) -> None:
        self.client.table("elements").delete().eq(
            "id", str(element_id)
        ).execute()

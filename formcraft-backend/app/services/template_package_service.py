"""F32 .formcraft package export/import service."""

import hashlib
import json
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status

from app.core.audit import AuditLogger


PACKAGE_SCHEMA_VERSION = "1.0"


class TemplatePackageService:
    """F32 .formcraft package export/import service."""

    def __init__(self, supabase_client):
        self.client = supabase_client

    async def export_package(self, template_id: UUID, actor_id: UUID) -> dict:
        """Export a template as a .formcraft package."""
        # Fetch template
        template_result = (
            self.client.table("templates")
            .select("*")
            .eq("id", str(template_id))
            .single()
            .execute()
        )
        if not template_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found",
            )

        template = template_result.data
        template["org_id"]

        # Fetch pages
        pages_result = (
            self.client.table("pages")
            .select("*")
            .eq("template_id", str(template_id))
            .execute()
        )
        pages = pages_result.data or []

        # Fetch elements for all pages
        page_ids = [p["id"] for p in pages]
        elements = []
        if page_ids:
            elements_result = (
                self.client.table("elements")
                .select("*")
                .in_("page_id", page_ids)
                .execute()
            )
            elements = elements_result.data or []

        # Build package
        package = {
            "schema_version": PACKAGE_SCHEMA_VERSION,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "template": {
                "name": template["name"],
                "category": template.get("category"),
                "language": template.get("language"),
                "country": template.get("country"),
                "lineage_id": str(template.get("lineage_id")),
            },
            "pages": [
                {
                    "width_mm": p["width_mm"],
                    "height_mm": p["height_mm"],
                    "background_asset": p.get("background_asset"),
                    "sort_order": p.get("sort_order", 0),
                }
                for p in pages
            ],
            "elements": [
                {
                    "type": e["type"],
                    "key": e["key"],
                    "label_ar": e.get("label_ar"),
                    "label_en": e.get("label_en"),
                    "x_mm": e["x_mm"],
                    "y_mm": e["y_mm"],
                    "width_mm": e["width_mm"],
                    "height_mm": e["height_mm"],
                    "validation": e.get("validation"),
                    "page_index": next(
                        (i for i, p in enumerate(pages) if p["id"] == e["page_id"]),
                        0,
                    ),
                }
                for e in elements
            ],
        }

        # Compute checksum
        package_json = json.dumps(package, sort_keys=True, ensure_ascii=False)
        checksum = hashlib.sha256(package_json.encode("utf-8")).hexdigest()
        package["checksum"] = checksum

        await AuditLogger(self.client).log_event(
            user_id=str(actor_id),
            action="TEMPLATE_PACKAGE_EXPORTED",
            resource_type="template",
            resource_id=str(template_id),
            metadata={"schema_version": PACKAGE_SCHEMA_VERSION},
        )

        return package

    async def import_review(self, package: dict, org_id: UUID, actor_id: UUID) -> dict:
        """Review a package before importing."""
        # Validate checksum
        package_copy = dict(package)
        original_checksum = package_copy.pop("checksum", None)
        package_json = json.dumps(package_copy, sort_keys=True, ensure_ascii=False)
        computed_checksum = hashlib.sha256(package_json.encode("utf-8")).hexdigest()

        if original_checksum != computed_checksum:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Package checksum mismatch - package may be corrupted",
            )

        # Check schema version
        schema_version = package.get("schema_version")
        if schema_version != PACKAGE_SCHEMA_VERSION:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported package schema version: {schema_version}",
            )

        template_name = package["template"]["name"]
        lineage_id = package["template"].get("lineage_id")

        # Check for existing templates with same name or lineage
        warnings = []
        existing = None

        if lineage_id:
            lineage_result = (
                self.client.table("templates")
                .select("id, name, version, status")
                .eq("org_id", str(org_id))
                .eq("lineage_id", lineage_id)
                .execute()
            )
            existing = lineage_result.data

        if not existing:
            name_result = (
                self.client.table("templates")
                .select("id, name, version, status")
                .eq("org_id", str(org_id))
                .eq("name", template_name)
                .execute()
            )
            existing = name_result.data

        if existing:
            warnings.append(f"Template '{template_name}' already exists. Import will create a new version.")

        await AuditLogger(self.client).log_event(
            user_id=str(actor_id),
            action="TEMPLATE_PACKAGE_IMPORT_REVIEWED",
            resource_type="template",
            metadata={"name": template_name, "warnings": warnings},
        )

        return {
            "can_import": True,
            "warnings": warnings,
            "existing_templates": existing or [],
            "template_name": template_name,
        }

    async def import_package(
        self,
        package: dict,
        org_id: UUID,
        actor_id: UUID,
        create_as_new: bool = False,
    ) -> dict:
        """Import a .formcraft package as a new template or version."""
        # First review
        review = await self.import_review(package, org_id, actor_id)

        template_name = package["template"]["name"]
        lineage_id = package["template"].get("lineage_id")

        # Determine if we should create new draft or new version
        existing = review["existing_templates"]
        target_template_id = None
        new_version = False

        if existing and not create_as_new:
            target_template_id = existing[0]["id"]
            new_version = True

        # Create template
        template_row = {
            "org_id": str(org_id),
            "created_by": str(actor_id),
            "name": template_name,
            "category": package["template"].get("category"),
            "language": package["template"].get("language"),
            "country": package["template"].get("country"),
            "status": "draft",
            "version": 1,
        }

        if target_template_id and new_version:
            # Create new version of existing template
            template_row["lineage_id"] = target_template_id
            template_row["parent_id"] = target_template_id
        elif lineage_id:
            template_row["lineage_id"] = lineage_id

        template_result = self.client.table("templates").insert(template_row).execute()
        new_template = template_result.data[0]
        new_template_id = new_template["id"]

        # Create pages
        page_id_map = {}
        for i, page_data in enumerate(package["pages"]):
            page_row = {
                "template_id": new_template_id,
                "width_mm": page_data["width_mm"],
                "height_mm": page_data["height_mm"],
                "background_asset": page_data.get("background_asset"),
                "sort_order": page_data.get("sort_order", i),
            }
            page_result = self.client.table("pages").insert(page_row).execute()
            page_id_map[i] = page_result.data[0]["id"]

        # Create elements
        for element_data in package["elements"]:
            element_row = {
                "page_id": page_id_map.get(element_data["page_index"]),
                "type": element_data["type"],
                "key": element_data["key"],
                "label_ar": element_data.get("label_ar"),
                "label_en": element_data.get("label_en"),
                "x_mm": element_data["x_mm"],
                "y_mm": element_data["y_mm"],
                "width_mm": element_data["width_mm"],
                "height_mm": element_data["height_mm"],
                "validation": element_data.get("validation"),
            }
            self.client.table("elements").insert(element_row).execute()

        await AuditLogger(self.client).log_event(
            user_id=str(actor_id),
            action="TEMPLATE_PACKAGE_IMPORTED",
            resource_type="template",
            resource_id=new_template_id,
            metadata={
                "name": template_name,
                "new_version": new_version,
                "source_lineage": lineage_id,
            },
        )

        return {
            "template_id": new_template_id,
            "name": template_name,
            "warnings": review["warnings"],
            "new_version": new_version,
        }
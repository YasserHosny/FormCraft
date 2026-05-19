"""Service for reference data list and entry management."""

from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.core.audit import AuditLogger


class ReferenceService:
    def __init__(self, client: Client):
        self.client = client
        self.audit = AuditLogger(client)

    # --- List CRUD ---

    async def create_list(self, data: dict, user_id: UUID, org_id: UUID) -> dict:
        row = {
            "name_ar": data["name_ar"],
            "name_en": data["name_en"],
            "description": data.get("description"),
            "schema": data["schema"],
            "org_id": str(org_id),
            "created_by": str(user_id),
        }
        result = self.client.table("reference_lists").insert(row).execute()
        created = result.data[0]
        await self.audit.log_event(
            user_id=str(user_id),
            action="reference_list.created",
            resource_type="reference_list",
            resource_id=created["id"],
            metadata={"name_en": data["name_en"]},
        )
        created["entry_count"] = 0
        return created

    async def get_list(self, list_id: UUID) -> dict:
        result = (
            self.client.table("reference_lists")
            .select("*")
            .eq("id", str(list_id))
            .single()
            .execute()
        )
        if not result.data:
            raise HTTPException(status_code=404, detail="Reference list not found")
        ref_list = result.data
        count_result = (
            self.client.table("reference_entries")
            .select("id", count="exact")
            .eq("list_id", str(list_id))
            .execute()
        )
        ref_list["entry_count"] = count_result.count or 0
        return ref_list

    async def list_lists(
        self,
        include_archived: bool = False,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[dict], int]:
        query = self.client.table("reference_lists").select("*", count="exact")
        if not include_archived:
            query = query.eq("is_archived", False)
        query = query.order("created_at", desc=True)
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)
        result = query.execute()
        items = result.data or []
        for item in items:
            item["column_count"] = len(item.get("schema", []))
            count_r = (
                self.client.table("reference_entries")
                .select("id", count="exact")
                .eq("list_id", item["id"])
                .execute()
            )
            item["entry_count"] = count_r.count or 0
        return items, result.count or 0

    async def update_list(self, list_id: UUID, data: dict, user_id: UUID) -> dict:
        update_data = {k: v for k, v in data.items() if v is not None}
        update_data["updated_at"] = "now()"
        result = (
            self.client.table("reference_lists")
            .update(update_data)
            .eq("id", str(list_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(status_code=404, detail="Reference list not found")
        await self.audit.log_event(
            user_id=str(user_id),
            action="reference_list.updated",
            resource_type="reference_list",
            resource_id=str(list_id),
            metadata={"changes": list(update_data.keys())},
        )
        return result.data[0]

    async def archive_list(self, list_id: UUID, user_id: UUID) -> dict:
        result = (
            self.client.table("reference_lists")
            .update({"is_archived": True, "updated_at": "now()"})
            .eq("id", str(list_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(status_code=404, detail="Reference list not found")
        await self.audit.log_event(
            user_id=str(user_id),
            action="reference_list.archived",
            resource_type="reference_list",
            resource_id=str(list_id),
        )
        return result.data[0]

    async def unarchive_list(self, list_id: UUID, user_id: UUID) -> dict:
        result = (
            self.client.table("reference_lists")
            .update({"is_archived": False, "updated_at": "now()"})
            .eq("id", str(list_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(status_code=404, detail="Reference list not found")
        await self.audit.log_event(
            user_id=str(user_id),
            action="reference_list.unarchived",
            resource_type="reference_list",
            resource_id=str(list_id),
        )
        return result.data[0]

    async def delete_list(self, list_id: UUID, user_id: UUID) -> None:
        bound = (
            self.client.table("elements")
            .select("id", count="exact")
            .contains("formatting", {"ref_binding": {"list_id": str(list_id)}})
            .execute()
        )
        bound_count = bound.count or 0
        if bound_count > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"List is bound to {bound_count} form elements",
            )
        self.client.table("reference_lists").delete().eq("id", str(list_id)).execute()
        await self.audit.log_event(
            user_id=str(user_id),
            action="reference_list.deleted",
            resource_type="reference_list",
            resource_id=str(list_id),
        )

    # --- Entry CRUD ---

    async def create_entry(
        self, list_id: UUID, values: dict, user_id: UUID, org_id: UUID
    ) -> dict:
        ref_list = await self.get_list(list_id)
        self._validate_entry_values(values, ref_list["schema"], list_id)
        await self._check_unique_key_conflict(list_id, ref_list["schema"], values)

        row = {
            "list_id": str(list_id),
            "values": values,
            "org_id": str(org_id),
            "created_by": str(user_id),
        }
        result = self.client.table("reference_entries").insert(row).execute()
        entry = result.data[0]
        await self.audit.log_event(
            user_id=str(user_id),
            action="reference_entry.created",
            resource_type="reference_entry",
            resource_id=entry["id"],
            metadata={"list_id": str(list_id)},
        )
        return entry

    async def update_entry(
        self, list_id: UUID, entry_id: UUID, values: dict, user_id: UUID
    ) -> dict:
        ref_list = await self.get_list(list_id)
        old_result = (
            self.client.table("reference_entries")
            .select("*")
            .eq("id", str(entry_id))
            .single()
            .execute()
        )
        if not old_result.data:
            raise HTTPException(status_code=404, detail="Entry not found")
        old_values = old_result.data["values"]

        merged = {**old_values, **values}
        self._validate_entry_values(merged, ref_list["schema"], list_id)
        await self._check_unique_key_conflict(
            list_id, ref_list["schema"], merged, exclude_entry_id=entry_id
        )

        result = (
            self.client.table("reference_entries")
            .update({"values": merged, "updated_at": "now()"})
            .eq("id", str(entry_id))
            .execute()
        )
        await self.audit.log_event(
            user_id=str(user_id),
            action="reference_entry.updated",
            resource_type="reference_entry",
            resource_id=str(entry_id),
            metadata={
                "list_id": str(list_id),
                "old_values": old_values,
                "new_values": merged,
            },
        )
        return result.data[0]

    async def deactivate_entry(
        self, entry_id: UUID, user_id: UUID
    ) -> dict:
        result = (
            self.client.table("reference_entries")
            .update({"is_active": False, "updated_at": "now()"})
            .eq("id", str(entry_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(status_code=404, detail="Entry not found")
        await self.audit.log_event(
            user_id=str(user_id),
            action="reference_entry.deactivated",
            resource_type="reference_entry",
            resource_id=str(entry_id),
        )
        return result.data[0]

    async def activate_entry(self, entry_id: UUID, user_id: UUID) -> dict:
        result = (
            self.client.table("reference_entries")
            .update({"is_active": True, "updated_at": "now()"})
            .eq("id", str(entry_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(status_code=404, detail="Entry not found")
        await self.audit.log_event(
            user_id=str(user_id),
            action="reference_entry.reactivated",
            resource_type="reference_entry",
            resource_id=str(entry_id),
        )
        return result.data[0]

    async def get_entries(
        self,
        list_id: UUID,
        active_only: bool = True,
        q: str | None = None,
        page: int = 1,
        page_size: int = 100,
    ) -> tuple[list[dict], int]:
        query = (
            self.client.table("reference_entries")
            .select("*", count="exact")
            .eq("list_id", str(list_id))
        )
        if active_only:
            query = query.eq("is_active", True)
        query = query.order("created_at", desc=True)
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)
        result = query.execute()
        return result.data or [], result.count or 0

    async def get_entry(self, entry_id: UUID) -> dict:
        result = (
            self.client.table("reference_entries")
            .select("*")
            .eq("id", str(entry_id))
            .single()
            .execute()
        )
        if not result.data:
            raise HTTPException(status_code=404, detail="Entry not found")
        return result.data

    # --- Dropdown endpoint ---

    async def get_dropdown_items(
        self,
        list_id: UUID,
        display_column: str,
        value_column: str,
        q: str | None = None,
    ) -> list[dict]:
        query = (
            self.client.table("reference_entries")
            .select("id, values")
            .eq("list_id", str(list_id))
            .eq("is_active", True)
        )
        result = query.execute()
        items = []
        for entry in result.data or []:
            vals = entry["values"]
            display = str(vals.get(display_column, ""))
            value = str(vals.get(value_column, ""))
            if q and q.lower() not in display.lower():
                continue
            items.append({
                "display": display,
                "value": value,
                "entry_id": entry["id"],
            })
        items.sort(key=lambda x: x["display"])
        return items

    # --- Validation helpers ---

    def _validate_entry_values(
        self, values: dict, schema: list[dict], list_id: UUID
    ) -> None:
        errors = []
        for col in schema:
            if col.get("is_hidden"):
                continue
            key = col["key"]
            val = values.get(key)
            if col.get("required") and (val is None or val == ""):
                errors.append({"field": key, "message": f"Required field '{key}' is empty"})
                continue
            if val is None or val == "":
                continue
            col_type = col.get("type", "text")
            if col_type == "number":
                try:
                    float(val)
                except (ValueError, TypeError):
                    errors.append({"field": key, "message": f"'{key}' must be a number"})
            elif col_type == "dropdown":
                options = col.get("options", [])
                if options and str(val) not in options:
                    errors.append({
                        "field": key,
                        "message": f"'{val}' is not a valid option for '{key}'",
                    })
        if errors:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"message": "Entry validation failed", "errors": errors},
            )

    async def _check_unique_key_conflict(
        self,
        list_id: UUID,
        schema: list[dict],
        values: dict,
        exclude_entry_id: UUID | None = None,
    ) -> None:
        unique_cols = [c for c in schema if c.get("is_unique_key")]
        for col in unique_cols:
            key = col["key"]
            val = values.get(key)
            if val is None:
                continue
            query = (
                self.client.table("reference_entries")
                .select("id, values")
                .eq("list_id", str(list_id))
                .eq("is_active", True)
            )
            if exclude_entry_id:
                query = query.neq("id", str(exclude_entry_id))
            result = query.execute()
            for entry in result.data or []:
                if str(entry["values"].get(key)) == str(val):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Duplicate value '{val}' for unique key '{key}'",
                    )

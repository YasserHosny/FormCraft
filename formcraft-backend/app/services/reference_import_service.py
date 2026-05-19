"""CSV import service for reference data entries."""

import csv
import io
import uuid
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.core.audit import AuditLogger

_preview_store: dict[str, dict] = {}

PREVIEW_TTL_MINUTES = 15
BATCH_SIZE = 100


class ReferenceImportService:
    def __init__(self, client: Client):
        self.client = client
        self.audit = AuditLogger(client)

    async def preview(
        self,
        list_id: UUID,
        schema: list[dict],
        csv_content: str,
        mode: str = "insert",
    ) -> dict:
        if mode == "update":
            unique_cols = [c for c in schema if c.get("is_unique_key")]
            if not unique_cols:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Update mode requires a unique key column in the schema",
                )

        rows = self._parse_csv(csv_content)
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="CSV file is empty or has no data rows",
            )

        headers = list(rows[0].keys())
        column_mapping = self._auto_map_columns(headers, schema)
        valid_rows, errors = self._validate_rows(rows, schema, column_mapping, mode, list_id)

        token = str(uuid.uuid4())
        _preview_store[token] = {
            "list_id": str(list_id),
            "valid_rows": valid_rows,
            "column_mapping": column_mapping,
            "schema": schema,
            "mode": mode,
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=PREVIEW_TTL_MINUTES),
        }

        return {
            "total_rows": len(rows),
            "valid_count": len(valid_rows),
            "invalid_count": len(errors),
            "column_mapping": column_mapping,
            "errors": errors,
            "preview_token": token,
        }

    async def confirm(
        self,
        list_id: UUID,
        preview_token: str,
        import_valid_only: bool,
        user_id: UUID,
        org_id: UUID,
    ) -> dict:
        preview = _preview_store.pop(preview_token, None)
        if not preview:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Preview token expired",
            )
        if datetime.now(timezone.utc) > preview["expires_at"]:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Preview token expired",
            )

        # Validate that the preview token was generated for this specific list
        if preview.get("list_id") != str(list_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Preview token does not belong to this reference list",
            )

        valid_rows = preview["valid_rows"]
        mode = preview["mode"]
        imported = 0

        for i in range(0, len(valid_rows), BATCH_SIZE):
            batch = valid_rows[i : i + BATCH_SIZE]
            if mode == "insert":
                rows_to_insert = [
                    {
                        "list_id": str(list_id),
                        "values": row,
                        "org_id": str(org_id),
                        "created_by": str(user_id),
                    }
                    for row in batch
                ]
                self.client.table("reference_entries").insert(rows_to_insert).execute()
                imported += len(batch)
            else:
                # Update mode: look up existing entries by unique key and update values
                schema_cols = preview.get("schema", [])
                unique_key_cols = [c["key"] for c in schema_cols if c.get("is_unique_key")]
                for row in batch:
                    if unique_key_cols and unique_key_cols[0] in row:
                        unique_key_col = unique_key_cols[0]
                        result = (
                            self.client.table("reference_entries")
                            .update({"values": row})
                            .eq("list_id", str(list_id))
                            .filter("values->>{}".format(unique_key_col), "eq", row[unique_key_col])
                            .execute()
                        )
                        if result.data:
                            imported += 1
                        else:
                            # If no existing entry found, insert as new
                            self.client.table("reference_entries").insert({
                                "list_id": str(list_id),
                                "values": row,
                                "org_id": str(org_id),
                                "created_by": str(user_id),
                            }).execute()
                            imported += 1

        await self.audit.log_event(
            user_id=str(user_id),
            action="reference_entries.imported",
            resource_type="reference_list",
            resource_id=str(list_id),
            metadata={"count": imported, "mode": mode},
        )

        return {
            "imported_count": imported,
            "skipped_count": len(valid_rows) - imported if not import_valid_only else 0,
            "mode": mode,
        }

    def _parse_csv(self, content: str) -> list[dict]:
        reader = csv.DictReader(io.StringIO(content))
        return list(reader)

    def _auto_map_columns(
        self, headers: list[str], schema: list[dict]
    ) -> dict[str, str]:
        mapping = {}
        schema_keys = {c["key"].lower(): c["key"] for c in schema}
        schema_labels_en = {c["label_en"].lower(): c["key"] for c in schema}
        schema_labels_ar = {c["label_ar"]: c["key"] for c in schema}

        for header in headers:
            h_lower = header.strip().lower()
            if h_lower in schema_keys:
                mapping[header] = schema_keys[h_lower]
            elif h_lower in schema_labels_en:
                mapping[header] = schema_labels_en[h_lower]
            elif header.strip() in schema_labels_ar:
                mapping[header] = schema_labels_ar[header.strip()]
        return mapping

    def _validate_rows(
        self,
        rows: list[dict],
        schema: list[dict],
        column_mapping: dict[str, str],
        mode: str,
        list_id: UUID,
    ) -> tuple[list[dict], list[dict]]:
        valid = []
        errors = []
        visible_schema = [c for c in schema if not c.get("is_hidden")]

        for row_num, row in enumerate(rows, start=2):
            mapped_values = {}
            for csv_col, schema_key in column_mapping.items():
                mapped_values[schema_key] = row.get(csv_col, "").strip()

            row_errors = []
            for col in visible_schema:
                key = col["key"]
                val = mapped_values.get(key, "")
                if col.get("required") and not val:
                    row_errors.append({
                        "row": row_num,
                        "column": key,
                        "message": "Required field is empty",
                    })
                    continue
                if not val:
                    continue
                if col["type"] == "number":
                    try:
                        float(val)
                    except ValueError:
                        row_errors.append({
                            "row": row_num,
                            "column": key,
                            "message": f"Expected number, got '{val}'",
                        })
                elif col["type"] == "dropdown":
                    options = col.get("options", [])
                    if options and val not in options:
                        row_errors.append({
                            "row": row_num,
                            "column": key,
                            "message": f"'{val}' is not a valid option",
                        })

            if row_errors:
                errors.extend(row_errors)
            else:
                valid.append(mapped_values)

        return valid, errors

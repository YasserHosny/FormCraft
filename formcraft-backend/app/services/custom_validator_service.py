"""Custom validator CRUD service for Feature 048.

Org-scoped CRUD with regex sandboxing, audit logging, and an in-process cache
for the designer-facing GET /api/validators/org payload.

See: formcraft-specs/specs/048-custom-locale-validators/spec.md
"""

from __future__ import annotations

import threading
import time
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.core.audit import AuditLogger
from app.schemas.custom_validator import (
    MAX_VALIDATORS_PER_ORG,
    CustomValidatorCreate,
    CustomValidatorUpdate,
)
from app.services.custom_validator_sandbox import (
    SandboxAccepted,
    SandboxRejection,
    validate_pattern,
)


_CACHE_TTL_SECONDS = 60.0

# Per-org in-process cache of the designer payload. Invalidated explicitly on any
# CRUD mutation. Process-local on purpose — distributed cache is out of scope.
_designer_cache: dict[str, tuple[float, list[dict]]] = {}
_cache_lock = threading.Lock()


def _invalidate_org_cache(org_id: str) -> None:
    with _cache_lock:
        _designer_cache.pop(org_id, None)


class CustomValidatorService:
    def __init__(self, client: Client):
        self.client = client
        self._audit = AuditLogger(client)

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    async def create(
        self,
        data: CustomValidatorCreate,
        org_id: UUID,
        created_by: UUID,
    ) -> dict:
        # Enforce hard cap (spec FR-1: 500 per org)
        existing = (
            self.client.table("custom_validators")
            .select("id", count="exact")
            .eq("org_id", str(org_id))
            .is_("deleted_at", "null")
            .execute()
        )
        total = existing.count if existing.count is not None else len(existing.data or [])
        if total >= MAX_VALIDATORS_PER_ORG:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "VALIDATOR_LIMIT_REACHED",
                    "message": f"Organization has reached the {MAX_VALIDATORS_PER_ORG} validator cap",
                },
            )

        sandbox_result = validate_pattern(data.regex_pattern)
        if isinstance(sandbox_result, SandboxRejection):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": sandbox_result.code, "message": sandbox_result.message},
            )

        row = {
            "org_id": str(org_id),
            "name": data.name,
            "description": data.description,
            "regex_pattern": data.regex_pattern,
            "error_message_ar": data.error_message_ar,
            "error_message_en": data.error_message_en,
            "created_by": str(created_by),
            "updated_by": str(created_by),
        }

        try:
            result = self.client.table("custom_validators").insert(row).execute()
        except Exception as exc:  # noqa: BLE001
            # Unique constraint on (org_id, name)
            if "duplicate key" in str(exc).lower() or "23505" in str(exc):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "code": "VALIDATOR_NAME_EXISTS",
                        "message": "A validator with this name already exists in your organization",
                    },
                ) from exc
            raise

        created = result.data[0]
        _invalidate_org_cache(str(org_id))

        await self._audit.log_event(
            user_id=str(created_by),
            action="VALIDATOR_CREATED",
            resource_type="custom_validator",
            resource_id=created["id"],
            metadata={
                "name": created["name"],
                "regex_pattern": created["regex_pattern"],
            },
        )
        return created

    async def get(self, validator_id: UUID, org_id: UUID) -> dict:
        result = (
            self.client.table("custom_validators")
            .select("*")
            .eq("id", str(validator_id))
            .eq("org_id", str(org_id))
            .is_("deleted_at", "null")
            .maybe_single()
            .execute()
        )
        if not result or not result.data:
            raise HTTPException(status_code=404, detail="Validator not found")
        return result.data

    async def list_for_admin(
        self,
        org_id: UUID,
        page: int,
        page_size: int,
        search: str | None,
    ) -> tuple[list[dict], int]:
        q = (
            self.client.table("custom_validators")
            .select("*", count="exact")
            .eq("org_id", str(org_id))
            .is_("deleted_at", "null")
        )
        if search:
            term = f"%{search.strip()}%"
            # FR-8: ILIKE search over name + description (Postgres OR)
            q = q.or_(f"name.ilike.{term},description.ilike.{term}")

        # FR-4: deterministic sort by name ASC
        offset = (page - 1) * page_size
        q = q.order("name", desc=False).range(offset, offset + page_size - 1)
        result = q.execute()
        total = result.count if result.count is not None else len(result.data or [])
        return result.data or [], total

    async def list_for_designer(self, org_id: UUID) -> list[dict]:
        """Designer payload for the canvas dropdown. Cached per-org for 60s."""
        key = str(org_id)
        now = time.monotonic()
        with _cache_lock:
            cached = _designer_cache.get(key)
            if cached and (now - cached[0]) < _CACHE_TTL_SECONDS:
                return list(cached[1])

        result = (
            self.client.table("custom_validators")
            .select("id, name, description, regex_pattern, error_message_ar, error_message_en")
            .eq("org_id", str(org_id))
            .is_("deleted_at", "null")
            .order("name", desc=False)
            .execute()
        )
        items = result.data or []
        with _cache_lock:
            _designer_cache[key] = (now, items)
        return items

    async def update(
        self,
        validator_id: UUID,
        data: CustomValidatorUpdate,
        org_id: UUID,
        updated_by: UUID,
    ) -> dict:
        existing = await self.get(validator_id, org_id)

        updates: dict = {"updated_by": str(updated_by), "updated_at": datetime.now(timezone.utc).isoformat()}
        changes: dict = {}

        if data.name is not None and data.name != existing["name"]:
            updates["name"] = data.name
            changes["name"] = {"before": existing["name"], "after": data.name}

        if data.description is not None and data.description != existing.get("description"):
            updates["description"] = data.description
            changes["description"] = {
                "before": existing.get("description"),
                "after": data.description,
            }

        if data.regex_pattern is not None and data.regex_pattern != existing["regex_pattern"]:
            sandbox_result = validate_pattern(data.regex_pattern)
            if isinstance(sandbox_result, SandboxRejection):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"code": sandbox_result.code, "message": sandbox_result.message},
                )
            updates["regex_pattern"] = data.regex_pattern
            changes["regex_pattern"] = {
                "before": existing["regex_pattern"],
                "after": data.regex_pattern,
            }

        if data.error_message_ar is not None and data.error_message_ar != existing["error_message_ar"]:
            updates["error_message_ar"] = data.error_message_ar
            changes["error_message_ar"] = {
                "before": existing["error_message_ar"],
                "after": data.error_message_ar,
            }

        if data.error_message_en is not None and data.error_message_en != existing["error_message_en"]:
            updates["error_message_en"] = data.error_message_en
            changes["error_message_en"] = {
                "before": existing["error_message_en"],
                "after": data.error_message_en,
            }

        if not changes:
            return existing  # no-op update

        try:
            result = (
                self.client.table("custom_validators")
                .update(updates)
                .eq("id", str(validator_id))
                .eq("org_id", str(org_id))
                .execute()
            )
        except Exception as exc:  # noqa: BLE001
            if "duplicate key" in str(exc).lower() or "23505" in str(exc):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "code": "VALIDATOR_NAME_EXISTS",
                        "message": "A validator with this name already exists",
                    },
                ) from exc
            raise

        updated = result.data[0] if result.data else existing
        _invalidate_org_cache(str(org_id))

        await self._audit.log_event(
            user_id=str(updated_by),
            action="VALIDATOR_UPDATED",
            resource_type="custom_validator",
            resource_id=str(validator_id),
            metadata={"changes": changes},
        )
        return updated

    async def soft_delete(
        self,
        validator_id: UUID,
        org_id: UUID,
        deleted_by: UUID,
    ) -> None:
        existing = await self.get(validator_id, org_id)
        now = datetime.now(timezone.utc).isoformat()
        self.client.table("custom_validators").update(
            {"deleted_at": now, "updated_at": now, "updated_by": str(deleted_by)}
        ).eq("id", str(validator_id)).eq("org_id", str(org_id)).execute()

        _invalidate_org_cache(str(org_id))

        await self._audit.log_event(
            user_id=str(deleted_by),
            action="VALIDATOR_DELETED",
            resource_type="custom_validator",
            resource_id=str(validator_id),
            metadata={"name": existing["name"]},
        )

    # ------------------------------------------------------------------
    # Template usage (FR-6)
    # ------------------------------------------------------------------
    async def list_template_usage(
        self,
        validator_id: UUID,
        org_id: UUID,
        page: int,
        page_size: int,
    ) -> tuple[list[dict], int]:
        """Return templates referencing this validator via elements.custom_validators_ids.

        Computes last_submission_at via the existing submissions table
        (FR-6: derived, NOT a stored column).
        """
        # Verify validator belongs to caller's org first (RLS would catch it but be explicit)
        await self.get(validator_id, org_id)

        # Postgres `?` element-of-array operator is awkward via PostgREST; use RPC if available,
        # otherwise fall back to filtering after a select. We use a generic select on elements
        # joined to pages to templates.
        elements_q = (
            self.client.table("elements")
            .select("page_id")
            .contains("custom_validators_ids", [str(validator_id)])
            .execute()
        )
        page_ids = list({row["page_id"] for row in (elements_q.data or [])})
        if not page_ids:
            return [], 0

        pages_q = (
            self.client.table("pages")
            .select("template_id")
            .in_("id", page_ids)
            .execute()
        )
        template_ids = list({row["template_id"] for row in (pages_q.data or [])})
        if not template_ids:
            return [], 0

        tpl_q = (
            self.client.table("templates")
            .select("id, name, status", count="exact")
            .in_("id", template_ids)
            .eq("org_id", str(org_id))
            .execute()
        )

        items: list[dict] = []
        for tpl in tpl_q.data or []:
            last_sub = (
                self.client.table("submissions")
                .select("created_at")
                .eq("template_id", tpl["id"])
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            last_at = last_sub.data[0]["created_at"] if last_sub.data else None
            items.append(
                {
                    "template_id": tpl["id"],
                    "template_name": tpl.get("name") or "",
                    "template_status": tpl.get("status") or "draft",
                    "last_submission_at": last_at,
                }
            )

        items.sort(key=lambda item: item["last_submission_at"] or "", reverse=True)
        total = tpl_q.count if tpl_q.count is not None else len(items)
        offset = (page - 1) * page_size
        return items[offset : offset + page_size], total

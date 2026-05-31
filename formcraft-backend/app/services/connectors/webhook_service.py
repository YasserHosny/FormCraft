"""Webhook CRUD service for Feature 049.

Each webhook stores an encrypted custom_headers dict (values only — keys are
plaintext for display) and an encrypted per-webhook HMAC signing secret. Both
are decrypted only inside the dispatcher worker.
"""

from __future__ import annotations

import secrets
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.core.audit import AuditLogger
from app.schemas.connector import WebhookCreate, WebhookUpdate
from app.services.connectors.encryption_service import (
    encrypt_dict_for_org,
    encrypt_for_org,
    mask_dict,
)


def _generate_webhook_secret() -> str:
    return secrets.token_urlsafe(48)


class WebhookService:
    def __init__(self, client: Client):
        self.client = client
        self._audit = AuditLogger(client)

    async def create(self, data: WebhookCreate, org_id: UUID, by_user: UUID) -> dict:
        webhook_secret = _generate_webhook_secret()
        row = {
            "org_id": str(org_id),
            "name": data.name,
            "event_type": data.event_type.value,
            "endpoint_url": data.endpoint_url,
            "custom_headers_enc": encrypt_dict_for_org(data.custom_headers or {}, org_id),
            "webhook_secret_enc": encrypt_for_org(webhook_secret, org_id),
            "created_by": str(by_user),
            "updated_by": str(by_user),
        }
        try:
            result = self.client.table("webhooks").insert(row).execute()
        except Exception as exc:  # noqa: BLE001
            msg = str(exc).lower()
            if "duplicate key" in msg or "23505" in msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "code": "WEBHOOK_DUPLICATE",
                        "message": "Webhook for this event + URL already exists",
                    },
                ) from exc
            raise

        created = result.data[0]
        await self._audit.log_event(
            user_id=str(by_user),
            action="WEBHOOK_CREATED",
            resource_type="webhook",
            resource_id=created["id"],
            metadata={
                "name": data.name,
                "event_type": data.event_type.value,
                "endpoint_url": data.endpoint_url,
            },
        )
        return self._to_response_dict(created)

    async def list(self, org_id: UUID) -> list[dict]:
        result = (
            self.client.table("webhooks")
            .select("*")
            .eq("org_id", str(org_id))
            .is_("deleted_at", "null")
            .order("created_at", desc=True)
            .execute()
        )
        return [self._to_response_dict(row) for row in (result.data or [])]

    async def get(self, webhook_id: UUID, org_id: UUID, include_secrets: bool = False) -> dict:
        result = (
            self.client.table("webhooks")
            .select("*")
            .eq("id", str(webhook_id))
            .eq("org_id", str(org_id))
            .is_("deleted_at", "null")
            .maybe_single()
            .execute()
        )
        if not result or not result.data:
            raise HTTPException(status_code=404, detail="Webhook not found")
        if include_secrets:
            # Internal use only — never returned via API
            return result.data
        return self._to_response_dict(result.data)

    async def update(
        self, webhook_id: UUID, data: WebhookUpdate, org_id: UUID, by_user: UUID
    ) -> dict:
        existing_full = await self.get(webhook_id, org_id, include_secrets=True)

        updates: dict = {"updated_by": str(by_user), "updated_at": datetime.now(timezone.utc).isoformat()}
        changes: dict = {}

        if data.name is not None and data.name != existing_full["name"]:
            updates["name"] = data.name
            changes["name"] = {"before": existing_full["name"], "after": data.name}
        if data.endpoint_url is not None and data.endpoint_url != existing_full["endpoint_url"]:
            if not data.endpoint_url.startswith("https://"):
                raise HTTPException(
                    status_code=400,
                    detail={"code": "WEBHOOK_HTTPS_REQUIRED", "message": "endpoint_url must use HTTPS"},
                )
            updates["endpoint_url"] = data.endpoint_url
            changes["endpoint_url"] = {"before": existing_full["endpoint_url"], "after": data.endpoint_url}
        if data.custom_headers is not None:
            updates["custom_headers_enc"] = encrypt_dict_for_org(data.custom_headers, org_id)
            changes["custom_headers"] = "rotated"
        if data.is_active is not None:
            updates["is_active"] = data.is_active
            changes["is_active"] = {"before": existing_full["is_active"], "after": data.is_active}

        if not changes:
            return self._to_response_dict(existing_full)

        result = (
            self.client.table("webhooks")
            .update(updates)
            .eq("id", str(webhook_id))
            .eq("org_id", str(org_id))
            .execute()
        )
        updated = result.data[0] if result.data else existing_full

        await self._audit.log_event(
            user_id=str(by_user),
            action="WEBHOOK_UPDATED",
            resource_type="webhook",
            resource_id=str(webhook_id),
            metadata={"changes": changes},
        )
        return self._to_response_dict(updated)

    async def delete(self, webhook_id: UUID, org_id: UUID, by_user: UUID) -> None:
        existing = await self.get(webhook_id, org_id, include_secrets=False)
        now = datetime.now(timezone.utc).isoformat()
        self.client.table("webhooks").update(
            {"deleted_at": now, "is_active": False, "updated_at": now, "updated_by": str(by_user)}
        ).eq("id", str(webhook_id)).eq("org_id", str(org_id)).execute()

        await self._audit.log_event(
            user_id=str(by_user),
            action="WEBHOOK_DELETED",
            resource_type="webhook",
            resource_id=str(webhook_id),
            metadata={"name": existing.get("name")},
        )

    # ------------------------------------------------------------------
    def _to_response_dict(self, row: dict) -> dict:
        """Strip encrypted columns and add masked equivalents for safe display."""
        return {
            "id": row["id"],
            "org_id": row["org_id"],
            "name": row["name"],
            "event_type": row["event_type"],
            "endpoint_url": row["endpoint_url"],
            "custom_headers_masked": mask_dict(row.get("custom_headers_enc") or {}),
            "is_active": row["is_active"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "last_triggered_at": row.get("last_triggered_at"),
        }

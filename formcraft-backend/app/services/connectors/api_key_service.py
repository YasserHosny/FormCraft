"""API Key CRUD service for Feature 049.

Secrets are HMAC-SHA256-hashed before storage. Cleartext is returned exactly
once on create / regenerate and never persisted.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.core.audit import AuditLogger
from app.schemas.connector import ApiKeyCreate, ApiKeyUpdate


_SECRET_PREFIX = "fck_"


def _master_secret() -> bytes:
    raw = os.environ.get("INTEGRATION_MASTER_KEY", "")
    if not raw:
        # Fallback so tests that don't set the env var don't immediately fail
        # during import. Hashing is still deterministic — just with an empty key.
        raw = "dev-only-no-master-key-set"
    return raw.encode("utf-8")


def _hash_secret(secret: str) -> str:
    return hmac.new(_master_secret(), secret.encode("utf-8"), hashlib.sha256).hexdigest()


def _generate_secret() -> tuple[str, str]:
    """Returns (cleartext_secret, key_prefix). Prefix is shown in the admin UI as an identifier."""
    body = secrets.token_urlsafe(32)
    cleartext = f"{_SECRET_PREFIX}{body}"
    prefix = cleartext[:12]
    return cleartext, prefix


class ApiKeyService:
    def __init__(self, client: Client):
        self.client = client
        self._audit = AuditLogger(client)

    async def create(self, data: ApiKeyCreate, org_id: UUID, created_by: UUID) -> dict:
        cleartext, prefix = _generate_secret()
        row = {
            "org_id": str(org_id),
            "name": data.name,
            "key_prefix": prefix,
            "key_hash": _hash_secret(cleartext),
            "scopes": data.scopes,
            "expires_at": data.expires_at.isoformat() if data.expires_at else None,
            "created_by": str(created_by),
        }
        try:
            result = self.client.table("api_keys").insert(row).execute()
        except Exception as exc:  # noqa: BLE001
            if "duplicate key" in str(exc).lower() or "23505" in str(exc):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={"code": "API_KEY_NAME_EXISTS", "message": "Name already in use"},
                ) from exc
            raise

        created = result.data[0]
        await self._audit.log_event(
            user_id=str(created_by),
            action="API_KEY_CREATED",
            resource_type="api_key",
            resource_id=created["id"],
            metadata={"name": data.name, "scopes": data.scopes, "key_prefix": prefix},
        )
        # Return cleartext ONCE
        return {**created, "secret": cleartext}

    async def list(self, org_id: UUID) -> list[dict]:
        result = (
            self.client.table("api_keys")
            .select("id, org_id, name, key_prefix, scopes, created_at, last_used_at, expires_at, is_active")
            .eq("org_id", str(org_id))
            .is_("deleted_at", "null")
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []

    async def get(self, key_id: UUID, org_id: UUID) -> dict:
        result = (
            self.client.table("api_keys")
            .select("id, org_id, name, key_prefix, scopes, created_at, last_used_at, expires_at, is_active")
            .eq("id", str(key_id))
            .eq("org_id", str(org_id))
            .is_("deleted_at", "null")
            .maybe_single()
            .execute()
        )
        if not result or not result.data:
            raise HTTPException(status_code=404, detail="API key not found")
        return result.data

    async def update(self, key_id: UUID, data: ApiKeyUpdate, org_id: UUID, by_user: UUID) -> dict:
        existing = await self.get(key_id, org_id)
        updates: dict = {}
        changes: dict = {}

        if data.name is not None and data.name != existing["name"]:
            updates["name"] = data.name
            changes["name"] = {"before": existing["name"], "after": data.name}
        if data.scopes is not None and data.scopes != existing["scopes"]:
            updates["scopes"] = data.scopes
            changes["scopes"] = {"before": existing["scopes"], "after": data.scopes}
        if data.expires_at is not None:
            expires_at = data.expires_at.isoformat()
            if expires_at != existing.get("expires_at"):
                updates["expires_at"] = expires_at
                changes["expires_at"] = {"before": existing.get("expires_at"), "after": expires_at}

        if not changes:
            return existing

        try:
            result = (
                self.client.table("api_keys")
                .update(updates)
                .eq("id", str(key_id))
                .eq("org_id", str(org_id))
                .execute()
            )
        except Exception as exc:  # noqa: BLE001
            if "duplicate key" in str(exc).lower() or "23505" in str(exc):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={"code": "API_KEY_NAME_EXISTS", "message": "Name already in use"},
                ) from exc
            raise

        await self._audit.log_event(
            user_id=str(by_user),
            action="API_KEY_UPDATED",
            resource_type="api_key",
            resource_id=str(key_id),
            metadata={"changes": changes, "key_prefix": existing.get("key_prefix")},
        )
        updated = result.data[0] if result.data else {**existing, **updates}
        return {
            k: updated[k]
            for k in ("id", "org_id", "name", "key_prefix", "scopes", "created_at", "last_used_at", "expires_at", "is_active")
            if k in updated
        }

    async def regenerate(self, key_id: UUID, org_id: UUID, by_user: UUID) -> dict:
        existing = await self.get(key_id, org_id)
        cleartext, prefix = _generate_secret()
        self.client.table("api_keys").update(
            {
                "key_prefix": prefix,
                "key_hash": _hash_secret(cleartext),
                "last_used_at": None,
            }
        ).eq("id", str(key_id)).eq("org_id", str(org_id)).execute()

        await self._audit.log_event(
            user_id=str(by_user),
            action="API_KEY_REGENERATED",
            resource_type="api_key",
            resource_id=str(key_id),
            metadata={"name": existing.get("name"), "new_prefix": prefix},
        )
        return {**existing, "key_prefix": prefix, "secret": cleartext}

    async def revoke(self, key_id: UUID, org_id: UUID, by_user: UUID) -> None:
        existing = await self.get(key_id, org_id)
        now = datetime.now(timezone.utc).isoformat()
        self.client.table("api_keys").update(
            {"is_active": False, "deleted_at": now}
        ).eq("id", str(key_id)).eq("org_id", str(org_id)).execute()

        await self._audit.log_event(
            user_id=str(by_user),
            action="API_KEY_REVOKED",
            resource_type="api_key",
            resource_id=str(key_id),
            metadata={"name": existing.get("name")},
        )

    @staticmethod
    def hash_for_lookup(cleartext: str) -> str:
        """Public helper used by auth middleware when validating an incoming key."""
        return _hash_secret(cleartext)

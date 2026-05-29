import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.db_errors import is_missing_schema_error


class WebhookService:
    """F32 signed webhook subscription and delivery service."""

    def __init__(self, supabase_client):
        self.client = supabase_client

    @staticmethod
    def _payload_bytes(payload: bytes | str | dict[str, Any] | list[Any]) -> bytes:
        if isinstance(payload, bytes):
            return payload
        if isinstance(payload, str):
            return payload.encode("utf-8")
        return json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")

    @classmethod
    def signature_header(
        cls,
        signing_secret: str,
        payload: bytes | str | dict[str, Any] | list[Any],
        timestamp: int | None = None,
    ) -> str:
        timestamp = timestamp or int(time.time())
        signed_payload = f"{timestamp}.".encode("utf-8") + cls._payload_bytes(payload)
        digest = hmac.new(
            signing_secret.encode("utf-8"),
            signed_payload,
            hashlib.sha256,
        ).hexdigest()
        return f"t={timestamp},v1={digest}"

    @classmethod
    def verify_signature(
        cls,
        header: str,
        signing_secret: str,
        payload: bytes | str | dict[str, Any] | list[Any],
        tolerance_seconds: int = 300,
    ) -> bool:
        try:
            parts = dict(item.split("=", 1) for item in header.split(","))
            timestamp = int(parts["t"])
            provided = parts["v1"]
        except (KeyError, TypeError, ValueError):
            return False

        now = int(time.time())
        if abs(now - timestamp) > tolerance_seconds:
            return False

        expected = cls.signature_header(signing_secret, payload, timestamp).split(
            "v1=", 1
        )[1]
        return hmac.compare_digest(provided, expected)

    @staticmethod
    def next_retry_at(attempt_count: int) -> datetime | None:
        if attempt_count >= 3:
            return None
        delay_minutes = [1, 5, 15][max(attempt_count - 1, 0)]
        return datetime.now(timezone.utc) + timedelta(minutes=delay_minutes)

    async def create_subscription(self, org_id, actor_id, url, event_types, signing_secret):
        """Create a webhook subscription."""
        from uuid import uuid4
        row = {
            "id": str(uuid4()),
            "org_id": str(org_id),
            "created_by": str(actor_id),
            "url": url,
            "event_types": event_types,
            "signing_secret": signing_secret,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        result = self.client.table("webhook_subscriptions").insert(row).execute()
        return result.data[0] if result.data else None

    async def list_subscriptions(self, org_id):
        """List webhook subscriptions for an org."""
        try:
            result = (
                self.client.table("webhook_subscriptions")
                .select("id, url, event_types, status, created_at")
                .eq("org_id", str(org_id))
                .order("created_at", desc=True)
                .execute()
            )
        except Exception as exc:
            if is_missing_schema_error(exc):
                return []
            raise
        return result.data or []

    async def update_subscription(self, org_id, subscription_id, updates):
        """Update a webhook subscription."""
        result = (
            self.client.table("webhook_subscriptions")
            .update(updates)
            .eq("id", str(subscription_id))
            .eq("org_id", str(org_id))
            .execute()
        )
        return result.data[0] if result.data else None

    async def record_delivery(self, org_id, subscription_id, payload, response_status, response_body, attempt_count=1, status_value="sent"):
        """Record a webhook delivery."""
        from uuid import uuid4
        row = {
            "id": str(uuid4()),
            "org_id": str(org_id),
            "subscription_id": str(subscription_id),
            "payload": payload,
            "response_status": response_status,
            "response_body": response_body,
            "attempt_count": attempt_count,
            "status": status_value,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        result = self.client.table("webhook_deliveries").insert(row).execute()
        return result.data[0] if result.data else None

    async def list_deliveries(self, org_id, subscription_id=None):
        """List webhook deliveries."""
        query = self.client.table("webhook_deliveries").select("*").eq("org_id", str(org_id))
        if subscription_id:
            query = query.eq("subscription_id", str(subscription_id))
        try:
            result = query.order("created_at", desc=True).execute()
        except Exception as exc:
            if is_missing_schema_error(exc):
                return []
            raise
        return result.data or []

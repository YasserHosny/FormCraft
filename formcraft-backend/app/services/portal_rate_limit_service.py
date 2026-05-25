"""Portal rate limit service for key derivation and event recording."""

import hashlib
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from supabase import Client

logger = logging.getLogger(__name__)


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class PortalRateLimitService:
    """Service for pre-OTP and verified-contact rate limiting."""

    def __init__(self, client: Client):
        self.client = client

    def derive_pre_otp_key(self, ip_hash: str, browser_key_hash: str | None) -> str:
        """Derive rate-limit key before OTP verification."""
        parts = [ip_hash]
        if browser_key_hash:
            parts.append(browser_key_hash)
        return _hash("|".join(parts))

    def derive_verified_key(self, contact_hash: str) -> str:
        """Derive rate-limit key after OTP verification."""
        return contact_hash

    async def is_allowed(
        self,
        org_id: UUID,
        portal_configuration_id: UUID,
        key_type: str,
        key_hash: str,
        event_type: str,
        max_requests: int,
        window_minutes: int,
    ) -> bool:
        """Check if an event is allowed under the current rate limit window."""
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(minutes=window_minutes)
        resp = (
            self.client.table("portal_rate_limit_events")
            .select("*", count="exact")
            .eq("org_id", str(org_id))
            .eq("portal_configuration_id", str(portal_configuration_id))
            .eq("key_type", key_type)
            .eq("key_hash", key_hash)
            .eq("event_type", event_type)
            .gte("window_start", window_start.isoformat())
            .execute()
        )
        count = resp.count or 0
        allowed = count < max_requests
        return allowed

    async def record_event(
        self,
        org_id: UUID,
        portal_configuration_id: UUID,
        portal_session_id: UUID | None,
        key_type: str,
        key_hash: str,
        event_type: str,
        allowed: bool,
    ) -> None:
        """Record a rate limit event."""
        now = datetime.now(timezone.utc)
        data = {
            "org_id": str(org_id),
            "portal_configuration_id": str(portal_configuration_id),
            "portal_session_id": str(portal_session_id) if portal_session_id else None,
            "key_type": key_type,
            "key_hash": key_hash,
            "event_type": event_type,
            "allowed": allowed,
            "window_start": now.isoformat(),
        }
        self.client.table("portal_rate_limit_events").insert(data).execute()

    async def check_and_record(
        self,
        org_id: UUID,
        portal_configuration_id: UUID,
        portal_session_id: UUID | None,
        key_type: str,
        key_hash: str,
        event_type: str,
        max_requests: int,
        window_minutes: int,
    ) -> bool:
        """Check rate limit and record the event in one call."""
        allowed = await self.is_allowed(
            org_id, portal_configuration_id, key_type, key_hash, event_type, max_requests, window_minutes
        )
        await self.record_event(
            org_id, portal_configuration_id, portal_session_id, key_type, key_hash, event_type, allowed
        )
        return allowed

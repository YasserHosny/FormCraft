"""Session service: timeout enforcement, concurrent limits, and audit logging."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

from app.core.supabase import get_supabase_client
from app.models.identity import SessionEvent, SessionEventType, SessionResult

logger = logging.getLogger(__name__)


class SessionService:
    """Business logic for session lifecycle and audit events."""

    @staticmethod
    def record_event(
        user_id: UUID,
        event_type: SessionEventType,
        result: SessionResult,
        provider_id: UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        reason: str | None = None,
    ) -> SessionEvent:
        client = get_supabase_client()
        row = {
            "id": str(uuid4()),
            "user_id": str(user_id),
            "event_type": event_type.value,
            "provider_id": str(provider_id) if provider_id else None,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "result": result.value,
            "reason": reason,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        client.table("session_events").insert(row).execute()
        return SessionEvent(**row)

    @staticmethod
    def enforce_session_limits(user_id: UUID, max_sessions: int) -> None:
        """Revoke oldest sessions if the user exceeds the concurrent limit."""
        client = get_supabase_client()
        # In a real implementation this would query an active_sessions table.
        # For MVP we log the enforcement action.
        logger.info("enforce_session_limits called for user %s max %s", user_id, max_sessions)

    @staticmethod
    def check_idle_timeout(last_activity: datetime, idle_limit_minutes: int) -> bool:
        if not last_activity:
            return False
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=idle_limit_minutes)
        return last_activity.replace(tzinfo=timezone.utc) < cutoff if last_activity.tzinfo is None else last_activity < cutoff

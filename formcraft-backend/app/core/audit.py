import asyncio
import logging
from datetime import datetime, timezone

from supabase import Client


logger = logging.getLogger(__name__)


class AuditLogger:
    """Async, non-blocking audit logger writing to Supabase audit_logs table."""

    def __init__(self, supabase_client: Client):
        self.client = supabase_client

    async def log_event(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        metadata: dict | None = None,
        ip_address: str | None = None,
    ) -> None:
        """Fire-and-forget audit log write. Never blocks the request path."""
        entry = {
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "metadata": metadata or {},
            "ip_address": ip_address,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            asyncio.create_task(self._write(entry))
            logger.info(
                "audit_log_enqueued",
                extra={"action": action, "resource_type": resource_type, "user_id": user_id},
            )
        except Exception:
            logger.warning(
                "audit_log_enqueue_failed",
                extra={"action": action, "resource_type": resource_type, "user_id": user_id},
            )

    async def _write(self, entry: dict) -> None:
        self.client.table("audit_logs").insert(entry).execute()
        logger.debug("audit_log_written", extra={"action": entry.get("action")})

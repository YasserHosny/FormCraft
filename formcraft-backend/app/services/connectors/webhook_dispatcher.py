"""Webhook dispatcher for Feature 049.

Polls `webhook_deliveries WHERE status='pending' AND next_retry_at <= NOW()`
and POSTs the payload to the webhook's endpoint with HMAC-SHA256 signature.

Retry backoff per spec FR-8: 1s, 5s, 30s (attempts 1→2, 2→3, 3→fail).

This module exposes two public surfaces:
  * `enqueue(...)` — called from form submission / print / publish handlers
  * `dispatch_pending(...)` — invoked by a background scheduler (one row at a time
    in Phase 1; concurrent workers handled later via `FOR UPDATE SKIP LOCKED` RPC).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import httpx
from supabase import Client

from app.services.connectors.encryption_service import (
    decrypt_dict_for_org,
    decrypt_for_org,
)


logger = logging.getLogger(__name__)


# Retry schedule (seconds from previous attempt) — spec FR-8
_RETRY_SCHEDULE = (1, 5, 30)

# Outbound HTTP timeout per attempt
_HTTP_TIMEOUT_SECONDS = 10

# Maximum response body bytes to persist (FR-6: ≤ 1KB)
_RESPONSE_BODY_LIMIT = 1024

# Banking PAN/account masking heuristic. We mask any run of 16-25 digits not surrounded
# by other digits — covers PAN (13-19), IBAN bodies (15-30), and account numbers.
# Lookarounds (?<!\d) / (?!\d) instead of \b so we match digits adjacent to letters
# (e.g. the digit body of "AE0703..." in a full IBAN).
import re
_PAN_RE = re.compile(r"(?<!\d)(\d{8})\d{4,17}(\d{4})(?!\d)")


def _mask_sensitive(body_excerpt: str) -> str:
    """Mask PAN-like digit runs to last-4. Conservative — over-masks rather than under-masks."""
    return _PAN_RE.sub(lambda m: f"{m.group(1)[:4]}{'*' * 6}{m.group(2)}", body_excerpt)


def _sign_payload(payload_bytes: bytes, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()


def _write_worker_audit(
    client: Client,
    *,
    action: str,
    resource_id: str,
    metadata: dict[str, Any],
) -> None:
    """Write dispatcher audit rows synchronously from the worker context."""
    client.table("audit_logs").insert(
        {
            "user_id": "00000000-0000-0000-0000-000000000000",
            "action": action,
            "resource_type": "webhook_delivery",
            "resource_id": resource_id,
            "metadata": metadata,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    ).execute()


def enqueue(
    client: Client,
    *,
    org_id: UUID | str,
    event_type: str,
    resource_id: UUID | str,
    payload: dict[str, Any],
) -> int:
    """Enqueue one row per active webhook subscribed to this event_type.

    Returns the count of rows enqueued. Form-submission handlers MUST NOT
    `await` outbound delivery — they just call this and move on.
    """
    webhooks = (
        client.table("webhooks")
        .select("id")
        .eq("org_id", str(org_id))
        .eq("event_type", event_type)
        .eq("is_active", True)
        .is_("deleted_at", "null")
        .execute()
    )
    rows = webhooks.data or []
    if not rows:
        return 0

    now = datetime.now(timezone.utc).isoformat()
    inserts = [
        {
            "webhook_id": w["id"],
            "org_id": str(org_id),
            "event_type": event_type,
            "resource_id": str(resource_id),
            "payload": payload,
            "next_retry_at": now,
        }
        for w in rows
    ]
    client.table("webhook_deliveries").insert(inserts).execute()
    return len(inserts)


def _claim_next_pending(client: Client) -> dict | None:
    """Claim one pending delivery whose retry time has arrived.

    Phase 1 uses optimistic UPDATE..RETURNING via PostgREST (single-worker safe).
    For multi-worker we'd switch to a SECURITY DEFINER SQL function with
    `FOR UPDATE SKIP LOCKED` semantics — deferred until throughput requires it.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    pending = (
        client.table("webhook_deliveries")
        .select("*")
        .eq("status", "pending")
        .lte("next_retry_at", now_iso)
        .order("next_retry_at", desc=False)
        .limit(1)
        .execute()
    )
    if not pending.data:
        return None
    row = pending.data[0]
    # Atomically flip pending→sent so concurrent workers can't pick it twice
    update = (
        client.table("webhook_deliveries")
        .update({"status": "sent", "sent_at": now_iso})
        .eq("id", row["id"])
        .eq("status", "pending")  # CAS guard
        .execute()
    )
    if not update.data:
        return None  # raced
    return {**row, "status": "sent", "sent_at": now_iso}


def _load_webhook(client: Client, webhook_id: str) -> dict | None:
    res = (
        client.table("webhooks")
        .select("*")
        .eq("id", webhook_id)
        .is_("deleted_at", "null")
        .maybe_single()
        .execute()
    )
    return res.data if res else None


def _schedule_retry(
    client: Client, delivery_id: str, attempt_number: int, error_message: str | None, status_code: int | None
) -> None:
    """Mark this attempt failed; schedule the next one if budget remains."""
    if attempt_number >= len(_RETRY_SCHEDULE):
        client.table("webhook_deliveries").update(
            {
                "status": "failed",
                "error_message": error_message,
                "status_code": status_code,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
        ).eq("id", delivery_id).execute()
        return

    next_in_s = _RETRY_SCHEDULE[attempt_number]  # index = current attempt count, gives delay until next
    next_at = (datetime.now(timezone.utc) + timedelta(seconds=next_in_s)).isoformat()
    client.table("webhook_deliveries").update(
        {
            "status": "pending",
            "attempt_number": attempt_number + 1,
            "next_retry_at": next_at,
            "error_message": error_message,
            "status_code": status_code,
        }
    ).eq("id", delivery_id).execute()


def dispatch_pending(client: Client) -> bool:
    """Process one pending delivery. Returns True if a row was processed, False if queue empty.

    Designed to be called in a tight poll loop (sleep 2s on False) by a background task.
    """
    delivery = _claim_next_pending(client)
    if not delivery:
        return False

    webhook = _load_webhook(client, delivery["webhook_id"])
    if not webhook:
        # Webhook deleted between enqueue and dispatch — mark failed and move on
        client.table("webhook_deliveries").update(
            {
                "status": "failed",
                "error_message": "webhook deleted before dispatch",
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
        ).eq("id", delivery["id"]).execute()
        return True

    org_id = webhook["org_id"]
    headers_plain = decrypt_dict_for_org(webhook.get("custom_headers_enc") or {}, org_id)
    webhook_secret = decrypt_for_org(webhook["webhook_secret_enc"], org_id) or ""

    payload_bytes = json.dumps(delivery["payload"], separators=(",", ":"), sort_keys=True).encode("utf-8")
    signature = _sign_payload(payload_bytes, webhook_secret)

    request_headers = {
        "Content-Type": "application/json",
        "X-FormCraft-Signature": signature,
        "X-FormCraft-Event": delivery["event_type"],
        "X-FormCraft-Delivery-Id": delivery["id"],
        **headers_plain,
    }

    status_code: int | None = None
    body_excerpt: str | None = None
    error_message: str | None = None
    started = time.monotonic()
    try:
        with httpx.Client(timeout=_HTTP_TIMEOUT_SECONDS) as http:
            resp = http.post(webhook["endpoint_url"], content=payload_bytes, headers=request_headers)
        status_code = resp.status_code
        body = resp.text[:_RESPONSE_BODY_LIMIT]
        body_excerpt = _mask_sensitive(body) if body else None
    except httpx.RequestError as exc:
        error_message = f"network error: {type(exc).__name__}: {str(exc)[:200]}"
    except Exception as exc:  # noqa: BLE001
        error_message = f"dispatcher error: {type(exc).__name__}: {str(exc)[:200]}"

    duration_ms = int((time.monotonic() - started) * 1000)
    success = status_code is not None and 200 <= status_code < 300

    if success:
        client.table("webhook_deliveries").update(
            {
                "status": "success",
                "status_code": status_code,
                "response_body": body_excerpt,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
        ).eq("id", delivery["id"]).execute()
        client.table("webhooks").update({"last_triggered_at": datetime.now(timezone.utc).isoformat()}).eq(
            "id", webhook["id"]
        ).execute()
        _write_worker_audit(
            client,
            action="WEBHOOK_DELIVERY_SUCCESS",
            resource_id=delivery["id"],
            metadata={
                "webhook_id": webhook["id"],
                "status_code": status_code,
                "duration_ms": duration_ms,
            },
        )
    else:
        _schedule_retry(
            client,
            delivery_id=delivery["id"],
            attempt_number=delivery["attempt_number"],
            error_message=error_message or f"HTTP {status_code}",
            status_code=status_code,
        )
        _write_worker_audit(
            client,
            action="WEBHOOK_DELIVERY_FAILED",
            resource_id=delivery["id"],
            metadata={
                "webhook_id": webhook["id"],
                "status_code": status_code,
                "error": error_message,
                "attempt": delivery["attempt_number"],
            },
        )
    return True

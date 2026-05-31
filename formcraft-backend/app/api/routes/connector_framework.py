"""API routes for Feature 049 Connector Framework Phase 1.

Phase 1 surface:
  POST/GET/PUT/DELETE /admin/integrations/api-keys
  POST/GET/PUT/DELETE /admin/integrations/webhooks (+ /test, /deliveries)

Pre-built connector CRUD (DMS/Email/CRM/Banking) lives in Phase 4 per tasks.md.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.api.deps import require_role
from app.core.middleware.rate_limit import limiter
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile
from app.schemas.connector import (
    ApiKeyCreate,
    ApiKeyCreatedResponse,
    ApiKeyResponse,
    EventType,
    WebhookCreate,
    WebhookDeliveryListResponse,
    WebhookDeliveryResponse,
    WebhookResponse,
    WebhookTestResponse,
    WebhookUpdate,
)
from app.services.connectors.api_key_service import ApiKeyService
from app.services.connectors.webhook_service import WebhookService


router = APIRouter(prefix="/integrations", tags=["Connector Framework (Admin)"])


def _require_org(user: UserProfile) -> UUID:
    if not user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )
    return user.org_id


# ----------------------------------------------------------------------
# API Keys
# ----------------------------------------------------------------------

@router.post("/api-keys", status_code=201, response_model=ApiKeyCreatedResponse)
@limiter.limit("10/minute")
async def create_api_key(
    request: Request,
    body: ApiKeyCreate,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    org_id = _require_org(current_user)
    service = ApiKeyService(get_supabase_client())
    created = await service.create(body, org_id=org_id, created_by=current_user.id)
    return ApiKeyCreatedResponse(**created)


@router.get("/api-keys", response_model=list[ApiKeyResponse])
async def list_api_keys(
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    org_id = _require_org(current_user)
    service = ApiKeyService(get_supabase_client())
    return [ApiKeyResponse(**k) for k in await service.list(org_id)]


@router.get("/api-keys/{key_id}", response_model=ApiKeyResponse)
async def get_api_key(
    key_id: UUID,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    org_id = _require_org(current_user)
    service = ApiKeyService(get_supabase_client())
    return ApiKeyResponse(**await service.get(key_id, org_id))


@router.post("/api-keys/{key_id}/regenerate", response_model=ApiKeyCreatedResponse)
@limiter.limit("10/minute")
async def regenerate_api_key(
    request: Request,
    key_id: UUID,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    org_id = _require_org(current_user)
    service = ApiKeyService(get_supabase_client())
    return ApiKeyCreatedResponse(**await service.regenerate(key_id, org_id, current_user.id))


@router.delete("/api-keys/{key_id}", status_code=204)
async def revoke_api_key(
    key_id: UUID,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    org_id = _require_org(current_user)
    service = ApiKeyService(get_supabase_client())
    await service.revoke(key_id, org_id, current_user.id)


# ----------------------------------------------------------------------
# Webhooks
# ----------------------------------------------------------------------

@router.post("/webhooks", status_code=201, response_model=WebhookResponse)
@limiter.limit("30/minute")
async def create_webhook(
    request: Request,
    body: WebhookCreate,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    org_id = _require_org(current_user)
    service = WebhookService(get_supabase_client())
    return WebhookResponse(**await service.create(body, org_id=org_id, by_user=current_user.id))


@router.get("/webhooks", response_model=list[WebhookResponse])
async def list_webhooks(
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    org_id = _require_org(current_user)
    service = WebhookService(get_supabase_client())
    return [WebhookResponse(**w) for w in await service.list(org_id)]


@router.get("/webhooks/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: UUID,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    org_id = _require_org(current_user)
    service = WebhookService(get_supabase_client())
    return WebhookResponse(**await service.get(webhook_id, org_id))


@router.put("/webhooks/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: UUID,
    body: WebhookUpdate,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    org_id = _require_org(current_user)
    service = WebhookService(get_supabase_client())
    return WebhookResponse(**await service.update(webhook_id, body, org_id, current_user.id))


@router.delete("/webhooks/{webhook_id}", status_code=204)
async def delete_webhook(
    webhook_id: UUID,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    org_id = _require_org(current_user)
    service = WebhookService(get_supabase_client())
    await service.delete(webhook_id, org_id, current_user.id)


@router.post("/webhooks/{webhook_id}/test", response_model=WebhookTestResponse)
@limiter.limit("10/minute")
async def test_webhook(
    request: Request,
    webhook_id: UUID,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    """Send a canonical test payload and return the response synchronously."""
    org_id = _require_org(current_user)
    service = WebhookService(get_supabase_client())
    # Need internal access (encrypted secret) to send the test
    raw = await service.get(webhook_id, org_id, include_secrets=True)

    from app.services.connectors.encryption_service import decrypt_dict_for_org, decrypt_for_org
    import hashlib
    import hmac
    import json
    import time

    headers_plain = decrypt_dict_for_org(raw.get("custom_headers_enc") or {}, org_id)
    secret = decrypt_for_org(raw["webhook_secret_enc"], org_id) or ""
    payload = {
        "event": raw["event_type"],
        "test": True,
        "org_id": str(org_id),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    body_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()

    started = time.monotonic()
    try:
        with httpx.Client(timeout=10.0) as http:
            resp = http.post(
                raw["endpoint_url"],
                content=body_bytes,
                headers={
                    "Content-Type": "application/json",
                    "X-FormCraft-Signature": signature,
                    "X-FormCraft-Event": raw["event_type"],
                    "X-FormCraft-Test": "true",
                    **headers_plain,
                },
            )
        duration_ms = int((time.monotonic() - started) * 1000)
        return WebhookTestResponse(
            success=200 <= resp.status_code < 300,
            status_code=resp.status_code,
            response_body_excerpt=resp.text[:512],
            duration_ms=duration_ms,
        )
    except httpx.RequestError as exc:
        duration_ms = int((time.monotonic() - started) * 1000)
        return WebhookTestResponse(
            success=False,
            status_code=None,
            error=f"{type(exc).__name__}: {str(exc)[:200]}",
            duration_ms=duration_ms,
        )


@router.get("/webhooks/{webhook_id}/deliveries", response_model=WebhookDeliveryListResponse)
async def list_deliveries(
    webhook_id: UUID,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    delivery_status: str | None = Query(None, alias="status"),
):
    org_id = _require_org(current_user)
    client = get_supabase_client()

    # Verify webhook belongs to org first
    wh = (
        client.table("webhooks")
        .select("id")
        .eq("id", str(webhook_id))
        .eq("org_id", str(org_id))
        .maybe_single()
        .execute()
    )
    if not wh or not wh.data:
        raise HTTPException(status_code=404, detail="Webhook not found")

    q = (
        client.table("webhook_deliveries")
        .select(
            "id, webhook_id, event_type, resource_id, attempt_number, status, status_code, error_message, "
            "created_at, sent_at, next_retry_at, completed_at",
            count="exact",
        )
        .eq("webhook_id", str(webhook_id))
        .eq("org_id", str(org_id))
    )
    if delivery_status:
        q = q.eq("status", delivery_status)
    offset = (page - 1) * page_size
    res = q.order("created_at", desc=True).range(offset, offset + page_size - 1).execute()
    total = res.count if res.count is not None else len(res.data or [])
    return WebhookDeliveryListResponse(
        items=[WebhookDeliveryResponse(**row) for row in (res.data or [])],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/webhooks/{webhook_id}/deliveries/{delivery_id}/retry", status_code=202)
async def retry_delivery(
    webhook_id: UUID,
    delivery_id: UUID,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    """Reset a failed delivery so the dispatcher will pick it up immediately."""
    org_id = _require_org(current_user)
    client = get_supabase_client()
    now = datetime.now(timezone.utc).isoformat()
    res = (
        client.table("webhook_deliveries")
        .update(
            {
                "status": "pending",
                "next_retry_at": now,
                "attempt_number": 1,
                "error_message": None,
                "status_code": None,
                "completed_at": None,
            }
        )
        .eq("id", str(delivery_id))
        .eq("webhook_id", str(webhook_id))
        .eq("org_id", str(org_id))
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return {"queued": True}

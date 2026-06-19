from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status

from app.core.supabase import get_supabase_client
from app.middleware.org_context import OrgContext, get_org_context, require_org_admin, require_platform_admin
from app.schemas.billing import (
    BillingOptionsResponse,
    BillingPurchaseListResponse,
    BillingPurchaseResponse,
    BillingPurpose,
    PayGatewayWebhookRequest,
    PayGatewayWebhookResponse,
    PurchaseCreateRequest,
    PurchaseCreateResponse,
    PurchaseVerifyRequest,
    PurchaseVerifyResponse,
    RefundCreateRequest,
    RefundResponse,
)
from app.services.billing_service import BillingService
from app.services.paygateway_client import PayGatewayClient


router = APIRouter(prefix="/billing", tags=["Billing"])
platform_router = APIRouter(prefix="/platform/billing", tags=["Platform Billing"])


def _service() -> BillingService:
    return BillingService(get_supabase_client())


@router.get("/options", response_model=BillingOptionsResponse)
async def get_billing_options(
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
    purpose: BillingPurpose | None = None,
    listing_id: UUID | None = None,
):
    if not ctx.org_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "billing.org_required")
    return await _service().get_options(org_id=ctx.org_id, purpose=purpose, listing_id=listing_id)


@router.post("/purchases", response_model=PurchaseCreateResponse, status_code=201)
async def create_billing_purchase(
    body: PurchaseCreateRequest,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    if not ctx.org_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "billing.org_required")
    return await _service().create_purchase(
        org_id=ctx.org_id,
        actor_id=ctx.user_id,
        purpose=body.purpose,
        target=body.target,
        quantity=body.quantity,
        return_url=body.return_url,
    )


@router.post("/purchases/{purchase_id}/verify", response_model=PurchaseVerifyResponse)
async def verify_billing_purchase(
    purchase_id: UUID,
    body: PurchaseVerifyRequest,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    return await _service().verify_purchase(
        org_id=ctx.org_id,
        purchase_id=purchase_id,
        actor_id=ctx.user_id,
        provider_payment_id=body.provider_payment_id,
    )


@router.get("/purchases", response_model=BillingPurchaseListResponse)
async def list_billing_purchases(
    ctx: Annotated[OrgContext, Depends(get_org_context)],
    organization_id: UUID | None = None,
    status_value: str | None = Query(default=None, alias="status"),
    purpose: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
):
    org_id = organization_id if ctx.is_platform_admin and organization_id else ctx.org_id
    return {"items": _service().list_purchases(org_id=org_id, status_value=status_value, purpose=purpose, limit=limit)}


@router.get("/purchases/{purchase_id}", response_model=BillingPurchaseResponse)
async def get_billing_purchase(
    purchase_id: UUID,
    ctx: Annotated[OrgContext, Depends(get_org_context)],
):
    return _service().get_purchase(purchase_id=purchase_id, org_id=None if ctx.is_platform_admin else ctx.org_id)


@router.post("/paygateway/webhook", response_model=PayGatewayWebhookResponse)
async def paygateway_webhook(
    body: PayGatewayWebhookRequest,
    request: Request,
    x_paygateway_signature: Annotated[str | None, Header(alias="X-PayGateway-Signature")] = None,
):
    raw = await request.body()
    if not PayGatewayClient().verify_webhook_signature(body=raw, signature=x_paygateway_signature):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "billing.webhook_invalid")
    service = _service()
    purchase = service.get_purchase(purchase_id=body.purchase_reference, org_id=None)
    if body.event_type in {"payment.succeeded", "payment.completed"}:
        await service.verify_purchase(
            org_id=None,
            purchase_id=body.purchase_reference,
            actor_id=UUID(str(purchase["created_by"])),
            provider_payment_id=body.payment_id,
        )
        purchase = service.get_purchase(purchase_id=body.purchase_reference, org_id=None)
    return {"received": True, "purchase_id": body.purchase_reference, "status": purchase["status"]}


@platform_router.post("/purchases/{purchase_id}/refund", response_model=RefundResponse)
async def refund_billing_purchase(
    purchase_id: UUID,
    body: RefundCreateRequest,
    ctx: Annotated[OrgContext, Depends(require_platform_admin())],
):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "billing.refund_not_implemented")

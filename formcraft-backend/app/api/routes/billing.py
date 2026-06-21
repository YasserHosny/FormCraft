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
    CancelSubscriptionResponse,
    CreateSubscriptionRequest,
    CreateSubscriptionResponse,
    DowngradeScheduleRequest,
    DowngradeScheduleResponse,
    PayGatewayWebhookRequest,
    PayGatewayWebhookResponse,
    PortalUrlRequest,
    PortalUrlResponse,
    PurchaseCreateRequest,
    PurchaseCreateResponse,
    PurchaseVerifyRequest,
    PurchaseVerifyResponse,
    ReactivateSubscriptionResponse,
    RefundCreateRequest,
    RefundResponse,
    SubscriptionResponse,
    SubscriptionWebhookRequest,
    SubscriptionWebhookResponse,
    UpgradeSubscriptionRequest,
    UpgradeSubscriptionResponse,
)
from app.services.billing_service import BillingService
from app.services.paygateway_client import PayGatewayClient
from app.services.subscription_service import SubscriptionService


router = APIRouter(prefix="/billing", tags=["Billing"])
platform_router = APIRouter(prefix="/platform/billing", tags=["Platform Billing"])


def _service() -> BillingService:
    return BillingService(get_supabase_client())


def _subscription_service() -> SubscriptionService:
    return SubscriptionService(get_supabase_client())


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
    return await _service().refund_purchase(
        org_id=None,
        purchase_id=purchase_id,
        actor_id=ctx.user_id,
        reason=body.reason,
        amount_minor=body.amount_minor,
    )


# ---------------------------------------------------------------------------
# F059 — Subscription endpoints
# ---------------------------------------------------------------------------

subscription_router = APIRouter(prefix="/billing/subscriptions", tags=["Billing Subscriptions"])


@subscription_router.get("/current", response_model=SubscriptionResponse)
async def get_current_subscription(
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    sub = _subscription_service().get_current_subscription(ctx.org_id)
    if sub is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "billing.subscription_not_found")
    return sub


@subscription_router.post("", response_model=CreateSubscriptionResponse, status_code=201)
async def create_subscription(
    body: CreateSubscriptionRequest,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    return await _subscription_service().create_subscription(
        org_id=ctx.org_id,
        actor_id=ctx.user_id,
        tier=body.tier,
        billing_interval=body.billing_interval.value,
        return_url=body.return_url,
    )


@subscription_router.post("/upgrade", response_model=UpgradeSubscriptionResponse)
async def upgrade_subscription(
    body: UpgradeSubscriptionRequest,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    return await _subscription_service().upgrade_subscription(org_id=ctx.org_id, new_tier=body.tier)


@subscription_router.post("/downgrade-schedule", response_model=DowngradeScheduleResponse)
async def schedule_downgrade(
    body: DowngradeScheduleRequest,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    return _subscription_service().schedule_downgrade(org_id=ctx.org_id, new_tier=body.tier)


@subscription_router.delete("/downgrade-schedule", response_model=DowngradeScheduleResponse)
async def cancel_downgrade_schedule(
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    return _subscription_service().cancel_downgrade_schedule(ctx.org_id)


@subscription_router.post("/cancel", response_model=CancelSubscriptionResponse)
async def cancel_subscription(
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    return await _subscription_service().cancel_subscription(ctx.org_id)


@subscription_router.post("/reactivate", response_model=ReactivateSubscriptionResponse)
async def reactivate_subscription(
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    return await _subscription_service().reactivate_subscription(ctx.org_id)


@subscription_router.post("/portal-url", response_model=PortalUrlResponse)
async def get_portal_url(
    body: PortalUrlRequest,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    return await _subscription_service().get_portal_url(org_id=ctx.org_id, return_url=body.return_url)


# ---------------------------------------------------------------------------
# F059 — Subscription lifecycle webhook (separate from payment webhook)
# ---------------------------------------------------------------------------

@router.post("/paygateway/subscription-webhook", response_model=SubscriptionWebhookResponse)
async def subscription_webhook(
    body: SubscriptionWebhookRequest,
    request: Request,
    x_paygateway_signature: Annotated[str | None, Header(alias="X-PayGateway-Signature")] = None,
):
    raw = await request.body()
    if not PayGatewayClient().verify_webhook_signature(body=raw, signature=x_paygateway_signature):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "billing.webhook_invalid")

    svc = _subscription_service()
    event = body.model_dump()

    match body.event_type:
        case "invoice.paid":
            await svc.handle_invoice_paid(event)
        case "invoice.payment_failed":
            await svc.handle_payment_failed(event)
        case "customer.subscription.updated":
            await svc.handle_subscription_updated(event)
        case "customer.subscription.deleted":
            svc.handle_subscription_deleted(event)
        case _:
            # Unknown event — acknowledge without processing
            pass

    return {"received": True, "event_type": body.event_type}

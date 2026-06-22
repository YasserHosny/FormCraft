"""Billing DTOs for PayGateway-backed purchases (F058)."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class BillingPurpose(StrEnum):
    SUBSCRIPTION_TIER = "subscription_tier"
    SEATS = "seats"
    OCR_BATCH = "ocr_batch"
    MARKETPLACE_TEMPLATE = "marketplace_template"


class BillingPurchaseStatus(StrEnum):
    CREATED = "created"
    REQUIRES_ACTION = "requires_action"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class BillingFulfillmentSource(StrEnum):
    CHECKOUT_RETURN = "checkout_return"
    STATUS_POLL = "status_poll"
    WEBHOOK = "webhook"
    RECONCILIATION = "reconciliation"
    ZERO_AMOUNT = "zero_amount"


class BillingRefundStatus(StrEnum):
    REQUESTED = "requested"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class BillingReversalStatus(StrEnum):
    PENDING = "pending"
    APPLIED = "applied"
    FAILED = "failed"


class CheckoutToken(BaseModel):
    provider: str = "paygateway"
    client_token: str
    requires_action: bool = False
    expires_at: datetime | None = None


class TierOption(BaseModel):
    tier: str
    amount_minor: int | None = Field(default=None, ge=0)
    currency: str
    available: bool = True
    unavailable_reason_key: str | None = None
    is_current: bool = False


class AddonOption(BaseModel):
    purpose: BillingPurpose
    unit_amount_minor: int | None = Field(default=None, ge=0)
    currency: str
    min_quantity: int | None = Field(default=None, ge=0)
    max_quantity: int | None = Field(default=None, ge=0)
    available: bool = True
    unavailable_reason_key: str | None = None


class BillingOptionsResponse(BaseModel):
    currency: str
    current_tier: str
    tiers: list[TierOption] = Field(default_factory=list)
    addons: list[AddonOption] = Field(default_factory=list)


class PurchaseCreateRequest(BaseModel):
    purpose: BillingPurpose
    target: dict[str, Any] = Field(default_factory=dict)
    quantity: int | None = Field(default=None, ge=0)
    return_url: str | None = None

    @field_validator("target")
    @classmethod
    def target_must_be_object(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("target must be an object")
        return value


class PurchaseCreateResponse(BaseModel):
    purchase_id: UUID
    status: BillingPurchaseStatus
    amount_minor: int = Field(ge=0)
    currency: str
    checkout: CheckoutToken | None = None
    message_key: str | None = None


class PurchaseVerifyRequest(BaseModel):
    provider_payment_id: str | None = None
    client_reference: str | None = None


class PurchaseVerifyResponse(BaseModel):
    purchase_id: UUID
    status: BillingPurchaseStatus
    fulfilled: bool = False
    message_key: str | None = None


class BillingPurchaseResponse(BaseModel):
    id: UUID
    organization_id: UUID
    purpose: BillingPurpose
    target: dict[str, Any]
    quantity: int | None = None
    amount_minor: int = Field(ge=0)
    currency: str
    status: BillingPurchaseStatus
    fulfilled_at: datetime | None = None
    created_at: datetime


class BillingPurchaseListResponse(BaseModel):
    items: list[BillingPurchaseResponse]
    next_cursor: str | None = None


class PayGatewayWebhookRequest(BaseModel):
    event_id: str
    event_type: str
    payment_id: str
    purchase_reference: UUID


class PayGatewayWebhookResponse(BaseModel):
    received: bool
    purchase_id: UUID
    status: BillingPurchaseStatus


class RefundCreateRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=1000)
    amount_minor: int | None = Field(default=None, ge=1, description="Omit for full refund; pass a value < purchase amount for partial refund")


class RefundResponse(BaseModel):
    refund_id: UUID
    purchase_id: UUID
    status: BillingRefundStatus
    reversal_status: BillingReversalStatus
    amount_minor: int = Field(ge=0)
    currency: str
    message_key: str


# ---------------------------------------------------------------------------
# F059 — Recurring subscription billing schemas
# ---------------------------------------------------------------------------


class SubscriptionStatus(StrEnum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"


class BillingIntervalEnum(StrEnum):
    MONTHLY = "monthly"
    ANNUAL = "annual"


class SubscriptionResponse(BaseModel):
    id: UUID
    org_id: UUID
    tier: str
    billing_interval: BillingIntervalEnum
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    next_renewal_amount_minor: int = Field(ge=0)
    currency: str
    scheduled_downgrade_tier: str | None = None
    cancel_at_period_end: bool = False
    failed_payment_count: int = Field(ge=0, default=0)
    provider_subscription_id: str | None = None


class CreateSubscriptionRequest(BaseModel):
    tier: str
    billing_interval: BillingIntervalEnum
    return_url: str


class CreateSubscriptionResponse(BaseModel):
    subscription_id: str
    status: str
    checkout: CheckoutToken | None = None


class UpgradeSubscriptionRequest(BaseModel):
    tier: str


class UpgradeSubscriptionResponse(BaseModel):
    subscription_id: str
    previous_tier: str
    new_tier: str
    proration_amount_minor: int = Field(ge=0)
    currency: str
    status: SubscriptionStatus


class DowngradeScheduleRequest(BaseModel):
    tier: str


class DowngradeScheduleResponse(BaseModel):
    subscription_id: str
    current_tier: str
    scheduled_downgrade_tier: str | None
    effective_date: datetime | None = None


class CancelSubscriptionResponse(BaseModel):
    subscription_id: str
    tier: str
    cancel_at_period_end: bool
    period_end: datetime


class ReactivateSubscriptionResponse(BaseModel):
    subscription_id: str
    tier: str
    cancel_at_period_end: bool
    next_renewal_date: datetime


class PortalUrlRequest(BaseModel):
    return_url: str


class PortalUrlResponse(BaseModel):
    portal_url: str
    expires_at: datetime


class SubscriptionWebhookRequest(BaseModel):
    event_id: str
    event_type: str
    subscription_id: str
    invoice_id: str | None = None
    amount_paid_minor: int | None = None
    currency: str | None = None
    period_start: datetime | None = None
    period_end: datetime | None = None
    metadata: dict = Field(default_factory=dict)


class SubscriptionWebhookResponse(BaseModel):
    received: bool
    event_type: str

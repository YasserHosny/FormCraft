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


class RefundResponse(BaseModel):
    refund_id: UUID
    purchase_id: UUID
    status: BillingRefundStatus
    reversal_status: BillingReversalStatus
    amount_minor: int = Field(ge=0)
    currency: str
    message_key: str

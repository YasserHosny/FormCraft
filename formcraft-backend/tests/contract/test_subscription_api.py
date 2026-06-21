"""Contract tests — validate F059 subscription Pydantic schema shapes."""
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.schemas.billing import (
    BillingIntervalEnum,
    CancelSubscriptionResponse,
    CreateSubscriptionRequest,
    CreateSubscriptionResponse,
    DowngradeScheduleRequest,
    DowngradeScheduleResponse,
    PortalUrlRequest,
    PortalUrlResponse,
    ReactivateSubscriptionResponse,
    SubscriptionResponse,
    SubscriptionStatus,
    SubscriptionWebhookRequest,
    SubscriptionWebhookResponse,
    UpgradeSubscriptionRequest,
    UpgradeSubscriptionResponse,
)

NOW = datetime.now(timezone.utc)
SUB_ID = "sub_1ABCDEFabcdef"


def _sub_response(**kwargs):
    defaults = {
        "id": uuid4(),
        "org_id": uuid4(),
        "tier": "professional",
        "billing_interval": "monthly",
        "status": "active",
        "current_period_start": NOW,
        "current_period_end": NOW,
        "next_renewal_amount_minor": 490000,
        "currency": "EGP",
    }
    return SubscriptionResponse(**{**defaults, **kwargs})


# ---------------------------------------------------------------------------
# SubscriptionStatus enum
# ---------------------------------------------------------------------------

def test_subscription_status_values():
    assert SubscriptionStatus.ACTIVE == "active"
    assert SubscriptionStatus.PAST_DUE == "past_due"
    assert SubscriptionStatus.CANCELLED == "cancelled"


# ---------------------------------------------------------------------------
# BillingIntervalEnum
# ---------------------------------------------------------------------------

def test_billing_interval_values():
    assert BillingIntervalEnum.MONTHLY == "monthly"
    assert BillingIntervalEnum.ANNUAL == "annual"


# ---------------------------------------------------------------------------
# SubscriptionResponse
# ---------------------------------------------------------------------------

def test_subscription_response_minimal_fields():
    sub = _sub_response()
    assert sub.tier == "professional"
    assert sub.billing_interval == BillingIntervalEnum.MONTHLY
    assert sub.status == SubscriptionStatus.ACTIVE
    assert sub.cancel_at_period_end is False
    assert sub.scheduled_downgrade_tier is None
    assert sub.failed_payment_count == 0
    assert sub.provider_subscription_id is None


def test_subscription_response_optional_fields():
    sub = _sub_response(
        status="past_due",
        scheduled_downgrade_tier="starter",
        cancel_at_period_end=True,
        failed_payment_count=2,
        provider_subscription_id=SUB_ID,
    )
    assert sub.status == SubscriptionStatus.PAST_DUE
    assert sub.scheduled_downgrade_tier == "starter"
    assert sub.cancel_at_period_end is True
    assert sub.failed_payment_count == 2
    assert sub.provider_subscription_id == SUB_ID


def test_subscription_response_next_renewal_amount_non_negative():
    with pytest.raises(Exception):
        _sub_response(next_renewal_amount_minor=-1)


def test_subscription_response_failed_payment_count_non_negative():
    with pytest.raises(Exception):
        _sub_response(failed_payment_count=-1)


# ---------------------------------------------------------------------------
# CreateSubscriptionRequest / Response
# ---------------------------------------------------------------------------

def test_create_subscription_request_monthly():
    req = CreateSubscriptionRequest(
        tier="professional",
        billing_interval="monthly",
        return_url="https://app.example/billing",
    )
    assert req.tier == "professional"
    assert req.billing_interval == BillingIntervalEnum.MONTHLY
    assert req.return_url.startswith("https://")


def test_create_subscription_request_annual():
    req = CreateSubscriptionRequest(
        tier="enterprise",
        billing_interval="annual",
        return_url="https://app.example/billing",
    )
    assert req.billing_interval == BillingIntervalEnum.ANNUAL


def test_create_subscription_response_no_checkout():
    resp = CreateSubscriptionResponse(
        subscription_id=SUB_ID,
        status="active",
        checkout=None,
    )
    assert resp.subscription_id == SUB_ID
    assert resp.checkout is None


def test_create_subscription_response_with_checkout():
    resp = CreateSubscriptionResponse(
        subscription_id=SUB_ID,
        status="requires_action",
        checkout={"provider": "paygateway", "client_token": "tok_1", "requires_action": True},
    )
    assert resp.checkout is not None
    assert resp.checkout.client_token == "tok_1"


# ---------------------------------------------------------------------------
# UpgradeSubscriptionRequest / Response
# ---------------------------------------------------------------------------

def test_upgrade_subscription_request():
    req = UpgradeSubscriptionRequest(tier="enterprise")
    assert req.tier == "enterprise"


def test_upgrade_subscription_response():
    resp = UpgradeSubscriptionResponse(
        subscription_id=SUB_ID,
        previous_tier="professional",
        new_tier="enterprise",
        proration_amount_minor=2500,
        currency="EGP",
        status="active",
    )
    assert resp.proration_amount_minor == 2500
    assert resp.status == SubscriptionStatus.ACTIVE


def test_upgrade_response_proration_non_negative():
    with pytest.raises(Exception):
        UpgradeSubscriptionResponse(
            subscription_id=SUB_ID,
            previous_tier="professional",
            new_tier="enterprise",
            proration_amount_minor=-1,
            currency="EGP",
            status="active",
        )


# ---------------------------------------------------------------------------
# DowngradeScheduleRequest / Response
# ---------------------------------------------------------------------------

def test_downgrade_schedule_request():
    req = DowngradeScheduleRequest(tier="starter")
    assert req.tier == "starter"


def test_downgrade_schedule_response_with_date():
    resp = DowngradeScheduleResponse(
        subscription_id=SUB_ID,
        current_tier="professional",
        scheduled_downgrade_tier="starter",
        effective_date=NOW,
    )
    assert resp.scheduled_downgrade_tier == "starter"
    assert resp.effective_date is not None


def test_downgrade_schedule_response_no_tier():
    resp = DowngradeScheduleResponse(
        subscription_id=SUB_ID,
        current_tier="professional",
        scheduled_downgrade_tier=None,
    )
    assert resp.scheduled_downgrade_tier is None
    assert resp.effective_date is None


# ---------------------------------------------------------------------------
# CancelSubscriptionResponse
# ---------------------------------------------------------------------------

def test_cancel_subscription_response():
    resp = CancelSubscriptionResponse(
        subscription_id=SUB_ID,
        tier="professional",
        cancel_at_period_end=True,
        period_end=NOW,
    )
    assert resp.cancel_at_period_end is True


# ---------------------------------------------------------------------------
# ReactivateSubscriptionResponse
# ---------------------------------------------------------------------------

def test_reactivate_subscription_response():
    resp = ReactivateSubscriptionResponse(
        subscription_id=SUB_ID,
        tier="professional",
        cancel_at_period_end=False,
        next_renewal_date=NOW,
    )
    assert resp.cancel_at_period_end is False


# ---------------------------------------------------------------------------
# PortalUrlRequest / Response
# ---------------------------------------------------------------------------

def test_portal_url_request():
    req = PortalUrlRequest(return_url="https://app.example/billing")
    assert "billing" in req.return_url


def test_portal_url_response():
    resp = PortalUrlResponse(
        portal_url="https://billing.stripe.com/session/xxx",
        expires_at=NOW,
    )
    assert resp.portal_url.startswith("https://billing.stripe.com")


# ---------------------------------------------------------------------------
# SubscriptionWebhookRequest / Response
# ---------------------------------------------------------------------------

def test_webhook_request_invoice_paid():
    req = SubscriptionWebhookRequest(
        event_id="evt_1",
        event_type="invoice.paid",
        subscription_id=SUB_ID,
        invoice_id="in_1",
        amount_paid_minor=490000,
        currency="EGP",
        period_start=NOW,
        period_end=NOW,
    )
    assert req.event_type == "invoice.paid"
    assert req.invoice_id == "in_1"
    assert req.amount_paid_minor == 490000


def test_webhook_request_minimal_fields():
    req = SubscriptionWebhookRequest(
        event_id="evt_2",
        event_type="customer.subscription.deleted",
        subscription_id=SUB_ID,
    )
    assert req.invoice_id is None
    assert req.amount_paid_minor is None
    assert req.metadata == {}


def test_webhook_request_with_metadata():
    req = SubscriptionWebhookRequest(
        event_id="evt_3",
        event_type="customer.subscription.updated",
        subscription_id=SUB_ID,
        metadata={"org_id": "44444444-4444-4444-4444-444444444444"},
    )
    assert req.metadata["org_id"] == "44444444-4444-4444-4444-444444444444"


def test_webhook_response():
    resp = SubscriptionWebhookResponse(received=True, event_type="invoice.paid")
    assert resp.received is True
    assert resp.event_type == "invoice.paid"

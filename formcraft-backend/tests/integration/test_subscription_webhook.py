"""Integration tests for the F059 subscription-webhook endpoint.

Tests HMAC validation, event dispatch, idempotency, and dunning.
"""
import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app

NOW = datetime.now(timezone.utc)
SUB_ID = "sub_1ABCDEFabcdef"
ORG_ID = "44444444-4444-4444-4444-444444444444"
VALID_SIG = "valid-signature"

_BILLING_PATCH = "app.api.routes.billing.get_supabase_client"


def _body(event_type: str = "invoice.paid", **kwargs) -> dict:
    defaults = {
        "event_id": "evt_001",
        "event_type": event_type,
        "subscription_id": SUB_ID,
        "invoice_id": "in_001",
        "amount_paid_minor": 490000,
        "currency": "EGP",
        "period_start": NOW.isoformat(),
        "period_end": NOW.isoformat(),
        "metadata": {"org_id": ORG_ID},
    }
    return {**defaults, **kwargs}


def _post(body: dict, *, signature: str | None = VALID_SIG):
    headers = {"Content-Type": "application/json"}
    if signature is not None:
        headers["X-PayGateway-Signature"] = signature
    return TestClient(app).post(
        "/api/billing/paygateway/subscription-webhook",
        content=json.dumps(body),
        headers=headers,
    )


def _valid_sig():
    return patch(
        "app.api.routes.billing.PayGatewayClient.verify_webhook_signature",
        return_value=True,
    )


def _invalid_sig():
    return patch(
        "app.api.routes.billing.PayGatewayClient.verify_webhook_signature",
        return_value=False,
    )


def _mock_supa():
    return patch(_BILLING_PATCH, return_value=MagicMock())


# ---------------------------------------------------------------------------
# HMAC signature verification
# ---------------------------------------------------------------------------

def test_webhook_rejects_invalid_signature():
    with _invalid_sig(), _mock_supa():
        resp = _post(_body(), signature="bad-sig")
    assert resp.status_code == 401


def test_webhook_rejects_missing_signature():
    with _invalid_sig(), _mock_supa():
        resp = _post(_body(), signature=None)
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# invoice.paid → handle_invoice_paid
# ---------------------------------------------------------------------------

def test_invoice_paid_dispatches_to_handle_invoice_paid():
    mock_handler = AsyncMock()
    with (
        _valid_sig(),
        _mock_supa(),
        patch("app.api.routes.billing.SubscriptionService.handle_invoice_paid", mock_handler),
    ):
        resp = _post(_body("invoice.paid"))

    assert resp.status_code == 200
    assert resp.json()["received"] is True
    mock_handler.assert_awaited_once()
    called_event = mock_handler.call_args[0][0]
    assert called_event["event_type"] == "invoice.paid"
    assert called_event["invoice_id"] == "in_001"


def test_invoice_paid_idempotent_replay():
    """Same invoice_id delivered twice — both should succeed (idempotency handled inside service)."""
    mock_handler = AsyncMock()
    with (
        _valid_sig(),
        _mock_supa(),
        patch("app.api.routes.billing.SubscriptionService.handle_invoice_paid", mock_handler),
    ):
        r1 = _post(_body("invoice.paid"))
        r2 = _post(_body("invoice.paid"))

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert mock_handler.await_count == 2  # route calls handler; service de-dupes internally


# ---------------------------------------------------------------------------
# invoice.payment_failed → handle_payment_failed
# ---------------------------------------------------------------------------

def test_payment_failed_dispatches_to_handle_payment_failed():
    mock_handler = AsyncMock()
    body = _body("invoice.payment_failed", invoice_id="in_fail_001", amount_paid_minor=None)
    with (
        _valid_sig(),
        _mock_supa(),
        patch("app.api.routes.billing.SubscriptionService.handle_payment_failed", mock_handler),
    ):
        resp = _post(body)

    assert resp.status_code == 200
    mock_handler.assert_awaited_once()
    called_event = mock_handler.call_args[0][0]
    assert called_event["event_type"] == "invoice.payment_failed"


def test_payment_failed_dunning_exhaustion_still_returns_200():
    """Even when dunning downgrades the org, the webhook must ack 200."""
    mock_handler = AsyncMock()
    body = _body("invoice.payment_failed", invoice_id="in_fail_003")
    with (
        _valid_sig(),
        _mock_supa(),
        patch("app.api.routes.billing.SubscriptionService.handle_payment_failed", mock_handler),
    ):
        resp = _post(body)

    assert resp.status_code == 200
    assert resp.json()["received"] is True


# ---------------------------------------------------------------------------
# customer.subscription.updated → handle_subscription_updated
# ---------------------------------------------------------------------------

def test_subscription_updated_dispatches_to_handle_subscription_updated():
    mock_handler = AsyncMock()
    body = _body("customer.subscription.updated", invoice_id=None, amount_paid_minor=None)
    with (
        _valid_sig(),
        _mock_supa(),
        patch("app.api.routes.billing.SubscriptionService.handle_subscription_updated", mock_handler),
    ):
        resp = _post(body)

    assert resp.status_code == 200
    mock_handler.assert_awaited_once()
    called_event = mock_handler.call_args[0][0]
    assert called_event["event_type"] == "customer.subscription.updated"


# ---------------------------------------------------------------------------
# customer.subscription.deleted → handle_subscription_deleted
# ---------------------------------------------------------------------------

def test_subscription_deleted_dispatches_to_handle_subscription_deleted():
    mock_handler = MagicMock()  # sync method
    body = _body("customer.subscription.deleted", invoice_id=None, amount_paid_minor=None)
    with (
        _valid_sig(),
        _mock_supa(),
        patch("app.api.routes.billing.SubscriptionService.handle_subscription_deleted", mock_handler),
    ):
        resp = _post(body)

    assert resp.status_code == 200
    mock_handler.assert_called_once()
    called_event = mock_handler.call_args[0][0]
    assert called_event["subscription_id"] == SUB_ID


# ---------------------------------------------------------------------------
# Unknown event type — pass-through without error
# ---------------------------------------------------------------------------

def test_unknown_event_type_returns_200_without_dispatch():
    inv_paid = AsyncMock()
    inv_failed = AsyncMock()
    body = _body("customer.subscription.trial_will_end")
    with (
        _valid_sig(),
        _mock_supa(),
        patch("app.api.routes.billing.SubscriptionService.handle_invoice_paid", inv_paid),
        patch("app.api.routes.billing.SubscriptionService.handle_payment_failed", inv_failed),
    ):
        resp = _post(body)

    assert resp.status_code == 200
    assert resp.json()["received"] is True
    inv_paid.assert_not_awaited()
    inv_failed.assert_not_awaited()


def test_completely_unknown_event_type_returns_200():
    body = _body("made.up.event")
    with _valid_sig(), _mock_supa():
        resp = _post(body)

    assert resp.status_code == 200
    assert resp.json()["received"] is True


# ---------------------------------------------------------------------------
# Response schema
# ---------------------------------------------------------------------------

def test_webhook_response_includes_event_type():
    with (
        _valid_sig(),
        _mock_supa(),
        patch("app.api.routes.billing.SubscriptionService.handle_invoice_paid", AsyncMock()),
    ):
        resp = _post(_body("invoice.paid"))

    data = resp.json()
    assert data["received"] is True
    assert data["event_type"] == "invoice.paid"

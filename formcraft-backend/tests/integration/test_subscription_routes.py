"""Integration tests for F059 subscription API endpoints.

Mocks SubscriptionService methods; tests route auth, dispatch, and response shape.
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import make_supabase_response

ORG_ID = "44444444-4444-4444-4444-444444444444"
SUB_ID = "sub_1ABCDEFabcdef"
NOW = datetime.now(timezone.utc)

_DEPS_PATCH = "app.api.deps.get_supabase_client"
_BILLING_PATCH = "app.api.routes.billing.get_supabase_client"


def _setup_profile(mock_client, profile, *, org_id=ORG_ID, platform_admin=False):
    p = dict(profile)
    p["org_id"] = str(org_id)
    p["is_platform_admin"] = platform_admin
    mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = make_supabase_response(p)


def _sub():
    return {
        "id": str(uuid4()),
        "org_id": ORG_ID,
        "tier": "professional",
        "billing_interval": "monthly",
        "status": "active",
        "current_period_start": NOW.isoformat(),
        "current_period_end": NOW.isoformat(),
        "next_renewal_amount_minor": 490000,
        "currency": "EGP",
        "scheduled_downgrade_tier": None,
        "cancel_at_period_end": False,
        "failed_payment_count": 0,
        "provider_subscription_id": SUB_ID,
    }


# ---------------------------------------------------------------------------
# GET /api/billing/subscriptions/current
# ---------------------------------------------------------------------------

def test_get_current_subscription_returns_200(valid_admin_token, admin_profile):
    mock_client = MagicMock()
    _setup_profile(mock_client, admin_profile)
    sub = _sub()

    with (
        patch(_DEPS_PATCH, return_value=mock_client),
        patch(_BILLING_PATCH, return_value=mock_client),
        patch("app.api.routes.billing.SubscriptionService.get_current_subscription", return_value=sub),
    ):
        resp = TestClient(app).get(
            "/api/billing/subscriptions/current",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
        )

    assert resp.status_code == 200
    assert resp.json()["tier"] == "professional"
    assert resp.json()["status"] == "active"


def test_get_current_subscription_returns_404_when_no_sub(valid_admin_token, admin_profile):
    mock_client = MagicMock()
    _setup_profile(mock_client, admin_profile)

    with (
        patch(_DEPS_PATCH, return_value=mock_client),
        patch(_BILLING_PATCH, return_value=mock_client),
        patch("app.api.routes.billing.SubscriptionService.get_current_subscription", return_value=None),
    ):
        resp = TestClient(app).get(
            "/api/billing/subscriptions/current",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
        )

    assert resp.status_code == 404


def test_get_current_subscription_requires_admin(valid_designer_token, designer_profile):
    mock_client = MagicMock()
    _setup_profile(mock_client, designer_profile)

    with (
        patch(_DEPS_PATCH, return_value=mock_client),
        patch(_BILLING_PATCH, return_value=mock_client),
    ):
        resp = TestClient(app).get(
            "/api/billing/subscriptions/current",
            headers={"Authorization": f"Bearer {valid_designer_token}"},
        )

    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# POST /api/billing/subscriptions
# ---------------------------------------------------------------------------

def test_create_subscription_returns_201(valid_admin_token, admin_profile):
    mock_client = MagicMock()
    _setup_profile(mock_client, admin_profile)
    result = {"subscription_id": SUB_ID, "status": "active", "checkout": None}

    with (
        patch(_DEPS_PATCH, return_value=mock_client),
        patch(_BILLING_PATCH, return_value=mock_client),
        patch("app.api.routes.billing.SubscriptionService.create_subscription", new=AsyncMock(return_value=result)),
    ):
        resp = TestClient(app).post(
            "/api/billing/subscriptions",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
            json={"tier": "professional", "billing_interval": "monthly", "return_url": "https://app/billing"},
        )

    assert resp.status_code == 201
    assert resp.json()["subscription_id"] == SUB_ID


def test_create_subscription_returns_409_when_already_active(valid_admin_token, admin_profile):
    mock_client = MagicMock()
    _setup_profile(mock_client, admin_profile)

    with (
        patch(_DEPS_PATCH, return_value=mock_client),
        patch(_BILLING_PATCH, return_value=mock_client),
        patch(
            "app.api.routes.billing.SubscriptionService.create_subscription",
            new=AsyncMock(side_effect=HTTPException(409, "billing.subscription_already_active")),
        ),
    ):
        resp = TestClient(app).post(
            "/api/billing/subscriptions",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
            json={"tier": "professional", "billing_interval": "monthly", "return_url": "https://app/billing"},
        )

    assert resp.status_code == 409


def test_create_subscription_requires_admin(valid_designer_token, designer_profile):
    mock_client = MagicMock()
    _setup_profile(mock_client, designer_profile)

    with (
        patch(_DEPS_PATCH, return_value=mock_client),
        patch(_BILLING_PATCH, return_value=mock_client),
    ):
        resp = TestClient(app).post(
            "/api/billing/subscriptions",
            headers={"Authorization": f"Bearer {valid_designer_token}"},
            json={"tier": "professional", "billing_interval": "monthly", "return_url": "https://app/billing"},
        )

    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# POST /api/billing/subscriptions/upgrade
# ---------------------------------------------------------------------------

def test_upgrade_subscription_returns_200(valid_admin_token, admin_profile):
    mock_client = MagicMock()
    _setup_profile(mock_client, admin_profile)
    result = {
        "subscription_id": SUB_ID,
        "previous_tier": "professional",
        "new_tier": "enterprise",
        "proration_amount_minor": 2500,
        "currency": "EGP",
        "status": "active",
    }

    with (
        patch(_DEPS_PATCH, return_value=mock_client),
        patch(_BILLING_PATCH, return_value=mock_client),
        patch("app.api.routes.billing.SubscriptionService.upgrade_subscription", new=AsyncMock(return_value=result)),
    ):
        resp = TestClient(app).post(
            "/api/billing/subscriptions/upgrade",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
            json={"tier": "enterprise"},
        )

    assert resp.status_code == 200
    assert resp.json()["proration_amount_minor"] == 2500
    assert resp.json()["new_tier"] == "enterprise"


def test_upgrade_subscription_returns_409_for_downgrade_attempt(valid_admin_token, admin_profile):
    mock_client = MagicMock()
    _setup_profile(mock_client, admin_profile)

    with (
        patch(_DEPS_PATCH, return_value=mock_client),
        patch(_BILLING_PATCH, return_value=mock_client),
        patch(
            "app.api.routes.billing.SubscriptionService.upgrade_subscription",
            new=AsyncMock(side_effect=HTTPException(409, "billing.upgrade_requires_higher_tier")),
        ),
    ):
        resp = TestClient(app).post(
            "/api/billing/subscriptions/upgrade",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
            json={"tier": "starter"},
        )

    assert resp.status_code == 409


def test_upgrade_subscription_returns_404_when_no_sub(valid_admin_token, admin_profile):
    mock_client = MagicMock()
    _setup_profile(mock_client, admin_profile)

    with (
        patch(_DEPS_PATCH, return_value=mock_client),
        patch(_BILLING_PATCH, return_value=mock_client),
        patch(
            "app.api.routes.billing.SubscriptionService.upgrade_subscription",
            new=AsyncMock(side_effect=HTTPException(404, "billing.subscription_not_found")),
        ),
    ):
        resp = TestClient(app).post(
            "/api/billing/subscriptions/upgrade",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
            json={"tier": "enterprise"},
        )

    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/billing/subscriptions/downgrade-schedule
# ---------------------------------------------------------------------------

def test_schedule_downgrade_returns_200(valid_admin_token, admin_profile):
    mock_client = MagicMock()
    _setup_profile(mock_client, admin_profile)
    result = {
        "subscription_id": SUB_ID,
        "current_tier": "professional",
        "scheduled_downgrade_tier": "starter",
        "effective_date": NOW.isoformat(),
    }

    with (
        patch(_DEPS_PATCH, return_value=mock_client),
        patch(_BILLING_PATCH, return_value=mock_client),
        patch("app.api.routes.billing.SubscriptionService.schedule_downgrade", return_value=result),
    ):
        resp = TestClient(app).post(
            "/api/billing/subscriptions/downgrade-schedule",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
            json={"tier": "starter"},
        )

    assert resp.status_code == 200
    assert resp.json()["scheduled_downgrade_tier"] == "starter"


def test_schedule_downgrade_returns_409_for_higher_tier(valid_admin_token, admin_profile):
    mock_client = MagicMock()
    _setup_profile(mock_client, admin_profile)

    with (
        patch(_DEPS_PATCH, return_value=mock_client),
        patch(_BILLING_PATCH, return_value=mock_client),
        patch(
            "app.api.routes.billing.SubscriptionService.schedule_downgrade",
            side_effect=HTTPException(409, "billing.downgrade_requires_lower_tier"),
        ),
    ):
        resp = TestClient(app).post(
            "/api/billing/subscriptions/downgrade-schedule",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
            json={"tier": "enterprise"},
        )

    assert resp.status_code == 409


# ---------------------------------------------------------------------------
# DELETE /api/billing/subscriptions/downgrade-schedule
# ---------------------------------------------------------------------------

def test_cancel_downgrade_schedule_returns_200(valid_admin_token, admin_profile):
    mock_client = MagicMock()
    _setup_profile(mock_client, admin_profile)
    result = {
        "subscription_id": SUB_ID,
        "current_tier": "professional",
        "scheduled_downgrade_tier": None,
        "effective_date": None,
    }

    with (
        patch(_DEPS_PATCH, return_value=mock_client),
        patch(_BILLING_PATCH, return_value=mock_client),
        patch("app.api.routes.billing.SubscriptionService.cancel_downgrade_schedule", return_value=result),
    ):
        resp = TestClient(app).delete(
            "/api/billing/subscriptions/downgrade-schedule",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
        )

    assert resp.status_code == 200
    assert resp.json()["scheduled_downgrade_tier"] is None


def test_cancel_downgrade_schedule_returns_409_when_none_scheduled(valid_admin_token, admin_profile):
    mock_client = MagicMock()
    _setup_profile(mock_client, admin_profile)

    with (
        patch(_DEPS_PATCH, return_value=mock_client),
        patch(_BILLING_PATCH, return_value=mock_client),
        patch(
            "app.api.routes.billing.SubscriptionService.cancel_downgrade_schedule",
            side_effect=HTTPException(409, "billing.no_downgrade_scheduled"),
        ),
    ):
        resp = TestClient(app).delete(
            "/api/billing/subscriptions/downgrade-schedule",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
        )

    assert resp.status_code == 409


# ---------------------------------------------------------------------------
# POST /api/billing/subscriptions/cancel
# ---------------------------------------------------------------------------

def test_cancel_subscription_returns_200(valid_admin_token, admin_profile):
    mock_client = MagicMock()
    _setup_profile(mock_client, admin_profile)
    result = {
        "subscription_id": SUB_ID,
        "tier": "professional",
        "cancel_at_period_end": True,
        "period_end": NOW.isoformat(),
    }

    with (
        patch(_DEPS_PATCH, return_value=mock_client),
        patch(_BILLING_PATCH, return_value=mock_client),
        patch("app.api.routes.billing.SubscriptionService.cancel_subscription", new=AsyncMock(return_value=result)),
    ):
        resp = TestClient(app).post(
            "/api/billing/subscriptions/cancel",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
        )

    assert resp.status_code == 200
    assert resp.json()["cancel_at_period_end"] is True


def test_cancel_subscription_returns_409_when_already_scheduled(valid_admin_token, admin_profile):
    mock_client = MagicMock()
    _setup_profile(mock_client, admin_profile)

    with (
        patch(_DEPS_PATCH, return_value=mock_client),
        patch(_BILLING_PATCH, return_value=mock_client),
        patch(
            "app.api.routes.billing.SubscriptionService.cancel_subscription",
            new=AsyncMock(side_effect=HTTPException(409, "billing.already_scheduled_for_cancellation")),
        ),
    ):
        resp = TestClient(app).post(
            "/api/billing/subscriptions/cancel",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
        )

    assert resp.status_code == 409


# ---------------------------------------------------------------------------
# POST /api/billing/subscriptions/reactivate
# ---------------------------------------------------------------------------

def test_reactivate_subscription_returns_200(valid_admin_token, admin_profile):
    mock_client = MagicMock()
    _setup_profile(mock_client, admin_profile)
    result = {
        "subscription_id": SUB_ID,
        "tier": "professional",
        "cancel_at_period_end": False,
        "next_renewal_date": NOW.isoformat(),
    }

    with (
        patch(_DEPS_PATCH, return_value=mock_client),
        patch(_BILLING_PATCH, return_value=mock_client),
        patch("app.api.routes.billing.SubscriptionService.reactivate_subscription", new=AsyncMock(return_value=result)),
    ):
        resp = TestClient(app).post(
            "/api/billing/subscriptions/reactivate",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
        )

    assert resp.status_code == 200
    assert resp.json()["cancel_at_period_end"] is False


def test_reactivate_returns_409_when_not_scheduled_for_cancel(valid_admin_token, admin_profile):
    mock_client = MagicMock()
    _setup_profile(mock_client, admin_profile)

    with (
        patch(_DEPS_PATCH, return_value=mock_client),
        patch(_BILLING_PATCH, return_value=mock_client),
        patch(
            "app.api.routes.billing.SubscriptionService.reactivate_subscription",
            new=AsyncMock(side_effect=HTTPException(409, "billing.not_scheduled_for_cancellation")),
        ),
    ):
        resp = TestClient(app).post(
            "/api/billing/subscriptions/reactivate",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
        )

    assert resp.status_code == 409


def test_reactivate_returns_409_when_period_already_ended(valid_admin_token, admin_profile):
    mock_client = MagicMock()
    _setup_profile(mock_client, admin_profile)

    with (
        patch(_DEPS_PATCH, return_value=mock_client),
        patch(_BILLING_PATCH, return_value=mock_client),
        patch(
            "app.api.routes.billing.SubscriptionService.reactivate_subscription",
            new=AsyncMock(side_effect=HTTPException(409, "billing.subscription_period_ended")),
        ),
    ):
        resp = TestClient(app).post(
            "/api/billing/subscriptions/reactivate",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
        )

    assert resp.status_code == 409


# ---------------------------------------------------------------------------
# POST /api/billing/subscriptions/portal-url
# ---------------------------------------------------------------------------

def test_portal_url_returns_200_when_past_due(valid_admin_token, admin_profile):
    mock_client = MagicMock()
    _setup_profile(mock_client, admin_profile)
    result = {
        "portal_url": "https://billing.stripe.com/session/xyz",
        "expires_at": NOW.isoformat(),
    }

    with (
        patch(_DEPS_PATCH, return_value=mock_client),
        patch(_BILLING_PATCH, return_value=mock_client),
        patch("app.api.routes.billing.SubscriptionService.get_portal_url", new=AsyncMock(return_value=result)),
    ):
        resp = TestClient(app).post(
            "/api/billing/subscriptions/portal-url",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
            json={"return_url": "https://app/billing"},
        )

    assert resp.status_code == 200
    assert "billing.stripe.com" in resp.json()["portal_url"]


def test_portal_url_returns_409_when_not_past_due(valid_admin_token, admin_profile):
    mock_client = MagicMock()
    _setup_profile(mock_client, admin_profile)

    with (
        patch(_DEPS_PATCH, return_value=mock_client),
        patch(_BILLING_PATCH, return_value=mock_client),
        patch(
            "app.api.routes.billing.SubscriptionService.get_portal_url",
            new=AsyncMock(side_effect=HTTPException(409, "billing.portal_only_for_past_due")),
        ),
    ):
        resp = TestClient(app).post(
            "/api/billing/subscriptions/portal-url",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
            json={"return_url": "https://app/billing"},
        )

    assert resp.status_code == 409

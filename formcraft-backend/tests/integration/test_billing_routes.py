from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import make_supabase_response


ORG_ID = UUID("44444444-4444-4444-4444-444444444444")


def _setup_profile_mock(mock_client, profile, *, org_id=ORG_ID, platform_admin=False):
    profile_with_org = dict(profile)
    profile_with_org["org_id"] = str(org_id) if org_id else None
    profile_with_org["is_platform_admin"] = platform_admin
    mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = make_supabase_response(profile_with_org)


def _purchase(purchase_id=None):
    return {
        "id": str(purchase_id or uuid4()),
        "organization_id": str(ORG_ID),
        "purpose": "subscription_tier",
        "target": {"tier": "professional"},
        "quantity": None,
        "amount_minor": 250000,
        "currency": "EGP",
        "status": "succeeded",
        "fulfilled_at": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def test_get_billing_options(valid_admin_token, admin_profile):
    mock_client = MagicMock()
    _setup_profile_mock(mock_client, admin_profile)

    with (
        patch("app.api.deps.get_supabase_client", return_value=mock_client),
        patch("app.api.routes.billing.get_supabase_client", return_value=mock_client),
        patch(
            "app.api.routes.billing.BillingService.get_options",
            new=AsyncMock(return_value={"currency": "EGP", "current_tier": "starter", "tiers": [], "addons": []}),
        ),
    ):
        response = TestClient(app).get("/api/billing/options", headers={"Authorization": f"Bearer {valid_admin_token}"})

    assert response.status_code == 200
    assert response.json()["currency"] == "EGP"


def test_get_billing_options_requires_admin(valid_designer_token, designer_profile):
    mock_client = MagicMock()
    _setup_profile_mock(mock_client, designer_profile)

    with (
        patch("app.api.deps.get_supabase_client", return_value=mock_client),
        patch("app.api.routes.billing.get_supabase_client", return_value=mock_client),
    ):
        response = TestClient(app).get("/api/billing/options", headers={"Authorization": f"Bearer {valid_designer_token}"})

    assert response.status_code == 403


def test_create_purchase_returns_checkout(valid_admin_token, admin_profile):
    purchase_id = uuid4()
    mock_client = MagicMock()
    _setup_profile_mock(mock_client, admin_profile)

    with (
        patch("app.api.deps.get_supabase_client", return_value=mock_client),
        patch("app.api.routes.billing.get_supabase_client", return_value=mock_client),
        patch(
            "app.api.routes.billing.BillingService.create_purchase",
            new=AsyncMock(
                return_value={
                    "purchase_id": purchase_id,
                    "status": "created",
                    "amount_minor": 250000,
                    "currency": "EGP",
                    "checkout": {"provider": "paygateway", "client_token": "token", "requires_action": False},
                }
            ),
        ),
    ):
        response = TestClient(app).post(
            "/api/billing/purchases",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
            json={"purpose": "subscription_tier", "target": {"tier": "professional"}},
        )

    assert response.status_code == 201
    assert response.json()["checkout"]["client_token"] == "token"


def test_list_and_get_purchase_are_org_scoped(valid_admin_token, admin_profile):
    purchase = _purchase()
    mock_client = MagicMock()
    _setup_profile_mock(mock_client, admin_profile)

    with (
        patch("app.api.deps.get_supabase_client", return_value=mock_client),
        patch("app.api.routes.billing.get_supabase_client", return_value=mock_client),
        patch("app.api.routes.billing.BillingService.list_purchases", return_value=[purchase]),
        patch("app.api.routes.billing.BillingService.get_purchase", return_value=purchase),
    ):
        client = TestClient(app)
        headers = {"Authorization": f"Bearer {valid_admin_token}"}
        list_response = client.get("/api/billing/purchases", headers=headers)
        get_response = client.get(f"/api/billing/purchases/{purchase['id']}", headers=headers)

    assert list_response.status_code == 200
    assert list_response.json()["items"][0]["id"] == purchase["id"]
    assert get_response.status_code == 200


def test_verify_purchase_for_browser_close_recovery(valid_admin_token, admin_profile):
    purchase_id = uuid4()
    mock_client = MagicMock()
    _setup_profile_mock(mock_client, admin_profile)

    with (
        patch("app.api.deps.get_supabase_client", return_value=mock_client),
        patch("app.api.routes.billing.get_supabase_client", return_value=mock_client),
        patch(
            "app.api.routes.billing.BillingService.verify_purchase",
            new=AsyncMock(return_value={"purchase_id": purchase_id, "status": "succeeded", "fulfilled": True, "message_key": "billing.purchase.fulfilled"}),
        ),
    ):
        response = TestClient(app).post(
            f"/api/billing/purchases/{purchase_id}/verify",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
            json={"provider_payment_id": "pay_1"},
        )

    assert response.status_code == 200
    assert response.json()["fulfilled"] is True

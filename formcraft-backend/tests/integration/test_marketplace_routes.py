from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import make_supabase_response


ORG_ID = UUID("44444444-4444-4444-4444-444444444444")


def _setup_profile_mock(mock_client, profile):
    profile_with_org = dict(profile)
    profile_with_org["org_id"] = str(ORG_ID)
    mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = make_supabase_response(profile_with_org)


def _listing(listing_id=None):
    return {
        "id": str(listing_id or uuid4()),
        "template_id": str(uuid4()),
        "publisher_org_id": str(uuid4()),
        "publisher_org_name": "Publisher",
        "created_by": str(uuid4()),
        "name": "Permit Template",
        "description": "Reusable permit",
        "tags": ["permit"],
        "preview_image_urls": [],
        "compliance_badges": ["VAT"],
        "category": "permits",
        "country": "AE",
        "language": "ar",
        "quality_score": 95,
        "price_type": "free",
        "price_amount": None,
        "currency": "USD",
        "status": "active",
        "review_status": "approved",
        "download_count": 2,
        "average_rating": 4.5,
        "review_count": 1,
        "published_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def test_list_marketplace_listings(valid_admin_token, admin_profile):
    token = valid_admin_token
    mock_client = MagicMock()
    _setup_profile_mock(mock_client, admin_profile)
    listing = _listing()

    with (
        patch("app.api.deps.get_supabase_client", return_value=mock_client),
        patch("app.api.routes.marketplace.get_supabase_client", return_value=mock_client),
        patch(
            "app.api.routes.marketplace.MarketplaceService.list_listings",
            new=AsyncMock(return_value=([listing], 1)),
        ),
    ):
        response = TestClient(app).get(
            "/api/marketplace/listings",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    assert response.json()["items"][0]["name"] == "Permit Template"


def test_import_marketplace_listing_requires_admin(valid_designer_token, designer_profile):
    mock_client = MagicMock()
    _setup_profile_mock(mock_client, designer_profile)

    with (
        patch("app.api.deps.get_supabase_client", return_value=mock_client),
        patch("app.api.routes.marketplace.get_supabase_client", return_value=mock_client),
    ):
        response = TestClient(app).post(
            f"/api/marketplace/listings/{uuid4()}/import",
            headers={"Authorization": f"Bearer {valid_designer_token}"},
            json={"draft_name": "Imported"},
        )

    assert response.status_code == 403


def test_purchase_marketplace_listing_returns_transaction(valid_admin_token, admin_profile):
    listing_id = uuid4()
    transaction_id = uuid4()
    mock_client = MagicMock()
    _setup_profile_mock(mock_client, admin_profile)

    with (
        patch("app.api.deps.get_supabase_client", return_value=mock_client),
        patch("app.api.routes.marketplace.get_supabase_client", return_value=mock_client),
        patch(
            "app.api.routes.marketplace.MarketplaceService.purchase_listing",
            new=AsyncMock(
                return_value={
                    "transaction_id": transaction_id,
                    "payment_status": "completed",
                    "amount": "50.00",
                    "currency": "USD",
                    "publisher_share": "35.00",
                    "platform_share": "15.00",
                }
            ),
        ),
    ):
        response = TestClient(app).post(
            f"/api/marketplace/listings/{listing_id}/purchase",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
            json={"provider": "internal", "idempotency_key": "key-1"},
        )

    assert response.status_code == 201
    assert response.json()["publisher_share"] == "35.00"


def test_create_marketplace_review(valid_admin_token, admin_profile):
    listing_id = uuid4()
    import_id = uuid4()
    review_id = uuid4()
    mock_client = MagicMock()
    _setup_profile_mock(mock_client, admin_profile)

    with (
        patch("app.api.deps.get_supabase_client", return_value=mock_client),
        patch("app.api.routes.marketplace.get_supabase_client", return_value=mock_client),
        patch(
            "app.api.routes.marketplace.MarketplaceService.create_or_update_review",
            new=AsyncMock(
                return_value={
                    "id": review_id,
                    "listing_id": listing_id,
                    "consumer_org_id": ORG_ID,
                    "reviewer_id": UUID(admin_profile["id"]),
                    "import_id": import_id,
                    "rating": 4,
                    "review_text": "Useful",
                    "verified_import": True,
                    "status": "active",
                }
            ),
        ),
    ):
        response = TestClient(app).post(
            f"/api/marketplace/listings/{listing_id}/reviews",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
            json={"import_id": str(import_id), "rating": 4, "review_text": "Useful"},
        )

    assert response.status_code == 201
    assert response.json()["verified_import"] is True


def test_moderate_marketplace_listing(valid_admin_token, admin_profile):
    listing_id = uuid4()
    listing = _listing(listing_id)
    mock_client = MagicMock()
    _setup_profile_mock(mock_client, admin_profile)

    with (
        patch("app.api.deps.get_supabase_client", return_value=mock_client),
        patch("app.api.routes.marketplace.get_supabase_client", return_value=mock_client),
        patch(
            "app.api.routes.marketplace.MarketplaceService.moderate_listing",
            new=AsyncMock(return_value=listing),
        ),
    ):
        response = TestClient(app).post(
            f"/api/admin/marketplace/listings/{listing_id}/moderation",
            headers={"Authorization": f"Bearer {valid_admin_token}"},
            json={"action": "approve", "comment": "ok"},
        )

    assert response.status_code == 200
    assert response.json()["id"] == str(listing_id)


def test_marketplace_migration_defines_required_tables():
    from pathlib import Path

    migration = Path(__file__).resolve().parents[2] / "migrations" / "037_template_marketplace.sql"
    sql = migration.read_text(encoding="utf-8")

    for table in (
        "marketplace_listings",
        "marketplace_imports",
        "marketplace_reviews",
        "marketplace_transactions",
    ):
        assert f"CREATE TABLE IF NOT EXISTS {table}" in sql
        assert f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY" in sql

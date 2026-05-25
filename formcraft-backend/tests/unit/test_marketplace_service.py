from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException

from app.services.marketplace_service import MarketplaceService
from tests.conftest import make_supabase_response


ORG_ID = UUID("44444444-4444-4444-4444-444444444444")
ACTOR_ID = UUID("11111111-1111-1111-1111-111111111111")
PUBLISHER_ORG_ID = UUID("55555555-5555-5555-5555-555555555555")


def _chain(data=None, count=None):
    chain = MagicMock()
    chain.eq.return_value = chain
    chain.ilike.return_value = chain
    chain.contains.return_value = chain
    chain.order.return_value = chain
    chain.range.return_value = chain
    chain.in_.return_value = chain
    chain.single.return_value = chain
    chain.execute.return_value = make_supabase_response(data or [], count=count)
    return chain


def _table(select_data=None, insert_data=None, update_data=None, count=None):
    table = MagicMock()
    table.select.return_value = _chain(select_data, count=count)
    table.insert.return_value = _chain(insert_data or select_data)
    table.update.return_value = _chain(update_data or select_data)
    return table


def _listing(listing_id=None, price_type="free"):
    return {
        "id": str(listing_id or uuid4()),
        "template_id": str(uuid4()),
        "publisher_org_id": str(PUBLISHER_ORG_ID),
        "created_by": str(ACTOR_ID),
        "name": "Permit Template",
        "description": "A reusable permit template",
        "tags": ["permit"],
        "preview_image_urls": [],
        "category": "permits",
        "country": "AE",
        "language": "ar",
        "compliance_badges": ["VAT"],
        "quality_score": 95,
        "price_type": price_type,
        "price_amount": "50.00" if price_type == "premium" else None,
        "currency": "USD",
        "status": "active",
        "review_status": "approved",
        "download_count": 2,
        "average_rating": 4.5,
        "review_count": 1,
        "published_version": 1,
    }


def _template(template_id=None, org_id=ORG_ID, status="published"):
    return {
        "id": str(template_id or uuid4()),
        "org_id": str(org_id),
        "created_by": str(ACTOR_ID),
        "name": "Permit Template",
        "description": "Template",
        "category": "permits",
        "country": "AE",
        "language": "ar",
        "status": status,
        "version": 3,
    }


@pytest.mark.asyncio
async def test_purchase_listing_records_70_30_revenue_share():
    listing_id = uuid4()
    listing = _listing(listing_id, price_type="premium")
    transaction_id = uuid4()
    mock_client = MagicMock()

    def table_side_effect(name):
        if name == "marketplace_listings":
            return _table(select_data=listing)
        if name == "marketplace_transactions":
            return _table(insert_data=[{"id": str(transaction_id), "payment_status": "completed"}])
        return _table()

    mock_client.table.side_effect = table_side_effect
    audit = MagicMock()
    audit.log_event = AsyncMock()

    with patch("app.services.marketplace_service.AuditLogger", return_value=audit):
        result = await MarketplaceService(mock_client).purchase_listing(
            listing_id=listing_id,
            consumer_org_id=ORG_ID,
            actor_id=ACTOR_ID,
            idempotency_key="key-1",
        )

    assert result["payment_status"] == "completed"
    assert result["publisher_share"] == Decimal("35.00")
    assert result["platform_share"] == Decimal("15.00")
    audit.log_event.assert_awaited_once()


@pytest.mark.asyncio
async def test_publish_listing_requires_published_template_owned_by_org():
    template_id = uuid4()
    mock_client = MagicMock()
    mock_client.table.return_value = _table(select_data=_template(template_id, org_id=uuid4()))

    with pytest.raises(HTTPException) as exc_info:
        await MarketplaceService(mock_client).publish_listing(
            org_id=ORG_ID,
            actor_id=ACTOR_ID,
            data={"template_id": str(template_id), "price_type": "free"},
        )

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_import_listing_requires_purchase_for_premium_listing():
    listing_id = uuid4()
    mock_client = MagicMock()

    def table_side_effect(name):
        if name == "marketplace_listings":
            return _table(select_data=_listing(listing_id, price_type="premium"))
        if name == "marketplace_transactions":
            return _table(select_data=[])
        return _table()

    mock_client.table.side_effect = table_side_effect

    with pytest.raises(HTTPException) as exc_info:
        await MarketplaceService(mock_client).import_listing(
            listing_id=listing_id,
            consumer_org_id=ORG_ID,
            actor_id=ACTOR_ID,
        )

    assert exc_info.value.status_code == 402


@pytest.mark.asyncio
async def test_dependency_warnings_detect_reference_and_custom_validator():
    service = MarketplaceService(MagicMock())
    warnings = service._dependency_warnings(
        [
            {"key": "department", "validation": {"reference_list_id": "ref-1"}},
            {"key": "legacy", "validation": {"custom_validator_id": "custom-1"}},
        ]
    )

    assert "department" in warnings[0]
    assert "legacy" in warnings[1]


@pytest.mark.asyncio
async def test_review_requires_import_from_same_listing_and_org():
    listing_id = uuid4()
    import_id = uuid4()
    mock_client = MagicMock()
    mock_client.table.return_value = _table(
        select_data={
            "id": str(import_id),
            "listing_id": str(uuid4()),
            "consumer_org_id": str(ORG_ID),
        }
    )

    with pytest.raises(HTTPException) as exc_info:
        await MarketplaceService(mock_client).create_or_update_review(
            listing_id=listing_id,
            consumer_org_id=ORG_ID,
            actor_id=ACTOR_ID,
            import_id=import_id,
            rating=4,
            review_text="Useful",
        )

    assert exc_info.value.status_code == 403

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException

from app.schemas.billing import BillingFulfillmentSource, BillingPurpose
from app.services.billing_service import BillingService
from tests.conftest import make_supabase_response


ORG_ID = UUID("44444444-4444-4444-4444-444444444444")
ACTOR_ID = UUID("11111111-1111-1111-1111-111111111111")


def _chain(data=None):
    chain = MagicMock()
    chain.eq.return_value = chain
    chain.limit.return_value = chain
    chain.single.return_value = chain
    chain.order.return_value = chain
    chain.execute.return_value = make_supabase_response(data if data is not None else [])
    return chain


def _table(select_data=None, insert_data=None, update_data=None):
    table = MagicMock()
    table.select.return_value = _chain(select_data)
    table.insert.return_value = _chain(insert_data if insert_data is not None else select_data)
    table.update.return_value = _chain(update_data if update_data is not None else select_data)
    return table


def _org(tier="starter", currency="EGP"):
    return {
        "id": str(ORG_ID),
        "subscription_tier": tier,
        "default_currency": currency,
        "purchased_seat_allowance": 0,
        "ocr_scan_credit_balance": 0,
    }


def _price(amount=1000):
    return {"unit_amount_minor": amount, "min_quantity": 1, "max_quantity": 500}


@pytest.mark.asyncio
async def test_get_options_filters_to_higher_tiers_and_marks_missing_prices():
    client = MagicMock()

    def table(name):
        if name == "organizations":
            return _table(select_data=_org(tier="starter"))
        if name == "billing_prices":
            return _table(select_data=[_price(1000)])
        return _table()

    client.table.side_effect = table

    result = await BillingService(client).get_options(org_id=ORG_ID)

    assert [item["tier"] for item in result["tiers"]] == ["professional", "enterprise", "platform"]
    assert result["currency"] == "EGP"


@pytest.mark.asyncio
async def test_create_purchase_rejects_lower_or_same_tier():
    client = MagicMock()
    client.table.return_value = _table(select_data=_org(tier="professional"))

    with pytest.raises(HTTPException) as exc_info:
        await BillingService(client).create_purchase(
            org_id=ORG_ID,
            actor_id=ACTOR_ID,
            purpose=BillingPurpose.SUBSCRIPTION_TIER,
            target={"tier": "starter"},
            quantity=None,
            return_url=None,
        )

    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_zero_amount_purchase_bypasses_paygateway_and_fulfills():
    purchase_id = uuid4()
    client = MagicMock()
    inserted = {}

    def table(name):
        table_mock = _table()
        if name == "organizations":
            return _table(select_data=_org())
        if name == "billing_prices":
            return _table(select_data=[_price(0)])
        if name == "billing_purchases":
            table_mock.insert.return_value = _chain([{"id": str(purchase_id)}])
            table_mock.select.return_value = _chain(
                {
                    "id": str(purchase_id),
                    "organization_id": str(ORG_ID),
                    "created_by": str(ACTOR_ID),
                    "purpose": "subscription_tier",
                    "target": {"tier": "professional"},
                    "quantity": None,
                    "amount_minor": 0,
                    "currency": "EGP",
                }
            )
            return table_mock
        if name == "billing_fulfillments":
            table_mock.select.return_value = _chain([])
            def insert_fulfillment(row):
                inserted["fulfillment"] = row
                return _chain([row])

            table_mock.insert.side_effect = insert_fulfillment
            return table_mock
        return table_mock

    client.table.side_effect = table
    paygateway = MagicMock()
    audit = MagicMock()
    audit.log_event = AsyncMock()

    with (
        patch("app.services.billing_service.uuid4", return_value=purchase_id),
        patch("app.services.billing_service.AuditLogger", return_value=audit),
    ):
        result = await BillingService(client, paygateway=paygateway).create_purchase(
            org_id=ORG_ID,
            actor_id=ACTOR_ID,
            purpose=BillingPurpose.SUBSCRIPTION_TIER,
            target={"tier": "professional"},
            quantity=None,
            return_url=None,
        )

    assert result["status"] == "succeeded"
    assert result["checkout"] is None
    paygateway.create_payment.assert_not_called()


def test_cross_org_purchase_access_is_hidden():
    purchase = {"id": str(uuid4()), "organization_id": str(uuid4())}

    with pytest.raises(HTTPException) as exc_info:
        BillingService._assert_org_access(purchase, ORG_ID)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_fulfill_purchase_once_returns_false_for_existing_fulfillment():
    purchase_id = uuid4()
    client = MagicMock()

    def table(name):
        if name == "billing_purchases":
            return _table(select_data={"id": str(purchase_id), "organization_id": str(ORG_ID), "purpose": "seats", "target": {}, "quantity": 1})
        if name == "billing_fulfillments":
            return _table(select_data=[{"id": str(uuid4())}])
        return _table()

    client.table.side_effect = table

    fulfilled = await BillingService(client).fulfill_purchase_once(
        purchase_id=purchase_id,
        actor_id=ACTOR_ID,
        source=BillingFulfillmentSource.STATUS_POLL,
    )

    assert fulfilled is False

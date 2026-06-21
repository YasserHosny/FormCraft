"""Unit tests for SubscriptionService — proration math, state transitions, idempotency."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException

from app.services.subscription_service import SubscriptionService
from tests.conftest import make_supabase_response


ORG_ID = UUID("55555555-5555-5555-5555-555555555555")
ACTOR_ID = UUID("11111111-1111-1111-1111-111111111111")
SUB_ID = "sub_test_123"
SUB_ROW_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _chain(data=None, count=None):
    chain = MagicMock()
    chain.select.return_value = chain
    chain.eq.return_value = chain
    chain.in_.return_value = chain
    chain.gte.return_value = chain
    chain.limit.return_value = chain
    chain.single.return_value = chain
    chain.order.return_value = chain
    chain.execute.return_value = make_supabase_response(data if data is not None else [], count=count)
    return chain


def _org(stripe_customer_id=None, currency="SAR", tier="professional"):
    return {
        "id": str(ORG_ID),
        "subscription_tier": tier,
        "default_currency": currency,
        "stripe_customer_id": stripe_customer_id,
        "purchased_seat_allowance": 0,
    }


def _sub(
    tier="professional",
    status="active",
    scheduled_downgrade=None,
    cancel_at_period_end=False,
    failed_payment_count=0,
    last_invoice_id=None,
    interval="monthly",
    days_remaining=15,
    period_days=30,
):
    now = datetime.now(UTC)
    period_start = now - timedelta(days=period_days - days_remaining)
    period_end = now + timedelta(days=days_remaining)
    return {
        "id": str(SUB_ROW_ID),
        "org_id": str(ORG_ID),
        "provider_subscription_id": SUB_ID,
        "tier": tier,
        "billing_interval": interval,
        "current_period_start": period_start.isoformat(),
        "current_period_end": period_end.isoformat(),
        "status": status,
        "next_renewal_amount_minor": 4900,
        "currency": "SAR",
        "scheduled_downgrade_tier": scheduled_downgrade,
        "cancel_at_period_end": cancel_at_period_end,
        "failed_payment_count": failed_payment_count,
        "last_invoice_id": last_invoice_id,
    }


def _price_row(tier, amount, interval="monthly", provider_price_id="price_test"):
    return {
        "id": str(uuid4()),
        "price_type": "tier",
        "target_key": tier,
        "unit_amount_minor": amount,
        "billing_interval": interval,
        "currency": "SAR",
        "is_active": True,
        "provider_price_id": provider_price_id,
    }


def _mock_client(*, sub=None, org=None, prices=None, admins=None, settings_data=None):
    """Build a minimal mock Supabase client routing table() calls."""
    client = MagicMock()

    def table(name):
        if name == "billing_subscriptions":
            return _chain([sub] if sub else [])
        if name == "organizations":
            return _chain(org or _org())
        if name == "billing_prices":
            return _chain(prices or [])
        if name == "profiles":
            return _chain(admins or [{"id": str(ACTOR_ID), "email": "admin@test.com", "full_name": "Test Admin", "role": "org_admin"}])
        if name == "org_settings":
            return _chain(settings_data or [])
        c = _chain([])
        c.insert.return_value = _chain([{}])
        c.update.return_value = _chain([{}])
        return c

    client.table.side_effect = table
    return client


# ---------------------------------------------------------------------------
# compute_proration_preview
# ---------------------------------------------------------------------------


def test_proration_both_tiers_prorated():
    """Formula: (new × days/period) − (old × days/period)."""
    # Build sub with explicit timestamps so timedelta.days truncation is stable.
    # Adding 12h buffer keeps (period_end - now).days == 15 across test execution time.
    now = datetime.now(UTC)
    sub = _sub(tier="professional")
    sub["current_period_start"] = (now - timedelta(days=15)).isoformat()
    sub["current_period_end"] = (now + timedelta(days=15, hours=12)).isoformat()

    svc = SubscriptionService(MagicMock())
    with (
        patch.object(svc, "_get_active_subscription", return_value=sub),
        patch.object(svc, "_get_org", return_value=_org()),
        patch.object(svc, "_get_price", side_effect=[
            _price_row("enterprise", 9900),    # first call: new tier
            _price_row("professional", 4900),  # second call: old tier
        ]),
    ):
        result = svc.compute_proration_preview(org_id=ORG_ID, new_tier="enterprise")
    # (9900 × 15/30) − (4900 × 15/30) = 4950 − 2450 = 2500
    assert result == 2500


def test_proration_zero_days_remaining_returns_zero():
    client = _mock_client(
        sub=_sub(tier="professional", days_remaining=0, period_days=30),
        prices=[_price_row("professional", 4900), _price_row("enterprise", 9900)],
    )
    result = SubscriptionService(client).compute_proration_preview(org_id=ORG_ID, new_tier="enterprise")
    assert result == 0


def test_proration_same_price_tiers_returns_zero():
    client = _mock_client(
        sub=_sub(tier="professional", days_remaining=10, period_days=30),
        prices=[_price_row("professional", 5000), _price_row("enterprise", 5000)],
    )
    result = SubscriptionService(client).compute_proration_preview(org_id=ORG_ID, new_tier="enterprise")
    assert result == 0


def test_proration_no_active_subscription_returns_zero():
    client = _mock_client(sub=None)
    result = SubscriptionService(client).compute_proration_preview(org_id=ORG_ID, new_tier="enterprise")
    assert result == 0


def test_proration_clamps_to_zero_for_negative_result():
    """New price lower than old price should clamp to 0, not go negative."""
    client = _mock_client(
        sub=_sub(tier="enterprise", days_remaining=10, period_days=30),
        prices=[_price_row("enterprise", 9900), _price_row("professional", 4900)],
    )
    result = SubscriptionService(client).compute_proration_preview(org_id=ORG_ID, new_tier="professional")
    assert result == 0


# ---------------------------------------------------------------------------
# get_current_subscription
# ---------------------------------------------------------------------------


def test_get_current_subscription_returns_active_row():
    sub = _sub()
    client = _mock_client(sub=sub)
    result = SubscriptionService(client).get_current_subscription(ORG_ID)
    assert result is not None
    assert result["provider_subscription_id"] == SUB_ID


def test_get_current_subscription_returns_none_when_no_row():
    client = _mock_client(sub=None)
    result = SubscriptionService(client).get_current_subscription(ORG_ID)
    assert result is None


# ---------------------------------------------------------------------------
# create_subscription
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_subscription_raises_409_when_already_active():
    client = _mock_client(sub=_sub())
    svc = SubscriptionService(client)
    with pytest.raises(HTTPException) as exc:
        await svc.create_subscription(
            org_id=ORG_ID, actor_id=ACTOR_ID,
            tier="enterprise", billing_interval="monthly",
            return_url="https://example.com/billing",
        )
    assert exc.value.status_code == 409
    assert "already_active" in exc.value.detail


@pytest.mark.asyncio
async def test_create_subscription_raises_400_for_starter_tier():
    client = _mock_client(sub=None)
    svc = SubscriptionService(client)
    with pytest.raises(HTTPException) as exc:
        await svc.create_subscription(
            org_id=ORG_ID, actor_id=ACTOR_ID,
            tier="starter", billing_interval="monthly",
            return_url="https://example.com/billing",
        )
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_create_subscription_lazily_creates_stripe_customer():
    org = _org(stripe_customer_id=None)

    client = MagicMock()
    calls = []

    def table(name):
        if name == "billing_subscriptions":
            return _chain([])
        if name == "organizations":
            c = _chain(org)
            def update_side(data):
                calls.append(("org_update", data))
                return _chain([{}])
            c.update.side_effect = update_side
            return c
        if name == "profiles":
            return _chain([{"id": str(ACTOR_ID), "email": "admin@test.com", "full_name": "Admin"}])
        if name == "billing_prices":
            return _chain([_price_row("professional", 4900, provider_price_id="price_pro_monthly")])
        return _chain([])

    client.table.side_effect = table

    paygateway = MagicMock()
    paygateway.create_customer = AsyncMock(return_value={"id": "cus_new", "email": "admin@test.com"})
    paygateway.create_subscription = AsyncMock(return_value={"id": SUB_ID, "status": "active"})

    result = await SubscriptionService(client, paygateway=paygateway).create_subscription(
        org_id=ORG_ID, actor_id=ACTOR_ID,
        tier="professional", billing_interval="monthly",
        return_url="https://example.com/billing",
    )

    paygateway.create_customer.assert_called_once_with(email="admin@test.com", name="Admin")
    paygateway.create_subscription.assert_called_once()
    # Stripe customer persisted on org
    assert any("stripe_customer_id" in str(c) for c in calls)
    assert result["subscription_id"] == SUB_ID


@pytest.mark.asyncio
async def test_create_subscription_skips_customer_creation_when_already_present():
    client = _mock_client(
        sub=None,
        org=_org(stripe_customer_id="cus_existing"),
        prices=[_price_row("professional", 4900, provider_price_id="price_pro")],
    )
    paygateway = MagicMock()
    paygateway.create_subscription = AsyncMock(return_value={"id": SUB_ID, "status": "active"})

    await SubscriptionService(client, paygateway=paygateway).create_subscription(
        org_id=ORG_ID, actor_id=ACTOR_ID,
        tier="professional", billing_interval="monthly",
        return_url="https://example.com/billing",
    )

    paygateway.create_customer.assert_not_called()


# ---------------------------------------------------------------------------
# handle_invoice_paid
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_handle_invoice_paid_creates_row_on_first_event():
    client = MagicMock()
    inserted_rows = []

    def table(name):
        if name == "billing_subscriptions":
            c = _chain([])  # no existing row
            def ins(row):
                inserted_rows.append(row)
                return _chain([{}])
            c.insert.side_effect = ins
            return c
        c = _chain([{}])
        c.update.return_value = _chain([{}])
        return c

    client.table.side_effect = table

    svc = SubscriptionService(client)
    now = datetime.now(UTC)
    await svc.handle_invoice_paid({
        "subscription_id": SUB_ID,
        "invoice_id": "in_001",
        "amount_paid_minor": 4900,
        "currency": "SAR",
        "period_start": now.isoformat(),
        "period_end": (now + timedelta(days=30)).isoformat(),
        "billing_interval": "monthly",
        "metadata": {"org_id": str(ORG_ID), "tier": "professional"},
    })

    assert any(r.get("provider_subscription_id") == SUB_ID for r in inserted_rows)
    assert inserted_rows[0]["status"] == "active"
    assert inserted_rows[0]["failed_payment_count"] == 0


@pytest.mark.asyncio
async def test_handle_invoice_paid_idempotent_on_duplicate_invoice():
    """Replaying the same invoice_id must NOT update the row."""
    sub = _sub(last_invoice_id="in_001")
    client = MagicMock()
    updated = []

    def table(name):
        if name == "billing_subscriptions":
            c = _chain([sub])
            def upd(data):
                updated.append(data)
                return _chain([{}])
            c.update.side_effect = upd
            return c
        return _chain([{}])

    client.table.side_effect = table
    svc = SubscriptionService(client)
    await svc.handle_invoice_paid({"subscription_id": SUB_ID, "invoice_id": "in_001"})

    assert updated == []  # no state change on replay


@pytest.mark.asyncio
async def test_handle_invoice_paid_applies_scheduled_downgrade():
    sub = _sub(tier="enterprise", scheduled_downgrade="professional")
    client = MagicMock()
    org_tier_updates = []

    def table(name):
        if name == "billing_subscriptions":
            c = _chain([sub])
            c.update.return_value = _chain([{}])
            return c
        if name == "organizations":
            c = _chain([_org(tier="enterprise")])
            def upd(data):
                org_tier_updates.append(data)
                return _chain([{}])
            c.update.side_effect = upd
            return c
        c = _chain([{}])
        c.insert.return_value = _chain([{}])
        c.update.return_value = _chain([{}])
        return c

    client.table.side_effect = table
    now = datetime.now(UTC)
    await SubscriptionService(client).handle_invoice_paid({
        "subscription_id": SUB_ID,
        "invoice_id": "in_002",
        "amount_paid_minor": 4900,
        "currency": "SAR",
        "period_start": now.isoformat(),
        "period_end": (now + timedelta(days=30)).isoformat(),
        "metadata": {},
    })

    # Org tier downgraded to professional
    assert any(u.get("subscription_tier") == "professional" for u in org_tier_updates)


# ---------------------------------------------------------------------------
# upgrade_subscription
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_upgrade_raises_409_when_new_tier_is_lower():
    client = _mock_client(sub=_sub(tier="enterprise"))
    with pytest.raises(HTTPException) as exc:
        await SubscriptionService(client).upgrade_subscription(org_id=ORG_ID, new_tier="professional")
    assert exc.value.status_code == 409
    assert "downgrade" in exc.value.detail


@pytest.mark.asyncio
async def test_upgrade_raises_404_when_no_subscription():
    client = _mock_client(sub=None)
    with pytest.raises(HTTPException) as exc:
        await SubscriptionService(client).upgrade_subscription(org_id=ORG_ID, new_tier="enterprise")
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_upgrade_clears_scheduled_downgrade():
    client = MagicMock()
    sub_updates = []

    def table(name):
        if name == "billing_subscriptions":
            c = _chain([_sub(tier="enterprise", scheduled_downgrade="professional")])
            def upd(data):
                sub_updates.append(data)
                return _chain([{}])
            c.update.side_effect = upd
            return c
        if name == "organizations":
            c = _chain(_org(tier="enterprise"))
            c.update.return_value = _chain([{}])
            return c
        if name == "billing_prices":
            return _chain([_price_row("platform", 19900, provider_price_id="price_platform")])
        return _chain([{}])

    client.table.side_effect = table
    paygateway = MagicMock()
    paygateway.upgrade_subscription = AsyncMock(return_value={"status": "active"})

    await SubscriptionService(client, paygateway=paygateway).upgrade_subscription(
        org_id=ORG_ID, new_tier="platform"
    )

    assert any(u.get("scheduled_downgrade_tier") is None for u in sub_updates)


# ---------------------------------------------------------------------------
# schedule_downgrade / cancel_downgrade_schedule
# ---------------------------------------------------------------------------


def test_schedule_downgrade_sets_field():
    client = MagicMock()
    update_calls = []

    def table(name):
        if name == "billing_subscriptions":
            c = _chain([_sub(tier="enterprise")])
            def upd(data):
                update_calls.append(data)
                return _chain([{}])
            c.update.side_effect = upd
            return c
        return _chain([{}])

    client.table.side_effect = table
    result = SubscriptionService(client).schedule_downgrade(org_id=ORG_ID, new_tier="professional")

    assert result["scheduled_downgrade_tier"] == "professional"
    assert any(u.get("scheduled_downgrade_tier") == "professional" for u in update_calls)


def test_schedule_downgrade_raises_409_for_higher_tier():
    client = _mock_client(sub=_sub(tier="professional"))
    with pytest.raises(HTTPException) as exc:
        SubscriptionService(client).schedule_downgrade(org_id=ORG_ID, new_tier="enterprise")
    assert exc.value.status_code == 409


def test_cancel_downgrade_schedule_raises_409_when_none_scheduled():
    client = _mock_client(sub=_sub(scheduled_downgrade=None))
    with pytest.raises(HTTPException) as exc:
        SubscriptionService(client).cancel_downgrade_schedule(ORG_ID)
    assert exc.value.status_code == 409
    assert "no_downgrade" in exc.value.detail


def test_cancel_downgrade_schedule_clears_field():
    client = MagicMock()
    update_calls = []

    def table(name):
        if name == "billing_subscriptions":
            c = _chain([_sub(scheduled_downgrade="professional")])
            def upd(data):
                update_calls.append(data)
                return _chain([{}])
            c.update.side_effect = upd
            return c
        return _chain([{}])

    client.table.side_effect = table
    result = SubscriptionService(client).cancel_downgrade_schedule(ORG_ID)

    assert result["scheduled_downgrade_tier"] is None


# ---------------------------------------------------------------------------
# cancel_subscription / reactivate_subscription
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cancel_raises_409_when_already_scheduled():
    client = _mock_client(sub=_sub(cancel_at_period_end=True))
    with pytest.raises(HTTPException) as exc:
        await SubscriptionService(client).cancel_subscription(ORG_ID)
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_cancel_sets_cancel_at_period_end():
    client = MagicMock()
    update_calls = []

    def table(name):
        if name == "billing_subscriptions":
            c = _chain([_sub(cancel_at_period_end=False)])
            def upd(data):
                update_calls.append(data)
                return _chain([{}])
            c.update.side_effect = upd
            return c
        return _chain([{}])

    client.table.side_effect = table
    paygateway = MagicMock()
    paygateway.cancel_subscription = AsyncMock(return_value={})

    result = await SubscriptionService(client, paygateway=paygateway).cancel_subscription(ORG_ID)

    assert result["cancel_at_period_end"] is True
    assert any(u.get("cancel_at_period_end") is True for u in update_calls)


@pytest.mark.asyncio
async def test_reactivate_raises_409_when_period_already_ended():
    past_sub = _sub(cancel_at_period_end=True, days_remaining=-5)
    # Manually set period_end to the past
    past_sub["current_period_end"] = (datetime.now(UTC) - timedelta(days=5)).isoformat()
    client = _mock_client(sub=past_sub)
    with pytest.raises(HTTPException) as exc:
        await SubscriptionService(client).reactivate_subscription(ORG_ID)
    assert exc.value.status_code == 409
    assert "expired" in exc.value.detail


@pytest.mark.asyncio
async def test_reactivate_raises_409_when_not_scheduled_for_cancel():
    client = _mock_client(sub=_sub(cancel_at_period_end=False))
    with pytest.raises(HTTPException) as exc:
        await SubscriptionService(client).reactivate_subscription(ORG_ID)
    assert exc.value.status_code == 409
    assert "not_cancelling" in exc.value.detail


# ---------------------------------------------------------------------------
# handle_payment_failed / dunning
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_payment_failed_increments_count_and_sets_past_due():
    sub = _sub(status="active", failed_payment_count=0, last_invoice_id=None)
    client = MagicMock()
    update_calls = []

    def table(name):
        if name == "billing_subscriptions":
            c = _chain([sub])
            def upd(data):
                update_calls.append(data)
                return _chain([{}])
            c.update.side_effect = upd
            return c
        if name == "org_settings":
            return _chain([])  # default threshold = 3
        if name == "profiles":
            return _chain([{"id": str(ACTOR_ID)}])
        c = _chain([{}])
        c.insert.return_value = _chain([{}])
        return c

    client.table.side_effect = table
    svc = SubscriptionService(client)
    await svc.handle_payment_failed({"subscription_id": SUB_ID, "invoice_id": "in_fail_001"})

    status_update = next((u for u in update_calls if "failed_payment_count" in u), None)
    assert status_update is not None
    assert status_update["failed_payment_count"] == 1
    assert status_update["status"] == "past_due"


@pytest.mark.asyncio
async def test_payment_failed_idempotent_on_same_invoice():
    """Same invoice_id must not increment the count twice."""
    sub = _sub(status="past_due", failed_payment_count=1, last_invoice_id="in_fail_001")
    client = MagicMock()
    update_calls = []

    def table(name):
        if name == "billing_subscriptions":
            c = _chain([sub])
            def upd(data):
                update_calls.append(data)
                return _chain([{}])
            c.update.side_effect = upd
            return c
        return _chain([])

    client.table.side_effect = table
    svc = SubscriptionService(client)
    await svc.handle_payment_failed({"subscription_id": SUB_ID, "invoice_id": "in_fail_001"})

    assert update_calls == []  # idempotent — no changes


@pytest.mark.asyncio
async def test_dunning_exhaustion_downgrades_org_to_starter():
    """After N=3 consecutive failures, org must be set to Starter."""
    sub = _sub(status="past_due", failed_payment_count=2, last_invoice_id="in_fail_002")
    client = MagicMock()
    org_updates = []
    sub_updates = []
    audit_written = []

    def table(name):
        if name == "billing_subscriptions":
            c = _chain([sub])
            def upd(data):
                sub_updates.append(data)
                return _chain([{}])
            c.update.side_effect = upd
            return c
        if name == "organizations":
            c = _chain([_org(tier="professional")])
            def upd(data):
                org_updates.append(data)
                return _chain([{}])
            c.update.side_effect = upd
            return c
        if name == "org_settings":
            return _chain([])  # default threshold = 3
        if name == "audit_logs":
            c = _chain([{}])
            def ins(data):
                audit_written.append(data)
                return _chain([{}])
            c.insert.side_effect = ins
            return c
        c = _chain([{}])
        c.insert.return_value = _chain([{}])
        return c

    client.table.side_effect = table

    with patch("app.services.subscription_service.AuditLogger") as mock_audit_cls:
        audit_instance = MagicMock()
        audit_instance.log_event = AsyncMock()
        mock_audit_cls.return_value = audit_instance

        await SubscriptionService(client).handle_payment_failed({
            "subscription_id": SUB_ID,
            "invoice_id": "in_fail_003",
        })

    # Org downgraded to Starter
    assert any(u.get("subscription_tier") == "starter" for u in org_updates)
    # Subscription cancelled
    assert any(u.get("status") == "cancelled" for u in sub_updates)
    # Audit log written
    audit_instance.log_event.assert_called_once()
    call_kwargs = audit_instance.log_event.call_args.kwargs
    assert call_kwargs["action"] == "billing.subscription.dunning_downgrade"


@pytest.mark.asyncio
async def test_dunning_threshold_read_from_org_settings():
    """If org_settings sets threshold=1, first failure triggers downgrade."""
    sub = _sub(status="active", failed_payment_count=0, last_invoice_id=None)
    client = MagicMock()
    org_updates = []

    def table(name):
        if name == "billing_subscriptions":
            c = _chain([sub])
            c.update.return_value = _chain([{}])
            return c
        if name == "organizations":
            c = _chain([_org(tier="professional")])
            def upd(data):
                org_updates.append(data)
                return _chain([{}])
            c.update.side_effect = upd
            return c
        if name == "org_settings":
            return _chain([{"value": "1"}])  # threshold = 1
        c = _chain([{}])
        c.insert.return_value = _chain([{}])
        return c

    client.table.side_effect = table

    with patch("app.services.subscription_service.AuditLogger") as mock_audit_cls:
        audit_instance = MagicMock()
        audit_instance.log_event = AsyncMock()
        mock_audit_cls.return_value = audit_instance

        await SubscriptionService(client).handle_payment_failed({
            "subscription_id": SUB_ID,
            "invoice_id": "in_fail_001",
        })

    assert any(u.get("subscription_tier") == "starter" for u in org_updates)


# ---------------------------------------------------------------------------
# handle_invoice_paid resets failed_payment_count
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_invoice_paid_resets_failed_payment_count():
    sub = _sub(status="past_due", failed_payment_count=2, last_invoice_id="in_fail_002")
    client = MagicMock()
    sub_updates = []

    def table(name):
        if name == "billing_subscriptions":
            c = _chain([sub])
            def upd(data):
                sub_updates.append(data)
                return _chain([{}])
            c.update.side_effect = upd
            return c
        c = _chain([{}])
        c.update.return_value = _chain([{}])
        c.insert.return_value = _chain([{}])
        return c

    client.table.side_effect = table
    now = datetime.now(UTC)
    await SubscriptionService(client).handle_invoice_paid({
        "subscription_id": SUB_ID,
        "invoice_id": "in_renewal_003",
        "amount_paid_minor": 4900,
        "currency": "SAR",
        "period_start": now.isoformat(),
        "period_end": (now + timedelta(days=30)).isoformat(),
        "metadata": {},
    })

    assert any(u.get("failed_payment_count") == 0 for u in sub_updates)
    assert any(u.get("status") == "active" for u in sub_updates)


# ---------------------------------------------------------------------------
# get_portal_url
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_portal_url_raises_409_when_not_past_due():
    client = _mock_client(sub=_sub(status="active"), org=_org(stripe_customer_id="cus_123"))
    with pytest.raises(HTTPException) as exc:
        await SubscriptionService(client).get_portal_url(org_id=ORG_ID, return_url="https://example.com")
    assert exc.value.status_code == 409
    assert "not_past_due" in exc.value.detail


@pytest.mark.asyncio
async def test_portal_url_returns_url_when_past_due():
    client = _mock_client(sub=_sub(status="past_due"), org=_org(stripe_customer_id="cus_123"))
    paygateway = MagicMock()
    paygateway.get_portal_url = AsyncMock(return_value={
        "portal_url": "https://billing.stripe.com/session/test",
        "expires_at": "2026-06-21T12:00:00Z",
    })

    result = await SubscriptionService(client, paygateway=paygateway).get_portal_url(
        org_id=ORG_ID, return_url="https://app.example/billing"
    )

    assert result["portal_url"] == "https://billing.stripe.com/session/test"
    paygateway.get_portal_url.assert_called_once_with(
        customer_id="cus_123", return_url="https://app.example/billing"
    )

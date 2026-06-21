# Data Model: 059 Recurring Subscription Billing

**Branch**: `059-recurring-billing` | **Migration**: `051_recurring_billing.sql`

---

## New Table: `billing_subscriptions`

Tracks the single active recurring subscription per organisation.

```sql
CREATE TABLE public.billing_subscriptions (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id                  UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    provider_subscription_id TEXT NOT NULL UNIQUE,   -- Stripe subscription ID, e.g. sub_...
    tier                    TEXT NOT NULL,            -- current tier: starter | professional | enterprise | platform
    billing_interval        billing_interval NOT NULL CHECK (billing_interval IN ('monthly', 'annual')),
    current_period_start    TIMESTAMPTZ NOT NULL,
    current_period_end      TIMESTAMPTZ NOT NULL,
    status                  TEXT NOT NULL DEFAULT 'active'
                            CHECK (status IN ('active', 'past_due', 'cancelled')),
    scheduled_downgrade_tier TEXT
                            CHECK (scheduled_downgrade_tier IN ('starter', 'professional', 'enterprise', 'platform')),
    failed_payment_count    INTEGER NOT NULL DEFAULT 0 CHECK (failed_payment_count >= 0),
    last_invoice_id         TEXT,                    -- idempotency: last processed Stripe invoice ID
    next_renewal_amount_minor INTEGER NOT NULL CHECK (next_renewal_amount_minor >= 0),
    currency                CHAR(3) NOT NULL,
    cancel_at_period_end    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by              UUID REFERENCES public.profiles(id)
);

-- Enforces one active/past_due subscription per org.
-- Cancelled subscriptions remain as historical records.
CREATE UNIQUE INDEX billing_subscriptions_one_active_per_org
ON public.billing_subscriptions (org_id)
WHERE status IN ('active', 'past_due');

CREATE INDEX billing_subscriptions_org_idx
ON public.billing_subscriptions (org_id, created_at DESC);

CREATE INDEX billing_subscriptions_provider_idx
ON public.billing_subscriptions (provider_subscription_id);
```

**RLS**: Enabled. Org admin and platform admin can SELECT/UPDATE; INSERT allowed for service role only.

> **Creation timing**: The `billing_subscriptions` row is inserted only when the first `invoice.paid` event is received (confirming successful payment, including 3DS completion). The Stripe Subscription is created in Stripe before this row exists; the pending state is tracked in `billing_purchases` (F058 pattern). The `status` CHECK constraint (`active | past_due | cancelled`) intentionally excludes `requires_action` — that transient state lives in the payment intent, not here.

---

## Table Extensions

### `billing_prices` — add `provider_price_id`

```sql
ALTER TABLE public.billing_prices
ADD COLUMN IF NOT EXISTS provider_price_id TEXT;
```

Links each `(price_type='tier', billing_interval='monthly'|'annual')` row to the corresponding Stripe Price object (`price_...`). Seeded per environment (test/production). `NULL` for one-off / add-on prices that don't use subscriptions.

### `organizations` — add `stripe_customer_id`

```sql
ALTER TABLE public.organizations
ADD COLUMN IF NOT EXISTS stripe_customer_id TEXT;
```

Created lazily on first subscription via `POST /api/v1/customers` in PayGateway. Stored here so subsequent subscriptions reuse the same Stripe Customer.

---

## State Machine: `billing_subscriptions.status`

```
           ┌──────────────────────────┐
  (create) │                          │ (invoice.paid on renewal
           ▼                          │  with scheduled_downgrade_tier)
        ┌──────┐                      │
        │active│◄─────────────────────┤
        └──┬───┘                      │
           │                          │
     invoice.payment_failed           │
           │                          │
           ▼                          │
       ┌─────────┐   invoice.paid     │
       │past_due │───────────────────►┘
       └────┬────┘
            │
    failed_payment_count >= threshold
            │
            ▼
       ┌──────────┐
       │cancelled │  (auto-downgrade to Starter; period_end already past)
       └──────────┘
            ▲
            │
     cancel action (cancel_at_period_end = TRUE)
     → stays 'active' until period_end → then 'cancelled'
```

**Transitions:**
| Event | From | To | Side Effect |
|---|---|---|---|
| Subscription created | — | `active` | org tier updated |
| `invoice.paid` (renewal, no downgrade) | `active`/`past_due` | `active` | period refreshed, count reset |
| `invoice.paid` (renewal, with downgrade) | `active` | `active` | tier downgraded, schedule cleared |
| `invoice.payment_failed` (count < threshold) | `active`/`past_due` | `past_due` | count++, email sent |
| `invoice.payment_failed` (count = threshold) | `past_due` | `cancelled` | tier→Starter, audit log |
| `customer.subscription.deleted` | any | `cancelled` | tier→Starter if still elevated |
| Cancel action | `active` | `active` (cancel_at_period_end=true) | no tier change until period_end |
| Period end reached (cancelled) | `active` w/ cancel_at_period_end | `cancelled` | tier→Starter |
| Reactivate | `active` w/ cancel_at_period_end | `active` | cancel_at_period_end=false |

---

## Entity Relationships

```
organizations (1) ─────────────────────────── (0..N) billing_subscriptions
     │ stripe_customer_id                              │ provider_subscription_id
     │                                                  │ org_id → organizations
     │                                                  │ tier (text, not FK — mirrors org tier)
     │
     └── (1) ──── (0..N) billing_purchases             billing_prices
                                                        │ provider_price_id (Stripe Price ID)
                                                        │ billing_interval: monthly | annual
```

---

## Seed Data Required

For each environment, `billing_prices` rows for tier subscriptions need `provider_price_id` populated:

| price_type | target_key | billing_interval | provider_price_id |
|---|---|---|---|
| tier | professional | monthly | `price_...` (Stripe test/prod) |
| tier | professional | annual | `price_...` |
| tier | enterprise | monthly | `price_...` |
| tier | enterprise | annual | `price_...` |
| tier | platform | monthly | `price_...` |
| tier | platform | annual | `price_...` |

Seed SQL included in `051_recurring_billing.sql` as UPDATE statements with placeholder values to be overridden per environment.

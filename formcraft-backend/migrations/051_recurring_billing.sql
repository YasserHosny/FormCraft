-- F059 Recurring subscription billing.
-- Adds billing_subscriptions table, extends billing_prices with provider_price_id,
-- and extends organizations with stripe_customer_id.

ALTER TABLE public.billing_prices
ADD COLUMN IF NOT EXISTS provider_price_id TEXT;

ALTER TABLE public.organizations
ADD COLUMN IF NOT EXISTS stripe_customer_id TEXT;

CREATE TABLE IF NOT EXISTS public.billing_subscriptions (
    id                        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id                    UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    provider_subscription_id  TEXT NOT NULL UNIQUE,
    tier                      TEXT NOT NULL,
    billing_interval          billing_interval NOT NULL CHECK (billing_interval IN ('monthly', 'annual')),
    current_period_start      TIMESTAMPTZ NOT NULL,
    current_period_end        TIMESTAMPTZ NOT NULL,
    status                    TEXT NOT NULL DEFAULT 'active'
                              CHECK (status IN ('active', 'past_due', 'cancelled')),
    scheduled_downgrade_tier  TEXT
                              CHECK (scheduled_downgrade_tier IN ('starter', 'professional', 'enterprise', 'platform')),
    failed_payment_count      INTEGER NOT NULL DEFAULT 0 CHECK (failed_payment_count >= 0),
    last_invoice_id           TEXT,
    next_renewal_amount_minor INTEGER NOT NULL CHECK (next_renewal_amount_minor >= 0),
    currency                  CHAR(3) NOT NULL,
    cancel_at_period_end      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at                TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by                UUID REFERENCES public.profiles(id)
);

-- One active/past_due subscription per org; cancelled rows are historical records.
CREATE UNIQUE INDEX IF NOT EXISTS billing_subscriptions_one_active_per_org
ON public.billing_subscriptions (org_id)
WHERE status IN ('active', 'past_due');

CREATE INDEX IF NOT EXISTS billing_subscriptions_org_idx
ON public.billing_subscriptions (org_id, created_at DESC);

CREATE INDEX IF NOT EXISTS billing_subscriptions_provider_idx
ON public.billing_subscriptions (provider_subscription_id);

ALTER TABLE public.billing_subscriptions ENABLE ROW LEVEL SECURITY;

GRANT SELECT, UPDATE ON public.billing_subscriptions TO authenticated;
GRANT INSERT ON public.billing_subscriptions TO service_role;

-- Seed: populate provider_price_id for tier prices (replace with real Stripe Price IDs per env)
UPDATE public.billing_prices SET provider_price_id = 'price_professional_monthly_REPLACE'
WHERE price_type = 'tier' AND target_key = 'professional' AND billing_interval = 'monthly' AND is_active = TRUE AND provider_price_id IS NULL;

UPDATE public.billing_prices SET provider_price_id = 'price_professional_annual_REPLACE'
WHERE price_type = 'tier' AND target_key = 'professional' AND billing_interval = 'annual' AND is_active = TRUE AND provider_price_id IS NULL;

UPDATE public.billing_prices SET provider_price_id = 'price_enterprise_monthly_REPLACE'
WHERE price_type = 'tier' AND target_key = 'enterprise' AND billing_interval = 'monthly' AND is_active = TRUE AND provider_price_id IS NULL;

UPDATE public.billing_prices SET provider_price_id = 'price_enterprise_annual_REPLACE'
WHERE price_type = 'tier' AND target_key = 'enterprise' AND billing_interval = 'annual' AND is_active = TRUE AND provider_price_id IS NULL;

UPDATE public.billing_prices SET provider_price_id = 'price_platform_monthly_REPLACE'
WHERE price_type = 'tier' AND target_key = 'platform' AND billing_interval = 'monthly' AND is_active = TRUE AND provider_price_id IS NULL;

UPDATE public.billing_prices SET provider_price_id = 'price_platform_annual_REPLACE'
WHERE price_type = 'tier' AND target_key = 'platform' AND billing_interval = 'annual' AND is_active = TRUE AND provider_price_id IS NULL;

-- F058 PayGateway billing integration.
-- Adds authoritative billing prices, purchase lifecycle, idempotent fulfillment,
-- full refunds, and marketplace split records.

DO $$
BEGIN
    CREATE TYPE billing_price_type AS ENUM ('tier', 'seat', 'ocr_batch');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE billing_interval AS ENUM ('one_time', 'monthly', 'annual');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE billing_purchase_purpose AS ENUM ('subscription_tier', 'seats', 'ocr_batch', 'marketplace_template');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE billing_purchase_status AS ENUM ('created', 'requires_action', 'succeeded', 'failed', 'refunded', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE billing_fulfillment_effect AS ENUM ('tier_changed', 'seats_added', 'ocr_credited', 'template_copied');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE billing_fulfillment_source AS ENUM ('checkout_return', 'status_poll', 'webhook', 'reconciliation', 'zero_amount');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE billing_refund_status AS ENUM ('requested', 'succeeded', 'failed');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE billing_reversal_status AS ENUM ('pending', 'applied', 'failed');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

ALTER TABLE public.organizations
ADD COLUMN IF NOT EXISTS default_currency CHAR(3) DEFAULT 'SAR',
ADD COLUMN IF NOT EXISTS purchased_seat_allowance INTEGER NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS ocr_scan_credit_balance INTEGER NOT NULL DEFAULT 0;

CREATE TABLE IF NOT EXISTS public.billing_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    price_type billing_price_type NOT NULL,
    target_key TEXT NOT NULL,
    currency CHAR(3) NOT NULL,
    billing_interval billing_interval NOT NULL DEFAULT 'one_time',
    unit_amount_minor INTEGER NOT NULL CHECK (unit_amount_minor >= 0),
    min_quantity INTEGER,
    max_quantity INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    starts_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ends_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by UUID REFERENCES public.profiles(id),
    CHECK (min_quantity IS NULL OR min_quantity >= 0),
    CHECK (max_quantity IS NULL OR max_quantity >= COALESCE(min_quantity, 0))
);

CREATE UNIQUE INDEX IF NOT EXISTS billing_prices_one_active_idx
ON public.billing_prices (price_type, target_key, currency, billing_interval)
WHERE is_active = TRUE AND ends_at IS NULL;

CREATE TABLE IF NOT EXISTS public.billing_purchases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES public.profiles(id),
    purpose billing_purchase_purpose NOT NULL,
    target JSONB NOT NULL DEFAULT '{}'::jsonb,
    quantity INTEGER,
    currency CHAR(3) NOT NULL,
    amount_minor INTEGER NOT NULL CHECK (amount_minor >= 0),
    status billing_purchase_status NOT NULL DEFAULT 'created',
    provider TEXT NOT NULL DEFAULT 'paygateway',
    provider_payment_id TEXT,
    provider_checkout_token_hash TEXT,
    provider_status TEXT,
    idempotency_key TEXT NOT NULL UNIQUE,
    failure_code TEXT,
    failure_message_key TEXT,
    previous_effect_snapshot JSONB,
    fulfilled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS billing_purchases_org_created_idx
ON public.billing_purchases (organization_id, created_at DESC);

CREATE INDEX IF NOT EXISTS billing_purchases_provider_payment_idx
ON public.billing_purchases (provider_payment_id);

CREATE TABLE IF NOT EXISTS public.billing_fulfillments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    purchase_id UUID NOT NULL UNIQUE REFERENCES public.billing_purchases(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    effect_type billing_fulfillment_effect NOT NULL,
    effect_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    applied_by UUID REFERENCES public.profiles(id),
    source billing_fulfillment_source NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.billing_refunds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    purchase_id UUID NOT NULL UNIQUE REFERENCES public.billing_purchases(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    requested_by UUID NOT NULL REFERENCES public.profiles(id),
    reason TEXT NOT NULL,
    provider_refund_id TEXT,
    amount_minor INTEGER NOT NULL CHECK (amount_minor >= 0),
    currency CHAR(3) NOT NULL,
    status billing_refund_status NOT NULL DEFAULT 'requested',
    reversal_status billing_reversal_status NOT NULL DEFAULT 'pending',
    reversal_payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    applied_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS public.billing_marketplace_splits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    purchase_id UUID NOT NULL UNIQUE REFERENCES public.billing_purchases(id) ON DELETE CASCADE,
    listing_id UUID NOT NULL REFERENCES public.marketplace_listings(id),
    publisher_org_id UUID NOT NULL REFERENCES public.organizations(id),
    buyer_org_id UUID NOT NULL REFERENCES public.organizations(id),
    gross_amount_minor INTEGER NOT NULL CHECK (gross_amount_minor >= 0),
    platform_share_minor INTEGER NOT NULL CHECK (platform_share_minor >= 0),
    publisher_share_minor INTEGER NOT NULL CHECK (publisher_share_minor >= 0),
    currency CHAR(3) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (platform_share_minor + publisher_share_minor = gross_amount_minor)
);

ALTER TABLE public.billing_prices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.billing_purchases ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.billing_fulfillments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.billing_refunds ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.billing_marketplace_splits ENABLE ROW LEVEL SECURITY;

GRANT SELECT ON public.billing_prices TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.billing_purchases TO authenticated;
GRANT SELECT, INSERT ON public.billing_fulfillments TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.billing_refunds TO authenticated;
GRANT SELECT, INSERT ON public.billing_marketplace_splits TO authenticated;

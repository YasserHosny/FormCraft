-- F035 Template Marketplace

CREATE TABLE IF NOT EXISTS marketplace_listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    publisher_org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES profiles(id),
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    tags TEXT[] NOT NULL DEFAULT '{}',
    preview_image_urls TEXT[] NOT NULL DEFAULT '{}',
    sample_pdf_path TEXT,
    category TEXT NOT NULL DEFAULT 'general',
    country TEXT NOT NULL,
    language TEXT NOT NULL,
    compliance_badges TEXT[] NOT NULL DEFAULT '{}',
    quality_score NUMERIC(5,2) NOT NULL DEFAULT 0,
    price_type TEXT NOT NULL DEFAULT 'free',
    price_amount NUMERIC(12,2),
    currency TEXT NOT NULL DEFAULT 'USD',
    status TEXT NOT NULL DEFAULT 'submitted',
    review_status TEXT NOT NULL DEFAULT 'pending',
    download_count INTEGER NOT NULL DEFAULT 0,
    average_rating NUMERIC(3,2),
    review_count INTEGER NOT NULL DEFAULT 0,
    published_version INTEGER NOT NULL DEFAULT 1,
    approved_at TIMESTAMPTZ,
    suspended_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (price_type IN ('free', 'premium')),
    CHECK (
        (price_type = 'free' AND price_amount IS NULL)
        OR (price_type = 'premium' AND price_amount > 0)
    ),
    CHECK (status IN ('draft', 'submitted', 'approved', 'rejected', 'active', 'suspended', 'archived')),
    CHECK (review_status IN ('pending', 'approved', 'rejected'))
);

CREATE TABLE IF NOT EXISTS marketplace_imports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID NOT NULL REFERENCES marketplace_listings(id) ON DELETE CASCADE,
    consumer_org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    imported_template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    imported_by UUID NOT NULL REFERENCES profiles(id),
    listing_version INTEGER NOT NULL DEFAULT 1,
    remapping_status TEXT NOT NULL DEFAULT 'not_required',
    disabled_dependency_warnings JSONB NOT NULL DEFAULT '[]'::jsonb,
    source_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (remapping_status IN ('not_required', 'pending', 'completed'))
);

CREATE TABLE IF NOT EXISTS marketplace_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID NOT NULL REFERENCES marketplace_listings(id) ON DELETE CASCADE,
    consumer_org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL REFERENCES profiles(id),
    import_id UUID NOT NULL REFERENCES marketplace_imports(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT NOT NULL DEFAULT '',
    verified_import BOOLEAN NOT NULL DEFAULT TRUE,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (status IN ('active', 'hidden')),
    UNIQUE (listing_id, consumer_org_id)
);

CREATE TABLE IF NOT EXISTS marketplace_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID NOT NULL REFERENCES marketplace_listings(id) ON DELETE CASCADE,
    consumer_org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    publisher_org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    import_id UUID REFERENCES marketplace_imports(id) ON DELETE SET NULL,
    amount NUMERIC(12,2) NOT NULL,
    currency TEXT NOT NULL DEFAULT 'USD',
    platform_share NUMERIC(12,2) NOT NULL,
    publisher_share NUMERIC(12,2) NOT NULL,
    payment_status TEXT NOT NULL DEFAULT 'pending',
    provider TEXT NOT NULL DEFAULT 'internal',
    provider_reference TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    completed_at TIMESTAMPTZ,
    refunded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (payment_status IN ('pending', 'completed', 'failed', 'refunded', 'reversed'))
);

CREATE INDEX IF NOT EXISTS idx_marketplace_listings_discovery
    ON marketplace_listings(status, country, category, language, price_type);
CREATE INDEX IF NOT EXISTS idx_marketplace_listings_rating
    ON marketplace_listings(average_rating DESC NULLS LAST, download_count DESC);
CREATE INDEX IF NOT EXISTS idx_marketplace_listings_tags
    ON marketplace_listings USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_marketplace_imports_org_listing
    ON marketplace_imports(consumer_org_id, listing_id);
CREATE INDEX IF NOT EXISTS idx_marketplace_reviews_listing
    ON marketplace_reviews(listing_id, status);
CREATE INDEX IF NOT EXISTS idx_marketplace_transactions_listing_org
    ON marketplace_transactions(listing_id, consumer_org_id, payment_status);

ALTER TABLE marketplace_listings ENABLE ROW LEVEL SECURITY;
ALTER TABLE marketplace_imports ENABLE ROW LEVEL SECURITY;
ALTER TABLE marketplace_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE marketplace_transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY marketplace_listings_active_read
    ON marketplace_listings FOR SELECT
    USING (status = 'active' OR publisher_org_id::text = auth.jwt() ->> 'org_id');

CREATE POLICY marketplace_listings_publisher_write
    ON marketplace_listings FOR ALL
    USING (publisher_org_id::text = auth.jwt() ->> 'org_id')
    WITH CHECK (publisher_org_id::text = auth.jwt() ->> 'org_id');

CREATE POLICY marketplace_imports_org_isolation
    ON marketplace_imports FOR ALL
    USING (consumer_org_id::text = auth.jwt() ->> 'org_id')
    WITH CHECK (consumer_org_id::text = auth.jwt() ->> 'org_id');

CREATE POLICY marketplace_reviews_org_isolation
    ON marketplace_reviews FOR ALL
    USING (consumer_org_id::text = auth.jwt() ->> 'org_id')
    WITH CHECK (consumer_org_id::text = auth.jwt() ->> 'org_id');

CREATE POLICY marketplace_transactions_org_isolation
    ON marketplace_transactions FOR SELECT
    USING (
        consumer_org_id::text = auth.jwt() ->> 'org_id'
        OR publisher_org_id::text = auth.jwt() ->> 'org_id'
    );

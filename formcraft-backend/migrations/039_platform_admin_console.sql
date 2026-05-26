-- F039: Platform Admin Console
-- 2026-05-26

-- 1. Add domain column to organizations
ALTER TABLE organizations
ADD COLUMN IF NOT EXISTS domain text UNIQUE;

-- 2. Add status column to organizations if not present
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'organizations' AND column_name = 'status'
    ) THEN
        ALTER TABLE organizations ADD COLUMN status text NOT NULL DEFAULT 'active';
        ALTER TABLE organizations ADD CONSTRAINT organizations_status_check
            CHECK (status IN ('active', 'suspended'));
    END IF;
END $$;

-- 3. Create tier_limits lookup table
CREATE TABLE IF NOT EXISTS tier_limits (
    tier text PRIMARY KEY,
    user_limit integer NOT NULL,
    template_limit integer NOT NULL,
    storage_limit_gb integer NOT NULL
);

INSERT INTO tier_limits (tier, user_limit, template_limit, storage_limit_gb) VALUES
    ('starter', 10, 50, 5),
    ('professional', 50, 200, 25),
    ('enterprise', 200, 1000, 100),
    ('platform', 1000, 5000, 500)
ON CONFLICT (tier) DO NOTHING;

-- 4. Create materialized view for platform metrics
CREATE MATERIALIZED VIEW IF NOT EXISTS platform_metrics_mv AS
SELECT
    (SELECT COUNT(*) FROM organizations WHERE status = 'active' OR status = 'suspended') AS total_orgs,
    (SELECT COUNT(*) FROM profiles) AS total_users,
    (SELECT COUNT(*) FROM submissions) AS total_submissions,
    (
        SELECT jsonb_object_agg(subscription_tier, cnt)
        FROM (
            SELECT subscription_tier, COUNT(*) as cnt
            FROM organizations
            GROUP BY subscription_tier
        ) t
    ) AS orgs_by_tier;

-- Unique index required for REFRESH CONCURRENTLY
CREATE UNIQUE INDEX IF NOT EXISTS idx_platform_metrics_mv_dummy
ON platform_metrics_mv ((1));

-- 5. Create function to refresh materialized view
CREATE OR REPLACE FUNCTION refresh_platform_metrics_mv()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY platform_metrics_mv;
END;
$$ LANGUAGE plpgsql;

-- 6. Create function for tier limit alerts
CREATE OR REPLACE FUNCTION get_tier_limit_alerts()
RETURNS TABLE (
    org_id uuid,
    org_name text,
    tier text,
    limit_type text,
    current_usage bigint,
    limit_value integer,
    threshold_pct double precision
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        o.id AS org_id,
        o.name_ar AS org_name,
        o.subscription_tier AS tier,
        'users'::text AS limit_type,
        (SELECT COUNT(*) FROM profiles WHERE profiles.org_id = o.id) AS current_usage,
        tl.user_limit AS limit_value,
        ((SELECT COUNT(*)::double precision FROM profiles WHERE profiles.org_id = o.id) / NULLIF(tl.user_limit, 0)) * 100 AS threshold_pct
    FROM organizations o
    JOIN tier_limits tl ON tl.tier = o.subscription_tier
    WHERE (
        SELECT COUNT(*)::double precision FROM profiles WHERE profiles.org_id = o.id
    ) >= tl.user_limit * 0.9;
END;
$$ LANGUAGE plpgsql;

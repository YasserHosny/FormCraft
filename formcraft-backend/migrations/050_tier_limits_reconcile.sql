-- 050: Reconcile tier_limits to match documented revenue model tiers
-- Fixes two mismatches called out in system-critique-and-vision.md §Revenue Model:
--   1. user_limit values don't match documented tier sizes (starter=4, professional=30)
--   2. submissions_per_month_limit column was missing — Starter's 100/mo cap was untrackable
-- Enforcement gates (blocking invite/submit when limits exceeded) are out of scope here;
-- they are tracked separately in the vision doc.

-- 1. Add submissions_per_month_limit column (-1 = unlimited)
ALTER TABLE tier_limits
    ADD COLUMN IF NOT EXISTS submissions_per_month_limit INTEGER NOT NULL DEFAULT -1;

-- 2. Reconcile all four tiers to documented values
UPDATE tier_limits SET
    user_limit = 4,
    template_limit = 50,
    storage_limit_gb = 5,
    submissions_per_month_limit = 100
WHERE tier = 'starter';

UPDATE tier_limits SET
    user_limit = 30,
    template_limit = 200,
    storage_limit_gb = 25,
    submissions_per_month_limit = -1
WHERE tier = 'professional';

UPDATE tier_limits SET
    user_limit = 9999,
    template_limit = 9999,
    storage_limit_gb = 100,
    submissions_per_month_limit = -1
WHERE tier = 'enterprise';

UPDATE tier_limits SET
    user_limit = 99999,
    template_limit = 99999,
    storage_limit_gb = 500,
    submissions_per_month_limit = -1
WHERE tier = 'platform';

-- 3. Extend get_tier_limit_alerts() to also surface submission cap proximity
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
    -- User count alerts (≥90% of user_limit)
    RETURN QUERY
    SELECT
        o.id AS org_id,
        o.name_ar AS org_name,
        o.subscription_tier AS tier,
        'users'::text AS limit_type,
        (SELECT COUNT(*) FROM profiles WHERE profiles.org_id = o.id) AS current_usage,
        tl.user_limit AS limit_value,
        ((SELECT COUNT(*)::double precision FROM profiles WHERE profiles.org_id = o.id)
            / NULLIF(tl.user_limit, 0)) * 100 AS threshold_pct
    FROM organizations o
    JOIN tier_limits tl ON tl.tier = o.subscription_tier
    WHERE tl.user_limit > 0
      AND (SELECT COUNT(*)::double precision FROM profiles WHERE profiles.org_id = o.id)
          >= tl.user_limit * 0.9;

    -- Submission cap alerts for capped tiers (≥80% of monthly limit, current calendar month)
    RETURN QUERY
    SELECT
        o.id AS org_id,
        o.name_ar AS org_name,
        o.subscription_tier AS tier,
        'submissions_this_month'::text AS limit_type,
        (SELECT COUNT(*)
         FROM submissions s
         WHERE s.org_id = o.id
           AND s.created_at >= date_trunc('month', now())
           AND s.created_at < date_trunc('month', now()) + interval '1 month') AS current_usage,
        tl.submissions_per_month_limit AS limit_value,
        ((SELECT COUNT(*)::double precision
          FROM submissions s
          WHERE s.org_id = o.id
            AND s.created_at >= date_trunc('month', now())
            AND s.created_at < date_trunc('month', now()) + interval '1 month')
         / NULLIF(tl.submissions_per_month_limit, 0)) * 100 AS threshold_pct
    FROM organizations o
    JOIN tier_limits tl ON tl.tier = o.subscription_tier
    WHERE tl.submissions_per_month_limit > 0
      AND (SELECT COUNT(*)::double precision
           FROM submissions s
           WHERE s.org_id = o.id
             AND s.created_at >= date_trunc('month', now())
             AND s.created_at < date_trunc('month', now()) + interval '1 month')
          >= tl.submissions_per_month_limit * 0.8;
END;
$$ LANGUAGE plpgsql;

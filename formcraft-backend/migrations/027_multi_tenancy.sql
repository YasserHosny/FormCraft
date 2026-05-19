-- Migration 027: Multi-Tenancy — Organizations, Departments, Branches, User Invitations
-- Adds organizational hierarchy, user assignment, and invitation workflow.

-- Step 1: Create organizations table
CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name_ar TEXT NOT NULL,
  name_en TEXT NOT NULL,
  logo_url TEXT,
  primary_color TEXT,
  default_language TEXT NOT NULL DEFAULT 'ar' CHECK (default_language IN ('ar', 'en')),
  default_country TEXT NOT NULL DEFAULT 'EG' CHECK (default_country IN ('EG', 'SA', 'AE')),
  default_currency TEXT NOT NULL DEFAULT 'EGP',
  custom_domain TEXT UNIQUE,
  settings JSONB NOT NULL DEFAULT '{
    "approval_workflow_enabled": false,
    "draft_expiry_days": 7,
    "data_retention_months": 36,
    "allowed_file_types": ["image/png", "image/jpeg", "application/pdf"],
    "max_batch_size": 1000,
    "customer_profiles_enabled": false,
    "hijri_date_support": false,
    "notification_preferences": {"email": true, "in_app": true}
  }'::JSONB,
  subscription_tier TEXT NOT NULL DEFAULT 'starter'
    CHECK (subscription_tier IN ('starter', 'professional', 'enterprise')),
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Step 2: Create departments table
CREATE TABLE departments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name_ar TEXT NOT NULL,
  name_en TEXT NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_departments_org ON departments(org_id);

ALTER TABLE departments ENABLE ROW LEVEL SECURITY;
CREATE POLICY departments_org_isolation ON departments
  USING (org_id = current_setting('app.current_org_id', true)::UUID);

-- Step 3: Create branches table
CREATE TABLE branches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  department_id UUID NOT NULL REFERENCES departments(id) ON DELETE CASCADE,
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name_ar TEXT NOT NULL,
  name_en TEXT NOT NULL,
  location TEXT,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_branches_dept ON branches(department_id);
CREATE INDEX idx_branches_org ON branches(org_id);

ALTER TABLE branches ENABLE ROW LEVEL SECURITY;
CREATE POLICY branches_org_isolation ON branches
  USING (org_id = current_setting('app.current_org_id', true)::UUID);

-- Step 4: Create user_invitations table
CREATE TABLE user_invitations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL,
  token UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  role TEXT NOT NULL CHECK (role IN ('admin', 'designer', 'operator', 'viewer', 'branch_manager')),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  department_id UUID REFERENCES departments(id),
  branch_id UUID REFERENCES branches(id),
  invited_by UUID NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'expired')),
  expires_at TIMESTAMPTZ NOT NULL DEFAULT (now() + interval '72 hours'),
  accepted_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_invitations_token ON user_invitations(token);
CREATE INDEX idx_invitations_org ON user_invitations(org_id);
CREATE INDEX idx_invitations_email_org ON user_invitations(email, org_id);

-- Step 5: Seed default organization
INSERT INTO organizations (id, name_ar, name_en, default_language, default_country)
VALUES ('00000000-0000-0000-0000-000000000001', 'المؤسسة الافتراضية', 'Default Organization', 'ar', 'EG');

-- Step 6: Add columns to profiles
ALTER TABLE profiles
  ADD COLUMN IF NOT EXISTS org_id UUID REFERENCES organizations(id),
  ADD COLUMN IF NOT EXISTS department_id UUID REFERENCES departments(id),
  ADD COLUMN IF NOT EXISTS branch_id UUID REFERENCES branches(id),
  ADD COLUMN IF NOT EXISTS is_platform_admin BOOLEAN NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS invited_by UUID,
  ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMPTZ;

-- If is_active column doesn't exist yet, add it
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'profiles' AND column_name = 'is_active') THEN
    ALTER TABLE profiles ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true;
  END IF;
END $$;

-- Step 7: Backfill existing profiles with default org
UPDATE profiles SET org_id = '00000000-0000-0000-0000-000000000001' WHERE org_id IS NULL;

-- Step 8: Make org_id NOT NULL after backfill
ALTER TABLE profiles ALTER COLUMN org_id SET NOT NULL;

-- Step 9: Add RLS to profiles
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY profiles_org_isolation ON profiles
  USING (org_id = current_setting('app.current_org_id', true)::UUID
         OR (current_setting('app.is_platform_admin', true)::VARCHAR) = 'true');

-- Step 10: Add department_id to templates for scoping
ALTER TABLE templates ADD COLUMN IF NOT EXISTS department_id UUID REFERENCES departments(id);

-- Step 11: Ensure templates org_id FK to organizations
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints
    WHERE constraint_name = 'templates_org_id_fkey' AND table_name = 'templates'
  ) THEN
    ALTER TABLE templates ADD CONSTRAINT templates_org_id_fkey
      FOREIGN KEY (org_id) REFERENCES organizations(id);
  END IF;
END $$;

-- Step 12: Backfill templates org_id with default org
UPDATE templates SET org_id = '00000000-0000-0000-0000-000000000001' WHERE org_id IS NULL;

-- Step 13: Create indexes
CREATE INDEX IF NOT EXISTS idx_profiles_org ON profiles(org_id);
CREATE INDEX IF NOT EXISTS idx_profiles_dept ON profiles(department_id);
CREATE INDEX IF NOT EXISTS idx_profiles_branch ON profiles(branch_id);
CREATE INDEX IF NOT EXISTS idx_templates_dept ON templates(department_id);

-- Step 14: Add RLS to organizations for platform admin read access
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
CREATE POLICY organizations_read ON organizations
  USING (true);  -- Organizations are readable by all authenticated users; write is admin-only

-- Step 15: Add RLS to user_invitations
ALTER TABLE user_invitations ENABLE ROW LEVEL SECURITY;
CREATE POLICY invitations_org_isolation ON user_invitations
  USING (org_id = current_setting('app.current_org_id', true)::UUID);

-- Step 16: Add audit triggers
CREATE OR REPLACE FUNCTION audit_organizations() RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO audit_logs (action, resource_type, resource_id, metadata, user_id)
  VALUES (
    TG_OP,
    'organization',
    COALESCE(NEW.id::TEXT, OLD.id::TEXT),
    jsonb_build_object('name_en', COALESCE(NEW.name_en, OLD.name_en)),
    current_user::UUID
  );
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER organizations_audit AFTER INSERT OR UPDATE OR DELETE ON organizations
  FOR EACH ROW EXECUTE FUNCTION audit_organizations();

-- Step 17: Comments
-- Step 18: Ensure RLS on all org-scoped tables
DO $$
DECLARE
  tbl TEXT;
BEGIN
  FOR tbl IN SELECT unnest(ARRAY[
    'templates', 'submissions', 'reference_lists', 'reference_entries',
    'template_feedback', 'audit_logs'
  ])
  LOOP
    EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', tbl);
    IF NOT EXISTS (
      SELECT 1 FROM pg_policies WHERE tablename = tbl AND policyname = tbl || '_org_isolation'
    ) THEN
      EXECUTE format(
        'CREATE POLICY %I ON %I USING (org_id = current_setting(''app.current_org_id'')::UUID)',
        tbl || '_org_isolation', tbl
      );
    END IF;
  END LOOP;
END $$;

-- Step 19: Add branch_id to submissions if not present
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS branch_id UUID REFERENCES branches(id);

COMMENT ON TABLE organizations IS 'Multi-tenant organizations. All data is scoped by org_id via RLS.';
COMMENT ON TABLE departments IS 'Departments within an organization.';
COMMENT ON TABLE branches IS 'Physical branches within a department.';
COMMENT ON TABLE user_invitations IS 'Pending user invitations with pre-assigned role, department, and branch.';
COMMENT ON COLUMN profiles.is_platform_admin IS 'Super-admin: can manage all organizations. Separate from org-level admin role.';
COMMENT ON COLUMN templates.department_id IS 'Department scope. NULL = org-wide (visible to all departments).';
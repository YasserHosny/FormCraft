# Data Model: Multi-Tenancy (Organizations, Departments, Branches)

**Date**: 2026-05-17

## Schema Changes

### New Table: `organizations`

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | NO | PK, default gen_random_uuid() |
| name_ar | TEXT | NO | Arabic display name |
| name_en | TEXT | NO | English display name |
| logo_url | TEXT | YES | Supabase Storage path or URL |
| primary_color | TEXT | YES | Hex color for white-label (e.g., "#003366") |
| default_language | TEXT | NO | 'ar' or 'en'. Default 'ar' |
| default_country | TEXT | NO | 'EG', 'SA', 'AE'. Default 'EG' |
| default_currency | TEXT | NO | Default 'EGP' |
| custom_domain | TEXT | YES | UNIQUE. CNAME for white-label URL |
| settings | JSONB | NO | Org-level configuration (see schema below) |
| subscription_tier | TEXT | NO | 'starter', 'professional', 'enterprise'. Default 'starter' |
| is_active | BOOLEAN | NO | Default true |
| created_at | TIMESTAMPTZ | NO | Default now() |
| updated_at | TIMESTAMPTZ | NO | Default now() |

**Settings JSONB schema**:
```json
{
  "approval_workflow_enabled": false,
  "draft_expiry_days": 7,
  "data_retention_months": 36,
  "allowed_file_types": ["image/png", "image/jpeg", "application/pdf"],
  "max_batch_size": 1000,
  "customer_profiles_enabled": false,
  "hijri_date_support": false,
  "notification_preferences": { "email": true, "in_app": true }
}
```

### New Table: `departments`

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | NO | PK, default gen_random_uuid() |
| org_id | UUID | NO | FK → organizations(id) |
| name_ar | TEXT | NO | Arabic name |
| name_en | TEXT | NO | English name |
| is_active | BOOLEAN | NO | Default true. Soft-delete |
| created_at | TIMESTAMPTZ | NO | Default now() |

### New Table: `branches`

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | NO | PK, default gen_random_uuid() |
| department_id | UUID | NO | FK → departments(id) |
| org_id | UUID | NO | FK → organizations(id) |
| name_ar | TEXT | NO | Arabic name |
| name_en | TEXT | NO | English name |
| location | TEXT | YES | Physical address or description |
| is_active | BOOLEAN | NO | Default true. Soft-delete |
| created_at | TIMESTAMPTZ | NO | Default now() |

### New Table: `user_invitations`

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | NO | PK, default gen_random_uuid() |
| email | TEXT | NO | Invited email address |
| token | UUID | NO | UNIQUE. Secure invitation token |
| role | TEXT | NO | Assigned role on acceptance |
| org_id | UUID | NO | FK → organizations(id) |
| department_id | UUID | YES | FK → departments(id) |
| branch_id | UUID | YES | FK → branches(id) |
| invited_by | UUID | NO | FK → auth.users(id) |
| status | TEXT | NO | 'pending', 'accepted', 'expired'. Default 'pending' |
| expires_at | TIMESTAMPTZ | NO | Default now() + 72 hours |
| accepted_at | TIMESTAMPTZ | YES | |
| created_at | TIMESTAMPTZ | NO | Default now() |

### Note on Table Naming

The migration references `profiles` as the user table. Verify against the actual Supabase schema — if the table is named differently (e.g., `users` or `public.profiles`), adjust ALTER TABLE statements accordingly. The existing `formcraft-backend/app/models/user.py` model defines the ORM mapping.

### Modified Table: `profiles` (users)

| Column | Type | Change | Notes |
|--------|------|--------|-------|
| org_id | UUID | ADD | FK → organizations(id). NOT NULL after backfill |
| department_id | UUID | ADD | FK → departments(id). Nullable |
| branch_id | UUID | ADD | FK → branches(id). Nullable |
| is_platform_admin | BOOLEAN | ADD | Default false. Super-admin flag |
| is_active | BOOLEAN | ADD | Default true. Account deactivation |
| invited_by | UUID | ADD | FK → auth.users(id). Nullable (null for seed users) |
| last_login_at | TIMESTAMPTZ | ADD | Updated on each login |

### Modified Table: `templates`

| Column | Type | Change | Notes |
|--------|------|--------|-------|
| department_id | UUID | ADD | FK → departments(id). Nullable = org-wide access |

## Migration

**Migration file**: `027_multi_tenancy.sql`

```sql
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
  org_id UUID NOT NULL REFERENCES organizations(id),
  name_ar TEXT NOT NULL,
  name_en TEXT NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_departments_org ON departments(org_id);

ALTER TABLE departments ENABLE ROW LEVEL SECURITY;
CREATE POLICY departments_org_isolation ON departments
  USING (org_id = current_setting('app.current_org_id')::UUID);

-- Step 3: Create branches table
CREATE TABLE branches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  department_id UUID NOT NULL REFERENCES departments(id),
  org_id UUID NOT NULL REFERENCES organizations(id),
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
  USING (org_id = current_setting('app.current_org_id')::UUID);

-- Step 4: Create user_invitations table
CREATE TABLE user_invitations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL,
  token UUID NOT NULL UNIQUE DEFAULT gen_random_uuid(),
  role TEXT NOT NULL CHECK (role IN ('admin', 'designer', 'operator', 'viewer', 'branch_manager')),
  org_id UUID NOT NULL REFERENCES organizations(id),
  department_id UUID REFERENCES departments(id),
  branch_id UUID REFERENCES branches(id),
  invited_by UUID NOT NULL REFERENCES auth.users(id),
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'expired')),
  expires_at TIMESTAMPTZ NOT NULL DEFAULT (now() + interval '72 hours'),
  accepted_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_invitations_token ON user_invitations(token);
CREATE INDEX idx_invitations_org ON user_invitations(org_id);

-- Step 5: Seed default organization for existing data
INSERT INTO organizations (id, name_ar, name_en, default_language, default_country)
VALUES ('00000000-0000-0000-0000-000000000001', 'المؤسسة الافتراضية', 'Default Organization', 'ar', 'EG');

-- Step 6: Add columns to profiles
ALTER TABLE profiles
ADD COLUMN org_id UUID REFERENCES organizations(id),
ADD COLUMN department_id UUID REFERENCES departments(id),
ADD COLUMN branch_id UUID REFERENCES branches(id),
ADD COLUMN is_platform_admin BOOLEAN NOT NULL DEFAULT false,
ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true,
ADD COLUMN invited_by UUID REFERENCES auth.users(id),
ADD COLUMN last_login_at TIMESTAMPTZ;

-- Step 7: Backfill existing profiles with default org
UPDATE profiles SET org_id = '00000000-0000-0000-0000-000000000001' WHERE org_id IS NULL;

-- Step 8: Make org_id NOT NULL after backfill
ALTER TABLE profiles ALTER COLUMN org_id SET NOT NULL;

-- Step 9: Add RLS to profiles
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY profiles_org_isolation ON profiles
  USING (org_id = current_setting('app.current_org_id')::UUID
         OR current_setting('app.is_platform_admin', true)::BOOLEAN = true);

-- Step 10: Add department_id to templates for scoping
ALTER TABLE templates ADD COLUMN department_id UUID REFERENCES departments(id);

-- Step 11: Backfill existing org_id references where needed
-- (templates, reference_lists, etc. already have org_id — ensure FK to organizations)
-- Add FK constraint if not already present
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

-- Step 13: Create indexes for user lookups
CREATE INDEX idx_profiles_org ON profiles(org_id);
CREATE INDEX idx_profiles_dept ON profiles(department_id);
CREATE INDEX idx_profiles_branch ON profiles(branch_id);
CREATE INDEX idx_templates_dept ON templates(department_id);

COMMENT ON TABLE organizations IS 'Multi-tenant organizations. All data is scoped by org_id via RLS.';
COMMENT ON TABLE departments IS 'Departments within an organization (e.g., Retail Banking, Corporate Banking).';
COMMENT ON TABLE branches IS 'Physical branches within a department (e.g., Cairo Main, Giza Branch).';
COMMENT ON TABLE user_invitations IS 'Pending user invitations with pre-assigned role, department, and branch.';
COMMENT ON COLUMN profiles.is_platform_admin IS 'Super-admin: can manage all organizations. Separate from org-level admin role.';
COMMENT ON COLUMN templates.department_id IS 'Department scope. NULL = org-wide (visible to all departments).';
```

## Entity Relationships

```
organizations
├── id (UUID PK)
├── name_ar, name_en
├── logo_url, primary_color
├── default_language, default_country, default_currency
├── custom_domain (UNIQUE)
├── settings (JSONB)
├── subscription_tier
├── is_active
└── timestamps
     │
     │ 1:N
     ▼
departments
├── id (UUID PK)
├── org_id (UUID FK → organizations)
├── name_ar, name_en
├── is_active
└── created_at
     │
     │ 1:N
     ▼
branches
├── id (UUID PK)
├── department_id (UUID FK → departments)
├── org_id (UUID FK → organizations)
├── name_ar, name_en, location
├── is_active
└── created_at

profiles (MODIFIED)
├── org_id (UUID FK → organizations) ← NEW
├── department_id (UUID FK → departments) ← NEW
├── branch_id (UUID FK → branches) ← NEW
├── is_platform_admin (BOOLEAN) ← NEW
├── is_active (BOOLEAN) ← NEW
└── last_login_at (TIMESTAMPTZ) ← NEW

templates (MODIFIED)
└── department_id (UUID FK → departments) ← NEW (nullable = org-wide)

user_invitations
├── id (UUID PK)
├── email, token (UNIQUE)
├── role, org_id, department_id, branch_id
├── invited_by, status, expires_at
└── timestamps

RLS chain:
  JWT → middleware sets app.current_org_id → all queries filtered by org_id
  profiles, templates, submissions, reference_lists, etc. — all isolated
```

## Validation Rules

| Rule | Enforced At | Error |
|------|-------------|-------|
| Org name_ar and name_en required | DB NOT NULL + API | 422 "Name required" |
| Department org_id must match current org | RLS + API | 403/404 |
| Branch department must belong to same org | API service | 422 "Department not in this org" |
| User org_id must match invitation org_id | API service (on acceptance) | 422 "Organization mismatch" |
| Invitation token must be valid (pending + not expired) | API service | 410 "Invitation expired" |
| Custom domain must be unique across all orgs | DB UNIQUE | 409 "Domain already in use" |
| is_platform_admin can only be set by existing platform admin | API service | 403 "Insufficient permission" |
| Department deletion prevented if active users assigned | API service | 409 "Department has active users" |
| Branch deletion prevented if active users assigned | API service | 409 "Branch has active users" |
| All data queries return 404 (not 403) for cross-org access | API convention | 404 |

## Data Volume Impact

- organizations: Low volume (1-100 total on a platform instance)
- departments: Low volume (5-20 per org)
- branches: Medium volume (10-100 per org)
- user_invitations: Low volume (cleaned up after acceptance/expiry)
- profiles: Medium volume (10-5,000 per org)
- New indexes on profiles(org_id, department_id, branch_id) — negligible overhead
- RLS overhead: minimal (index-backed org_id filter on every query)

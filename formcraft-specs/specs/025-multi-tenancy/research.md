# Research: Multi-Tenancy (Organizations, Departments, Branches)

**Date**: 2026-05-17

## Research Questions

No NEEDS CLARIFICATION items. Research focused on RLS enforcement strategy, existing org_id usage, invitation mechanism, and migration path for existing data.

## Findings

### 1. Existing org_id Usage

The current codebase already has `org_id` on several tables (templates, reference_lists, reference_entries, template_feedback, printer_profiles, template_print_settings, audit_logs). However:

- There is NO `organizations` table yet — org_id columns exist but reference nothing
- There is NO `departments` or `branches` table
- RLS policies reference `current_setting('app.current_org_id')` which is set per-session
- The `profiles` table has no org_id, department_id, or branch_id columns

**Decision**: Formalize the org structure by creating the `organizations`, `departments`, and `branches` tables. Add org_id FK to profiles. Backfill existing data with a default org. Add department_id and branch_id to profiles.

### 2. RLS Enforcement Strategy

**Current state**: Some tables have RLS with `org_id = current_setting('app.current_org_id')::UUID`. This pattern works but requires the API to set the session variable before every query.

**Decision**: Continue this pattern (proven in Supabase ecosystem). The FastAPI middleware sets `app.current_org_id` from the JWT claims at the start of each request. All new and existing tables get RLS policies using this pattern.

**API middleware flow**:
1. JWT token includes `org_id` claim (set at login time based on user's org)
2. FastAPI middleware extracts org_id from JWT
3. Before any DB query: `SET LOCAL app.current_org_id = '{org_id}'`
4. All subsequent queries in that request are automatically filtered by RLS

### 3. Multi-Org Users

Some users (consultants, auditors) may need access to multiple orgs.

**Decision for v1**: A user belongs to exactly ONE org (simplest model). Multi-org access handled by separate profiles per org (same email, different profile rows, different org_id). On login, if email exists in multiple orgs, show org selector.

Future: Add `user_org_memberships` junction table for true multi-org in Phase 3.

### 4. Template Department Scoping

**Options**:
1. `department_id` FK on templates table — simple but only one department
2. `template_department_access` junction table — flexible multi-department access
3. JSONB array `department_ids[]` on templates — simple multi-department

**Decision**: Option 1 (single department_id on templates, nullable). NULL = org-wide (visible to all departments). Most templates belong to one department. Cross-department templates are rare and can be set to org-wide. If needed later, a junction table can be added without breaking the simple case.

### 5. Invitation Mechanism

**Implementation via Supabase Auth**:
- Supabase Auth supports `inviteUserByEmail()` which sends a magic link
- On link click, user is prompted to set password
- We extend this by storing invitation metadata (role, department, branch) in a `user_invitations` table
- After user completes setup, a trigger/webhook reads the invitation and assigns role/dept/branch to the profile

**Alternative**: Custom invitation flow (our own email + token table). More control over branding and multi-step onboarding.

**Decision**: Custom invitation flow for full control. Store invitations in `user_invitations` table with a secure token (UUID). API endpoint verifies token + creates profile. This lets us customize the email template (bilingual, org-branded) and the setup experience.

### 6. Super-Admin Role

**Decision**: Add a `is_platform_admin` boolean to profiles (default false). Platform admins can:
- Create/manage organizations
- Access any org (bypass RLS for admin operations)
- View platform-wide metrics

This is separate from org-level `admin` role. An org admin manages their org; a platform admin manages the platform.

### 7. Migration Path for Existing Data

**Strategy**:
1. Create `organizations` table with a seeded "Default Organization" (id = known UUID)
2. Backfill all existing rows: `UPDATE templates SET org_id = '<default_org_id>' WHERE org_id IS NULL`
3. Create default department and branch (or leave null for simple single-org setup)
4. Add org_id to profiles, backfill with default org
5. Existing users become members of the default org

This is non-breaking: single-org deployments continue working with the default org. Multi-org features activate when additional orgs are created.

### 8. Org Settings Storage

**Decision**: Store org-level settings in a `settings` JSONB column on organizations table:
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

JSONB allows adding new settings without migrations. Frontend reads these on app load and applies them throughout the session.

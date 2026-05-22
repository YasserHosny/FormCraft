# Implementation Plan: Multi-Tenancy (Organizations, Departments, Branches)

**Date**: 2026-05-17  
**Feature Branch**: `024-multi-tenancy`  
**Depends on**: All Phase 1 features (this is the Phase 2 foundation)

## Architecture Overview

Multi-tenancy formalizes the org isolation that Phase 1 prepared for (existing org_id columns, RLS policies). It introduces the organizational hierarchy (org → department → branch), user assignment, invitation workflow, and org-level settings. This is the most impactful migration in Phase 2 — all subsequent features depend on it.

```
┌──────────────────────────────────────────────────────────────────────┐
│                     Platform Admin Panel                               │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ OrgManagementComponent (create/manage orgs)                    │  │
│  └────────────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────────┤
│                     Org Admin Panel                                    │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ Departments   │  │ Branches     │  │ User Management         │  │
│  │ CRUD          │  │ CRUD         │  │ (invite, assign, deact) │  │
│  └───────────────┘  └──────────────┘  └──────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ Org Settings (branding, policies, white-label)                 │  │
│  └────────────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────────┤
│                     Backend Middleware                                 │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ JWT org_id claim → SET LOCAL app.current_org_id → RLS active  │  │
│  └────────────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────────┤
│                     Database                                          │
│  organizations ──1:N──> departments ──1:N──> branches                │
│  organizations ──1:N──> profiles (users)                             │
│  organizations ──1:N──> templates, submissions, reference_lists...   │
│  RLS on ALL tables using app.current_org_id                          │
└──────────────────────────────────────────────────────────────────────┘
```

## Technology Stack

- **Backend**: Python 3.12, FastAPI middleware (JWT → RLS session variable), Pydantic v2
- **Frontend**: Angular 17, Angular Material, @ngx-translate
- **Auth**: Supabase Auth (extended with org_id in JWT custom claims)
- **Email**: SMTP or Supabase email (for invitations)
- **Database**: Supabase PostgreSQL with RLS

## Implementation Phases

### Phase 1: Database Migration & Backfill

Create organizations, departments, branches, user_invitations tables. Add columns to profiles and templates. Seed default org. Backfill existing data. Add FK constraints.

### Phase 2: Backend Middleware — Org Context

FastAPI middleware that extracts org_id from JWT, sets `app.current_org_id` session variable. Platform admin bypass for cross-org operations.

### Phase 3: Backend — Organization & Hierarchy CRUD

Service and routes for organizations (platform admin), departments, branches.

### Phase 4: Backend — User Invitation & Management

Invitation service (create, send email, accept), user management (assign, deactivate, activate). Enhanced user listing with department/branch filters.

### Phase 5: Backend — Template Department Scoping

Template queries filter by user's department (or show all if org-wide). Template create/update accepts department_id.

### Phase 6: Backend — Auth Modifications

Login flow with multi-org detection, org selector response, JWT with org_id claim. Org branding endpoint for login page.

### Phase 7: Frontend — Org Admin UI

Admin pages for departments, branches, user management, invitations, org settings.

### Phase 8: Frontend — Invitation Acceptance Flow

Public pages: invitation acceptance form (set password + display name), expired invitation page.

### Phase 9: Frontend — Login & Branding

Org selector on login (multi-org users), org branding on login page (logo, color), org logo in nav bar.

### Phase 10: Frontend — Template Scoping & Submission Tagging

Template grid filters by department. New submissions auto-tagged with operator's branch_id.

### Phase 11: Migration & Existing Data

Ensure all existing data assigned to default org. Verify RLS doesn't break existing functionality. Add platform admin to seed user.

## Technical Constraints

1. **Non-breaking migration** — existing single-org deployments continue working via default org
2. **JWT size** — org_id in claims adds ~40 bytes; acceptable
3. **RLS performance** — org_id indexed on all tables; RLS uses index scans
4. **Email delivery** — invitation emails must support Arabic RTL
5. **Platform admin bypass** — uses separate RLS policy with `is_platform_admin` check
6. **Backwards compatible API** — existing endpoints work unchanged for single-org users

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| RLS migration breaks existing queries | All queries fail | Backfill default org BEFORE enabling RLS on new tables; test with existing data |
| Multi-org login UX complexity | Confusion for single-org users | Only show org selector if email exists in >1 org; single-org = auto-login |
| Invitation email delivery failures | Users can't onboard | Retry logic + admin can resend; show invitation link in admin panel as fallback |
| Department scope overly restrictive | Users can't access needed templates | NULL department_id = org-wide (default); explicit scoping is opt-in |
| Cross-org data leakage | Security breach | Automated test suite that creates 2 orgs and verifies isolation on every table |

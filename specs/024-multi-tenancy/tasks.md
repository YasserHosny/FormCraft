# Tasks: Multi-Tenancy (Organizations, Departments, Branches)

**Input**: Design documents from `/specs/024-multi-tenancy/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Depends on**: All Phase 1 features (existing org_id columns, RLS policies)

## Phase 1: Database Migration & Backfill

**Purpose**: Create organizational hierarchy tables, extend profiles/templates, backfill existing data

- [X] T001 Create migration `formcraft-backend/migrations/027_multi_tenancy.sql` — CREATE TABLE organizations (id, name_ar, name_en, logo_url, primary_color, default_language, default_country, default_currency, custom_domain UNIQUE, settings JSONB, subscription_tier, is_active, timestamps)
- [X] T002 [P] Extend migration: CREATE TABLE departments (id, org_id FK, name_ar, name_en, is_active, created_at) with RLS and indexes
- [X] T003 [P] Extend migration: CREATE TABLE branches (id, department_id FK, org_id FK, name_ar, name_en, location, is_active, created_at) with RLS and indexes
- [X] T004 [P] Extend migration: CREATE TABLE user_invitations (id, email, token UNIQUE, role, org_id FK, department_id FK, branch_id FK, invited_by FK, status, expires_at, accepted_at, created_at) with indexes
- [X] T005 Extend migration: ALTER TABLE profiles ADD COLUMN org_id, department_id, branch_id, is_platform_admin, is_active, invited_by, last_login_at; seed default org; backfill profiles with default org_id; SET NOT NULL; add RLS; add indexes
- [X] T006 Extend migration: ALTER TABLE templates ADD COLUMN department_id (FK → departments, nullable); add index; ALTER TABLE submissions ADD COLUMN branch_id (UUID FK → branches, nullable) if not already present
- [X] T006b Audit all existing tables (templates, submissions, reference_lists, reference_entries, template_feedback, template_print_settings, printer_profiles, audit_logs) — verify each has org_id column with RLS policy using `current_setting('app.current_org_id')::UUID`; add missing RLS policies in migration 027
- [X] T007 [P] Create `formcraft-backend/app/models/organization.py` — SQLAlchemy models: Organization, Department, Branch, UserInvitation
- [X] T008 [P] Create `formcraft-backend/app/schemas/organization.py` — Pydantic schemas: OrgCreate, OrgUpdate, OrgResponse, OrgSettingsUpdate, DepartmentCreate, DepartmentResponse, BranchCreate, BranchResponse, InvitationCreate, InvitationResponse, InvitationAcceptRequest
- [X] T009 [P] Add i18n keys to `formcraft-frontend/src/assets/i18n/ar.json` — org.*, departments.*, branches.*, invitations.*, settings.* keys
- [X] T010 [P] Add i18n keys to `formcraft-frontend/src/assets/i18n/en.json` — same keys in English

---

## Phase 2: Backend Middleware — Org Context

**Purpose**: Set org_id session variable from JWT on every request

- [X] T011 Create org context middleware `formcraft-backend/app/middleware/org_context.py` — extract org_id from JWT claims; execute `SET LOCAL app.current_org_id = '{org_id}'` before DB operations; if is_platform_admin, set `app.is_platform_admin = 'true'`
- [X] T012 Register middleware in `formcraft-backend/app/main.py` — ensure runs after auth middleware but before route handlers
- [X] T013 Update JWT token generation in auth service — include org_id and is_platform_admin in token claims

**Checkpoint**: Every authenticated request has org_id set in DB session. RLS policies automatically filter all queries.

---

## Phase 3: Backend — Organization & Hierarchy CRUD

**Purpose**: Service and routes for managing organizations, departments, and branches

- [X] T014 Create `formcraft-backend/app/services/organization_service.py` — methods: create_org() (platform admin), list_orgs() (platform admin), update_org(), get_org_settings(), update_org_settings(), upload_logo()
- [X] T015 Create `formcraft-backend/app/services/department_service.py` — methods: create_department(), list_departments(), update_department(), deactivate_department() (with active-user check)
- [X] T016 Create `formcraft-backend/app/services/branch_service.py` — methods: create_branch(), list_branches(), list_all_branches(), update_branch(), deactivate_branch() (with active-user check)
- [X] T017 Create `formcraft-backend/app/api/routes/organizations.py` — platform admin routes: POST/GET/PATCH /platform/organizations
- [X] T018 Create `formcraft-backend/app/api/routes/org_settings.py` — org admin routes: GET/PATCH /org/settings, POST /org/logo
- [X] T019 Create `formcraft-backend/app/api/routes/departments.py` — routes: POST/GET/PATCH/DELETE /departments, POST/GET /departments/:id/branches
- [X] T020 Create `formcraft-backend/app/api/routes/branches.py` — routes: GET /branches (flat), PATCH/DELETE /branches/:id
- [X] T021 Register all new routers in `formcraft-backend/app/main.py`

**Checkpoint**: Platform admin can create orgs. Org admin can manage departments and branches.

---

## Phase 4: Backend — User Invitation & Management

**Purpose**: Invitation workflow and enhanced user management

- [X] T022 Create `formcraft-backend/app/services/invitation_service.py` — methods: create_invitation() (generates token, validates email not already active in SAME org, sends email), list_invitations(), cancel_invitation(), accept_invitation() (validates token not expired, creates auth user + profile with role/dept/branch; allows email existing in OTHER orgs), expire_stale_invitations() (called by scheduled cron or DB-level trigger that sets status='expired' WHERE expires_at < now() AND status='pending')
- [X] T023 Create invitation email template — bilingual HTML email with org branding, invitation link, role info, expiry notice
- [X] T024 Update `formcraft-backend/app/services/user_service.py` — add: list_users() (with dept/branch/role filters), update_user_assignment(), deactivate_user(), activate_user(), update_last_login()
- [X] T025 Create `formcraft-backend/app/api/routes/invitations.py` — routes: POST/GET/DELETE /invitations, POST /invitations/:token/accept (public, no auth)
- [X] T026 Update `formcraft-backend/app/api/routes/users.py` — add: GET /users (enhanced with filters), PATCH /users/:id (assignment), POST /users/:id/deactivate, POST /users/:id/activate

**Checkpoint**: Admin can invite users, users can accept invitations. Admin can manage, reassign, deactivate users.

---

## Phase 5: Backend — Template Department Scoping & Submission Tagging

**Purpose**: Filter templates by user's department; auto-tag submissions with branch

- [X] T027 Modify template list query in `formcraft-backend/app/services/template_service.py` — filter: if template.department_id is not null, only return if user.department_id matches OR user is admin; if null, return for all org users
- [X] T028 Modify template create/update in template service — accept optional department_id; validate department belongs to same org
- [X] T029 Modify submission creation — auto-set branch_id from current user's profile.branch_id

**Checkpoint**: Templates scoped by department. Submissions tagged with branch.

---

## Phase 6: Backend — Auth Modifications

**Purpose**: Multi-org login detection, org branding

- [X] T030 Modify login flow in auth service — on login: check if email exists in multiple org profiles; if yes, return requires_org_selection with org list; if no, return normal JWT with org_id claim
- [X] T031 Add `POST /api/auth/login/select-org` endpoint — accepts org_id, returns JWT with that org_id in claims
- [X] T032 Add `GET /api/branding/:domain` public endpoint — lookup org by custom_domain, return name, logo, primary_color (for login page branding)
- [X] T033 Add login guard — check profile.is_active on login; reject deactivated users with appropriate message

**Checkpoint**: Multi-org users see org selector. Login page shows org branding via custom domain. Deactivated users blocked.

---

## Phase 7: Frontend — Org Admin UI

**Purpose**: Admin pages for managing org structure and users

- [X] T034 Create OrgSettingsComponent `formcraft-frontend/src/app/features/admin/org-settings/` — display org profile, edit settings, upload logo, color picker for white-label
- [X] T035 Create DepartmentsComponent `formcraft-frontend/src/app/features/admin/departments/` — mat-table with CRUD, expandable rows showing branches; add/edit dialogs
- [X] T036 Create BranchesComponent — inline within departments view, add/edit dialogs, location field
- [X] T037 Create UserManagementComponent `formcraft-frontend/src/app/features/admin/users/` — enhanced mat-table with filters (dept, branch, role, status); actions: edit assignment, deactivate, activate
- [X] T038 Create InvitationsComponent `formcraft-frontend/src/app/features/admin/invitations/` — invite form (email, role, dept, branch); pending invitations list with resend/cancel
- [X] T039 Create OrgAdminService — Angular HttpClient service wrapping org, dept, branch, invitation, user management endpoints
- [X] T040 Register admin routes — /admin/settings, /admin/departments, /admin/users, /admin/invitations

**Checkpoint**: Admin has full UI for managing org structure, users, and invitations.

---

## Phase 8: Frontend — Invitation Acceptance Flow

**Purpose**: Public pages for invited users to complete registration

- [X] T041 Create InvitationAcceptComponent `formcraft-frontend/src/app/features/auth/invitation/` — public route /invite/:token; shows org name + role assignment; form: display name + password (with strength meter); calls accept endpoint
- [X] T042 Create InvitationExpiredComponent — shown when token is invalid/expired; message + "Contact administrator" guidance
- [X] T043 Add invitation routes to auth routing module — /invite/:token (public, no guard)

**Checkpoint**: Invited users can set up their account via the invitation link.

---

## Phase 9: Frontend — Login & Branding

**Purpose**: Multi-org login selector and branded login page

- [X] T044 Modify LoginComponent — detect `requires_org_selection` response; show org selector dialog with org names + logos; call /login/select-org with chosen org
- [X] T045 Add org branding to login page — on custom domain, call /branding/:domain; apply logo + primary_color to login page
- [X] T046 Add org logo to AppShellComponent nav bar — read org logo from auth context; display in navigation

**Checkpoint**: Login supports multi-org selection and custom branding.

---

## Phase 10: Frontend — Template Scoping & Submission Tagging

**Purpose**: UI reflects department-scoped templates and branch-tagged submissions

- [X] T047 Update template grid in Form Desk — only display templates matching user's department (or org-wide); handled by backend filter, no frontend filter needed
- [X] T048 Add department selector to template create/edit in Design Studio — optional mat-select for department scope (null = org-wide)
- [X] T049 Display branch name on submissions in Submission History — show operator's branch alongside submission metadata

**Checkpoint**: Templates correctly filtered by department. Submissions show branch context.

---

## Phase 11: Integration Testing & Verification

**Purpose**: Verify complete multi-tenancy isolation

- [X] T050 Test RLS isolation — create 2 orgs, create data in each, verify cross-org access returns 404/empty on all major tables (templates, submissions, reference_lists, feedback, etc.)
- [X] T051 Test invitation flow — invite → accept → login → verify correct role/dept/branch → fill form → verify submission tagged with branch
- [X] T052 Test department scoping — create dept-scoped template → verify only same-dept users see it → verify admins see all
- [X] T053 Test deactivation — deactivate user → verify login blocked → reactivate → verify login works
- [X] T054 Test backwards compatibility — verify existing data (default org) works without any changes to existing workflows

**Checkpoint**: Multi-tenancy fully operational with verified isolation, invitation flow, and scoping.

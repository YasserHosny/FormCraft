# Feature Specification: Multi-Tenancy (Organizations, Departments, Branches)

**Feature Branch**: `024-multi-tenancy`  
**Created**: 2026-05-17  
**Status**: Draft  
**Input**: AC-01 — Organization Management, AC-02 — User Management (department/branch assignment); Roadmap 2.1

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Organization Setup (Priority: P1)

A super-admin (FormCraft platform operator) creates a new organization. The org has bilingual name, logo, default language/country, and a settings object for org-wide configuration. All data created within the org is isolated via RLS — users in Org A cannot see Org B's templates, submissions, or reference data.

**Why this priority**: Multi-tenancy is the foundational requirement for enterprise deployment. A single FormCraft instance must serve multiple banks/companies without data leakage. Every subsequent Phase 2 feature depends on org_id scoping.

**Independent Test**: Create Org "National Bank" → create user in that org → create template → login as user in different org → verify template not visible → verify API returns 0 templates → verify direct ID access returns 404.

**Acceptance Scenarios**:

1. **Given** a super-admin creates an organization, **When** providing name_ar, name_en, logo, defaults, **Then** the org is created with a UUID and all settings stored
2. **Given** a user belongs to Org A, **When** they query templates, **Then** only Org A templates are returned (RLS enforced at DB level)
3. **Given** a user attempts to access a template from Org B via direct UUID, **When** the API processes the request, **Then** it returns 404 (not 403, to avoid leaking existence)
4. **Given** an org admin updates org settings, **When** saved, **Then** all org members see the updated configuration (logo in nav, default language preference)
5. **Given** the org has a custom domain configured, **When** users access that domain, **Then** the login page shows org branding (logo, name, primary color)

---

### User Story 2 - Department & Branch Hierarchy (Priority: P1)

An org admin creates departments (e.g., "Retail Banking", "Corporate Banking") and branches within departments (e.g., "Cairo Main", "Giza Branch"). Users are assigned to a department and optionally a branch. Templates can be scoped to specific departments. Submissions are tagged with the branch where they were created.

**Why this priority**: Banks operate across multiple branches and departments. Reporting needs branch-level granularity, and template access often varies by department (corporate forms vs. retail forms).

**Independent Test**: Create department "Retail" → create branch "Cairo Main" under Retail → assign operator to Cairo Main → create template scoped to Retail dept → login as operator → verify template visible → login as Corporate dept user → verify template NOT visible.

**Acceptance Scenarios**:

1. **Given** an admin creates a department, **When** providing name_ar and name_en, **Then** the department appears in the org structure hierarchy
2. **Given** an admin creates a branch under a department, **When** providing name, location, **Then** the branch appears nested under its department
3. **Given** a user is assigned to branch "Cairo Main", **When** they submit a form, **Then** the submission.branch_id is automatically set to their branch
4. **Given** a template is scoped to department "Retail", **When** a "Corporate" user opens Form Desk, **Then** the template does not appear in their available templates
5. **Given** a template has no department scope (org-wide), **When** any user in the org opens Form Desk, **Then** the template is visible to all

---

### User Story 3 - User Assignment & Invitation (Priority: P1)

An org admin assigns users to departments and branches. New users are invited via email with a one-time setup link. The invitation specifies role, department, and branch. Admins can reassign users, deactivate accounts, and view user activity.

**Why this priority**: Secure onboarding without shared credentials. Department/branch assignment drives template access scoping and submission reporting. This replaces manual user creation with a professional invitation workflow.

**Independent Test**: Admin invites user@bank.com with role=operator, dept=Retail, branch=Cairo → user receives email → clicks link → sets password → logs in → sees only Retail templates → submits form → submission tagged with Cairo branch.

**Acceptance Scenarios**:

1. **Given** an admin enters an email + role + department + branch, **When** they click "Send Invitation", **Then** an email is sent with a one-time link (valid 72 hours)
2. **Given** the invited user clicks the link, **When** they set their password and display name, **Then** their profile is created with the pre-assigned role, department, and branch
3. **Given** an admin reassigns a user from "Cairo" to "Giza" branch, **When** the user's next session starts, **Then** their submissions are tagged with "Giza"
4. **Given** an admin deactivates a user, **When** the user attempts to login, **Then** they receive "Account deactivated — contact your administrator"
5. **Given** an invitation link has expired (>72h), **When** the user clicks it, **Then** they see "Invitation expired — contact your administrator for a new invitation"

---

### User Story 4 - Organization Settings & White-Label (Priority: P2)

An org admin configures org-level settings: approval workflow toggle, draft expiry period, data retention policy, allowed file types, and white-label customization (logo, primary color). These settings apply to all users in the org.

**Why this priority**: Each bank has different operational policies. Org-level settings allow FormCraft to serve diverse customers without code changes.

**Independent Test**: Set draft expiry to 14 days → create draft → verify expiry date = created + 14 days. Set primary_color = "#003366" → verify nav bar uses that color. Enable approval workflow → verify templates require review before publish.

**Acceptance Scenarios**:

1. **Given** an admin sets draft_expiry_days to 14, **When** an operator saves a draft, **Then** the draft's expires_at = now + 14 days
2. **Given** an admin uploads a logo, **When** any org user loads the app, **Then** the logo appears in the nav bar and login page
3. **Given** an admin enables the approval workflow, **When** a designer tries to publish directly, **Then** the system requires submit_for_review → approve → publish flow
4. **Given** an admin sets allowed_file_types to ["image/png", "image/jpeg"], **When** an operator tries to upload a PDF attachment, **Then** the upload is rejected with "File type not allowed"

---

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Platform supports multiple organizations with complete data isolation (RLS) | P1 |
| FR-02 | Organization has bilingual name, logo, primary color, default language/country/currency | P1 |
| FR-03 | Admin can create departments within an organization | P1 |
| FR-04 | Admin can create branches within a department (with name + location) | P1 |
| FR-05 | Users are assigned to org + department + branch | P1 |
| FR-06 | Templates can be scoped to a department (or org-wide if no scope) | P1 |
| FR-07 | Submissions automatically tagged with operator's branch_id | P1 |
| FR-08 | Admin can invite users via email with role + department + branch pre-assignment | P1 |
| FR-09 | Invitation link valid for 72 hours, one-time use | P1 |
| FR-10 | Admin can deactivate/reactivate user accounts | P1 |
| FR-11 | Admin can reassign user's department and branch | P1 |
| FR-12 | Org settings: draft_expiry_days, approval_workflow_enabled, allowed_file_types, max_batch_size | P2 |
| FR-13 | White-label: logo, primary_color, custom_domain | P2 |
| FR-14 | All existing tables retroactively enforce org_id via RLS | P1 |
| FR-15 | Super-admin role can manage multiple organizations (platform-level) | P1 |

## Non-Functional Requirements

| ID | Requirement | Metric |
|----|-------------|--------|
| NFR-01 | Zero cross-org data leakage (enforced at DB level, not just API) | 0 cross-org rows returned in any query |
| NFR-02 | Adding org/dept/branch does not degrade query performance for existing data | < 5% latency increase |
| NFR-03 | Invitation email delivered within 30 seconds of send | < 30s delivery |
| NFR-04 | Login page renders org branding within 500ms | < 500ms first meaningful paint |
| NFR-05 | RLS policies must not bypass-able via direct SQL (Supabase service key isolated) | RLS active on all connections |

## Edge Cases

| # | Case | Handling |
|---|------|----------|
| 1 | User belongs to org but no department/branch assigned | User can access org-wide templates only; submissions have null branch_id |
| 2 | Department deleted with users still assigned | Soft-delete: department marked inactive, users remain but get "unassigned" prompt on next login |
| 3 | Branch deleted with submissions linked to it | Submissions retain branch_id (historical); branch marked inactive |
| 4 | Org admin tries to access another org's admin panel | 404 — RLS prevents even admin cross-org access |
| 5 | User invited to org but email already exists in different org | Allow: same email can exist in multiple orgs (multi-org users); login shows org selector |
| 6 | Template scoped to deleted department | Template remains accessible to org admins; warning "Department inactive" shown |
| 7 | Invitation resent for same email (user never completed first invitation) | Previous invitation invalidated; new one issued |
| 8 | Existing single-tenant data migration to multi-tenant | Migration creates default org, assigns all existing data to it |

## Success Criteria

- Bank with 10 departments and 50 branches can onboard all users within 1 hour
- Zero cross-org data leakage verified via automated test suite
- Template scoping correctly limits visibility to assigned department
- Submission reports can filter by branch for reconciliation
- Invitation → active account flow completes in under 2 minutes

# Feature Specification: Platform Admin Console

**Feature Branch**: `039-platform-admin-console`  
**Created**: 2026-05-25  
**Status**: Draft  
**Vision Reference**: PC-01

## User Scenarios & Testing

### User Story 1 - Organization List & Management (Priority: P1)

As a platform admin (`is_platform_admin=true`), I need a dedicated `/platform` section to list all organizations with search, filtering, and sorting, and perform actions (view details, suspend, reactivate), so I can manage the multi-tenant platform from a single interface.

**Why this priority**: Core platform management capability — without this, platform admins must use direct database access or API calls to manage organizations.

**Independent Test**: Login as platform admin, navigate to `/platform/organizations`, see all orgs, search by name, click to view details, suspend an org.

**Acceptance Scenarios**:

1. **Given** a platform admin navigates to `/platform/organizations`, **When** the page loads, **Then** a table shows all organizations with columns: name (AR/EN), subscription tier, active users count, templates count, submissions this month, status (active/suspended), created date.
2. **Given** orgs exist with different tiers, **When** admin filters by "enterprise" tier, **Then** only enterprise organizations are shown.
3. **Given** admin clicks "Suspend" on an organization, **When** confirmed, **Then** all logins for that org are disabled and the status changes to "suspended".
4. **Given** admin clicks "Reactivate" on a suspended org, **When** confirmed, **Then** logins are re-enabled and status changes to "active".

---

### User Story 2 - Create Organization (Priority: P2)

As a platform admin, I need to create new organizations with required fields (name_ar, default_language, default_country, default_currency, subscription tier), which auto-generates the first admin invitation, so I can onboard new customers without direct database access.

**Why this priority**: Onboarding flow — new customers cannot use FormCraft until their org is created and first admin is invited.

**Independent Test**: Click "Create Organization", fill the form, submit, verify org created and first admin invitation generated.

**Acceptance Scenarios**:

1. **Given** platform admin clicks "Create Organization", **When** the form opens, **Then** fields show: name_ar (required), name_en, default_language, default_country, default_currency, subscription tier (starter/professional/enterprise/platform).
2. **Given** admin fills required fields and submits, **When** creation succeeds, **Then** the org detail page opens and a prompt shows "Invite the first admin user" with an email field.
3. **Given** admin enters the first admin's email, **When** invitation is sent, **Then** the invited user receives an email with a one-time setup link.

---

### User Story 3 - Organization Detail View (Priority: P3)

As a platform admin, I need a detailed view of each organization showing profile/branding, subscription info, user overview, and usage statistics across tabs, so I can monitor org health and make support decisions.

**Why this priority**: Support and monitoring — platform admins need visibility into each org to provide support and identify issues.

**Independent Test**: Navigate to `/platform/organizations/:id`, view profile tab, subscription tab, users tab, stats tab.

**Acceptance Scenarios**:

1. **Given** platform admin opens an org's detail page, **When** the Profile tab is active, **Then** org name, logo, domain, branding, and settings are shown (read/write).
2. **Given** the Subscription tab is active, **When** the page loads, **Then** current tier, limits, and usage stats are shown with upgrade/downgrade options.
3. **Given** the Users tab is active, **When** the page loads, **Then** a read-only overview shows user counts by role (admin, designer, operator, viewer).
4. **Given** the Stats tab is active, **When** the page loads, **Then** template count, submissions this month/total, and storage usage are shown.

---

### User Story 4 - Platform Dashboard (Priority: P4)

As a platform admin, I need a landing dashboard at `/platform` showing platform-wide metrics (total orgs, users, submissions), org-by-tier chart, submission volume trend, recently created orgs, and orgs approaching tier limits, so I can monitor platform health at a glance.

**Why this priority**: Overview — platform admins need a summary view before diving into specific orgs.

**Independent Test**: Navigate to `/platform`, see summary cards, charts, and alerts.

**Acceptance Scenarios**:

1. **Given** platform admin navigates to `/platform`, **When** the dashboard loads, **Then** summary cards show: total organizations, total users, total submissions (platform-wide).
2. **Given** organizations exist across tiers, **When** the dashboard loads, **Then** a pie chart shows org distribution by tier.
3. **Given** orgs have submission activity, **When** the dashboard loads, **Then** a line chart shows submission volume trend over the last 12 months.
4. **Given** an org is at 90% of its tier's user limit, **When** the alerts section loads, **Then** an alert shows "Org X approaching user limit (45/50)".

---

### Edge Cases

- What happens when a platform admin tries to delete an organization with active submissions?
- How does suspension work for users currently logged in to the suspended org?
- What happens when a platform admin is also an org admin — how do they switch contexts?
- How does the system handle creating an org with a custom domain that's already in use?

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide a `/platform` route accessible only to users with `is_platform_admin=true`.
- **FR-002**: A new `PlatformAdminGuard` MUST check the `is_platform_admin` flag on the user profile.
- **FR-003**: The nav bar MUST show a "Platform" tab only when `is_platform_admin=true`.
- **FR-004**: System MUST provide an organization list with search, filter (tier, status, country), and sort capabilities.
- **FR-005**: System MUST support organization creation with auto-generated first admin invitation.
- **FR-006**: System MUST support org suspension (disabling all logins) and reactivation.
- **FR-007**: System MUST provide org detail view with tabs: Profile, Subscription, Users, Stats.
- **FR-008**: System MUST provide a platform dashboard with aggregate metrics, charts, and alerts.
- **FR-009**: All platform admin actions MUST be recorded in the audit log.
- **FR-010**: Platform console MUST be completely separate from org admin (`/admin`) routes.

### Key Entities

- **Organization (existing, enhanced)**: Additional computed fields for platform view: active_users_count, templates_count, submissions_this_month, storage_usage.
- **Platform Metric**: Aggregate platform-wide counters: total_orgs, total_users, total_submissions, orgs_by_tier.
- **Tier Limit Alert**: Org reference, limit type (users/templates/storage), current usage, limit, threshold percentage.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Platform dashboard loads aggregate metrics for 100+ organizations within 3 seconds.
- **SC-002**: Organization creation to first admin login takes under 5 minutes.
- **SC-003**: Org suspension takes effect within 30 seconds (active sessions terminated).
- **SC-004**: 100% of platform admin actions are recorded in audit logs.
- **SC-005**: Platform admin can find any organization via search within 3 seconds.

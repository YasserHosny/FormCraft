# Feature Specification: New-Theme Admin Pages - Export, Portal, Integration

**Feature Branch**: `055-spark3-missing-pages`
**Created**: 2026-06-01
**Status**: Draft
**Input**: User description: "Spark 3 not implemented yet pages 'Export', 'Portal', 'Integration'"

---

## Context

The new theme admin console, referred to as Spark 3, currently has three top-level navigation tabs - **Export**, **Portal**, and **Integration** - that appear in the toolbar for admin users but route to old classic-theme pages instead of new-theme screens. This creates a broken user experience: the admin lands on a visually inconsistent classic page in the middle of the new theme.

All three classic-theme pages are fully functional and backed by existing APIs and services. No backend work is required. This feature implements the three missing new-theme pages with feature parity to their classic counterparts, properly integrated into the new theme navigation.

---

## Clarifications

### Session 2026-06-01

- Q: What exact export-size threshold should disable Download after preview? -> A: 50,000 records.
- Q: Should the Integrations page create new API credentials/webhooks or only manage existing ones? -> A: Manage existing only.
- Q: Where should non-admin direct navigation to these admin URLs redirect? -> A: `/ui/dashboard`.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Data Export Page (Priority: P1)

An admin wants to export form submission data in bulk. In the new theme, clicking the "Export" tab should open a new-theme export screen where the admin can filter submissions by template, date range, branch, operator, and status, preview how many records match, and download the result as CSV, XLSX, or JSON. The page also shows the history of previous exports.

**Why this priority**: Export is the most operationally critical of the three. Admins need it to produce compliance reports and feed external systems.

**Independent Test**: Navigate to `/ui/admin/export` while logged in as admin. The export filter form renders in the new-theme visual style. Selecting filters and clicking Preview shows a matching-record count. Clicking Download produces a file. Export history table lists prior exports.

**Acceptance Scenarios**:

1. **Given** an admin is on any new-theme page, **When** they click the "Export" tab in the toolbar, **Then** they are taken to `/ui/admin/export`, a new-theme styled page, not the classic theme.
2. **Given** the export page is open, **When** the admin fills in filter fields and clicks Preview, **Then** the page shows the number of matching submissions and any warnings.
3. **Given** a valid preview result with a downloadable count, **When** the admin clicks Download, **Then** the browser downloads a file in the selected format.
4. **Given** the export page is open, **When** the page loads, **Then** the export history table shows past export requests with date, format, status, and record count.
5. **Given** the matching count exceeds 50,000 records, **When** the preview result is displayed, **Then** the Download button is disabled and an oversized warning is shown.
6. **Given** the page is in Arabic mode, **When** the export page renders, **Then** all labels, filters, and table columns display in Arabic and the layout mirrors correctly.

### User Story 2 - Public Portal Management Page (Priority: P2)

An admin manages which form templates are published as public-facing web portal forms. In the new theme, clicking the "Portal" tab should open a portal management screen where the admin can select a template, enable/disable its public portal, configure OTP verification, captcha, rate limiting, email confirmation, and copy the public URL or scan a QR code.

**Why this priority**: Portal configuration affects external end-users. The classic-theme page works but is visually disconnected from the new theme.

**Independent Test**: Navigate to `/ui/admin/portal` while logged in as admin. The template list renders on the left. Selecting a template shows its portal configuration panel. Toggling "Enable" and saving succeeds. The public URL and QR code display correctly.

**Acceptance Scenarios**:

1. **Given** an admin clicks the "Portal" tab, **When** the page loads, **Then** they see a list of templates with a portal-enabled indicator beside each, rendered in the new-theme style.
2. **Given** the admin selects a template, **When** the configuration panel opens, **Then** they can toggle portal on/off, set the public slug, configure OTP modes, captcha provider, rate limiting, and email confirmation.
3. **Given** the admin saves a portal configuration, **When** the save succeeds, **Then** a success notification appears and the public URL is updated; **When** it fails, an inline error message is shown.
4. **Given** a template has a public URL, **When** the admin views its configuration, **Then** the public URL is displayed as copyable text and a QR code is rendered inline.
5. **Given** a template has portal analytics data, **When** the admin views its configuration, **Then** submission count, OTP success/failure, and rate-limit-hit counts are shown below the configuration panel.
6. **Given** OTP is enabled for a template, **When** the admin enables it, **Then** the allowed OTP modes are shown for selection; disabling OTP hides those options.

### User Story 3 - Integrations Page (Priority: P3)

An admin manages API credentials and webhook subscriptions. In the new theme, clicking the "Integration" tab should open an integrations screen with two sections: API Keys and Webhooks.

**Why this priority**: Integrations are used by technically advanced admins and less frequently than export or portal.

**Independent Test**: Navigate to `/ui/admin/integrations` while logged in as admin. The API keys list renders. The webhooks list renders. An admin can see credential status and toggle webhooks.

**Acceptance Scenarios**:

1. **Given** an admin clicks the "Integration" tab, **When** the page loads, **Then** they see a two-section page in the new-theme style.
2. **Given** the integrations page is open, **When** the API keys section loads, **Then** it lists all credentials with name, key prefix, status, and a Revoke action button.
3. **Given** an active credential exists, **When** the admin clicks Revoke, **Then** the credential status updates to revoked and the Revoke button becomes disabled.
4. **Given** the webhooks section is open, **When** it loads, **Then** it lists all webhooks with URL, subscribed events, status, and a toggle action.
5. **Given** a webhook is active, **When** the admin pauses it, **Then** the status updates to paused; **Given** it is paused, **When** they resume it, **Then** the status returns to active.
6. **Given** no credentials or webhooks exist, **When** the respective section loads, **Then** an empty-state message is displayed.

---

## Edge Cases

- Export preview request fails -> Inline error below the form; Download button stays disabled.
- Template public URL contains special characters -> URL displays verbatim; QR code still renders.
- Export history returns an empty list -> "No previous exports" empty state, not a blank table.
- Admin switches to Arabic mid-session -> All new-theme admin pages re-render in RTL without a page reload.
- Non-admin navigates directly to `/ui/admin/export`, `/ui/admin/portal`, or `/ui/admin/integrations` -> Role guard redirects to `/ui/dashboard`.
- Portal save fails because the public slug is already taken -> Server error is surfaced as an inline validation message.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The new-theme toolbar navigation tabs "Export", "Portal", and "Integration" MUST route to `/ui/admin/export`, `/ui/admin/portal`, and `/ui/admin/integrations` respectively.
- **FR-002**: All three pages MUST be accessible only to users with admin role; non-admin access MUST be rejected.
- **FR-003**: The Export page MUST allow the admin to filter submissions by template, date range, branch, operator, status, format, and export scope.
- **FR-004**: The Export page MUST show a preview of matching submission count and any warnings before download.
- **FR-005**: The Export page MUST allow downloading the filtered dataset; Download MUST be disabled when the matching count exceeds 50,000 records.
- **FR-006**: The Export page MUST display a paginated history of past export requests.
- **FR-007**: The Portal page MUST list all templates with a visible indicator of their portal-enabled status.
- **FR-008**: The Portal page MUST allow the admin to configure portal enabled/disabled, public slug, OTP requirement and modes, captcha, rate limiting, email confirmation, and PDF download toggle per template.
- **FR-009**: The Portal page MUST display the template public URL as copyable text and render a QR code when a public URL exists.
- **FR-010**: The Portal page MUST display per-template portal analytics when data is available.
- **FR-011**: The Portal page MUST show a success notification on successful save and an inline error on failure.
- **FR-012**: The Integrations page MUST display existing API credentials with name, prefix, status, and allow revoking active credentials; creating new credentials is out of scope.
- **FR-013**: The Integrations page MUST display existing webhook subscriptions with URL, event types, status, and allow toggling active/paused state; creating new webhooks is out of scope.
- **FR-014**: All three pages MUST display empty-state messages when their respective data lists are empty.
- **FR-015**: All three pages MUST display loading indicators while data is being fetched.
- **FR-016**: All three pages MUST display inline error messages when data loading fails, with a retry mechanism.
- **FR-017**: All user-visible strings on all three pages MUST use translation keys present in both `en.json` and `ar.json`.
- **FR-018**: All three pages MUST render correctly in RTL layout when Arabic is active.
- **FR-019**: All three pages MUST match the visual design language of the existing new-theme admin pages.

### Key Entities

- **Export Filter**: Template selector, date range, branch, operator, status, format, scope.
- **Export Preview**: Matching count, can-download flag, warnings list.
- **Export Record**: Historical export request with timestamp, format, status, matching count.
- **Portal Configuration**: Enabled state, public slug, OTP, captcha, rate limit, email confirmation, PDF download, public URL.
- **Portal Analytics**: Submission count, OTP metrics, rate-limit hits.
- **API Credential**: Name, key prefix, status, creation date.
- **Webhook Subscription**: URL, subscribed event types, status, creation date.

---

## Success Criteria *(mandatory)*

- **SC-001**: Clicking any of the three new-theme toolbar tabs loads the corresponding new-theme page in under 2 seconds on a standard connection, with no classic-theme redirect.
- **SC-002**: All in-scope features from the classic-theme versions are available in the new-theme versions, excluding scheduled exports and create-new integration flows explicitly marked out of scope.
- **SC-003**: All three pages pass visual inspection in Arabic RTL and English LTR without layout breakage, text overflow, or misaligned controls.
- **SC-004**: All user-visible strings render correctly in Arabic with no missing translation keys.
- **SC-005**: A non-admin user who navigates directly to any of the three new-theme admin URLs is redirected to `/ui/dashboard` and never sees admin page content.
- **SC-006**: Export download completes successfully for a dataset of up to 50,000 records without timeout or error.
- **SC-007**: Portal configuration changes take effect for public portal users within 60 seconds of saving.

---

## Assumptions

- No new backend endpoints are needed; all three pages consume existing APIs via `DataExportService`, `PortalService`, and `IntegrationService`.
- Spark 3 refers to the `ui-redesign` Angular application at the `/ui/` route prefix.
- The visual design reference is the existing Analytics page under `features/ui-redesign/admin/`.
- Export schedules are out of scope for this feature.
- Creating new API credentials or webhook subscriptions is out of scope.
- QR code generation reuses the same approach as the classic portal-admin component.

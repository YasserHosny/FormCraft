# Feature Specification: Operator Dashboard

**Feature Branch**: `015-operator-dashboard`  
**Created**: 2026-05-16  
**Status**: Draft  
**Input**: Form Desk landing page (FD-01) — the operator's personalized workspace for quick form access, draft management, and notifications

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Published Templates Grid with Search (Priority: P1)

When an operator opens the Form Desk dashboard (`/desk`), they see a searchable grid of all published templates available to their organization. They can filter by category, country, and language, and search by template name. Clicking a template card navigates to the Form Filler (`/desk/fill/:templateId`).

**Why this priority**: Without browsable templates, operators have no way to start filling forms. This is the minimum viable dashboard — everything else (pinning, drafts, recents) layers on top.

**Independent Test**: Log in as operator → land on `/desk` → verify published templates appear as cards → search by name → click a card → verify navigation to `/desk/fill/:templateId` (placeholder page for now).

**Acceptance Scenarios**:

1. **Given** an operator navigates to `/desk`, **When** the page loads, **Then** a grid of all published templates for their organization is displayed, sorted by name
2. **Given** 30 published templates exist, **When** the operator views the grid, **Then** templates are paginated (20 per page) with page navigation controls
3. **Given** the operator types "KYC" in the search bar, **When** the search debounces (300ms), **Then** only templates whose name or description contains "KYC" are shown
4. **Given** the operator selects category "Banking" from the filter dropdown, **When** the filter is applied, **Then** only banking-category templates appear
5. **Given** the operator clicks a template card, **When** the navigation fires, **Then** the browser navigates to `/desk/fill/:templateId`
6. **Given** no templates match the search or filters, **When** results are empty, **Then** an empty state message is shown with a "Clear filters" action

---

### User Story 2 - Recently Used Templates (Priority: P1)

The dashboard shows the operator's 10 most recently filled templates, ordered by last-used date (most recent first). This enables one-click access to the forms the operator fills daily.

**Why this priority**: Equal to P1 because bank tellers fill the same 3-5 forms all day. Surfacing recent templates eliminates browsing for repeat usage — the primary operator workflow.

**Independent Test**: Fill a template → return to `/desk` → verify the template appears in "Recently Used" section at the top. Fill another → verify ordering updates.

**Acceptance Scenarios**:

1. **Given** an operator has filled templates A, B, C (most recent: C), **When** they view the dashboard, **Then** "Recently Used" section shows C, B, A in order
2. **Given** an operator has never filled any template, **When** they view the dashboard, **Then** the "Recently Used" section is hidden (not shown with empty state)
3. **Given** the operator fills template A again after template C, **When** they return to the dashboard, **Then** A moves to the top of "Recently Used"
4. **Given** the operator has filled 15 different templates, **When** they view "Recently Used", **Then** only the 10 most recent are shown

---

### User Story 3 - Pinned/Favorite Templates (Priority: P2)

Operators can pin (star) templates to a "Pinned Forms" section that always appears at the top of the dashboard. Pinned forms provide persistent one-click access regardless of recency.

**Why this priority**: High value for operators who have a fixed daily set of forms, but the system is usable without it (recently used covers the common case).

**Independent Test**: Click the star icon on a template card → verify it appears in "Pinned Forms" → unpin → verify it's removed.

**Acceptance Scenarios**:

1. **Given** an operator clicks the pin/star icon on template A, **When** the action completes, **Then** template A appears in the "Pinned Forms" section
2. **Given** an operator has 3 pinned templates, **When** they view the dashboard, **Then** "Pinned Forms" section appears above "Recently Used" with all 3 templates
3. **Given** an operator clicks the unpin icon on a pinned template, **When** the action completes, **Then** the template is removed from "Pinned Forms"
4. **Given** an operator has no pinned templates, **When** they view the dashboard, **Then** the "Pinned Forms" section is hidden
5. **Given** an operator tries to pin more than 20 templates, **When** they click pin, **Then** a toast informs them of the 20-pin limit

---

### User Story 4 - Saved Drafts Section (Priority: P2)

The dashboard shows a "Saved Drafts" section listing partially filled forms the operator has saved. Each draft shows template name, last modified date, and completion percentage. Operators can resume or delete drafts.

**Why this priority**: Drafts prevent data loss when operators are interrupted. However, the draft save/resume mechanism itself is a separate feature (015+ scope). This story covers only the dashboard display of drafts — the actual draft CRUD is a dependency from the Form Filler feature.

**Independent Test**: Save a draft from Form Filler → return to dashboard → verify draft appears → click resume → verify Form Filler loads with saved data.

**Acceptance Scenarios**:

1. **Given** an operator has 3 saved drafts, **When** they view the dashboard, **Then** "Saved Drafts" section shows all 3 with template name, last modified timestamp, and fill completion percentage
2. **Given** a draft was last modified 6 days ago (expires in 1 day), **When** the dashboard loads, **Then** the draft card shows a warning badge "Expires tomorrow"
3. **Given** an operator clicks "Resume" on a draft, **When** the navigation fires, **Then** the Form Filler loads at `/desk/fill/:templateId?draft=:draftId` with previously entered data
4. **Given** an operator clicks "Delete" on a draft, **When** they confirm the deletion, **Then** the draft is removed from the list
5. **Given** an operator has no saved drafts, **When** they view the dashboard, **Then** the "Saved Drafts" section is hidden

---

### User Story 5 - Template Version Notifications (Priority: P3)

When a template the operator has recently used is updated to a new version, a notification appears on the dashboard informing them. This ensures operators are always aware of form changes.

**Why this priority**: Important for compliance but not a day-1 requirement. The system works fine without it — operators always get the latest published version when they start a new form.

**Independent Test**: Publish a new version of a template → log in as operator who used the old version → verify notification appears on dashboard.

**Acceptance Scenarios**:

1. **Given** template "KYC Form" was updated from v1 to v2, **When** an operator who filled v1 views the dashboard, **Then** a notification card says "KYC Form updated to v2"
2. **Given** the operator clicks the notification, **When** the action fires, **Then** they navigate to `/desk/fill/:templateId` (latest version)
3. **Given** the operator dismisses the notification, **When** they refresh the dashboard, **Then** the notification does not reappear

---

### Edge Cases

- What happens when the operator's organization has zero published templates? Dashboard shows an empty state with a message explaining that no forms are available and suggesting they contact their admin.
- What happens when a pinned template is unpublished by a designer? The pinned card shows a "Template unavailable" state and the operator cannot click to fill it. The pin remains but is visually dimmed.
- What happens when the operator loses network while the dashboard is loading? The dashboard shows a connection error with a retry button. Previously cached data (if any) is not shown to avoid stale state.
- What happens on mobile screens (< 768px)? The grid switches from multi-column cards to a single-column list layout. Sections stack vertically.
- What happens when a template's category changes? The template card updates on next dashboard load; no special notification.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Dashboard MUST display all published templates the operator's organization has access to, as a paginated grid of cards
- **FR-002**: Dashboard MUST provide a search bar that filters templates by name and description with 300ms debounce
- **FR-003**: Dashboard MUST provide filter controls for: category, country, language
- **FR-004**: Each template card MUST display: template name (bilingual), category, version number, and a pin/star toggle
- **FR-005**: Dashboard MUST show a "Recently Used" section with the operator's 10 most recently filled templates, ordered by last-used date descending
- **FR-006**: Dashboard MUST allow operators to pin/unpin templates to a "Pinned Forms" section, persisted server-side
- **FR-007**: Dashboard MUST show a "Saved Drafts" section listing unfinished forms with template name, last modified date, completion %, and expiry warning
- **FR-008**: Clicking a template card or "Resume" on a draft MUST navigate to `/desk/fill/:templateId` (or with `?draft=:draftId` for drafts)
- **FR-009**: Dashboard MUST display bilingual labels (Arabic/English) based on user's language preference for all section headings, card labels, and empty states
- **FR-010**: Dashboard MUST show template version update notifications for templates the operator has recently used
- **FR-011**: Dashboard sections with no data MUST be hidden (not shown with empty content), except the main templates grid which shows an empty state message
- **FR-012**: Pin limit MUST be enforced at 20 templates per operator with a user-friendly error message

### Non-Functional Requirements

- **NFR-001**: Dashboard initial load (first meaningful paint) MUST complete within 1 second for up to 200 templates
- **NFR-002**: Search results MUST update within 500ms of the debounce completing
- **NFR-003**: Pin/unpin actions MUST complete (UI update + API call) within 300ms
- **NFR-004**: Dashboard API response MUST be a single aggregated endpoint (not N+1 calls per section)

### Key Entities

- **Template Card**: A published template's summary displayed on the dashboard — name, category, version, country, language, last used date, pinned status
- **Operator Pin**: A join between operator and template representing a pinned/favorite form — persisted server-side for cross-device access
- **Recent Usage**: A record of the last time an operator filled a specific template — derived from submission history or tracked explicitly
- **Draft Summary**: A partially filled form's metadata — template reference, field data snapshot, completion %, last modified, expiry date
- **Version Notification**: An alert generated when a template version increments, targeting operators who used the previous version

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Operator finds and clicks their target form in under 5 seconds from dashboard load (measured via time-to-navigation for recently used / pinned templates)
- **SC-002**: 100% of published templates for the operator's organization are visible and searchable on the dashboard
- **SC-003**: Dashboard loads within 1 second on standard connection (3G+ / 1Mbps) for organizations with up to 200 published templates
- **SC-004**: Pin state and recent usage survive logout/login and cross-device access
- **SC-005**: All dashboard text renders correctly in both Arabic (RTL) and English (LTR) including search, filters, section headings, and card content
- **SC-006**: Zero stale draft data displayed — drafts reflect server-side truth on each dashboard load

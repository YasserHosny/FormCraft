# Feature Specification: New Theme Desk Live Data Integration

**Feature Branch**: `050-new-theme-desk-data`  
**Created**: 2026-05-31  
**Status**: Draft  
**Input**: Replace all hardcoded mock data in the new-theme desk (/ui/desk) with real API data using existing services

## Clarifications

### Session 2026-05-31

- Q: Does "real-time KPIs" mean auto-refreshing or fetch-on-load? → A: Fetch-on-load — fresh data on each page navigation, no background polling.
- Q: How many pinned/frequent templates should the dashboard display? → A: Maximum 6 templates displayed.
- Q: Should the form filler auto-save on navigation away? → A: Yes — auto-save current state as draft when the operator navigates away, preventing data loss.
- Q: Should hardcoded mock data be deleted or kept as fallback? → A: Delete all mock data entirely from components — no fallback arrays, no feature flags.
- Q: How many recent activity items should the dashboard show? → A: Show the 10 most recent items with a "View All" link to the full history page.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Dashboard Shows Real KPIs (Priority: P1)

As an operator opening the new-theme desk dashboard, I see real-time key performance indicators reflecting my actual work — today's submission count, pending drafts count, and active templates count — so I can gauge my workload at a glance.

**Why this priority**: KPIs are the first thing operators see on the dashboard. Displaying fake numbers erodes trust in the entire interface and defeats the purpose of a dashboard.

**Independent Test**: Log in as an operator, navigate to /ui/desk. Verify KPI cards show numbers matching the actual counts returned by the backend. Submit a new form and confirm the KPI updates on next dashboard visit.

**Acceptance Scenarios**:

1. **Given** an operator with 5 submissions today, 3 pending drafts, and 12 active templates, **When** they open the dashboard, **Then** KPI cards display "5", "3", and "12" respectively.
2. **Given** an operator with zero submissions today, **When** they open the dashboard, **Then** the submissions KPI displays "0" (not a placeholder or mock value).
3. **Given** the backend is temporarily unreachable, **When** the dashboard loads, **Then** KPI cards show a loading indicator followed by a user-friendly error state, not hardcoded fallback numbers.

---

### User Story 2 - Recent Activity From Real Submissions (Priority: P1)

As an operator, I see my recent submission activity (form name, customer, status, reference number, timestamp) on the dashboard, drawn from actual submission history, so I can track what I have processed recently.

**Why this priority**: The activity feed is the primary operational view. Without real data, operators cannot use the new theme for daily work.

**Independent Test**: Submit several forms via the classic desk, then navigate to /ui/desk and verify the activity table shows those submissions with correct details.

**Acceptance Scenarios**:

1. **Given** an operator who submitted 3 forms in the last hour, **When** they view the dashboard, **Then** the recent activity table lists those 3 submissions with correct form names, customer names, statuses, reference numbers, and timestamps.
2. **Given** an operator with no submissions, **When** they view the dashboard, **Then** the activity section shows an empty state message (e.g., "No recent activity").
3. **Given** submissions exist in multiple statuses (approved, pending, rejected), **When** the dashboard loads, **Then** each submission displays its correct status with appropriate visual indicator.

---

### User Story 3 - Drafts Panel From Real Drafts (Priority: P1)

As an operator, I see my actual in-progress drafts on the dashboard, so I can resume incomplete form submissions without losing work.

**Why this priority**: Drafts represent uncommitted work. Showing mock drafts prevents operators from finding and resuming their real in-progress forms.

**Independent Test**: Start filling a form, save as draft, then navigate to /ui/desk. Verify the draft appears in the drafts panel with correct form name and timestamp.

**Acceptance Scenarios**:

1. **Given** an operator with 2 saved drafts, **When** they open the dashboard, **Then** the drafts panel lists both drafts with form name, customer name, and last-modified time.
2. **Given** an operator clicks on a draft in the panel, **When** the draft opens, **Then** it navigates to the form filler pre-loaded with the saved draft data.
3. **Given** an operator with no drafts, **When** they view the dashboard, **Then** the drafts panel shows an empty state message.

---

### User Story 4 - Pinned/Frequently Used Templates (Priority: P2)

As an operator, I see my most frequently used or pinned form templates on the dashboard, so I can quickly start filling the forms I use every day.

**Why this priority**: Quick access to common forms improves daily efficiency, but operators can still access all templates through the full template list.

**Independent Test**: As an operator who has submitted forms using certain templates multiple times, verify those templates appear in the pinned/frequent section on the dashboard.

**Acceptance Scenarios**:

1. **Given** an operator who frequently uses 3 templates, **When** they view the dashboard, **Then** those 3 templates appear in the pinned forms section with correct names and template codes.
2. **Given** an operator clicks a pinned template, **When** the action completes, **Then** they are navigated to the form filler for that template.
3. **Given** a newly created operator with no submission history, **When** they view the dashboard, **Then** the pinned section shows published templates as suggestions or an empty state.

---

### User Story 5 - Form Filler With Real Template Structure (Priority: P1)

As an operator filling a form via the new theme, I see the actual template structure (sections, fields, field types, validations) loaded from the system, and I can fill and submit the form with full validation, conditional logic, and auto-fill support.

**Why this priority**: The form filler is the core operational tool. Without real template rendering, the new theme cannot be used for actual work.

**Independent Test**: Navigate to /ui/desk/fill/{templateId}. Verify the form displays real sections and fields matching the template definition. Fill in fields and verify validation rules, conditional visibility, and tafqeet (number-to-words) work correctly. Submit and verify the submission is saved.

**Acceptance Scenarios**:

1. **Given** a published template with 3 sections and 10 fields, **When** an operator opens it in the new-theme filler, **Then** all 3 sections and 10 fields render with correct labels, types, and ordering.
2. **Given** a template with required fields, **When** the operator tries to submit with empty required fields, **Then** validation errors display for each missing field.
3. **Given** a template with conditional fields (e.g., show field B only when field A equals "yes"), **When** the operator changes field A, **Then** field B appears or hides accordingly.
4. **Given** a numeric field with tafqeet enabled, **When** the operator enters a number, **Then** the Arabic number-to-words representation appears.
5. **Given** an operator selects a customer, **When** the customer has profile data matching form fields, **Then** those fields auto-fill with the customer's data.

---

### User Story 6 - Customers Page With Real Data (Priority: P2)

As an operator, I can browse and search real customer profiles from the customers page, so I can look up customer information and initiate forms for specific customers.

**Why this priority**: Customer data supports form filling but operators can still fill forms without the customer lookup page.

**Independent Test**: Navigate to /ui/desk/customers. Verify the list shows real customer records from the system. Search for a customer by name and verify results update.

**Acceptance Scenarios**:

1. **Given** 50 customer profiles exist, **When** an operator opens the customers page, **Then** the list displays real customer names, IDs, and key details with pagination.
2. **Given** an operator searches for "محمد", **When** results load, **Then** only customers whose names match the search appear.
3. **Given** an operator clicks on a customer, **When** the detail view opens, **Then** it shows the customer's real profile data and submission history.

---

### Edge Cases

- What happens when a template is unpublished after an operator pinned it? The pinned forms section should exclude unpublished templates and not show broken entries.
- What happens when a draft references a template that has been updated to a new version? The system should notify the operator and offer to reload with the latest template version.
- What happens when the operator's session expires while filling a form? Since auto-save is always active, the most recent state will already be persisted as a draft. The system redirects to login, and the operator can resume from the auto-saved draft after re-authentication.
- What happens when the backend returns an empty dataset for all sections? Each dashboard section should display an appropriate empty state, not a blank area.
- What happens when the operator has a role that restricts access to certain templates? The dashboard and form filler should only show templates the operator is authorized to access.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Dashboard MUST display KPI counts (today's submissions, pending drafts, active templates) fetched fresh from the backend on each page load (no background polling or auto-refresh).
- **FR-002**: Dashboard MUST display the 10 most recent submission activities, including form name, customer name, status, reference number, and timestamp, ordered by most recent first, with a "View All" link to the full history page.
- **FR-003**: Dashboard MUST display the operator's current drafts with form name, customer name, progress indicator, and last-modified timestamp.
- **FR-004**: Dashboard MUST display up to 6 of the operator's pinned templates (via the existing pin/unpin API), filtered to published-only, allowing one-click navigation to start filling that form.
- **FR-005**: Form filler MUST load the real template structure (sections, fields, field types, labels, ordering) from the published template definition.
- **FR-006**: Form filler MUST apply all field validations (required, pattern, min/max, custom validators) and display inline validation errors.
- **FR-007**: Form filler MUST evaluate conditional logic rules to show/hide fields and sections dynamically based on field values.
- **FR-008**: Form filler MUST support auto-fill from selected customer profile data.
- **FR-009**: Form filler MUST support tafqeet (Arabic number-to-words conversion) for enabled numeric fields.
- **FR-010**: Form filler MUST allow saving in-progress forms as drafts and resuming them later. The form MUST auto-save the current state as a draft when the operator navigates away, preventing accidental data loss.
- **FR-011**: Form filler MUST submit completed forms and create a submission record.
- **FR-012**: Customers page MUST display real customer profiles with search and pagination.
- **FR-013**: All dashboard sections MUST show a loading indicator while data is being fetched.
- **FR-014**: All dashboard sections MUST show an appropriate empty state when no data is available.
- **FR-015**: All components MUST support both RTL (Arabic) and LTR (English) layouts without visual regressions.
- **FR-016**: All components MUST respect the user's role-based permissions, showing only authorized templates and data.
- **FR-017**: All hardcoded mock data arrays and placeholder values MUST be removed entirely from components — no fallback mock data, no feature flags for mock mode.

### Key Entities

- **Dashboard KPI**: Aggregated counts (submissions today, pending drafts, active templates) representing the operator's current workload snapshot.
- **Pinned Template**: A template frequently used by the operator, displayed for quick access. Linked to the operator's usage history or explicit pinning preference.
- **Activity Entry**: A recent submission record showing form name, customer, status, reference, and timestamp.
- **Draft**: An in-progress form submission that has been saved but not yet submitted, with its associated template and partial field data.
- **Customer Profile**: A record containing customer identity and details, used for auto-filling form fields and associating submissions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All dashboard sections (KPIs, activity, drafts, pinned forms) display data from real backend sources with zero hardcoded mock values.
- **SC-002**: Operators can complete a full form submission workflow (select template, fill fields, validate, submit) entirely within the new theme without falling back to the classic theme.
- **SC-003**: Dashboard data loads and renders within 3 seconds on a standard connection.
- **SC-004**: Form validation errors appear inline within 500 milliseconds of the user moving to the next field.
- **SC-005**: Auto-fill from customer profile populates matching fields within 1 second of customer selection.
- **SC-006**: 100% of conditional field visibility rules behave identically to the classic theme form filler.
- **SC-007**: Dashboard correctly handles empty states for all sections (zero submissions, zero drafts, zero pinned templates) without displaying broken UI.
- **SC-008**: All content displays correctly in both Arabic (RTL) and English (LTR) with no layout breakage.

## Assumptions

- All required backend APIs already exist and are used by the classic desk. No new backend endpoints are needed.
- The new theme's visual design and layout will be preserved — this feature only replaces data sources, not the UI structure.
- "Pinned templates" use the existing `DeskService.pinTemplate()`/`unpinTemplate()` API and the `pinned` array returned by `getDashboard()`. No new backend work needed.
- The existing classic desk services can be directly imported into standalone components without modification.
- The form filler in the new theme will support the same field types and validation rules as the classic theme filler.
- Performance targets assume the same backend response times as the classic desk experiences.

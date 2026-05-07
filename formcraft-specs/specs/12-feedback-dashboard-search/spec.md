# Feature Specification: Feedback Dashboard Search & Labels

**Feature Branch**: `012-feedback-dashboard-search`  
**Created**: 2026-05-07  
**Status**: Draft  
**Depends on**: Feature 011 (Customer Feedback) — admin dashboard must exist  
**Input**: Deferred from feature 011 out-of-scope: "Advanced filtering, search on the admin feedback dashboard" and "Feedback categories, labels, or tagging"

## User Scenarios & Testing *(mandatory)*

### User Story 1 – Search and Filter Feedback (Priority: P1)

An admin managing a growing volume of feedback needs to locate specific entries without scrolling through the entire list. They use a keyword search across submission text and apply filters — by status, submitter, or date range — to narrow results instantly.

**Why this priority**: Search and filtering are the most immediate productivity need once submission volume grows. Labels (P2) provide additional filtering axes but require search infrastructure to be useful.

**Independent Test**: Can be tested by submitting several entries with distinct text and statuses, then applying each filter type and a keyword search, verifying only matching entries are returned.

**Acceptance Scenarios**:

1. **Given** an admin on the feedback dashboard, **When** they type a keyword in the search field, **Then** only submissions whose text content contains that keyword are shown, and the matching term is highlighted.
2. **Given** an admin on the feedback dashboard, **When** they select a status filter, **Then** only submissions with that status are shown.
3. **Given** an admin on the feedback dashboard, **When** they set a date range, **Then** only submissions within that range are shown.
4. **Given** an admin on the feedback dashboard, **When** they filter by a specific submitter, **Then** only that user's submissions are shown.
5. **Given** an admin with multiple active filters, **When** they view the list, **Then** only submissions satisfying all active filters simultaneously are shown.
6. **Given** an admin with active filters, **When** they click "Clear filters", **Then** all filters are removed and the full unfiltered list is restored.
7. **Given** an admin who has applied filters, **When** they navigate away and return, **Then** filter state is preserved within the same session.

---

### User Story 2 – Categorize Feedback with Labels (Priority: P2)

An admin reviewing feedback wants to classify entries into meaningful categories (e.g., "Bug Report", "Feature Request", "UI Issue") so that team members can quickly identify and act on relevant submissions. They create labels, assign them to submissions, and filter the dashboard by label.

**Why this priority**: Labels require the dashboard and filtering (P1) to be present before they deliver full organisational value.

**Independent Test**: Can be tested by creating a label, assigning it to a submission, filtering by that label, and verifying only the tagged submission appears.

**Acceptance Scenarios**:

1. **Given** an admin, **When** they create a label with a name and optional colour, **Then** the label is available for assignment and appears in the label management list.
2. **Given** an admin reviewing a feedback submission, **When** they assign one or more labels to it, **Then** the labels appear as chips on that row in the dashboard without a page reload.
3. **Given** an admin on the feedback dashboard, **When** they filter by one or more labels, **Then** submissions carrying any one of the selected labels are shown (OR logic within the label filter).
4. **Given** an admin, **When** they edit a label's name or colour, **Then** the change is immediately reflected on all submissions already tagged with that label.
5. **Given** an admin, **When** they delete a label, **Then** it is removed from all submissions and from the label management list; existing submissions lose only that label.
6. **Given** a non-admin user, **When** they interact with the feedback widget, **Then** labels are not visible and cannot be assigned by the submitter.

---

### Edge Cases

- What if two admins assign conflicting labels simultaneously? → Last write wins; no locking required for v1.
- What if a search query returns zero results? → Show an empty-state message with a "Clear filters" prompt; do not show an error.
- What if a label name already exists? → Block creation and show an inline validation message.
- What if there are more labels than fit in the filter bar? → Show a scrollable or overflow dropdown for label filter selection.

## Requirements *(mandatory)*

### Functional Requirements

#### Search & Filtering (User Story 1)

- **FR-001**: Admin dashboard MUST provide a free-text search field that filters submissions by text content in real time, firing automatically 300–500 ms after the user stops typing (debounced). No explicit submit action is required.
- **FR-002**: Admin dashboard MUST allow filtering by status (new / reviewed / resolved).
- **FR-003**: Admin dashboard MUST allow filtering by submitter (select from a list of users who have submitted feedback).
- **FR-004**: Admin dashboard MUST allow filtering by date range (from date, to date, both optional).
- **FR-005**: Admin dashboard MUST allow filtering by one or more labels (added in P2); multiple selected labels use OR logic — any submission carrying at least one selected label is included.
- **FR-006**: When multiple filters are active, results MUST reflect the intersection of all active filter criteria.
- **FR-007**: Admin dashboard MUST provide a single "Clear filters" action that resets all active filters and the search field.
- **FR-008**: Active filter state MUST be preserved within the same browser session when the admin navigates away and returns.

#### Labels & Categories (User Story 2)

- **FR-009**: System MUST allow admins to create labels with a required name (max 50 characters) and an optional colour chosen from a predefined palette of 8–12 named semantic colours (e.g., red, blue, green, yellow, purple, orange, teal, grey), stored as an enum string. Label management (create, edit, delete) is accessed via a "Manage Labels" button on the feedback dashboard that opens an inline side panel or modal — no separate route is required.
- **FR-010**: Label names MUST be unique; attempting to create a duplicate name MUST be blocked with a validation message.
- **FR-011**: System MUST allow admins to assign up to 5 labels per feedback submission; assignment MUST be reflected in the dashboard without a page reload. Attempting to assign a sixth label MUST be blocked with a validation message.
- **FR-012**: System MUST allow admins to remove a label from a specific submission without affecting other submissions carrying that label.
- **FR-013**: System MUST allow admins to edit an existing label's name or colour; the change MUST be reflected on all tagged submissions immediately.
- **FR-014**: System MUST allow admins to delete a label; deletion MUST remove it from all submissions and from the label list.
- **FR-015**: Admin dashboard MUST display assigned labels as chips on each submission row and in the expanded row view.
- **FR-016**: Labels MUST NOT be visible to or assignable by non-admin users.

### Key Entities

- **FeedbackLabel**: Represents an admin-defined category. Attributes: id, name (max 50 chars, unique), colour (nullable enum string — one of: red, blue, green, yellow, purple, orange, teal, grey, plus up to 4 additional palette entries), created_by, created_at.
- **FeedbackSubmissionLabel**: Join entity linking submissions to labels. Attributes: feedback_id, label_id.
- **FeedbackSubmission** (existing, from feature 011): Extended with label associations via FeedbackSubmissionLabel.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Search results are returned and displayed within 2 seconds for a dataset of up to 10,000 submissions.
- **SC-002**: Applying or clearing a filter updates the visible list within 1 second without a full page reload.
- **SC-003**: Assigning or removing a label on a submission is reflected in the dashboard within 1 second without a page reload.
- **SC-004**: An admin can locate a specific submission by keyword in under 15 seconds.
- **SC-005**: Zero submissions are incorrectly included or excluded when multiple filters are applied simultaneously.

## Assumptions

- Only authenticated admins can create, edit, delete, and assign labels; non-admin users have no visibility of labels.
- Label colours are chosen from a fixed predefined palette — free colour pickers are out of scope.
- Search is performed over text content only; searching by page URL or submitter email is not required in v1.
- Filter state persistence is session-only (browser memory); cross-session persistence (saved filters) is out of scope.
- The submitter filter shows display names resolved from user profiles, not raw user IDs.

## Clarifications

### Session 2026-05-07

- Q: Should text search trigger in real time or require explicit submit? → A: Real-time with debounce — search fires automatically 300–500 ms after the user stops typing (Option A).
- Q: Should multi-label filter use AND or OR logic? → A: OR — submissions carrying any one of the selected labels are shown (Option B).
- Q: Where should label management UI (create/edit/delete) live? → A: Inline panel on the feedback dashboard — a "Manage Labels" button opens a side panel or modal on the same page (Option A).
- Q: What is the maximum number of labels per submission? → A: 5 labels per submission; a sixth assignment is blocked with a validation message (Option B).
- Q: How are label colours stored and how many palette options exist? → A: Named semantic colour enum string (8–12 options: red, blue, green, yellow, purple, orange, teal, grey, etc.) — no hex codes or colour picker (Option A).

## Out of Scope

- Saved or named filter presets.
- Full-text search indexing with relevance ranking (simple ILIKE match is sufficient for v1).
- Label assignment by submitting users.
- Bulk label operations (assign/remove a label from multiple submissions at once).
- Label hierarchies or parent/child label relationships.
- Analytics or aggregations by label (e.g., "30% of feedback is Bug Reports").

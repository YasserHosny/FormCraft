# Feature Specification: Template Feedback

**Feature Branch**: `019-template-feedback`  
**Created**: 2026-05-17  
**Status**: Draft  
**Input**: DS-09 — Template Feedback System; Roadmap 1.8

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Operator Submits Feedback on Template (Priority: P1)

An operator filling a form in Form Desk encounters an issue (unclear field label, missing option, layout problem). They click a feedback button that opens a panel where they can describe the issue, optionally pin it to a specific page or element, and submit. The feedback is linked to the template's current version.

**Why this priority**: Operators are the primary users of templates daily. Without a structured feedback channel, issues are reported via chat/email and lost. Linking feedback to template version enables designers to see exactly which version has the problem.

**Independent Test**: Open form in Form Desk → click feedback button → select page 2 → select element "national_id" → type "Label is confusing — should say National ID Number" → submit → verify feedback appears in designer's panel with template_id, version, page, element reference.

**Acceptance Scenarios**:

1. **Given** an operator has a form open in Form Desk, **When** they click the feedback icon, **Then** a slide-out panel appears with fields: category (bug, suggestion, question), text, and optional page/element selector
2. **Given** the operator selects a page and element, **When** they submit feedback, **Then** the feedback record includes template_id, template_version, page_number, and element_key
3. **Given** feedback is submitted successfully, **When** the operator returns to the form, **Then** a confirmation toast appears and the feedback count badge increments
4. **Given** an operator submits feedback without selecting a specific element, **When** saved, **Then** page_number and element_key are null (general template feedback)

---

### User Story 2 - Designer Views Feedback in Design Studio (Priority: P1)

A designer opens a template in Design Studio and sees a feedback panel showing all feedback for this template (across all versions). They can filter by version, category, status (open/resolved), and page. Each feedback item shows the operator's comment, the version it was submitted against, and a "Resolve" action.

**Why this priority**: Designers need feedback visibility where they work — inside Design Studio, not in a separate admin panel. Version filtering lets them focus on current-version issues.

**Independent Test**: Submit 3 feedback items (2 for v1, 1 for v2) → open template in Design Studio → open feedback panel → verify all 3 appear → filter by v2 → verify only 1 shows → mark as resolved → verify status changes.

**Acceptance Scenarios**:

1. **Given** a designer opens a template with 5 feedback items, **When** they click the feedback tab, **Then** a panel shows all feedback sorted by newest first with category icon, text preview, version badge, and status
2. **Given** the feedback panel is open, **When** the designer filters by "current version", **Then** only feedback for the latest version is shown
3. **Given** a designer clicks "Resolve" on a feedback item, **When** confirmed, **Then** status changes to "resolved", the resolver's name and timestamp are recorded
4. **Given** feedback references a specific element, **When** the designer clicks the feedback item, **Then** the canvas scrolls to and highlights the referenced element

---

### User Story 3 - Admin Feedback Overview (Priority: P2)

An admin views all template feedback across the organization in a dedicated admin page. They can see open/resolved counts per template, identify templates with the most unresolved feedback, and export feedback for reporting.

**Why this priority**: Branch managers and admins need visibility across all templates to prioritize design improvements and track quality.

**Independent Test**: Submit feedback on 3 different templates → navigate to /admin/template-feedback → verify all appear with open counts → filter by "unresolved only" → verify correct count.

**Acceptance Scenarios**:

1. **Given** an admin navigates to /admin/template-feedback, **When** the page loads, **Then** a table shows all templates with columns: template name, version, open count, resolved count, last feedback date
2. **Given** the admin clicks a template row, **When** expanded, **Then** individual feedback items are shown with full text, category, submitter, and date
3. **Given** the admin clicks "Export", **When** the export completes, **Then** a CSV downloads with all feedback data for the selected time range

---

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Operator can submit feedback from Form Desk linked to template_id, template_version, page_number, element_key | P1 |
| FR-02 | Feedback has category: bug, suggestion, question | P1 |
| FR-03 | Feedback text is required (min 10 characters) | P1 |
| FR-04 | Designer can view all feedback for a template in Design Studio panel | P1 |
| FR-05 | Designer can filter feedback by version, category, status, page | P1 |
| FR-06 | Designer can resolve feedback with optional resolution note | P1 |
| FR-07 | Clicking element-linked feedback highlights the element on canvas | P1 |
| FR-08 | Admin can view all template feedback in /admin/template-feedback | P2 |
| FR-09 | Admin can export feedback as CSV | P2 |
| FR-10 | Feedback count badge shows on template card in Design Studio library | P2 |
| FR-11 | All feedback actions (submit, resolve) are recorded in audit trail | P1 |

## Non-Functional Requirements

| ID | Requirement | Metric |
|----|-------------|--------|
| NFR-01 | Feedback submission completes in < 500ms | < 500ms response time |
| NFR-02 | Feedback panel loads within 1 second for templates with up to 100 feedback items | < 1s load time |
| NFR-03 | All feedback scoped by org_id with RLS enforcement | Zero cross-org data leakage |
| NFR-04 | Feedback text stored as plain text (no HTML/scripts) to prevent XSS | Input sanitized |

## Edge Cases

| # | Case | Handling |
|---|------|----------|
| 1 | Operator submits feedback on element that designer later deletes | Feedback preserved with element_key; UI shows "Element no longer exists" |
| 2 | Template version incremented after feedback submitted | Feedback retains original version reference; designer sees it under that version |
| 3 | Operator submits duplicate feedback (same text, same element) within 1 minute | Debounce: reject with "Similar feedback already submitted" |
| 4 | Feedback text contains only whitespace or <10 chars | Validation rejects with specific error |
| 5 | Admin exports feedback for template with 0 items | Empty CSV with headers only |

## Success Criteria

- Operators can submit contextual feedback in under 30 seconds without leaving Form Desk
- Designers can see and resolve feedback without leaving Design Studio
- 90% of feedback includes page/element reference (not just general comments)
- Admin can identify top-3 templates needing attention within 10 seconds

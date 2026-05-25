# Feature Specification: Template Governance

**Feature Branch**: `031-template-governance`  
**Created**: 2026-05-25  
**Status**: Draft  
**Vision Reference**: AC-03

## Clarifications

### Session 2026-05-25

- Q: Does F31 replace or extend the existing F28 approval workflow? → A: F31 extends F28 — keep the existing review queue, add canvas preview + element comments to the review action, add compliance dashboard as a separate tab/page.
- Q: Is "reviewer" a distinct role or does the existing admin role perform reviews? → A: Admin acts as reviewer — no new role; any org admin can review submitted templates (matches current F28 implementation).
- Q: How is the template quality score computed? → A: Automated formula — weighted from: % fields with validators (40%), % fields with bilingual labels (30%), % fields with help text (20%), tab order defined (10%). Computed on read from existing element data.
- Q: What is the lifecycle of element-level review comments? → A: Simple lifecycle — comments are `open` or `resolved`. Designer marks each as resolved (with optional reply) before resubmitting. Admin sees resolution status in next review.
- Q: Are bulk actions constrained by template status? → A: Status-aware guardrails — archive of published templates shows warning ("X operators used this template this month — proceed?"); reassign and re-categorize allowed for all statuses.

## User Scenarios & Testing

### User Story 1 - Admin Template Oversight (Priority: P1)

As an org admin, I need a comprehensive view of all templates across all statuses so I can monitor template health, identify stale templates, and take bulk administrative actions without opening each template individually.

**Why this priority**: Core governance capability — admins cannot govern what they cannot see. This is the foundation for all other governance features.

**Independent Test**: Navigate to `/admin/templates`, see all templates with filters, perform bulk archive on selected templates.

**Acceptance Scenarios**:

1. **Given** an admin navigates to `/admin/templates`, **When** the page loads, **Then** a table shows all templates with columns: name, designer, status, department, category, version, quality score, last modified, and actions.
2. **Given** templates exist in multiple statuses, **When** admin filters by status "draft", **Then** only draft templates are shown.
3. **Given** admin selects 5 templates via checkboxes (including 2 published), **When** admin clicks "Bulk Archive", **Then** a confirmation warning shows "2 published templates selected — 15 operators used them this month. Proceed?" On confirm, all 5 move to archived status with audit log entries.
4. **Given** admin selects templates from different designers, **When** admin clicks "Reassign Designer" and picks a new designer, **Then** all selected templates are reassigned.

---

### User Story 2 - Template Review with Canvas Preview (Priority: P2)

As an org admin (acting as reviewer), I need to open a submitted template in a read-only canvas preview with a side panel showing version diff, designer notes, and previous feedback, so I can make informed approval/rejection decisions with element-level comments. No separate "reviewer" role is introduced; any org admin can perform reviews.

**Why this priority**: Enables quality-gate enforcement — reviewers need more than a table row to make good decisions.

**Independent Test**: Open a submitted template from review queue, view read-only canvas, add element-level comment, approve or reject with comment.

**Acceptance Scenarios**:

1. **Given** a template is in "submitted_for_review" status, **When** reviewer clicks "Review" from the queue, **Then** a read-only canvas preview opens showing the full template layout.
2. **Given** the reviewer is viewing a template update (not first version), **When** the review panel loads, **Then** a version diff section highlights what changed from the previous published version.
3. **Given** the reviewer identifies an issue with a specific element, **When** they click the element and add a comment, **Then** the comment is attached to that element's coordinates and visible to the designer.
4. **Given** reviewer clicks "Request Changes", **When** they submit with element-level comments, **Then** the template returns to "draft" status and the designer sees comments pinned to specific elements.

---

### User Story 3 - Template Compliance Dashboard (Priority: P3)

As an org admin, I need a compliance dashboard showing quality scores across all templates, validator coverage, bilingual label coverage, and staleness alerts so I can identify templates that need attention.

**Why this priority**: Proactive governance — prevents problems before they reach operators.

**Independent Test**: Navigate to compliance dashboard, see aggregated quality metrics, click a flagged template to view details.

**Acceptance Scenarios**:

1. **Given** admin opens the compliance dashboard, **When** templates exist with varying quality scores, **Then** summary cards show: average quality score, % with full validator coverage, % with bilingual labels, count of stale templates (>6 months without update).
2. **Given** a template has fields without validators, **When** admin views the "Missing Validators" list, **Then** each template shows the count and names of unvalidated fields.
3. **Given** a validator rule changes (e.g., national ID format updated), **When** the system detects affected templates, **Then** a "Regulatory Change" alert shows which templates need updating.

---

### Edge Cases

- What happens when a reviewer tries to approve a template that the designer deleted while under review?
- How does the system handle element-level comments when the designer restructures the template after rejection? Comments remain linked to original element_id; if element is deleted, comment shows as "orphaned" with original coordinates but no active element link. Admin can dismiss orphaned comments during next review.
- What happens when bulk reassignment targets a designer in a different department?
- How does staleness calculation handle templates that were recently cloned but not modified?

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide an admin template list view showing all templates across all statuses with filter, sort, and search capabilities.
- **FR-002**: System MUST support bulk actions on selected templates: archive, reassign designer, change category. Bulk archive of published templates MUST show a confirmation warning with usage impact ("X operators used this template this month — proceed?"). Reassign and re-categorize are allowed for all statuses without additional warnings.
- **FR-003**: System MUST extend the existing F28 review queue with a read-only canvas preview for templates in "submitted_for_review" status. The existing review-queue component and ReviewQueueService remain the foundation; canvas preview and element-level comments are added to the review action.
- **FR-004**: Org admins (acting as reviewers) MUST be able to add element-level comments pinned to specific coordinates on the canvas. **All coordinates MUST be stored in millimeters (mm) to preserve print fidelity per Constitution II.** No separate reviewer role is required.
- **FR-005**: System MUST show version diff when reviewing an updated template (comparing to previous published version).
- **FR-006**: System MUST provide a compliance dashboard with aggregated quality metrics across all templates.
- **FR-007**: System MUST flag templates not updated in more than 6 months as "stale" with alerts.
- **FR-008**: System MUST track and display regulatory change impact when validator rules are modified.
  - **FR-008a**: System MUST provide a backend-only admin endpoint `POST /api/admin/validators/{validator_key}/update` to update a validator rule (e.g., national ID format regex). On update, the system MUST create a `validator_change_event` record with the old rule, new rule, and affected template count.
  - **FR-008b**: The compliance dashboard MUST read from `validator_change_events` to surface "Regulatory Change" alerts for templates using the affected validator.
- **FR-009**: All governance actions MUST be recorded in the audit log.

### Key Entities

- **Template Review Comment**: See [data-model.md](data-model.md) for full schema. Element-level comment attached to specific canvas coordinates (in mm), linked to a review session. Lifecycle: `open` → `resolved`. Designer marks resolved with optional reply before resubmitting; admin sees resolution status in next review cycle.
- **Compliance Metric**: Computed quality indicators per template (calculated on read, not stored): validator coverage % (weight: 40%), bilingual label % (weight: 30%), help text coverage % (weight: 20%), tab order defined (weight: 10%). Combined into a 0–100 quality score. Staleness flag derived from last modified date > 6 months.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Admin can view and filter all organization templates from a single page in under 3 seconds.
- **SC-002**: Reviewers complete template reviews 40% faster with canvas preview vs. without.
- **SC-003**: 100% of bulk governance actions are reflected in audit logs.
- **SC-004**: Stale templates identified within 24 hours of crossing the 6-month threshold.
- **SC-005**: Compliance dashboard loads aggregated metrics for 500+ templates in under 5 seconds.

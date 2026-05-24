# Feature Specification: Template Approval Workflow

**Feature Branch**: `028-approval-workflow`    
**Created**: 2026-05-24  
**Status**: Draft  
**Input**: User description: "Template Approval Workflow — Enable multi-stage template review and approval lifecycle (submit for review, approve, reject with comments, publish) with a Reviewer role. Implements vision items DS-08 approval states and AC-03 Template Governance for enterprise compliance."

## Clarifications

### Session 2026-05-24

- Q: When approval workflow is disabled, what publish path should templates take? → A: Direct shortcut — `draft → published` (skip intermediate states entirely). No fake review records created.
- Q: Can a Designer withdraw a template from review before a decision is made? → A: Yes — Designer can self-service withdraw (`submitted_for_review → draft`) any time before a Reviewer acts.

## User Scenarios & Testing

### User Story 1 — Submit, Review & Publish (Priority: P1)

A Designer finishes editing a template and clicks "Submit for Review." The template becomes read-only for the Designer and appears in the review queue visible to Reviewers and Admins. A Reviewer opens the template in a read-only preview, inspects the design and field configuration, and either approves it (with optional notes) or rejects it with mandatory comments explaining what needs to change. When a template is approved, an Admin publishes it, making it available in Form Desk. If rejected, the Designer sees the rejection comments and can revise the template before resubmitting.

**Why this priority**: This is the core approval loop. Without it, any Designer can publish templates directly — a compliance risk for banks and government entities that require governance over customer-facing forms. This is the single most-requested enterprise governance feature.

**Independent Test**: Create a template as Designer, submit for review, log in as Reviewer to approve/reject, log in as Admin to publish. Verify each status transition, read-only enforcement, and comment visibility.

**Acceptance Scenarios**:

1. **Given** a Designer has a template in `draft` status, **When** they click "Submit for Review", **Then** the template status changes to `submitted_for_review`, the template becomes read-only for the Designer, and the template appears in the review queue.
2. **Given** a Reviewer opens a template in `submitted_for_review` status, **When** they click "Approve" and optionally add notes, **Then** the template status changes to `approved` and a review record is created with the Reviewer's identity, timestamp, and notes.
3. **Given** a Reviewer opens a template in `submitted_for_review` status, **When** they click "Reject", **Then** they must provide a comment explaining the reason. The template returns to `draft` status, and the Designer sees the rejection comment.
4. **Given** an Admin views a template in `approved` status, **When** they click "Publish", **Then** the template version increments, the status becomes `published`, and the template becomes available in Form Desk.
5. **Given** a Designer's template was rejected, **When** they view the template, **Then** they see all rejection comments with the Reviewer's name and timestamp. They can edit the template and resubmit.
6. **Given** a Designer has a template in `submitted_for_review` status and no Reviewer has acted yet, **When** the Designer clicks "Withdraw", **Then** the template returns to `draft` status and becomes editable again. A withdrawal audit event is recorded.

---

### User Story 2 — Review Queue & Template Governance Dashboard (Priority: P2)

An Admin or Reviewer needs a centralized view of all templates awaiting review, recently reviewed templates, and the overall governance status across the organization. The review queue shows templates grouped by status (pending review, approved awaiting publish, recently rejected) with filters for department, designer, and date. The governance dashboard shows metrics like average review time, rejection rate, and templates pending for more than a configurable threshold (e.g., 3 days).

**Why this priority**: Without a dedicated queue, Reviewers must hunt through the template list to find items needing attention. The governance dashboard provides organizational oversight for compliance officers.

**Independent Test**: Create multiple templates in various review states, log in as Reviewer/Admin, verify the queue shows correct grouping, filtering, and governance metrics.

**Acceptance Scenarios**:

1. **Given** an organization has 10 templates in various review states, **When** a Reviewer navigates to the review queue, **Then** they see templates grouped into: Pending Review, Approved (Awaiting Publish), and Recently Rejected — each with template name, designer, department, submitted date, and days waiting.
2. **Given** a Reviewer applies a department filter, **When** results refresh, **Then** only templates from that department are shown.
3. **Given** an Admin opens the governance dashboard, **When** the page loads, **Then** they see: total templates pending review, average review turnaround time, rejection rate (percentage), and templates overdue (waiting more than the configurable threshold).
4. **Given** a template has been in `submitted_for_review` for more than 3 days, **When** the queue loads, **Then** that template is highlighted as overdue with a visual indicator.

---

### User Story 3 — Element-Level Review Comments (Priority: P2)

A Reviewer needs to provide granular feedback on specific form elements rather than just an overall approve/reject. When reviewing a template, the Reviewer can click on individual elements on the canvas preview and attach comments — similar to how code review works with inline comments. The Designer sees these comments anchored to the specific elements when they revise the template, making it clear exactly what needs to change.

**Why this priority**: Overall comments like "fix the address section" are ambiguous. Element-level comments reduce back-and-forth iterations by precisely indicating what needs attention, especially on complex forms with 50+ fields.

**Independent Test**: Submit a template for review, add element-level comments as Reviewer, reject, verify Designer sees comments anchored to the correct elements.

**Acceptance Scenarios**:

1. **Given** a Reviewer is previewing a submitted template, **When** they click on a specific element (e.g., "National ID" field), **Then** a comment box appears where they can type feedback specific to that element.
2. **Given** a Reviewer has added 3 element-level comments and 1 overall comment, **When** they reject the template, **Then** all 4 comments are saved and associated with the review record.
3. **Given** a Designer opens a rejected template, **When** they view the canvas, **Then** elements with review comments show a visual indicator (e.g., comment badge). Clicking the indicator reveals the Reviewer's comment.
4. **Given** a Designer fixes an element and resubmits, **When** the Reviewer reviews again, **Then** they can see both their previous comments and the current state of each element.

---

### User Story 4 — Org-Level Approval Settings (Priority: P3)

An Org Admin configures whether the approval workflow is enabled or disabled for their organization. When disabled, Designers can publish templates directly (current behavior). When enabled, the submit-review-approve-publish flow is enforced. The Admin can also configure the overdue review threshold (default: 3 days) and optionally assign default Reviewers per department.

**Why this priority**: Not all organizations need formal approval — small teams may prefer direct publish. The toggle allows FormCraft to serve both enterprise (approval required) and SMB (direct publish) customers with the same codebase.

**Independent Test**: Toggle approval workflow on/off in org settings, verify the template publish flow changes accordingly.

**Acceptance Scenarios**:

1. **Given** an Org Admin navigates to organization settings, **When** they toggle "Approval Workflow" to enabled, **Then** all Designers in the organization must submit templates for review before publishing — direct publish is no longer available.
2. **Given** an Org Admin has approval workflow disabled, **When** a Designer clicks "Publish" on a draft, **Then** the template is published directly without requiring review (existing behavior preserved).
3. **Given** an Org Admin sets the overdue threshold to 5 days, **When** a template has been pending review for 6 days, **Then** it appears as overdue in the review queue.
4. **Given** an Org Admin assigns a default Reviewer to the "Retail Banking" department, **When** a Designer in that department submits a template, **Then** the default Reviewer is suggested (but not enforced — any Reviewer can still review it).

---

### User Story 5 — Review History & Audit Trail (Priority: P3)

All participants (Designer, Reviewer, Admin) can view the complete review history of a template — every submission, review decision, comment, and publish action — as a chronological timeline. This provides full traceability for compliance audits.

**Why this priority**: Banking and government compliance requires demonstrable proof of review and approval for any customer-facing document. The audit trail proves who approved what and when.

**Independent Test**: Put a template through multiple review cycles (submit → reject → revise → resubmit → approve → publish), verify the timeline shows every event with actor and timestamp.

**Acceptance Scenarios**:

1. **Given** a template has been through 3 review cycles, **When** any user opens the template's review history, **Then** they see a chronological timeline showing: each submission, each review decision (approve/reject), all comments (overall and element-level), and the final publish — each with actor name, role, and timestamp.
2. **Given** a compliance officer needs to audit a published template, **When** they view the review history, **Then** they can see exactly who designed it, who reviewed it, who approved it, and who published it — with no gaps in the chain.
3. **Given** a template's review history is viewed, **When** the user clicks "Export Audit Trail", **Then** a document is generated containing the complete review timeline suitable for compliance records.

---

### Edge Cases

- What happens when a Reviewer tries to review their own template? The system prevents self-review — a different Reviewer must review it. If the organization has only one user with review permissions, the Admin can approve directly.
- What happens when a template is submitted for review but the only Reviewer is deactivated? The Admin can still approve or reject since Admins have Reviewer capabilities.
- What happens when a Designer edits a template that is currently under review? They cannot — the template is read-only in `submitted_for_review` status. They must wait for a decision or ask an Admin to return it to draft.
- What happens when approval workflow is enabled mid-session and a template is already in `draft` status? Existing drafts follow the new rules — they must go through review to be published.
- What happens when approval workflow is disabled while templates are in `submitted_for_review` or `approved` status? Those templates remain in their current state. An Admin can either publish them directly or transition them back to draft. The settings page displays a warning count of in-flight items before confirming the toggle.
- What happens when a Reviewer adds element-level comments but the Designer deletes that element in revision? The comment is preserved in history but marked as "element removed" so the Reviewer can see what changed.

## Requirements

### Functional Requirements

- **FR-001**: System MUST support a template status lifecycle: `draft` → `submitted_for_review` → `approved` or `rejected` → `published` → `archived` or `deprecated`. A rejected template returns to `draft` for revision. Withdrawal is defined in FR-019.
- **FR-002**: System MUST enforce role-based transition permissions: Designers can submit for review, Reviewers and Admins can approve or reject, and only Admins can publish.
- **FR-003**: System MUST require a mandatory comment when rejecting a template, explaining what needs to change.
- **FR-004**: System MUST make templates read-only for Designers while in `submitted_for_review` or `approved` status. Only Admins can force-return an `approved` template to draft. Designers can withdraw their own templates from `submitted_for_review` via FR-019.
- **FR-005**: System MUST provide a review queue showing all templates in `submitted_for_review` status, filterable by department, designer, and date range, and sortable by submission date and days waiting.
- **FR-006**: System MUST support element-level review comments — Reviewers can attach comments to specific form elements during review, visible to the Designer on revision.
- **FR-007**: System MUST store a complete review history (all submissions, decisions, comments) per template as an immutable timeline.
- **FR-008**: System MUST support an organization-level toggle to enable or disable the approval workflow. When disabled, templates follow a direct `draft → published` shortcut — intermediate states (`submitted_for_review`, `approved`) are skipped entirely, and no review records are created.
- **FR-009**: When approval workflow is enabled, the system MUST prevent direct publish — the only path to `published` is through the review-approve flow.
- **FR-010**: System MUST prevent self-review — a Designer cannot review their own template submission.
- **FR-011**: System MUST display rejection comments to the Designer when they open a rejected template, with clear indication of which review cycle the comments belong to.
- **FR-012**: System MUST provide a governance dashboard showing: templates pending review count, average review turnaround time, rejection rate, and overdue items (past configurable threshold).
- **FR-013**: System MUST support a configurable overdue review threshold (default: 3 days) per organization.
- **FR-014**: System MUST highlight overdue templates in the review queue with a visual indicator.
- **FR-015**: System MUST log all status transitions as audit events with actor identity, timestamp, before/after status, and any comments.
- **FR-016**: System MUST support bilingual display (Arabic/English) for all approval workflow UI elements, review comments, and status labels.
- **FR-017**: System MUST allow Admins to assign default Reviewers per department as a suggestion — not a hard assignment.
- **FR-018**: System MUST allow exporting a template's review audit trail as a document for compliance records.
- **FR-019**: System MUST allow Designers to withdraw a template from review (`submitted_for_review → draft`) at any time before a Reviewer has made a decision. Withdrawal logs an audit event and clears the pending review entry.

### Non-Functional Requirements

- **NFR-001**: The review queue MUST load within 2 seconds for organizations with up to 500 templates.
- **NFR-002**: Status transitions MUST complete within 1 second including audit log creation.
- **NFR-003**: All review data (comments, decisions, timestamps) MUST respect multi-tenant isolation — no cross-organization data leakage.
- **NFR-004**: Element-level comments MUST correctly reference elements even after template revision, using stable element identifiers.

### Key Entities

- **Template Review**: A decision record created when a Reviewer approves or rejects a template. Contains reviewer identity, decision (approved/rejected), overall comment, element-level comments, and timestamp. Multiple reviews can exist per template (one per review cycle).
- **Review Comment**: A piece of feedback attached either to the overall template or to a specific element. Contains the commenter, comment text, and optionally the element key it references.
- **Approval Configuration**: Organization-level settings controlling whether the approval workflow is active, the overdue threshold, and default Reviewer assignments per department.

## Assumptions

- The existing backend state machine (draft → submitted_for_review → approved/rejected → published) and `POST /templates/:id/transition` endpoint already handle the core status transitions. This feature extends the UX, adds element-level comments, builds the review queue/governance dashboard, and wires up the org-level toggle.
- The `template_reviews` table already exists and stores review records. This feature may extend it with element-level comments.
- The `approval_workflow_enabled` field already exists in the org settings schema. This feature wires up the frontend toggle and enforcement logic.
- The Reviewer role is currently served by `branch_manager` and `admin` roles. This feature does NOT introduce a new "reviewer" role — instead, it uses the existing role hierarchy where branch_managers and admins can review templates. A dedicated Reviewer role may be added in a future iteration if organizations need separation of reviewer and branch management duties.
- Notifications for review events (submitted, approved, rejected, published) are out of scope for this feature — they will be addressed by the Notification Center feature (vision item AC-06). This feature focuses on the workflow mechanics and UI.
- The read-only canvas preview for Reviewers reuses the existing Design Studio canvas in view-only mode — no new canvas implementation needed.

## Dependencies

- **F19 Template Versioning**: Provides the template lifecycle states, `lineage_id`, and version tracking that the approval workflow extends.
- **F25 Multi-Tenancy**: Organization, department, and branch scoping for review queue filtering and org-level settings.
- **F01 Auth & Users**: Role-based access control determines who can submit, review, and publish.
- **F08 Security & Audit**: Audit logging infrastructure for recording all status transitions and review actions.
- **F02 i18n**: Bilingual support for all approval workflow labels and review comments.

## Out of Scope

- Notification delivery for review events (email, in-app) — deferred to Notification Center feature.
- Dedicated "Reviewer" role separate from branch_manager — deferred to future role management enhancement.
- Multi-stage review (sequential reviewers, e.g., technical review then compliance review) — this feature implements single-stage review only.
- Template diff view (visual comparison between versions) — deferred to a separate feature (vision item 3.15).
- Automated review rules (e.g., auto-approve templates that only change metadata) — deferred to future iteration.
- Custom approval workflows per template category — all templates follow the same single-stage review process.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A template can complete the full lifecycle (draft → submit → review → approve → publish) within 5 user interactions, each completing in under 2 seconds.
- **SC-002**: 100% of published templates in organizations with approval workflow enabled have at least one review record with reviewer identity and timestamp — no unreviewed templates can reach production.
- **SC-003**: Reviewers can locate and begin reviewing a pending template within 30 seconds of opening the review queue.
- **SC-004**: Designers see rejection comments within 1 click of opening a rejected template — no hunting through separate screens.
- **SC-005**: The governance dashboard accurately reflects real-time review metrics (pending count, average turnaround, rejection rate) with data no more than 1 minute stale.
- **SC-006**: All status transitions produce audit log entries with actor, action, before/after status, and comments — zero gaps in the audit trail for any published template.

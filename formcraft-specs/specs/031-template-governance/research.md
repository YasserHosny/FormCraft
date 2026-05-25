# Research: Template Governance

## Decision: Extend F28 Review Queue Instead Of Replacing It

**Rationale**: The existing backend already exposes `/api/admin/review-queue`, `ReviewQueueService`, `template_reviews`, status transition rules, notification hooks, and a review timeline. F31 explicitly extends F28, so the implementation should add review context and element-comment capabilities to the existing review action rather than creating a second approval workflow.

**Alternatives considered**:
- Build a new `/api/admin/template-governance/reviews` subsystem. Rejected because it would duplicate status transitions and increase risk of divergent review state.
- Store all new review UI state only in `template_reviews.element_comments`. Rejected because lifecycle requirements (`open`/`resolved`, designer replies, orphaned comments) are awkward and inefficient inside append-only review JSON.

## Decision: Add `template_review_comments` For Lifecycle-Aware Element Comments

**Rationale**: Existing `template_reviews.element_comments` can keep review action snapshots, but F31 requires comments to remain open/resolved across rejection, designer edits, resubmission, and next review. A normalized `template_review_comments` table supports filtering open comments, resolving with designer reply, orphan handling when elements are deleted, RLS, and audit logging.

**Alternatives considered**:
- Embed status and replies in `template_reviews.element_comments` JSONB. Rejected because updates would mutate historical review records and complicate querying open comments.
- Reuse generic `template_feedback`. Rejected because review comments are governance decisions by admins, not operator/design feedback.

## Decision: Compute Quality Score On Read From Existing Template Data

**Rationale**: The spec requires an automated formula and says compliance metric is calculated on read, not stored. The backend can fetch templates with pages/elements and compute weighted coverage: validator coverage 40%, bilingual labels 30%, help text 20%, tab order 10%. This avoids stale cached scores and keeps changes to element metadata immediately visible.

**Alternatives considered**:
- Persist `templates.quality_score`. Rejected because it conflicts with the spec and requires invalidation across element edits.
- Compute metrics only in Angular. Rejected because backend filtering/export and future reports need consistent server-side computation.

## Decision: Implement Admin Template Oversight As `/api/admin/templates`

**Rationale**: `/api/templates` is a mixed-role template CRUD API used by designers and app workflows. F31 needs admin-only all-status list, bulk archive, bulk reassignment, category changes, usage-impact warnings, and compliance fields. A dedicated admin route keeps governance permissions clear while reusing `TemplateService` internals where appropriate.

**Alternatives considered**:
- Expand `/api/templates` with admin query flags. Rejected because it risks weakening role scoping and complicates existing designer/operator uses.
- Put all governance endpoints under `/api/admin/review-queue`. Rejected because all-status oversight and bulk actions are broader than the review queue.

## Decision: Usage Impact Uses Monthly Submission Counts

**Rationale**: The bulk archive warning needs "X operators used this template this month". Existing `form_submissions` contains `template_id`, `operator_id`, `created_at`, and `org_id`. Counting distinct operators for selected published templates in the current calendar month gives a direct, auditable warning without introducing telemetry.

**Alternatives considered**:
- Use recent template dashboard/favorites data. Rejected because it measures interest, not actual usage.
- Use audit logs. Rejected because print/submit actions may be inconsistent historically and are slower to query for usage impact.

## Decision: Version Diff Reuses Existing `TemplateService.compute_diff`

**Rationale**: The backend already exposes `/api/templates/{template_id}/diff?compare_to=...` and frontend has version diff components. Review context should include the previous published version id/summary or let the frontend call the existing diff endpoint. This avoids a second diff algorithm.

**Alternatives considered**:
- Build a separate review-specific diff format. Rejected unless existing diff proves insufficient during implementation.
- Diff in the browser only. Rejected because backend already owns template version lineage and can identify the previous published version reliably.

## Decision: Regulatory Change Alerts Are Derived From Validator Change Records

**Rationale**: The app has built-in validators and custom validators. F31 requires impact when validator rules are modified. The plan adds a lightweight `validator_change_events` table for org/custom validator changes and built-in rule migration markers. Compliance service joins impacted validator keys against template elements' validation JSON and reports affected templates.

**Alternatives considered**:
- Scan all templates without storing validator changes. Rejected because the dashboard would not know which regulatory change triggered the alert.
- Store alert rows per template. Rejected initially because impact can be computed from current validator keys and recent change events.

## Decision: Read-Only Canvas Preview Reuses Designer Canvas Rendering Concepts

**Rationale**: The review workspace needs accurate visual layout without edit controls. The existing designer canvas service uses Konva and understands template pages/elements. A read-only review component should reuse rendering concepts but avoid mutating the designer page. Element click selection should only open/comment on coordinates.

**Alternatives considered**:
- Render review preview as PDF/image only. Rejected because element-level comments need element hit testing and coordinate pinning.
- Open the designer page in disabled mode. Possible fallback, but a dedicated review workspace is cleaner for version diff, notes, comments, and review actions.

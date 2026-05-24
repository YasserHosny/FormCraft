# Tasks: Template Approval Workflow

**Input**: Design documents from `/specs/028-approval-workflow/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/approval-api.md, quickstart.md

**Tests**: Not explicitly requested in spec — test tasks omitted. Use quickstart.md scenarios for manual validation.

**Organization**: Tasks grouped by user story (US1–US5) to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US5)
- Exact file paths included in every task description

## Path Conventions

- **Backend**: `formcraft-backend/`
- **Frontend**: `formcraft-frontend/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Database migration, shared schemas, and TypeScript models used across all user stories.

- [X] T001 Create database migration in `formcraft-backend/migrations/030_approval_workflow.sql` — ADD `element_comments JSONB DEFAULT NULL` column to `template_reviews` table, CREATE `department_default_reviewers` table (id UUID PK, department_id UUID FK UNIQUE, reviewer_id UUID FK, org_id UUID FK, created_at TIMESTAMPTZ DEFAULT NOW()) with RLS policy scoped by org_id, ADD composite index `idx_templates_org_status(org_id, status)` on `templates` table for review queue performance
- [X] T002 [P] Create review queue schemas in `formcraft-backend/app/schemas/review_queue.py` — define Pydantic models: `ReviewQueueItem` (template_id, template_name, category, status, version, designer_id, designer_name, department_name, submitted_at, days_waiting, is_overdue), `ReviewQueueResponse` (items list, total, overdue_count), `GovernanceMetrics` (pending_count, approved_awaiting_publish, avg_turnaround_days, rejection_rate_pct, overdue_count, total_reviews, overdue_threshold_days), `TimelineEvent` (event, actor_id, actor_name, actor_role, timestamp, comment, element_comments), `TimelineResponse` (template_id, template_name, timeline list), `DefaultReviewerRequest` (reviewer_id), `DefaultReviewerResponse` (department_id, reviewer_id, reviewer_name)
- [X] T003 [P] Create shared TypeScript interfaces in `formcraft-frontend/src/app/shared/models/review.models.ts` — define interfaces: `ReviewQueueItem`, `ReviewQueueResponse`, `GovernanceMetrics`, `TimelineEvent`, `TimelineResponse`, `ElementComment` (element_key, comment), `ReviewRecord` (id, template_id, reviewer_id, reviewer_name, action, comment, element_comments, created_at), `DefaultReviewer` (department_id, reviewer_id, reviewer_name)

**Checkpoint**: Migration ready, shared types defined in backend and frontend. No behavioral changes yet.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Extend existing backend schemas and service logic that ALL user stories depend on.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 Extend `TransitionRequest` schema in `formcraft-backend/app/schemas/template.py` — add optional field `element_comments: list[dict] | None = None` (each dict has `element_key: str` and `comment: str`). Also extend `TemplateReviewResponse` to include `element_comments: list[dict] | None` in the response model.
- [X] T005 Extend `transition_status()` in `formcraft-backend/app/services/template_service.py` — add three new behaviors: (1) **Self-review prevention**: before allowing `submitted_for_review → approved` or `submitted_for_review → rejected`, compare `template.created_by` with `actor_id` and return 403 if they match. (2) **Withdrawal**: add `submitted_for_review → draft` to allowed transitions for roles `["designer", "admin"]`, log audit event `TEMPLATE_WITHDRAWN`. (3) **Approval-disabled shortcut**: when target status is `published` and source is `draft`, check org setting `approval_workflow_enabled`; if `false` and actor is designer+, allow `draft → published` directly; if `true`, return 422 requiring review flow. (4) **Element comments**: when `element_comments` is provided and action is `approved` or `rejected`, store them in the `template_reviews` record's new `element_comments` JSONB column.
- [X] T006 Extend `get_reviews()` in `formcraft-backend/app/services/template_service.py` — include `element_comments` field in the review records returned by `GET /templates/{id}/reviews`. Join with `profiles` to include `reviewer_name` in each review record.

**Checkpoint**: Core backend logic extended. Transition endpoint now supports self-review prevention, withdrawal, approval-disabled shortcut, and element comments. All user stories can proceed.

---

## Phase 3: User Story 1 — Submit, Review & Publish (Priority: P1) MVP

**Goal**: Complete lifecycle: Designer submits template for review, Reviewer approves/rejects with comments, Admin publishes. Designers can withdraw before review.

**Independent Test**: Quickstart Scenario 1 (Full Approval Lifecycle), Scenario 2 (Self-Review Prevention), Scenario 3 (Designer Withdrawal). Use API smoke tests from quickstart.md.

### Implementation for User Story 1

- [X] T007 [US1] Extend transition route in `formcraft-backend/app/api/routes/templates.py` — update `POST /templates/{template_id}/transition` handler to pass `element_comments` from `TransitionRequest` to `transition_status()`. Add proper error response handling: 403 for self-review attempts (with message "Cannot review your own template"), 422 for direct publish when approval enabled (with message "Approval workflow requires review before publishing"), 422 for invalid withdrawal.
- [X] T008 [P] [US1] Create submit-review component in `formcraft-frontend/src/app/features/studio/designer/submit-review/submit-review.component.ts` — component with: (1) "Submit for Review" button visible when template is in `draft` status and `approval_workflow_enabled` is true, (2) "Publish" button visible when template is in `draft` status and `approval_workflow_enabled` is false (direct shortcut), (3) "Withdraw" button visible when template is in `submitted_for_review` status and current user is the creator, (4) Status banner showing current template status with bilingual labels (ar/en), (5) Read-only indicator when template is in `submitted_for_review` or `approved` status.
- [X] T009 [P] [US1] Create submit-review template in `formcraft-frontend/src/app/features/studio/designer/submit-review/submit-review.component.html` — render conditional buttons ("Submit for Review" / "Publish" / "Withdraw"), status chip with color coding (draft=grey, submitted=blue, approved=green, rejected=red, published=teal), and a read-only banner when template is locked for review. Include Angular Material button, chip, and banner components.
- [X] T010 [P] [US1] Create submit-review styles in `formcraft-frontend/src/app/features/studio/designer/submit-review/submit-review.component.scss` — style status banner, action buttons, read-only overlay indicator. Support RTL layout via `[dir="rtl"]` selectors.
- [ ] T011 [US1] Integrate submit-review component into the designer page — add the `<app-submit-review>` component to the existing designer layout (alongside the canvas toolbar area) in the appropriate designer component. Pass template data and approval_workflow_enabled org setting as inputs. Wire up button click events to call `POST /templates/{id}/transition` with appropriate status values. When template status is `submitted_for_review` or `approved`, disable all canvas editing interactions (element drag, resize, property panel edits) by leveraging the existing view-only mode.
- [ ] T012 [US1] Add rejection comments display to designer — when a template has status `rejected`, call `GET /templates/{id}/reviews` and display the most recent rejection's overall comment prominently in the submit-review component. Show reviewer name and timestamp. Style as a warning card with Material theming.

**Checkpoint**: Full submit/review/approve/publish lifecycle works end-to-end. Test with Quickstart Scenarios 1, 2, and 3.

---

## Phase 4: User Story 2 — Review Queue & Governance Dashboard (Priority: P2)

**Goal**: Centralized review queue for Reviewers/Admins with filtering, sorting, and overdue highlighting. Governance dashboard with metrics.

**Independent Test**: Quickstart Scenario 5 (Review Queue), Scenario 7 (Governance Dashboard).

### Implementation for User Story 2

- [X] T013 [US2] Create review queue service in `formcraft-backend/app/services/review_queue_service.py` — implement: (1) `get_review_queue(org_id, filters)`: query `templates` table joined with `profiles` and `departments`, filter by status (default: submitted_for_review), department_id, designer_id; calculate `days_waiting` as days since `updated_at`; determine `is_overdue` by comparing against org's `review_overdue_threshold_days` setting (default 3); scope results for branch_manager to only their department's templates. (2) `get_governance_metrics(org_id, since)`: compute pending_count, approved_awaiting_publish, avg_turnaround_days, rejection_rate_pct, overdue_count, total_reviews from `template_reviews` and `templates` tables.
- [X] T014 [US2] Create review queue routes in `formcraft-backend/app/api/routes/review_queue.py` — implement: (1) `GET /admin/review-queue` with query params (status, department_id, designer_id, sort_by, sort_dir), role gate admin/branch_manager. (2) `GET /admin/review-queue/metrics` with query param `since` (YYYY-MM-DD, default 30 days ago), role gate admin only. Register the router in the main app with prefix `/api/admin/review-queue`.
- [X] T015 [US2] Register review queue router in `formcraft-backend/app/main.py` or equivalent app initialization file — add `from app.api.routes.review_queue import router as review_queue_router` and register with `app.include_router(review_queue_router, prefix="/api/admin")`.
- [X] T016 [P] [US2] Implement review queue component in `formcraft-frontend/src/app/features/admin/review-queue/review-queue.component.ts` — replace scaffolded content with full implementation: (1) Load review queue items from `GET /admin/review-queue`, (2) Filter controls: status dropdown (submitted_for_review, approved, rejected, all), department dropdown (populated from org departments), designer search, (3) Sort controls: submitted_at, days_waiting, name with asc/desc toggle, (4) Display as Material table with columns: template name, category, designer, department, submitted date, days waiting, status, actions (Review button), (5) Overdue rows highlighted with warning color, (6) Overdue count badge in header.
- [X] T017 [P] [US2] Create review queue template in `formcraft-frontend/src/app/features/admin/review-queue/review-queue.component.html` — Material table with `mat-sort`, filter bar with `mat-select` for status and department, `mat-form-field` for designer search, overdue badge counter, "Review" action button per row linking to the template designer in preview mode.
- [X] T018 [P] [US2] Create review queue styles in `formcraft-frontend/src/app/features/admin/review-queue/review-queue.component.scss` — style overdue row highlighting (amber background), status chips with color coding, filter bar layout, responsive table. Support RTL.
- [X] T019 [P] [US2] Create governance dashboard component in `formcraft-frontend/src/app/features/admin/governance-dashboard/governance-dashboard.component.ts` — load metrics from `GET /admin/review-queue/metrics`, display 4 metric cards: (1) Pending Reviews (count), (2) Avg Turnaround (days), (3) Rejection Rate (percentage), (4) Overdue (count with warning styling if > 0). Include a date range selector for the `since` parameter.
- [X] T020 [P] [US2] Create governance dashboard template and styles in `formcraft-frontend/src/app/features/admin/governance-dashboard/governance-dashboard.component.html` and `.scss` — Material card grid layout, metric values with labels, color coding (red for overdue > 0, green for low rejection rate), responsive grid, RTL support.
- [ ] T021 [US2] Add admin routing for review queue and governance dashboard — register `/admin/review-queue` and `/admin/governance` routes in the admin module routing (likely `formcraft-frontend/src/app/features/admin/admin-routing.module.ts` or equivalent), add navigation links in admin sidebar/menu.

**Checkpoint**: Review queue and governance dashboard fully functional. Test with Quickstart Scenarios 5 and 7.

---

## Phase 5: User Story 3 — Element-Level Review Comments (Priority: P2)

**Goal**: Reviewers can attach comments to specific form elements during review. Designers see element-anchored comments when revising.

**Independent Test**: Quickstart Scenario 6 (Element-Level Comments).

### Implementation for User Story 3

- [X] T022 [P] [US3] Create review panel component in `formcraft-frontend/src/app/features/studio/designer/review-panel/review-panel.component.ts` — component for Reviewers to add element-level comments during review: (1) Activate when user is a reviewer and template is in `submitted_for_review`, (2) On element click on the canvas, open a comment popover anchored to that element, (3) Track comments as `ElementComment[]` (element_key, comment), (4) Include "Add Overall Comment" text area, (5) "Approve" and "Reject" action buttons that call `POST /templates/{id}/transition` with collected element_comments and overall comment, (6) Require at least overall comment when rejecting.
- [X] T023 [P] [US3] Create review panel template and styles in `formcraft-frontend/src/app/features/studio/designer/review-panel/review-panel.component.html` and `.scss` — comment popover anchored to element position, Material textarea for comments, floating action bar with Approve/Reject buttons, element comment count badge, overall comment section. RTL support.
- [ ] T024 [US3] Integrate review panel into designer — add `<app-review-panel>` to the designer layout, conditionally shown when the current user has reviewer role and the template status is `submitted_for_review`. Wire element click events from the canvas to the review panel's comment creation flow. Pass template elements list for element_key mapping.
- [ ] T025 [US3] Add element comment badges to designer canvas — when viewing a template with existing review comments (loaded from `GET /templates/{id}/reviews`), overlay comment badges on elements that have comments. Clicking a badge opens a read-only popover showing the reviewer's comment, reviewer name, and timestamp. For designers, this enables seeing exactly which elements need attention. When an `element_key` from a review comment no longer exists in the current template elements list, show the comment in a separate "Removed Elements" section with an "element removed" indicator instead of anchoring to the canvas.

**Checkpoint**: Element-level review comments work end-to-end. Test with Quickstart Scenario 6.

---

## Phase 6: User Story 4 — Org-Level Approval Settings (Priority: P3)

**Goal**: Admins configure approval workflow toggle, overdue threshold, and default reviewers per department.

**Independent Test**: Quickstart Scenario 4 (Approval Workflow Disabled), Scenario 9 (Default Reviewer Assignment).

### Implementation for User Story 4

- [X] T026 [US4] Add default reviewer endpoints to review queue routes in `formcraft-backend/app/api/routes/review_queue.py` — implement: (1) `GET /admin/departments/{department_id}/default-reviewer` returning reviewer_id and reviewer_name (404 if none assigned), (2) `PUT /admin/departments/{department_id}/default-reviewer` accepting `{reviewer_id}` body, creating or updating the `department_default_reviewers` record, (3) `DELETE /admin/departments/{department_id}/default-reviewer` removing the assignment (204). All role-gated to admin.
- [X] T027 [US4] Add default reviewer service methods in `formcraft-backend/app/services/review_queue_service.py` — implement: (1) `get_default_reviewer(org_id, department_id)`: query `department_default_reviewers` joined with `profiles` for reviewer_name, (2) `set_default_reviewer(org_id, department_id, reviewer_id)`: upsert into `department_default_reviewers`, (3) `remove_default_reviewer(org_id, department_id)`: delete from `department_default_reviewers`.
- [X] T028 [US4] Add overdue threshold to org settings — extend the org settings update flow (if not already present) to accept `review_overdue_threshold_days` (integer, default 3) in the organization's settings JSONB column. Ensure it is readable by `review_queue_service.py` when computing `is_overdue`.
- [ ] T029 [P] [US4] Add approval workflow toggle UI to org settings page — in the existing org settings frontend component (likely in `formcraft-frontend/src/app/features/admin/` org settings area), add: (1) Material slide toggle for "Approval Workflow" with bilingual label, (2) Number input for "Overdue Review Threshold (days)" (default: 3, min: 1), (3) Save button persisting to org settings API. Show/hide the threshold input based on toggle state.
- [ ] T030 [P] [US4] Add default reviewer assignment UI — in the departments management section of admin, add a "Default Reviewer" dropdown per department showing branch_managers and admins from that department's org. Wire to `PUT /admin/departments/{id}/default-reviewer` on change and `DELETE` on clear. Show current assignment from `GET /admin/departments/{id}/default-reviewer`.

**Checkpoint**: Org settings control the approval workflow behavior. Test with Quickstart Scenarios 4 and 9.

---

## Phase 7: User Story 5 — Review History & Audit Trail (Priority: P3)

**Goal**: Chronological timeline of all review events per template. PDF export for compliance.

**Independent Test**: Quickstart Scenario 8 (Review History Timeline).

### Implementation for User Story 5

- [X] T031 [US5] Add timeline service methods in `formcraft-backend/app/services/review_queue_service.py` — implement: (1) `get_timeline(org_id, template_id)`: query `template_reviews` joined with `profiles` (for actor_name) and `audit_logs` (for submission/publish events), ordered by timestamp ascending. Map each record to `TimelineEvent` schema. Include events: submitted_for_review, approved, rejected, withdrawn, published. (2) `export_timeline_pdf(org_id, template_id)`: use WeasyPrint to generate a PDF containing template name, all timeline events in a table with columns: Date/Time, Event, Actor, Role, Comment. Include element-level comments as sub-rows. Add header with org name and export date.
- [X] T032 [US5] Add timeline and export routes in `formcraft-backend/app/api/routes/review_queue.py` — implement: (1) `GET /admin/review-queue/{template_id}/timeline` returning `TimelineResponse`. Role gate: admin sees all, branch_manager sees own department templates, designer sees own templates. (2) `POST /admin/review-queue/{template_id}/export-timeline` returning `application/pdf` with `Content-Disposition: attachment` header. Role gate: admin, branch_manager.
- [X] T033 [P] [US5] Create review timeline component in `formcraft-frontend/src/app/features/admin/review-timeline/review-timeline.component.ts` — load timeline from `GET /admin/review-queue/{id}/timeline`, display as a vertical Material stepper/timeline: each step shows event type icon (submit=send, approve=check, reject=close, publish=cloud_upload, withdraw=undo), actor name and role, timestamp, comment (if any), element comments (expandable list). Include "Export Audit Trail" button triggering PDF download.
- [X] T034 [P] [US5] Create review timeline template and styles in `formcraft-frontend/src/app/features/admin/review-timeline/review-timeline.component.html` and `.scss` — vertical timeline layout with Material icons, event cards with comment sections, expandable element comments, export button. RTL support with mirrored timeline rail.
- [ ] T035 [US5] Integrate timeline access — add "View History" button/link to: (1) review queue table rows (for reviewers/admins), (2) template detail view in designer (for designers viewing own templates). Route to `/admin/review-timeline/{template_id}` or open as a side panel/dialog.

**Checkpoint**: Complete audit trail visible and exportable. Test with Quickstart Scenario 8.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Bilingual support, NFR validation, and final integration testing.

- [ ] T036 [P] Add bilingual labels for all approval workflow UI — add Arabic and English translations for: status labels (draft, submitted_for_review, approved, rejected, published, withdrawn), button labels (Submit for Review, Approve, Reject, Withdraw, Publish, Export Audit Trail), review queue headers, governance dashboard labels, timeline event names, error messages. Add to the existing i18n translation files in `formcraft-frontend/src/assets/i18n/`.
- [ ] T037 [P] Add bilingual labels for backend error messages — ensure all error responses from approval workflow endpoints include bilingual messages (ar/en) following existing patterns in `formcraft-backend/`.
- [ ] T038 NFR performance validation — verify review queue loads in < 2s with 500 templates by checking the composite index `idx_templates_org_status` is used in query plans. Verify status transitions complete in < 1s including audit log creation.
- [ ] T039 NFR security validation — verify multi-tenant isolation: review queue, governance metrics, timeline, and default reviewer endpoints all filter by `org_id` from the authenticated user's context. Verify no cross-org data leakage in review records or element comments.
- [ ] T040 Run quickstart.md validation — execute all 10 test scenarios from `formcraft-specs/specs/028-approval-workflow/quickstart.md` and all API smoke tests. Document any gaps found and address them.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on T001 (migration) — BLOCKS all user stories
- **User Stories (Phase 3–7)**: All depend on Foundational phase completion
  - US1 (P1): Can start immediately after Phase 2
  - US2 (P2): Can start after Phase 2, independent of US1
  - US3 (P2): Can start after Phase 2, independent of US1/US2 (but integrates with designer from US1)
  - US4 (P3): Can start after Phase 2, independent (but approval toggle affects US1 behavior)
  - US5 (P3): Can start after Phase 2, benefits from US2 routes file existing
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Standalone after Phase 2. Creates the submit-review component other stories reference.
- **US2 (P2)**: Standalone after Phase 2. Creates `review_queue.py` routes file that US4 and US5 extend.
- **US3 (P2)**: Standalone after Phase 2. Integrates with designer canvas (shares designer layout with US1).
- **US4 (P3)**: Extends `review_queue.py` from US2 (adds default reviewer endpoints). Recommended after US2.
- **US5 (P3)**: Extends `review_queue.py` from US2 (adds timeline/export endpoints). Recommended after US2.

### Recommended Execution Order

```
Phase 1 → Phase 2 → US1 (MVP) → US2 → [US3 ∥ US4 ∥ US5] → Polish
```

### Within Each User Story

- Models/schemas before services
- Services before route handlers
- Backend before frontend
- Core components before integration
- Story complete before moving to next priority

### Parallel Opportunities

- T002 + T003 can run in parallel (backend schemas and frontend models)
- Within US1: T008 + T009 + T010 (frontend component files)
- Within US2: T016 + T017 + T018 + T019 + T020 (frontend components)
- Within US3: T022 + T023 (component files)
- Within US4: T029 + T030 (frontend components)
- Within US5: T033 + T034 (timeline component files)
- T036 + T037 (bilingual labels)

---

## Parallel Example: User Story 2

```bash
# After T013 (service) and T014 (routes) complete sequentially:

# Launch all frontend components in parallel:
Task T016: "Review queue component TS"
Task T017: "Review queue template HTML"
Task T018: "Review queue styles SCSS"
Task T019: "Governance dashboard component TS"
Task T020: "Governance dashboard template + styles"

# Then integrate:
Task T021: "Admin routing registration"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (migration + shared types)
2. Complete Phase 2: Foundational (extend transition logic)
3. Complete Phase 3: User Story 1 (submit/review/publish lifecycle)
4. **STOP and VALIDATE**: Test with Quickstart Scenarios 1, 2, 3
5. Deploy/demo — core approval workflow is functional

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 → Test → Deploy (MVP: core lifecycle works)
3. US2 → Test → Deploy (Reviewers have a dedicated queue + metrics)
4. US3 → Test → Deploy (Element-level feedback improves review quality)
5. US4 → Test → Deploy (Orgs can toggle workflow on/off)
6. US5 → Test → Deploy (Full audit trail for compliance)
7. Polish → Final validation with all 10 quickstart scenarios

### Parallel Team Strategy

With multiple developers after Phase 2:
- Developer A: US1 (backend + frontend)
- Developer B: US2 (backend + frontend)
- After US2 routes file exists: Developer C takes US4 + US5

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Backend extends existing `template_service.py` and `templates.py` routes — do NOT rebuild
- Frontend `review-queue/` component already exists (scaffolded) — extend, do not recreate
- All statuses already exist in `enums.py` — no enum changes needed
- Migration is numbered 030 (after existing 001–029)
- Element comments keyed by element `key` (stable identifier), NOT element `id` (UUID)
- WeasyPrint already in project dependencies (used by PDF engine) — reuse for timeline export
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently

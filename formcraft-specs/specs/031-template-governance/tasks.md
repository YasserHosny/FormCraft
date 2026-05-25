# Tasks: Template Governance

**Input**: Design documents from `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-specs/specs/031-template-governance/`
**Prerequisites**: [plan.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/031-template-governance/plan.md), [spec.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/031-template-governance/spec.md), [research.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/031-template-governance/research.md), [data-model.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/031-template-governance/data-model.md), [contracts/openapi.yaml](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/031-template-governance/contracts/openapi.yaml), [quickstart.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/031-template-governance/quickstart.md)

**Tests**: Required by the FormCraft Constitution. Test tasks must be written first and fail before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup

**Purpose**: Prepare shared files, routing slots, and test scaffolding.

- [ ] T001 Create backend governance route placeholder in `formcraft-backend/app/api/routes/admin_templates.py`
- [ ] T002 Register the admin templates router in `formcraft-backend/app/main.py`
- [ ] T003 [P] Create backend schema placeholder in `formcraft-backend/app/schemas/admin_templates.py`
- [ ] T004 [P] Create backend governance service placeholder in `formcraft-backend/app/services/template_governance_service.py`
- [ ] T005 [P] Create backend compliance service placeholder in `formcraft-backend/app/services/compliance_service.py`
- [ ] T006 [P] Create frontend governance models placeholder in `formcraft-frontend/src/app/shared/models/governance.models.ts`
- [ ] T007 [P] Create frontend governance API service placeholder in `formcraft-frontend/src/app/core/services/template-governance.service.ts`
- [ ] T008 Add admin child routes for `/admin/templates`, `/admin/templates/compliance`, and `/admin/reviews/:template_id` in `formcraft-frontend/src/app/features/admin/admin.module.ts`

---

## Phase 2: Foundational

**Purpose**: Shared schema, normalized persistence, RLS, and utilities required before user stories.

**Critical**: No user story implementation should begin until this phase is complete.

- [ ] T009 Write failing migration validation test for `template_review_comments` and `validator_change_events` in `formcraft-backend/tests/integration/test_template_governance_routes.py`
- [ ] T010 Create Supabase migration for `template_review_comments`, `validator_change_events`, indexes, RLS policies, and audit fields in `formcraft-backend/migrations/033_template_governance.sql`
- [ ] T011 Implement shared Pydantic DTOs for review comments, bulk actions, governance list items, and compliance responses in `formcraft-backend/app/schemas/admin_templates.py`
- [ ] T012 Extend review queue Pydantic DTOs for review context and lifecycle comments in `formcraft-backend/app/schemas/review_queue.py`
- [ ] T013 [P] Implement governance TypeScript interfaces matching the OpenAPI contract in `formcraft-frontend/src/app/shared/models/governance.models.ts`
- [ ] T014 [P] Add Arabic and English i18n keys for governance, bulk actions, review workspace, and compliance UI in `formcraft-frontend/src/assets/i18n/en.json`
- [ ] T015 [P] Add Arabic and English i18n keys for governance, bulk actions, review workspace, and compliance UI in `formcraft-frontend/src/assets/i18n/ar.json`
- [ ] T016 Add admin navigation entry for Template Governance in `formcraft-frontend/src/app/shared/components/app-shell/app-shell.component.ts`

**Checkpoint**: Database, schemas, frontend models, and admin routing are ready.

---

## Phase 3: User Story 1 - Admin Template Oversight (Priority: P1)

**Goal**: Admins can view all organization templates, filter/sort/search them, and perform bulk archive/reassign/category actions with usage warnings and audit logs.

**Independent Test**: Navigate to `/admin/templates`, filter templates by status, select multiple templates, preview and execute bulk archive with published-template usage warning.

### Tests for User Story 1

- [ ] T017 [P] [US1] Write failing contract tests for `GET /api/admin/templates` response shape, filters, sorting, and admin-only access in `formcraft-backend/tests/integration/test_template_governance_routes.py`
- [ ] T018 [P] [US1] Write failing contract tests for `POST /api/admin/templates/bulk-actions` dry-run and execution responses in `formcraft-backend/tests/integration/test_template_governance_routes.py`
- [ ] T019 [P] [US1] Write failing unit tests for monthly published-template usage counting and bulk action guardrails in `formcraft-backend/tests/unit/test_template_governance_service.py`
- [ ] T020 [P] [US1] Write failing frontend service tests for governance list and bulk action calls in `formcraft-frontend/src/app/core/services/template-governance.service.spec.ts`

### Implementation for User Story 1

- [ ] T021 [US1] Implement admin template list query with org scoping, filters, sorting, pagination, designer joins, department joins, and computed quality summary in `formcraft-backend/app/services/template_governance_service.py`
- [ ] T022 [US1] Implement bulk action dry-run logic including published count and current-month distinct operator usage warning in `formcraft-backend/app/services/template_governance_service.py`
- [ ] T023 [US1] Implement bulk archive, reassign designer, and change category execution with status-aware validation in `formcraft-backend/app/services/template_governance_service.py`
- [ ] T024 [US1] Add audit events `TEMPLATE_BULK_ARCHIVED`, `TEMPLATE_REASSIGNED`, and `TEMPLATE_CATEGORY_CHANGED` in `formcraft-backend/app/services/template_governance_service.py`
- [ ] T025 [US1] Expose `GET /api/admin/templates` and `POST /api/admin/templates/bulk-actions` with admin-only guards in `formcraft-backend/app/api/routes/admin_templates.py`
- [ ] T026 [US1] Implement Angular API methods for template governance list and bulk actions in `formcraft-frontend/src/app/core/services/template-governance.service.ts`
- [ ] T027 [P] [US1] Create admin template governance component class with filters, selection state, sorting, pagination, and bulk action handlers in `formcraft-frontend/src/app/features/admin/template-governance/template-governance.component.ts`
- [ ] T028 [P] [US1] Create admin template governance template with Material table, translated filters, checkboxes, quality score, and bulk action controls in `formcraft-frontend/src/app/features/admin/template-governance/template-governance.component.html`
- [ ] T029 [P] [US1] Create admin template governance styles with RTL/LTR-safe spacing and responsive table behavior in `formcraft-frontend/src/app/features/admin/template-governance/template-governance.component.scss`
- [ ] T030 [US1] Add bulk archive confirmation dialog with published-template usage warning in `formcraft-frontend/src/app/features/admin/template-governance/template-governance.component.ts`
- [ ] T031 [US1] Wire Template Governance standalone component into `formcraft-frontend/src/app/features/admin/admin.module.ts`

**Checkpoint**: User Story 1 is functional and independently testable as the MVP.

---

## Phase 4: User Story 2 - Template Review With Canvas Preview (Priority: P2)

**Goal**: Admins can open submitted templates in a read-only canvas review workspace, inspect version diff and context, add element-level comments, approve, or request changes.

**Independent Test**: Open a submitted template from the review queue, see read-only canvas, add a pinned comment, request changes, and verify the designer can resolve the comment before resubmission.

### Tests for User Story 2

- [ ] T032 [P] [US2] Write failing contract tests for `GET /api/admin/review-queue/{template_id}/review-context` in `formcraft-backend/tests/integration/test_template_governance_routes.py`
- [ ] T033 [P] [US2] Write failing contract tests for creating and listing review comments in `formcraft-backend/tests/integration/test_template_governance_routes.py`
- [ ] T034 [P] [US2] Write failing contract tests for resolving review comments as designer/admin in `formcraft-backend/tests/integration/test_template_governance_routes.py`
- [ ] T035 [P] [US2] Write failing contract tests that block designer resubmission while unresolved review comments exist in `formcraft-backend/tests/integration/test_template_governance_routes.py`
- [ ] T036 [P] [US2] Write failing unit tests for comment orphan handling and review context assembly in `formcraft-backend/tests/unit/test_review_queue_service.py`
- [ ] T037 [P] [US2] Write failing frontend service tests for review context and comments in `formcraft-frontend/src/app/core/services/review-queue.service.spec.ts`

### Implementation for User Story 2

- [ ] T038 [US2] Implement review context assembly with template pages, elements, previous published version id, diff summary, feedback summary, and open/resolved comments in `formcraft-backend/app/services/review_queue_service.py`
- [ ] T039 [US2] Implement create review comment service logic with mm coordinates, element links, org scoping, and audit event `TEMPLATE_REVIEW_COMMENT_CREATED` in `formcraft-backend/app/services/review_queue_service.py`
- [ ] T040 [US2] Implement list and resolve review comments with designer replies, `open -> resolved` transition, orphan display support, and audit event `TEMPLATE_REVIEW_COMMENT_RESOLVED` in `formcraft-backend/app/services/review_queue_service.py`
- [ ] T041 [US2] Add review context and admin create-comment endpoints in `formcraft-backend/app/api/routes/review_queue.py`
- [ ] T042 [US2] Add designer/admin visible list-comment and resolve-comment endpoints matching `/api/templates/{template_id}/review-comments` in `formcraft-backend/app/api/routes/templates.py`
- [ ] T043 [US2] Add template resubmission guard that rejects submission when open review comments exist, returning the unresolved comment count in `formcraft-backend/app/services/template_service.py`
- [ ] T044 [US2] Extend `TransitionRequest` to submit lifecycle comment snapshots during approve/reject/request-changes in `formcraft-backend/app/schemas/template.py`
- [ ] T045 [US2] Update template status transition handling to persist compatible review snapshots without replacing normalized comments in `formcraft-backend/app/services/template_service.py`
- [ ] T046 [US2] Extend Angular review queue service for review context/comment creation in `formcraft-frontend/src/app/core/services/review-queue.service.ts` and the template API client for comment listing/resolution in `formcraft-frontend/src/app/core/services/template.service.ts`
- [ ] T047 [US2] Update existing review queue actions to navigate to `/admin/reviews/:template_id` instead of prompt-only approval/rejection in `formcraft-frontend/src/app/features/admin/review-queue/review-queue.component.ts`
- [ ] T048 [US2] Create review workspace component class with read-only canvas setup, selected element tracking, comment pins, diff data, and review actions in `formcraft-frontend/src/app/features/admin/review-workspace/review-workspace.component.ts`
- [ ] T049 [US2] Create review workspace template with canvas area, side panel, version diff section, previous feedback, comment form, and translated approve/request-changes controls in `formcraft-frontend/src/app/features/admin/review-workspace/review-workspace.component.html`
- [ ] T050 [US2] Create review workspace styles with RTL/LTR-safe panel layout and stable canvas dimensions in `formcraft-frontend/src/app/features/admin/review-workspace/review-workspace.component.scss`
- [ ] T051 [US2] Add designer-visible review comment panel or section for rejected templates in `formcraft-frontend/src/app/features/designer/designer-page/designer-page.component.ts`
- [ ] T052 [US2] Render designer-visible review comments and resolve controls with translation keys in `formcraft-frontend/src/app/features/designer/designer-page/designer-page.component.html`
- [ ] T053 [US2] Add RTL/LTR-safe comment pin and panel styling for designer review comments in `formcraft-frontend/src/app/features/designer/designer-page/designer-page.component.scss`
- [ ] T054 [US2] Wire Review Workspace standalone component into `formcraft-frontend/src/app/features/admin/admin.module.ts`

**Checkpoint**: User Story 2 is functional and independently testable without requiring the compliance dashboard.

---

## Phase 5: User Story 3 - Template Compliance Dashboard (Priority: P3)

**Goal**: Admins can view aggregated quality metrics, stale templates, missing validator/bilingual label lists, and regulatory change impact.

**Independent Test**: Navigate to `/admin/templates/compliance`, see summary cards and flagged templates, and verify a validator change event surfaces affected templates.

### Tests for User Story 3

- [ ] T055 [P] [US3] Write failing unit tests for quality score formula weights and edge cases in `formcraft-backend/tests/unit/test_compliance_service.py`
- [ ] T056 [P] [US3] Write failing unit tests for stale template detection and missing-field extraction in `formcraft-backend/tests/unit/test_compliance_service.py`
- [ ] T057 [P] [US3] Write failing contract tests for `GET /api/admin/templates/compliance` in `formcraft-backend/tests/integration/test_template_governance_routes.py`
- [ ] T058 [P] [US3] Write failing frontend service tests for compliance dashboard API calls in `formcraft-frontend/src/app/core/services/template-governance.service.spec.ts`

### Implementation for User Story 3

- [ ] T059 [US3] Implement deterministic quality score computation for validator coverage, bilingual labels, help text, and tab order in `formcraft-backend/app/services/compliance_service.py`
- [ ] T060 [US3] Implement stale template detection, missing validator extraction, and missing bilingual label extraction in `formcraft-backend/app/services/compliance_service.py`
- [ ] T061 [US3] Implement regulatory impact matching from `validator_change_events` to element validation metadata in `formcraft-backend/app/services/compliance_service.py`
- [ ] T062 [US3] Expose `GET /api/admin/templates/compliance` with admin-only guard and org scoping in `formcraft-backend/app/api/routes/admin_templates.py`
- [ ] T063 [US3] Add compliance dashboard API method in `formcraft-frontend/src/app/core/services/template-governance.service.ts`
- [ ] T064 [P] [US3] Create compliance dashboard component class with filters, summary data, flagged-template lists, and drilldown state in `formcraft-frontend/src/app/features/admin/compliance-dashboard/compliance-dashboard.component.ts`
- [ ] T065 [P] [US3] Create compliance dashboard template with summary cards, missing validators list, bilingual coverage list, stale templates, and regulatory alerts in `formcraft-frontend/src/app/features/admin/compliance-dashboard/compliance-dashboard.component.html`
- [ ] T066 [P] [US3] Create compliance dashboard styles with Arabic-first RTL and LTR mirrored layouts in `formcraft-frontend/src/app/features/admin/compliance-dashboard/compliance-dashboard.component.scss`
- [ ] T067 [US3] Wire Compliance Dashboard standalone component into `formcraft-frontend/src/app/features/admin/admin.module.ts`

**Checkpoint**: User Story 3 is functional and independently testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate constitution compliance, performance, docs, and end-to-end flows.

- [ ] T068 [P] Verify no hardcoded user-facing strings were introduced in `formcraft-frontend/src/app/features/admin/template-governance/`
- [ ] T069 [P] Verify no hardcoded user-facing strings were introduced in `formcraft-frontend/src/app/features/admin/review-workspace/`
- [ ] T070 [P] Verify no hardcoded user-facing strings were introduced in `formcraft-frontend/src/app/features/admin/compliance-dashboard/`
- [ ] T071 [P] Add quickstart API smoke examples to project documentation in `formcraft-specs/specs/031-template-governance/quickstart.md`
- [ ] T072 Run backend tests for F31 in `formcraft-backend/tests/unit/test_compliance_service.py` and `formcraft-backend/tests/integration/test_template_governance_routes.py`
- [ ] T073 Run backend lint with `ruff check .` in `formcraft-backend/`
- [ ] T074 Run frontend build with `npm run build` in `formcraft-frontend/`
- [ ] T075 Manually validate the quickstart flow from admin list through review comments and compliance dashboard using `formcraft-specs/specs/031-template-governance/quickstart.md`
- [ ] T076 Update implementation notes and status after validation in `formcraft-specs/specs/031-template-governance/tasks.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational; recommended MVP.
- **User Story 2 (Phase 4)**: Depends on Foundational and can start after US1 backend route scaffolding exists; review queue UI benefits from US1 navigation but remains independently testable.
- **User Story 3 (Phase 5)**: Depends on Foundational and can run in parallel with US1/US2 after shared compliance DTOs exist.
- **Polish (Phase 6)**: Depends on desired user stories being complete.

### User Story Dependencies

- **US1 Admin Template Oversight**: MVP; no dependency on US2 or US3.
- **US2 Template Review with Canvas Preview**: Extends existing F28 review queue; independent of US3.
- **US3 Template Compliance Dashboard**: Reuses compliance service concepts also visible in US1 list; independent endpoint and UI.

### Within Each User Story

- Write tests first and confirm they fail.
- Implement backend schemas before services.
- Implement services before routes.
- Implement Angular models/services before components.
- Add i18n keys before final UI validation.

---

## Parallel Execution Examples

### User Story 1

```bash
Task: "T017 contract tests for GET /api/admin/templates"
Task: "T018 contract tests for POST /api/admin/templates/bulk-actions"
Task: "T019 unit tests for bulk usage guardrails"
Task: "T020 frontend service tests"
```

```bash
Task: "T027 component class"
Task: "T028 component template"
Task: "T029 component styles"
```

### User Story 2

```bash
Task: "T032 review context contract test"
Task: "T033 review comment contract test"
Task: "T034 resolve comment contract test"
Task: "T036 review service unit test"
Task: "T037 frontend review service test"
```

```bash
Task: "T048 review workspace class"
Task: "T049 review workspace template"
Task: "T050 review workspace styles"
```

### User Story 3

```bash
Task: "T055 quality score unit tests"
Task: "T056 stale and missing-field unit tests"
Task: "T057 compliance endpoint contract tests"
Task: "T058 frontend compliance service tests"
```

```bash
Task: "T064 compliance component class"
Task: "T065 compliance component template"
Task: "T066 compliance component styles"
```

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 for User Story 1.
3. Validate `/admin/templates`, filters, bulk archive dry-run, bulk archive execution, reassignment, category change, and audit entries.
4. Stop for review/demo before adding review workspace and compliance dashboard.

### Incremental Delivery

1. Deliver US1: Admin all-status template oversight and bulk actions.
2. Deliver US2: Read-only review workspace and lifecycle comments.
3. Deliver US3: Compliance dashboard and regulatory impact alerts.
4. Run Phase 6 checks after each story if shipping incrementally.

### Constitution Reminders

- Keep all UI strings in `en.json` and `ar.json`.
- Test RTL and LTR layouts before merge.
- Keep comment pins in mm coordinates.
- Do not add AI, OCR, or unrelated automation.
- Preserve Supabase RLS and authenticated admin-only access for governance endpoints.

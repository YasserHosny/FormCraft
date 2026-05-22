# Tasks: Template Versioning & Cloning

**Input**: Design documents from `/specs/018-template-versioning/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Depends on**: Feature 016 (submissions reference template_version), Feature 015 (dashboard shows templates)

## Phase 1: Database Migration & Enum Expansion

**Purpose**: Add lineage columns, expand status enum, create reviews table

- [X] T001 [P] Create migration `formcraft-backend/migrations/020_template_versioning.sql` — drop old status CHECK, add expanded CHECK (draft, submitted_for_review, approved, rejected, published, archived, deprecated), add lineage_id (UUID), add parent_version_id (UUID FK), backfill lineage_id=id, set NOT NULL, add indexes
- [X] T002 [P] Create migration `formcraft-backend/migrations/021_template_reviews.sql` — CREATE TABLE template_reviews (id, template_id, reviewer_id, action, comment, org_id, created_at) with RLS policy and indexes
- [X] T003 [P] Update `formcraft-backend/app/models/enums.py` — expand TemplateStatus enum: add SUBMITTED_FOR_REVIEW, APPROVED, ARCHIVED, DEPRECATED, REJECTED
- [X] T004 [P] Add i18n keys to `formcraft-frontend/src/assets/i18n/ar.json` — versioning.*, review.*, status.* keys
- [X] T005 [P] Add i18n keys to `formcraft-frontend/src/assets/i18n/en.json` — same keys in English

---

## Phase 2: Backend State Machine & Immutability

**Purpose**: Enforce lifecycle transitions and published immutability

- [X] T006 Add transition map and `transition_status()` method to `formcraft-backend/app/services/template_service.py` — validate from→to against allowed map, validate role permission, update status, create audit log, create template_reviews row on approve/reject
- [X] T007 Add immutability guard to template edit methods in `formcraft-backend/app/services/template_service.py` — before any update/delete on template/page/element, check template status is in ['draft', 'rejected']; raise 403 otherwise
- [X] T008 Update `formcraft-backend/app/schemas/template.py` — add TransitionRequest (status, comment), TemplateReview response schema, expand TemplateResponse with lineage_id, parent_version_id
- [X] T009 Add `POST /api/templates/:id/transition` route to `formcraft-backend/app/api/routes/templates.py` — calls transition_status(), returns updated template

**Checkpoint**: Status transitions validated. Published templates cannot be edited. Audit log records transitions.

---

## Phase 3: Backend Versioning, Clone, History, Diff

**Purpose**: Add lineage-aware version creation, independent cloning, history listing, and diff computation

- [X] T010 Update `create_new_version()` in `formcraft-backend/app/services/template_service.py` — set lineage_id from source, set parent_version_id to source id, audit log TEMPLATE_VERSIONED
- [X] T011 Add `clone_template(template_id, name, user_id)` to `formcraft-backend/app/services/template_service.py` — copy pages/elements into new template with new lineage_id=new_id, parent_version_id=NULL, version=1, status=draft, audit log TEMPLATE_CLONED
- [X] T012 Add `get_version_history(template_id)` to `formcraft-backend/app/services/template_service.py` — query all templates with same lineage_id, return ordered by version DESC with element_count, page_count, creator name
- [X] T013 Add `compute_diff(template_id_a, template_id_b)` to `formcraft-backend/app/services/template_service.py` — validate same lineage, load elements for both, match by key, compute added/removed/modified with property-level changes
- [X] T014 Add routes to `formcraft-backend/app/api/routes/templates.py`: POST /:id/clone, GET /:id/history, GET /:id/diff?compare_to=, GET /:id/reviews
- [X] T015 Add schemas: CloneRequest (name optional), VersionHistoryResponse, DiffResponse (summary + changes), ReviewListResponse

**Checkpoint**: Version creation tracks lineage. Clone creates independent template. History lists all versions. Diff computes element changes.

---

## Phase 4: Frontend Lifecycle UI (Priority: P1)

**Purpose**: Status badges, transition actions in Design Studio, review queue in Admin

- [X] T016 Create `formcraft-frontend/src/app/features/designer/components/status-badge/status-badge.component.ts` — displays current status with color-coded badge (draft=gray, submitted=blue, approved=green, published=teal, archived=orange, deprecated=red)
- [X] T017 Update template toolbar/header in Design Studio — show StatusBadge; add "Submit for Review" button (visible when status=draft); add "Create New Version" button (visible when status=published)
- [X] T018 Create `formcraft-frontend/src/app/features/admin/review-queue/review-queue.component.ts` — lists templates with status=submitted_for_review in user's org; approve/reject buttons with comment dialog for rejection
- [X] T019 Create `formcraft-frontend/src/app/features/admin/review-queue/review-queue.component.html` — table: template name, version, submitted by, submitted date, actions (approve/reject)
- [X] T020 Update admin routing — add `{ path: 'reviews', component: ReviewQueueComponent }` under /admin children
- [X] T021 Create `formcraft-frontend/src/app/core/services/template-version.service.ts` — TemplateVersionService: transitionStatus(id, status, comment?), clone(id, name?), getHistory(id), getDiff(id, compareToId), getReviews(id)

**Checkpoint**: Designers can submit for review. Admins see review queue. Status badges reflect lifecycle state.

---

## Phase 5: Frontend Version History & Diff (Priority: P1)

**Purpose**: Version history panel and diff view for compliance

- [X] T022 Create `formcraft-frontend/src/app/features/designer/version-history/version-history.component.ts` — slide-over panel showing all versions in lineage; each version shows: version number, status badge, creator, date, element count; "Compare" checkbox to select two versions
- [X] T023 Create `formcraft-frontend/src/app/features/designer/version-history/version-history.component.html` — timeline/list UI with version cards, compare button (enabled when exactly 2 selected)
- [X] T024 Create `formcraft-frontend/src/app/features/designer/version-diff/version-diff.component.ts` — displays diff result: summary stats (added/removed/modified counts), element-level changes with color coding (green=added, red=removed, yellow=modified)
- [X] T025 Create `formcraft-frontend/src/app/features/designer/version-diff/version-diff.component.html` — summary card + changes table (element key, change type, property diffs for modified)
- [X] T026 Create `formcraft-frontend/src/app/features/designer/version-diff/version-diff.component.scss` — diff colors, RTL-aware layout, responsive
- [X] T027 Add "Version History" button to template toolbar — opens version-history panel; wire routing or dialog

**Checkpoint**: Designers can view all versions. Two versions can be compared with full diff output.

---

## Phase 6: Frontend Cloning (Priority: P2)

**Purpose**: Clone dialog and library update

- [X] T028 Add "Clone" button to template actions (in template list and detail toolbar) — opens dialog with name input (pre-filled with "{name} (Copy)")
- [X] T029 Create clone confirmation dialog — input for new name, info text "Creates an independent copy with no version link to the original", confirm/cancel
- [X] T030 Update template list component — after clone, navigate to new template in Design Studio

**Checkpoint**: Any template can be cloned into a new independent template via UI.

---

## Phase 7: Form Desk Integration (Priority: P1)

**Purpose**: Form Desk shows only latest published, handles deprecated warning

- [X] T031 Update `formcraft-backend/app/services/desk_service.py` (or equivalent dashboard query) — use DISTINCT ON (lineage_id) to return only latest published version per lineage; include `is_deprecated` flag for deprecated templates
- [X] T032 Update Operator Dashboard template grid — if template has `is_deprecated: true`, show warning banner "A newer version is available" with link to the latest published version in the same lineage (resolve via lineage_id, max version where status=published)
- [X] T033 Update Form Filler template loading — if template is archived, show error "This template is no longer available"; if deprecated, show warning but allow filling

**Checkpoint**: Form Desk shows correct latest versions. Deprecated templates show warning. Archived templates blocked.

---

## Phase 8: Polish & Edge Cases

**Purpose**: RTL, error handling, edge cases, navigation

- [X] T034 Add RTL styling to review queue, version history, and diff views
- [X] T035 Handle concurrent version creation — if two users create new versions simultaneously, each gets version=source.version+1 at creation time (matching existing `create_new_version()` behavior); if both publish, they coexist with the same version number distinguished by ID; template list shows both as separate entries in version history
- [X] T036 Add loading states and error handling — skeleton loaders for history/diff, toast messages for transition success/failure
- [X] T037 Add "Submitted for Review" notification to admin dashboard — badge/count showing pending reviews
- [X] T038 Verify immutability enforcement — test that all edit endpoints (element CRUD, page CRUD, template update) return 403 for non-draft templates
- [X] T039 Verify audit log completeness — test that every state transition creates an audit entry with from_status, to_status, actor_id

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Migration)**: No dependencies — all parallel
- **Phase 2 (State Machine)**: Depends on Phase 1 (enum expansion + migration)
- **Phase 3 (Versioning/Clone/Diff)**: Depends on Phase 2 (immutability guard must exist)
- **Phase 4 (Lifecycle UI)**: Depends on Phase 2 (transition API)
- **Phase 5 (History/Diff UI)**: Depends on Phase 3 (history/diff APIs)
- **Phase 6 (Clone UI)**: Depends on Phase 3 (clone API)
- **Phase 7 (Form Desk)**: Depends on Phase 1 (lineage columns) + Phase 2 (status expansion)
- **Phase 8 (Polish)**: Depends on all previous phases

### Parallel Opportunities

```
Phase 1: T001 || T002 || T003 || T004 || T005 (all parallel)
Phase 2: T006 → T007 → T008 → T009
Phase 3: T010 || T011 || T012 || T013 → T014 → T015
Phase 4-6: After Phase 3, Phases 4/5/6 can partially parallel:
  T016-T021 (lifecycle UI) || T022-T027 (history/diff UI) || T028-T030 (clone UI)
Phase 7: T031 → T032 → T033 (sequential, Form Desk depends on backend change)
```

### Critical Path

```
T001 → T003 → T006 → T007 → T009 (state machine works)
T001 → T010 → T012 → T013 → T014 (history/diff APIs work)
T004/T005 → T016 → T017 → T022 → T024 (frontend history/diff renders)
T031 → T032 (Form Desk shows correct versions)
```

## Notes

- Total tasks: 39
- Estimated effort: 4-5 days for single developer
- All frontend paths relative to `formcraft-frontend/`
- All backend paths relative to `formcraft-backend/`
- Commit after each phase completion
- The existing `create_new_version()` method at line 284 of template_service.py is the foundation — extended, not replaced
- Version number assigned at creation time (source.version + 1), matching existing `create_new_version()` behavior — concurrent drafts may share a version number but are distinguished by ID
- Clone explicitly breaks lineage (lineage_id = new_id) to distinguish from versioning

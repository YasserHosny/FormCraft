# Tasks: Submission History & Reprint

**Input**: Design documents from `/specs/017-submission-history/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Depends on**: Feature 016 (form-filler) — `submissions` table and Form Filler route must exist

## Phase 1: Setup (Migration + i18n)

**Purpose**: Add status column to submissions, add localization keys

- [x] T001 [P] Create migration `formcraft-backend/migrations/019_submissions_status.sql` — ALTER TABLE submissions ADD COLUMN status TEXT NOT NULL DEFAULT 'printed' CHECK (status IN ('printed', 'submitted'))
- [x] T002 [P] Add i18n keys to `formcraft-frontend/src/assets/i18n/ar.json` — history.* keys
- [x] T003 [P] Add i18n keys to `formcraft-frontend/src/assets/i18n/en.json` — same history.* keys in English

---

## Phase 2: Backend (List + Detail + Reprint + Export APIs)

**Purpose**: Extend submissions API with history listing, detail, reprint PDF, and export

- [x] T004 Update `formcraft-backend/app/schemas/submission.py` — add SubmissionListResponse (with key_summary), SubmissionDetailResponse (with operator_name, full field_values), ExportParams schema
- [x] T005 Update `formcraft-backend/app/services/submission_service.py` — add list_submissions(org_id, filters, pagination), get_submission(id), compute_key_summary(field_values, template_elements), export_submission(id, format)
- [x] T006 Update `formcraft-backend/app/services/pdf/renderer.py` — add render_reprint_pdf(template, field_values) that wraps render_template_pdf and injects SVG watermark overlay ("REPRINT" diagonal, 20% opacity) + footer with original/reprint dates
- [x] T007 Update `formcraft-backend/app/api/routes/submissions.py` — add: GET /api/submissions (list with search/filter/pagination/sort), GET /api/submissions/:id (detail), POST /api/submissions/:id/reprint (PDF stream + audit log), GET /api/submissions/:id/export?format=json|csv (download + audit log)
- [x] T008 Add CSV export utility — generate CSV with BOM prefix for Arabic Excel compatibility; field_values keys as columns, single row of values

**Checkpoint**: All history APIs work. List returns paginated results with key_summary. Reprint returns PDF with watermark. Export returns JSON or CSV.

---

## Phase 3: User Story 1 — History List with Search (Priority: P1)

**Goal**: Operator sees paginated table of past submissions with search and filters

### Implementation

- [x] T009 Create `formcraft-frontend/src/app/features/desk/services/history.service.ts` — HistoryService: getSubmissions(params), getSubmission(id), requestReprint(id), exportSubmission(id, format)
- [x] T010 Create `formcraft-frontend/src/app/features/desk/history/history.component.ts` — HistoryComponent: loads submissions via HistoryService, manages search/filter/sort/pagination state
- [x] T011 Create `formcraft-frontend/src/app/features/desk/history/history.component.html` — mat-table with columns (ref, template, date, status, key_summary, actions); search bar; date range picker; template filter dropdown; mat-paginator; empty state
- [x] T012 Create `formcraft-frontend/src/app/features/desk/history/history.component.scss` — responsive table (horizontal scroll on mobile), RTL-aware column alignment, status badges
- [x] T013 Update routing — add `{ path: 'history', component: HistoryComponent }` under /desk children in app-routing.module.ts

**Checkpoint**: `/desk/history` shows submissions table. Search by ref number works. Date filter works. Pagination works.

---

## Phase 4: User Story 2 — Submission Detail View (Priority: P1)

**Goal**: Click submission row to see full read-only detail with all field values

### Implementation

- [x] T014 Create `formcraft-frontend/src/app/features/desk/submission-detail/detail.component.ts` — DetailComponent: loads submission by ID, displays all field_values in read-only mode with labels from template elements
- [x] T015 Create `formcraft-frontend/src/app/features/desk/submission-detail/detail.component.html` — metadata section (ref, template, version, date, operator) + field values list (label: value pairs) + action buttons (Download PDF, Reprint, Clone, Export)
- [x] T016 Create `formcraft-frontend/src/app/features/desk/submission-detail/detail.component.scss` — read-only form layout, metadata card, action button row
- [x] T017 Update routing — add `{ path: 'history/:submissionId', component: DetailComponent }` under /desk children

**Checkpoint**: Click row → detail view shows all field values. Metadata visible. Action buttons present.

---

## Phase 5: User Story 3 — Reprint with Watermark (Priority: P1)

**Goal**: Reprint generates PDF with REPRINT watermark and logs audit event

### Implementation

- [x] T018 Update detail.component — "Reprint" button calls HistoryService.requestReprint(id); opens returned PDF in new tab/iframe for print dialog; shows success toast on completion
- [x] T019 Add confirmation dialog before reprint — "Generate reprint with watermark?" with confirm/cancel buttons
- [x] T020 Verify audit log integration — confirm FORM_REPRINTED audit entry is created by the backend endpoint (T007)

**Checkpoint**: Click Reprint → confirm → PDF with watermark opens → audit log entry exists.

---

## Phase 6: User Story 4 — Clone as New (Priority: P2)

**Goal**: Clone submission data into a new Form Filler session

### Implementation

- [x] T021 Update detail.component — "Clone as New" button navigates to `/desk/fill/:templateId?clone=:submissionId`
- [x] T022 Update Form Filler (fill.component.ts from feature 016) — detect `clone` query param; if present, load submission's field_values via HistoryService.getSubmission(); populate FormGroup with values mapped by element.key (skip keys not in current template version, leave new keys empty)
- [x] T023 Show info banner on cloned form — "Form opened with data from FC-2026-05-0042. A new reference number will be assigned on print." (translated)

**Checkpoint**: Clone → Form Filler opens pre-filled → modify → print → new reference number generated.

---

## Phase 7: User Story 5 — Export (Priority: P3)

**Goal**: Export single submission as JSON or CSV

### Implementation

- [x] T024 Update detail.component — "Export" button opens a dropdown menu with "JSON" and "CSV" options; calls HistoryService.exportSubmission(id, format); triggers browser file download
- [x] T025 Verify CSV includes UTF-8 BOM for Arabic Excel compatibility (handled in T008 backend)

**Checkpoint**: Export JSON → file downloads with field_values. Export CSV → file downloads with headers + values. Arabic text renders correctly in Excel.

---

## Phase 8: Polish & Edge Cases

**Purpose**: RTL, empty states, error handling, navigation integration

- [x] T026 Add RTL styling to history table and detail view — column alignment, action buttons, date formatting (locale-aware)
- [x] T027 Add loading states — skeleton table while loading; spinner on reprint/export actions
- [x] T028 Handle deleted/unavailable template on reprint — if template no longer exists, show warning "Template unavailable — export data only" and disable Reprint button
- [x] T029 Add "History" link to desk navigation — either in dashboard or mode sub-nav; ensure `/desk/history` is discoverable
- [x] T030 Mobile responsive table — horizontal scroll with sticky first column (reference number always visible)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — all parallel
- **Phase 2 (Backend)**: Depends on Phase 1 (migration)
- **Phase 3 (List)**: Depends on Phase 2 (API)
- **Phase 4 (Detail)**: Depends on Phase 3 (list navigates to detail)
- **Phase 5 (Reprint)**: Depends on Phase 4 (reprint button is in detail view)
- **Phase 6 (Clone)**: Depends on Phase 4 + Feature 016 Form Filler existing
- **Phase 7 (Export)**: Depends on Phase 4 (export button is in detail view)
- **Phase 8 (Polish)**: Depends on all previous phases

### Parallel Opportunities

```
Phase 1: T001 || T002 || T003 (all parallel)
Phase 2: T004 → T005 → T006 || T008 → T007
Phase 3-7: After Phase 2, Phases 5/6/7 can parallel (independent actions in detail view)
  T018-T020 (reprint) || T021-T023 (clone) || T024-T025 (export)
```

### Critical Path

```
T001 → T004 → T005 → T006 → T007 (backend complete)
T002/T003 → T009 → T010 → T011 → T013 (list renders)
T011 → T014 → T015 → T017 (detail renders)
T015 → T018 → T019 (reprint works)
```

## Notes

- Total tasks: 30
- Estimated effort: 3-4 days for single developer
- All frontend paths relative to `formcraft-frontend/`
- All backend paths relative to `formcraft-backend/`
- Commit after each phase completion
- Reprint uses CURRENT template version for positioning (not original version) — perfect version-pinned reprints require Template Versioning feature (roadmap 1.7)
- CSV export includes UTF-8 BOM (`\xEF\xBB\xBF`) to ensure Arabic text renders in Excel

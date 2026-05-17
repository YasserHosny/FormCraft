# Tasks: Template Feedback

**Input**: Design documents from `/specs/019-template-feedback/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Depends on**: Feature 015 (Form Desk context), Feature 018 (Template Versioning)

## Phase 1: Database Migration & Backend Models

**Purpose**: Create template_feedback table and backend schemas

- [ ] T001 [P] Create migration `formcraft-backend/migrations/022_template_feedback.sql` — CREATE TABLE template_feedback (id, template_id FK, template_version, page_number, element_key, category, text, status, submitted_by FK, resolved_by FK, resolved_at, resolution_note, org_id FK, created_at) with CHECK constraints, RLS policy, and indexes
- [ ] T002 [P] Create `formcraft-backend/app/models/template_feedback.py` — SQLAlchemy model for TemplateFeedback
- [ ] T003 [P] Create `formcraft-backend/app/schemas/template_feedback.py` — Pydantic schemas: FeedbackSubmitRequest, FeedbackResolveRequest, FeedbackResponse, FeedbackSummaryResponse, AdminFeedbackOverviewItem
- [ ] T004 [P] Add i18n keys to `formcraft-frontend/src/assets/i18n/ar.json` — template_feedback.* keys (categories, statuses, labels, messages)
- [ ] T005 [P] Add i18n keys to `formcraft-frontend/src/assets/i18n/en.json` — same keys in English

---

## Phase 2: Backend Service & Routes

**Purpose**: Business logic for feedback submission, listing, resolution, and admin overview

- [ ] T006 Create `formcraft-backend/app/services/template_feedback_service.py` — methods: submit_feedback() (with 60s debounce check), list_feedback() (with filters), resolve_feedback(), get_summary(), get_admin_overview(), export_csv()
- [ ] T007 Add audit logging to template feedback service — TEMPLATE_FEEDBACK_SUBMITTED, TEMPLATE_FEEDBACK_RESOLVED with metadata
- [ ] T008 Create `formcraft-backend/app/api/routes/template_feedback.py` — routes: POST /templates/:id/feedback, GET /templates/:id/feedback, POST /templates/:id/feedback/:fid/resolve, GET /templates/:id/feedback/summary, GET /admin/template-feedback, GET /admin/template-feedback/export
- [ ] T009 Register template feedback router in `formcraft-backend/app/main.py`

**Checkpoint**: Feedback can be submitted, listed, filtered, resolved, and exported via API. Audit trail records all actions.

---

## Phase 3: Frontend - Form Desk Feedback Panel

**Purpose**: Operator-facing UI for submitting template feedback

- [ ] T010 Create FeedbackButtonComponent `formcraft-frontend/src/app/features/desk/components/feedback-button/` — floating action button in Form Desk toolbar, shows open feedback count badge
- [ ] T011 Create FeedbackPanelComponent `formcraft-frontend/src/app/features/desk/components/feedback-panel/` — slide-out panel with reactive form: category (mat-radio-group), text (textarea), page selector (from current template pages), element selector (from selected page's elements)
- [ ] T012 Create TemplateFeedbackService `formcraft-frontend/src/app/features/desk/services/template-feedback.service.ts` — Angular HttpClient service for submit, list, summary endpoints
- [ ] T013 Integrate feedback button into Form Desk component — add FeedbackButtonComponent to form filler toolbar, pass template_id and template_version

**Checkpoint**: Operators can submit structured feedback from within Form Desk with page/element targeting.

---

## Phase 4: Frontend - Design Studio Feedback Tab

**Purpose**: Designer-facing UI for reviewing and resolving feedback

- [ ] T014 Create FeedbackTabComponent `formcraft-frontend/src/app/features/studio/components/feedback-tab/` — tab in Design Studio sidebar showing feedback list with filters (version, category, status, page)
- [ ] T015 Add resolve action to feedback tab — "Resolve" button per item, opens dialog for optional resolution_note, calls resolve endpoint
- [ ] T016 Add element navigation on feedback click — when feedback has element_key, clicking it emits event to canvas to scroll to and highlight that element
- [ ] T017 Add feedback count badge to template cards in Design Studio library — call summary endpoint, show badge with open_count

**Checkpoint**: Designers see feedback in-context, can filter/resolve, and navigate to referenced elements.

---

## Phase 5: Frontend - Admin Overview

**Purpose**: Admin page for cross-template feedback visibility

- [ ] T018 Create TemplateFeedbackOverviewComponent `formcraft-frontend/src/app/features/admin/template-feedback/` — mat-table with template name, version, open/resolved counts, last feedback date; expandable rows showing individual items
- [ ] T019 Add CSV export button — calls /admin/template-feedback/export, triggers download
- [ ] T020 Register route `/admin/template-feedback` in admin routing module

**Checkpoint**: Admins can see feedback across all templates and export for reporting.

---

## Phase 6: Polish & Integration

**Purpose**: Edge case handling and final UX touches

- [ ] T021 Handle deleted element reference — when element_key doesn't exist in current template version, show "Element no longer exists in current version" indicator
- [ ] T022 Add empty states — no feedback message in Design Studio tab, no templates message in admin overview
- [ ] T023 Add confirmation toast on feedback submission in Form Desk

**Checkpoint**: All edge cases handled, smooth UX across all three integration points.

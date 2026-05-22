# Tasks: Operator Dashboard

**Input**: Design documents from `/specs/015-operator-dashboard/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Depends on**: Feature 014 (mode-switching-ux) — `/desk` route prefix must exist

## Phase 1: Setup (Backend Schema + i18n)

**Purpose**: Database migration and localization keys

- [x] T001 [P] Create migration `formcraft-backend/migrations/016_operator_pins.sql` — CREATE TABLE operator_pins (id, operator_id, template_id, org_id, created_at) with unique constraint, index, RLS policy + CREATE TABLE notification_dismissals with RLS
- [x] T002 [P] Add i18n keys to `formcraft-frontend/src/assets/i18n/ar.json` — desk.* keys (title, search_placeholder, section headings, pin/unpin, draft labels, notification labels, empty states)
- [x] T003 [P] Add i18n keys to `formcraft-frontend/src/assets/i18n/en.json` — same desk.* keys in English

---

## Phase 2: Backend (API + Service Layer)

**Purpose**: Dashboard aggregation endpoint, pin CRUD, notification dismissal

- [x] T004 Create `formcraft-backend/app/schemas/desk.py` — Pydantic schemas: DashboardResponse, TemplateCardResponse, RecentTemplateResponse, PinnedTemplateResponse, NotificationResponse, PinRequest
- [x] T005 Create `formcraft-backend/app/models/desk.py` — OperatorPin model, NotificationDismissal model
- [x] T006 Create `formcraft-backend/app/services/desk_service.py` — DeskService with: get_dashboard(operator_id, org_id, filters), pin_template(operator_id, template_id, org_id), unpin_template(operator_id, template_id), dismiss_notification(operator_id, template_id, version, org_id), get_recent_templates(operator_id, limit=10), get_notifications(operator_id, org_id). Verify that templates and submissions tables have org_id RLS before querying (assert RLS is active).
- [x] T007 Create `formcraft-backend/app/api/routes/desk.py` — Router with: GET /api/desk/dashboard, POST /api/desk/pins, DELETE /api/desk/pins/:templateId, POST /api/desk/notifications/:notificationId/dismiss. notificationId format is `{template_id}:{version}` — parse in endpoint. Include AuditLogger calls for pin/unpin actions (same pattern as template CRUD).
- [x] T008 Register desk router in `formcraft-backend/app/api/routes/__init__.py` — add desk router to the app

**Checkpoint**: Dashboard API returns aggregated data. Pin CRUD works. Notification dismissal works. All endpoints auth-gated and org-scoped.

---

## Phase 3: User Story 1 — Templates Grid with Search (Priority: P1)

**Goal**: Operator sees all published templates in a searchable, filterable, paginated grid

**Independent Test**: Navigate to `/desk` → verify template cards appear → search by name → filter by category → verify pagination

### Implementation

- [x] T009 Create `formcraft-frontend/src/app/features/desk/desk.module.ts` — DeskModule declaring dashboard and sub-components, importing Angular Material modules (MatCard, MatPaginator, MatFormField, MatInput, MatSelect, MatIcon, MatChip, MatButton, MatTooltip)
- [x] T010 Create `formcraft-frontend/src/app/features/desk/services/desk.service.ts` — DeskService with: getDashboard(params), pinTemplate(templateId), unpinTemplate(templateId), dismissNotification(notificationId)
- [x] T011 Create `formcraft-frontend/src/app/features/desk/components/template-card/template-card.component.ts` — TemplateCardComponent with inputs: template data, is_pinned, last_used_at; outputs: pin toggle event, card click event; displays: name, category, version badge, pin star icon
- [x] T012 Create `formcraft-frontend/src/app/features/desk/dashboard/dashboard.component.ts` — DashboardComponent as the main container; calls DeskService.getDashboard(); manages search/filter state; handles pagination
- [x] T013 Create `formcraft-frontend/src/app/features/desk/dashboard/dashboard.component.html` — Template with: search bar (mat-form-field), filter dropdowns (mat-select × 3), "All Forms" grid section with mat-card per template, mat-paginator, empty state
- [x] T014 Create `formcraft-frontend/src/app/features/desk/dashboard/dashboard.component.scss` — Grid layout (CSS Grid, 4 columns desktop / 2 tablet / 1 mobile), RTL-aware via `[dir=rtl]`, responsive breakpoints
- [x] T015 Update `formcraft-frontend/src/app/app-routing.module.ts` — change `/desk` children: add `{ path: '', component: DashboardComponent }` as default route, keep `{ path: 'my-feedback', ... }` as sibling route, add `{ path: 'fill/:templateId', ... }` placeholder

**Checkpoint**: `/desk` shows published templates in a grid. Search and filters work. Pagination works. Cards are clickable.

---

## Phase 4: User Story 2 — Recently Used Templates (Priority: P1)

**Goal**: Dashboard shows operator's 10 most recently filled templates at the top

### Implementation

- [x] T016 Create `formcraft-frontend/src/app/features/desk/components/recent-templates/recent-templates.component.ts` — RecentTemplatesComponent with input: recent[] array from dashboard response; renders horizontal scrollable card strip; hidden when empty
- [x] T017 Update `formcraft-frontend/src/app/features/desk/dashboard/dashboard.component.html` — add `<fc-recent-templates>` section between search bar and "All Forms" grid, pass recent data, hide when empty

**Checkpoint**: Recent templates section appears with last-used forms. Hidden when operator has no history.

---

## Phase 5: User Story 3 — Pinned/Favorite Templates (Priority: P2)

**Goal**: Operators can pin templates; pinned section appears at the top of dashboard

### Implementation

- [x] T018 Create `formcraft-frontend/src/app/features/desk/components/pinned-templates/pinned-templates.component.ts` — PinnedTemplatesComponent with input: pinned[] array; renders card strip similar to recent; hidden when empty
- [x] T019 Update TemplateCardComponent (T011) — add pin/unpin toggle behavior: on star click, call DeskService.pinTemplate() or unpinTemplate(), emit event to parent to refresh pinned section
- [x] T020 Update DashboardComponent — handle pin toggle events: optimistic UI update on pin/unpin, refresh pinned section, handle 409/422 errors (already pinned, limit reached) with translated toast
- [x] T021 Update `formcraft-frontend/src/app/features/desk/dashboard/dashboard.component.html` — add `<fc-pinned-templates>` section above recent section, pass pinned data, hide when empty

**Checkpoint**: Pin star toggles on cards. Pinned section shows/hides. Pin limit enforced with toast.

---

## Phase 6: User Story 4 — Saved Drafts Section (Priority: P2)

**Goal**: Dashboard displays saved drafts (read-only display — actual draft CRUD is Form Filler scope)

### Implementation

- [x] T022 Create `formcraft-frontend/src/app/features/desk/components/draft-list/draft-list.component.ts` — DraftListComponent with input: drafts[] array; renders list rows with template name, completion %, last modified, expiry warning, Resume button, Delete button; hidden when empty
- [x] T023 Update `formcraft-frontend/src/app/features/desk/dashboard/dashboard.component.html` — add `<fc-draft-list>` section between recent and all-forms, pass drafts data, hide when empty

**Checkpoint**: Drafts section renders when data exists. Currently shows empty (until Form Filler creates drafts).

---

## Phase 7: User Story 5 — Version Notifications (Priority: P3)

**Goal**: Dashboard shows update notifications for templates the operator has used

### Implementation

- [x] T024 Create `formcraft-frontend/src/app/features/desk/components/version-notifications/version-notifications.component.ts` — VersionNotificationsComponent with input: notifications[] array; renders dismissable cards with template name, version change, "Open" and "Dismiss" buttons; hidden when empty
- [x] T025 Update DashboardComponent — handle notification dismiss: call DeskService.dismissNotification(), remove from local array optimistically
- [x] T026 Update `formcraft-frontend/src/app/features/desk/dashboard/dashboard.component.html` — add `<fc-version-notifications>` section, pass notifications data, hide when empty

**Checkpoint**: Version notifications appear and can be dismissed. Section hides when empty.

---

## Phase 8: Polish & Edge Cases

**Purpose**: Handle edge cases, RTL, mobile responsiveness, empty states

- [x] T027 Add RTL styling to all dashboard components — verify grid direction, card text alignment, search bar icon position, and pagination controls flip correctly in RTL mode
- [x] T028 Add mobile responsive breakpoints — grid collapses to 2 columns at < 960px and 1 column at < 600px; pinned/recent sections become horizontally scrollable on mobile
- [x] T029 Handle unpublished pinned templates — visually dim the card, show "Template unavailable" tooltip, disable click navigation
- [x] T030 Add loading skeleton — show placeholder cards while dashboard API call is in flight
- [x] T031 Handle API error state — show error message with retry button if dashboard endpoint fails
- [x] T032 Update mode.config.ts — change desk mode defaultRoute from `/desk` to `/desk` (verify it resolves to dashboard component, not my-feedback redirect)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — all tasks are parallel
- **Phase 2 (Backend)**: Depends on Phase 1 (T001 migration must exist)
- **Phase 3 (Templates Grid)**: Depends on Phase 2 (API must exist)
- **Phase 4 (Recent)**: Depends on Phase 3 (dashboard container must exist)
- **Phase 5 (Pinned)**: Depends on Phase 3 (template card must exist for pin toggle)
- **Phase 6 (Drafts)**: Depends on Phase 3 (dashboard container must exist)
- **Phase 7 (Notifications)**: Depends on Phase 3 (dashboard container must exist)
- **Phase 8 (Polish)**: Depends on all previous phases

### Parallel Opportunities

```
Phase 1: T001 || T002 || T003 (all parallel — different files)
Phase 2: T004 || T005 (schemas and models parallel) → T006 → T007 → T008
Phase 3: T009 + T010 → T011 → T012 → T013 → T014 → T015
Phase 4-7: Can be done in parallel after Phase 3 (independent sections)
  T016+T017 || T018+T019+T020+T021 || T022+T023 || T024+T025+T026
```

### Critical Path

```
T001 → T004/T005 → T006 → T007 → T008 (backend works)
T002/T003 → T009 → T010 → T011 → T012 → T013 → T015 (dashboard renders with data)
```

## Notes

- Total tasks: 32
- Estimated effort: 3-4 days for single developer
- All frontend paths relative to `formcraft-frontend/`
- All backend paths relative to `formcraft-backend/`
- Commit after each phase completion
- The `submissions` table (needed for "Recently Used") may not exist yet — backend must handle gracefully with empty results
- The `drafts` table (needed for "Saved Drafts") does not exist yet — backend returns empty array

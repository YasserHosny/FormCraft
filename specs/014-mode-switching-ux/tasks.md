# Tasks: Mode Switching UX

**Input**: Design documents from `/specs/014-mode-switching-ux/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Phase 1: Setup (Backend Schema + Frontend Module Scaffolding)

**Purpose**: Database migration and new module structure creation

- [x] T001 [P] Create migration `formcraft-backend/migrations/015_add_preferred_mode.sql` — ALTER profiles ADD preferred_mode TEXT with CHECK constraint
- [x] T002 [P] Create `formcraft-frontend/src/app/core/navigation/` directory and barrel export `index.ts`
- [x] T003 [P] Add i18n keys to `formcraft-frontend/src/assets/i18n/ar.json` — modes.studio, modes.desk, modes.admin, errors.unauthorized_mode
- [x] T004 [P] Add i18n keys to `formcraft-frontend/src/assets/i18n/en.json` — same keys in English

---

## Phase 2: Foundational (Mode Config + Service + Guard)

**Purpose**: Core mode-switching infrastructure that all user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create `formcraft-frontend/src/app/core/navigation/mode.config.ts` — define ModeConfig interface, MODES array, ROLE_DEFAULT_MODE map
- [x] T006 Create `formcraft-frontend/src/app/core/navigation/mode.service.ts` — ModeService with: getPermittedModes(role), getActiveMode(url), getDefaultMode(role, preferredMode), savePreference(mode)
- [x] T007 Create `formcraft-frontend/src/app/core/navigation/mode.guard.ts` — ModeGuard that checks if current route prefix is in user's permitted modes, redirects with toast if not
- [x] T008 Update `formcraft-backend/app/schemas/user.py` — add preferred_mode (Optional[str]) to UserUpdate and UserResponse schemas
- [x] T009 Update `formcraft-backend/app/models/user.py` — add preferred_mode field to User model
- [x] T010 Update `formcraft-backend/app/api/users.py` — PATCH /api/users/me accepts preferred_mode, validates against role's permitted modes, verify existing audit middleware logs preferred_mode changes

**Checkpoint**: Mode configuration defined, service can determine permitted modes, guard can block unauthorized access, backend can persist preference.

---

## Phase 3: User Story 1 — Role-Based Default Mode on Login (Priority: P1)

**Goal**: After login, user lands on their role-appropriate mode

**Independent Test**: Log in as operator → verify redirect to /desk; log in as designer → verify /studio/templates; log in as admin → verify /admin/feedback

### Implementation

- [x] T011 Update `formcraft-frontend/src/app/core/auth/auth.service.ts` — add preferred_mode to User interface, load it from GET /api/users/me response
- [x] T012 Update `formcraft-frontend/src/app/features/auth/` login component — after successful login, use ModeService.getDefaultMode(user.role, user.preferred_mode) to determine redirect target
- [x] T013 Update `formcraft-frontend/src/app/app-routing.module.ts` — change default redirect `{ path: '', redirectTo: ... }` to use a resolver or redirect guard that reads user role/preference

**Checkpoint**: Login correctly routes each role to their default mode.

---

## Phase 4: User Story 2 — Mode Switching via Navigation Bar (Priority: P1)

**Goal**: Visible mode tabs in toolbar; clicking switches modes; only permitted modes shown

**Independent Test**: As admin, see all 3 tabs; click each tab and verify URL + content change. As operator, verify only Form Desk tab visible.

### Implementation

- [x] T014 Create `formcraft-frontend/src/app/shared/components/mode-tabs/mode-tabs.component.ts` — uses ModeService to get permitted modes, renders MatTabNavBar with routerLink per mode, highlights active mode based on current URL
- [x] T015 Create `formcraft-frontend/src/app/shared/components/mode-tabs/mode-tabs.component.html` — mat-tab-nav-bar with mat-tab-link per permitted mode, translated labels, material icons
- [x] T016 Update `formcraft-frontend/src/app/shared/components/app-shell/app-shell.component.ts` — insert `<fc-mode-tabs>` between app-title and spacer in toolbar, remove hardcoded nav buttons (templates, register)
- [x] T017 Update `formcraft-frontend/src/app/shared/shared.module.ts` — declare and export ModeTabsComponent, import MatTabsModule
- [x] T018 Restructure `formcraft-frontend/src/app/app-routing.module.ts` — organize routes under mode prefixes: `/studio/*` (templates + designer), `/desk/*` (my-feedback + future), `/admin/*` (feedback + future)
- [x] T019 [P] Create `formcraft-frontend/src/app/features/studio/studio-routing.module.ts` — lazy-loads templates and designer modules under /studio prefix
- [x] T020 [P] Create `formcraft-frontend/src/app/features/desk/desk-routing.module.ts` — lazy-loads my-feedback under /desk prefix, adds placeholder dashboard route
- [x] T021 [P] Create `formcraft-frontend/src/app/features/admin/admin-routing.module.ts` — lazy-loads feedback module under /admin prefix
- [x] T022 Add redirect routes for backward compatibility: `/templates` → `/studio/templates`, `/designer/:pageId` → `/studio/designer/:pageId`, `/my-feedback` → `/desk/my-feedback`

**Checkpoint**: Mode tabs visible, clicking switches URL and content. Role-based tab visibility works.

---

## Phase 5: User Story 3 — Mode Preference Persistence (Priority: P2)

**Goal**: System remembers last-used mode and restores it on next login

**Independent Test**: Switch to Form Desk, log out, log in → verify landing on Form Desk

### Implementation

- [x] T023 Update `formcraft-frontend/src/app/core/navigation/mode.service.ts` — on mode switch, fire-and-forget PATCH to /api/users/me with { preferred_mode: newMode }
- [x] T024 Update mode-tabs click handler to call ModeService.savePreference() after navigation
- [x] T025 Update login redirect logic (T012) to prioritize stored preferred_mode over role default

**Checkpoint**: Mode preference survives logout/login cycle.

---

## Phase 6: User Story 4 — Route Guards Enforce Mode Access (Priority: P1)

**Goal**: Manual URL access to forbidden modes is blocked with redirect + toast

**Independent Test**: As operator, type /studio/templates in URL bar → verify redirect to /desk with Arabic toast

### Implementation

- [x] T026 Integrate ModeGuard into route configuration — apply as canActivate on `/studio`, `/desk`, `/admin` parent routes
- [x] T027 Update `formcraft-frontend/src/app/core/auth/role.guard.ts` — change redirect target from `/templates` to user's default mode route (use ModeService)
- [x] T028 Update `formcraft-frontend/src/app/core/auth/auth.guard.ts` — on unauthenticated, redirect to `/auth/login` (unchanged behavior but verify with new route structure)
- [x] T029 Add toast notification on unauthorized redirect — use MatSnackBar with translated message key `errors.unauthorized_mode`

**Checkpoint**: All unauthorized URL access correctly redirected with bilingual feedback.

---

## Phase 7: User Story 5 — Bilingual Navigation (Priority: P2)

**Goal**: Mode tabs display correctly in both Arabic (RTL) and English (LTR)

**Independent Test**: Switch language toggle → verify tab labels change, direction flips

### Implementation

- [x] T030 Verify mode-tabs.component uses `translate` pipe for labels (should be done in T015 — validate here)
- [x] T031 Add CSS for RTL mode tab layout — ensure ink bar and tab order respects `[dir]` attribute
- [x] T032 Test with language toggle: switch AR→EN and EN→AR while on each mode, verify no navigation disruption

**Checkpoint**: Full bilingual support verified.

---

## Phase 8: Polish & Edge Cases

**Purpose**: Handle edge cases identified in spec

- [x] T033 Handle role change while logged in: on 403 response from any API call, refresh user profile via GET /api/users/me, update ModeService permitted modes, hide/show tabs accordingly
- [x] T034 Handle deep-link sharing: if user navigates to a specific route within a forbidden mode, redirect to their default mode root (not to the same path in their mode)
- [x] T035 Mobile responsiveness: add CSS breakpoint to collapse mode tabs into a dropdown/hamburger at < 768px width
- [x] T036 Browser history: verify back/forward buttons work correctly across mode boundaries (no duplicate history entries from redirects)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — all tasks are parallel
- **Phase 2 (Foundational)**: Depends on Phase 1 completion — BLOCKS all user stories
- **Phases 3-7 (User Stories)**: All depend on Phase 2 completion
  - US1 (Phase 3) and US4 (Phase 6) are P1 — do first
  - US2 (Phase 4) is also P1 — can parallel with US1 after T005-T010 are done
  - US3 (Phase 5) and US5 (Phase 7) are P2 — do after P1 stories
- **Phase 8 (Polish)**: Depends on all user stories being complete

### Parallel Opportunities

```
Phase 1: T001 || T002 || T003 || T004 (all parallel — different files)
Phase 2: T005 → T006 → T007 (sequential — each builds on previous)
         T008 || T009 || T010 (backend tasks parallel with frontend T005-T007)
Phase 4: T019 || T020 || T021 (routing modules are independent files)
```

### Critical Path

```
T001 → T008/T009/T010 → T011 → T012 → T013 (login redirect works)
T002 → T005 → T006 → T007 → T026 (guards work)
T002 → T005 → T014 → T015 → T016 → T018 (tabs visible and functional)
```

## Notes

- Total tasks: 36
- Estimated effort: 3-4 days for single developer
- All frontend paths relative to `formcraft-frontend/`
- All backend paths relative to `formcraft-backend/`
- Commit after each phase completion

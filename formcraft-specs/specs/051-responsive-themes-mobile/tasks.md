# Tasks: Responsive Classic and New Themes

**Input**: Design documents from `formcraft-specs/specs/051-responsive-themes-mobile/`
**Prerequisites**: plan.md, spec.md

**Tests**: Constitution V mandates TDD. Playwright viewport tests included per user story.

**Organization**: Tasks grouped by phase for dependency-safe implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Responsive Infrastructure

**Purpose**: Create shared responsive foundation used by all subsequent phases

- [ ] T001 Create shared responsive breakpoint mixins at `formcraft-frontend/src/styles/_responsive.scss` — define `$fc-phone-max: 599px`, `$fc-tablet-min: 600px`, `$fc-tablet-max: 959px`, `$fc-desktop-min: 960px` and mixins `@mixin fc-phone {}`, `@mixin fc-tablet {}`, `@mixin fc-desktop {}` that wrap `@media` queries. Include a `@mixin fc-phone-tablet {}` for shared phone+tablet rules.

- [ ] T002 Add responsive token overrides to `formcraft-frontend/src/app/features/ui-redesign/shared/fc-tokens.scss` — inside `@media (max-width: 599px)` override `--fc-toolbar-h: 48px`, `--fc-sidebar-w: 0px` (hidden by default on phone), add `--fc-action-bar-h: 56px` for sticky mobile action bars.

- [ ] T003 Import `_responsive.scss` into `formcraft-frontend/src/styles.scss` alongside existing `_direction-mixins.scss` and `_rtl.scss`.

- [ ] T004 Add global mobile dialog override in `formcraft-frontend/src/styles.scss` — `@media (max-width: 599px) { .cdk-overlay-pane { max-width: 95vw !important; } .mat-mdc-dialog-container { max-height: 90vh; overflow-y: auto; } }` to ensure all Material dialogs fit phone viewports (FR-013).

**Checkpoint**: Shared responsive infrastructure ready — all subsequent phases can import mixins ✓

---

## Phase 2: New Theme Shell Responsiveness (US2)

**Purpose**: Make New theme toolbar and sidebar responsive

**⚠️ CRITICAL**: Depends on Phase 1 completion

- [ ] T005 [US2] Modify `formcraft-frontend/src/app/features/ui-redesign/shell/toolbar.component.ts` — inject `BreakpointObserver`, expose `isMobile` signal. Add hamburger button (`mat-icon-button` with `menu` icon) visible only on phone/tablet. On phone: hide brand name, mode tab labels, search bar, theme switch label, user info text. On tablet: hide search bar and mode tab labels only.

- [ ] T006 [US2] Modify `formcraft-frontend/src/app/features/ui-redesign/shell/toolbar.component.scss` — using `@include fc-phone` and `@include fc-tablet` mixins, add responsive rules: phone hides `.brand-name`, `.brand-sep`, `.fc-toolbar-search-wrap`, `.fc-mode-tab span`, `.fc-theme-switch span`, `.fc-user-chip .user-info`; set `--fc-toolbar-h: 48px`; hamburger button display. Tablet hides search and tab labels. Extend existing `@media (max-width: 960px)` and `@media (max-width: 1180px)` to use shared mixins.

- [ ] T007 [US2] Modify `formcraft-frontend/src/app/features/ui-redesign/shell/sidebar.component.ts` — accept `isMobile` input or inject `BreakpointObserver`. On phone: sidebar becomes an overlay drawer (position fixed, z-index above content, backdrop). On tablet: sidebar collapses to 56px icon rail. Add `close()` method that emits event to parent. Add `@HostListener('document:keydown.escape')` to close drawer.

- [ ] T008 [US2] Modify `formcraft-frontend/src/app/features/ui-redesign/shell/sidebar.component.scss` — add phone styles: `position: fixed; inset-inline-start: 0; top: var(--fc-toolbar-h); bottom: 0; width: 280px; z-index: 100; transform: translateX(-100%); transition: transform 0.25s ease; &.open { transform: translateX(0); }`. For RTL: `[dir="rtl"] & { transform: translateX(100%); &.open { transform: translateX(0); } }`. Add backdrop overlay. Tablet: `width: 56px; .fc-side-link span, .group-label, .count, .sidebar-footer .lang-label, .sidebar-footer .lang-alt { display: none; }`.

- [ ] T009 [P] [US2] Write Playwright e2e test at `formcraft-frontend/e2e/051-responsive-shell-new.spec.ts` — test New theme shell at 360px and 768px viewports in both RTL and LTR: hamburger opens drawer, sidebar items navigable, drawer closes on escape, drawer closes on backdrop click, mode tabs accessible, user chip shows avatar only on phone, language switch works from drawer.

**Checkpoint**: New theme shell fully responsive ✓

---

## Phase 3: Classic Theme Shell Responsiveness (US2)

**Purpose**: Make Classic theme toolbar and navigation responsive

- [ ] T010 [US2] Modify `formcraft-frontend/src/app/shared/components/app-shell/app-shell.component.ts` — inject `BreakpointObserver`, add `isMobile` and `isTablet` properties. Add `showMobileMenu` toggle. On phone: mode tabs move into a slide-out drawer, toolbar shows hamburger button. Profile menu accessible via avatar-only button. Global search hidden on phone/tablet (already hidden at 1180px).

- [ ] T011 [US2] Add responsive SCSS to classic app-shell — the component uses inline template, so add styles via `styles:` array or create `app-shell.component.scss`. Phone: `.mode-tabs { display: none; }`, hamburger visible, drawer overlay for mode tabs. Tablet: `.mode-tab-label { display: none; }` (icons only). Profile area: avatar only on phone. Use `@include fc-phone` and `@include fc-tablet` mixins.

- [ ] T012 [P] [US2] Write Playwright e2e test at `formcraft-frontend/e2e/051-responsive-shell-classic.spec.ts` — test Classic theme shell at 360px and 768px viewports in both RTL and LTR: hamburger opens drawer, mode tabs navigable from drawer, drawer closes properly, theme switch accessible, language switch works, profile menu reachable.

**Checkpoint**: Classic theme shell fully responsive ✓

---

## Phase 4: Form Desk Responsiveness (US3)

**Purpose**: Make form filling workflow mobile-friendly in both themes

- [ ] T013 [US3] Modify `formcraft-frontend/src/app/features/desk/fill/fill.component.scss` — phone: single-column field layout (`grid-template-columns: 1fr`), sticky bottom action bar for Submit/Save Draft/Print buttons, section navigation as horizontal scrollable chips or collapsible accordion. Tablet: two-column fields where space allows. Normalize existing `@media (max-width: 599px)` to use shared mixins.

- [ ] T014 [US3] Modify `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.scss` — same responsive patterns as T013 for New theme form filler. Phone: single column, sticky action bar. Ensure validation messages display below fields without overlap.

- [ ] T015 [P] [US3] Modify form validation scroll behavior — in the form submission handler (both themes), when validation fails on mobile, use `element.scrollIntoView({ behavior: 'smooth', block: 'center' })` to scroll the first error field into the center of the viewport, accounting for sticky action bar height. Applies to: `formcraft-frontend/src/app/features/desk/fill/fill.component.ts` and `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts`.

- [ ] T016 [P] [US3] Write Playwright e2e test at `formcraft-frontend/e2e/051-responsive-form-fill.spec.ts` — test form filling at 360px and 768px in both themes and both language directions: template selection, form field input, required field validation, validation error scroll-to, draft save, draft resume, submit confirmation.

**Checkpoint**: Form filling responsive in both themes ✓

---

## Phase 5: Desk Dashboard & Data Views (US1, US4)

**Purpose**: Make dashboards, tables, lists, and cards responsive

- [ ] T017 [P] [US1] Modify `formcraft-frontend/src/app/features/desk/dashboard/dashboard.component.scss` — phone: KPI cards stack single column, template grid single column, recent submissions as card list. Tablet: KPI cards 2-column, template grid 2-column. Normalize existing breakpoints (959px, 599px) to shared mixins.

- [ ] T018 [P] [US1] Modify `formcraft-frontend/src/app/features/ui-redesign/desk/dashboard.component.scss` — same responsive patterns for New theme dashboard. KPI cards reflow via CSS Grid `auto-fit minmax(280px, 1fr)`.

- [ ] T019 [P] [US4] Modify `formcraft-frontend/src/app/features/desk/history/history.component.scss` — phone: submission history table switches to card layout (each row becomes a card showing reference, template name, status chip, date, primary action). Normalize existing `@media (max-width: 768px)` to shared mixin. Tablet: horizontal scroll within contained region.

- [ ] T020 [P] [US4] Modify `formcraft-frontend/src/app/features/desk/customers/customer-list.component.scss` — phone: customer table switches to card layout (name, ID, status, last activity, primary action). Tablet: contained horizontal scroll.

- [ ] T021 [P] [US4] Modify `formcraft-frontend/src/app/features/desk/customers/customer-detail.component.scss` — phone: detail sections stack vertically, metadata cards single column. Normalize existing breakpoints.

- [ ] T022 [P] [US4] Modify `formcraft-frontend/src/app/features/ui-redesign/desk/customers.component.scss` — New theme customer list responsive: phone card layout, tablet contained scroll.

- [ ] T023 [P] [US4] Modify `formcraft-frontend/src/app/features/desk/submission-detail/detail.component.scss` — phone: submission detail stacks vertically, action buttons in sticky bottom bar. Normalize existing `@media (max-width: 599px)`.

- [ ] T024 [P] [US4] Write Playwright e2e test at `formcraft-frontend/e2e/051-responsive-data-views.spec.ts` — test dashboard, history, customers at 360px and 768px in both themes: KPI cards visible, table/card transformation, filters accessible, pagination works, empty states display correctly.

**Checkpoint**: Desk dashboard and data views responsive ✓

---

## Phase 6: Studio, Admin & Secondary Pages (US1, US4)

**Purpose**: Make remaining production-reachable pages responsive

- [ ] T025 [P] [US1] Modify `formcraft-frontend/src/app/features/ui-redesign/studio/template-list.component.scss` — phone: template cards single column stack. Tablet: 2-column grid. Search/filter bar stacks vertically on phone.

- [ ] T026 [P] [US1] Modify `formcraft-frontend/src/app/features/ui-redesign/studio/designer.component.ts` — add mobile-unavailable guard: when `BreakpointObserver` detects phone viewport, show a centered card with desktop-required message and navigation button to template list (FR-019).

- [ ] T027 [P] [US1] Modify `formcraft-frontend/src/app/features/ui-redesign/admin/analytics.component.scss` — phone: chart containers full width, single column. Tablet: 2-column chart grid. Filter panel collapses to expandable section.

- [ ] T028 [P] [US1] Modify `formcraft-frontend/src/app/features/auth/profile/profile.component.scss` — phone: profile sections stack vertically, avatar section full width. Form fields single column.

- [ ] T029 [P] [US4] Modify batch queue pages responsive: `formcraft-frontend/src/app/features/desk/batch-queue/batch-list/batch-list.component.scss` — phone: card layout. Tablet: contained scroll.

- [ ] T030 [P] [US1] Write Playwright e2e test at `formcraft-frontend/e2e/051-responsive-secondary.spec.ts` — test template list, analytics, profile at 360px and 768px: card reflow, designer unavailable message, chart visibility, profile form usable.

**Checkpoint**: All production-reachable pages responsive ✓

---

## Phase 7: RTL/LTR Verification (US5)

**Purpose**: Verify all responsive changes work correctly in both language directions

- [ ] T031 [US5] Audit all SCSS changes from Phases 2–6 for RTL correctness — ensure no physical `left`/`right`/`margin-left`/`padding-right` properties were introduced. All directional properties must use logical properties (`inline-start/end`) or `@include` direction mixins. Fix any violations.

- [ ] T032 [US5] Test language switching on mobile — verify that switching between Arabic and English on a phone viewport recalculates layout direction without page reload, sidebar drawer direction flips, toolbar alignment flips, form field alignment updates. Both themes.

- [ ] T033 [P] [US5] Write Playwright e2e test at `formcraft-frontend/e2e/051-responsive-rtl.spec.ts` — comprehensive RTL test at 360px: shell drawer opens from correct side, form labels aligned correctly, table/card content aligned, dialog close button positioned correctly, sticky action bar aligned. Run same tests in LTR for comparison.

**Checkpoint**: RTL/LTR verified across all responsive changes ✓

---

## Phase 8: Cross-Theme & Edge Cases (US1, US2)

**Purpose**: Handle theme switching on mobile and edge cases from spec

- [ ] T034 [US1] Implement mobile theme switch behavior — when switching from Classic to New (or vice versa) on a phone viewport, route to the equivalent mobile-ready destination. Modify `ThemePreferenceService` or theme switch handlers in both shells to check current route against a mobile-ready route map and redirect if needed (FR-017).

- [ ] T035 [US1] Handle edge cases: long labels truncation with `text-overflow: ellipsis` and `title` attribute for accessible full text across all responsive components. Dialogs become full-screen on phone via `mat-dialog` `maxWidth: '100vw', maxHeight: '100vh', width: '100vw', height: '100vh'` config when `BreakpointObserver` detects phone. Orientation change preservation verified (no explicit code needed — CSS media queries handle reflow, Angular preserves component state).

- [ ] T036 [P] Write Playwright e2e test at `formcraft-frontend/e2e/051-responsive-edge-cases.spec.ts` — test theme switching on mobile, long label truncation, dialog full-screen on phone, orientation change simulation (resize from 360x640 to 640x360 and back).

**Checkpoint**: All edge cases and cross-theme behavior handled ✓

---

## Phase 9: Final Validation

**Purpose**: Run complete acceptance matrix and verify no desktop regressions

- [ ] T037 Run full Playwright test suite at desktop viewport (1280px) to verify no regressions to existing desktop layouts from responsive CSS changes.

- [ ] T038 Run complete Viewport Acceptance Matrix: both themes × both languages × phone (360px) × tablet (768px) × top 5 desk workflows. Document pass/fail in test results.

- [ ] T039 Verify SC-001 through SC-008 success criteria are met. Document results.

**Checkpoint**: Feature complete — all acceptance criteria validated ✓

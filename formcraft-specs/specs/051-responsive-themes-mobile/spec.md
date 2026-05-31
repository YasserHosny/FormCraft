# Feature Specification: Responsive Classic and New Themes

**Feature Branch**: `051-responsive-themes-mobile`  
**Created**: 2026-05-31  
**Status**: Clarified  
**Input**: User description: "Make both classic and new theme responsive for mobile view"

## Clarifications *(resolved 2026-06-01)*

### Q1: What are the standard breakpoints?
**Answer**: Three breakpoints aligned with Angular Material conventions: phone ≤599px, tablet 600–959px, desktop ≥960px. The acceptance viewports (360px phone, 768px tablet) are test targets within these ranges. Existing inconsistent breakpoints (599px, 768px, 959px in classic theme) will be normalized.

### Q2: Which classic theme pages are excluded from scope (Designer Canvas, etc.)?
**Answer**: The Form Designer canvas (drag-and-drop template builder) is excluded from mobile responsive scope — it is inherently desktop-only. On mobile, designer routes show an "unavailable on mobile" message per FR-019. All other production-reachable classic theme pages (Desk dashboard, form fill, history, customers, submissions, admin, analytics, profile) are in scope.

### Q3: What mobile navigation pattern should the classic theme use?
**Answer**: The classic theme toolbar collapses mode tabs into a hamburger menu/drawer on phone viewports, matching the pattern already started in `app-shell.component.ts`. The New theme sidebar converts to an overlay drawer triggered by a hamburger button in the toolbar.

### Q4: How should tables transform on mobile?
**Answer**: Tables with ≤4 columns use horizontal scroll within a contained region. Tables with >4 columns switch to a card-based layout showing key columns (identity, status, date, primary action) with an expandable detail row. This applies to both themes consistently.

### Q5: Should the Studio/Designer template list be responsive?
**Answer**: Yes, the template list (grid of template cards) is production-reachable and should be responsive. The cards reflow from a multi-column grid to a single-column stack on phone viewports. The actual designer canvas is excluded per Q2.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Use Core Workflows on Mobile (Priority: P1)

As an authenticated FormCraft user, I want both Classic and New themes to adapt cleanly to phone and tablet screens so that I can complete my assigned work without switching devices.

**Why this priority**: Mobile usability is only valuable if the primary work areas remain usable in both themes. Users should not discover that one theme works on mobile while the other blocks the same workflow.

**Independent Test**: Sign in on supported phone and tablet viewport sizes, open each production-reachable Classic and New theme workflow, and confirm users can navigate, read content, interact with controls, and complete the primary task without horizontal scrolling or clipped actions.

**Acceptance Scenarios**:

1. **Given** a user opens a production-reachable Classic theme page on a 360px phone viewport, **When** they use the page's primary workflow, **Then** all required content and actions remain visible, reachable, and usable without horizontal scrolling.
2. **Given** a user opens the matching New theme page on a 360px phone viewport, **When** they use the same primary workflow, **Then** the New theme provides an equivalent responsive experience without hiding required actions.
3. **Given** a user opens either theme on a 768px tablet viewport, **When** they navigate between workflow steps, **Then** the layout uses the additional width without overlapping navigation, toolbar, forms, cards, tables, or dialogs.

---

### User Story 2 - Navigate Theme Shells on Small Screens (Priority: P1)

As a FormCraft user on a small screen, I want the top navigation, side navigation, mode switching, theme switching, language switching, notifications, profile menu, and logout controls to remain accessible without crowding the page.

**Why this priority**: If the shell controls fail on mobile, users cannot safely move between modules, themes, languages, or account actions even when the page content itself is responsive.

**Independent Test**: Open the Classic and New theme shells on supported phone and tablet viewport sizes in Arabic and English, then operate every shell-level control and confirm menus, drawers, dialogs, and route changes behave predictably.

**Acceptance Scenarios**:

1. **Given** a user is in the Classic theme on a phone viewport, **When** they open navigation and account controls, **Then** the controls are reachable through touch-friendly menus or drawers and do not cover required page content permanently.
2. **Given** a user is in the New theme on a phone viewport, **When** they switch theme or language, **Then** the selected setting is applied and the layout remains usable after the change.
3. **Given** a user opens a menu or drawer in either theme, **When** they dismiss it, **Then** focus and scroll position return to a sensible page location without trapping the user.

---

### User Story 3 - Complete Form-Filling on Mobile (Priority: P1)

As a branch operator, I want form search, template selection, form filling, validation, draft saving, PDF/print actions where available, and submission to work on phones and tablets in both themes.

**Why this priority**: Form Desk is the most mobile-sensitive workflow and has the highest operational value for branch users.

**Independent Test**: On supported phone and tablet viewport sizes, complete a published form from template selection through submission in Classic and New themes, including required fields, conditional fields, validation errors, draft save/resume, and confirmation states.

**Acceptance Scenarios**:

1. **Given** a published template with multiple sections and required fields, **When** an operator fills it on a phone viewport in either theme, **Then** fields, labels, validation messages, section navigation, and primary actions are readable and touch-accessible.
2. **Given** a validation error appears near the bottom of a mobile form, **When** the operator attempts to submit, **Then** the page guides them to the error without obscuring the field or action area.
3. **Given** the operator resumes a draft on a tablet viewport, **When** the form loads, **Then** saved values, progress, and available actions are presented without layout breakage.

---

### User Story 4 - Preserve Responsive Data Views (Priority: P2)

As a user reviewing lists, tables, cards, reports, dashboards, customers, submissions, or template records, I want dense desktop data to transform into mobile-friendly views without losing key information.

**Why this priority**: Many FormCraft screens rely on tables and dashboards. Responsive behavior must preserve decision-making context, not merely shrink desktop layouts.

**Independent Test**: Open representative dashboard, list, table, card, and detail screens in both themes on phone and tablet viewports, then confirm search, filters, pagination, sorting, row actions, empty states, loading states, and error states remain usable.

**Acceptance Scenarios**:

1. **Given** a data table has more columns than fit on a phone viewport, **When** the page renders, **Then** the data is transformed into an accessible compact layout, prioritized columns, expandable rows, or controlled horizontal region that does not cause full-page horizontal scrolling.
2. **Given** filters are available on desktop, **When** a user opens the same page on mobile, **Then** the filters remain discoverable and usable through a mobile-appropriate panel, sheet, drawer, or stacked layout.
3. **Given** an empty, loading, or error state appears on mobile, **When** the user views it in either theme, **Then** the message and recovery action fit the viewport and remain actionable.

---

### User Story 5 - Support Arabic RTL and English LTR Responsively (Priority: P1)

As an Arabic or English user, I want both themes to remain readable and correctly aligned on mobile regardless of language direction.

**Why this priority**: FormCraft is bilingual and RTL-first for many users. Mobile fixes that only work in one direction would create immediate regressions.

**Independent Test**: Repeat shell, form-filling, and data-view acceptance tests in Arabic RTL and English LTR on supported phone and tablet viewport sizes.

**Acceptance Scenarios**:

1. **Given** the interface is in Arabic RTL, **When** a user opens either theme on a phone viewport, **Then** navigation, labels, icons, forms, tables, dialogs, and action placement follow RTL expectations without overlap.
2. **Given** the interface is in English LTR, **When** a user opens either theme on a phone viewport, **Then** the same workflows remain aligned and readable without relying on RTL-specific spacing.
3. **Given** a user switches language on a mobile viewport, **When** the layout direction changes, **Then** the page recalculates spacing and alignment without requiring a full browser refresh.

### Edge Cases

- What happens when long Arabic labels, customer names, template names, or reference numbers exceed the available mobile width? They should wrap, truncate with accessible full text, or move to secondary lines without overlapping controls.
- What happens when a user opens a large dialog on a phone? The dialog should become a full-screen or viewport-contained surface with reachable close, cancel, and confirm actions.
- What happens when the browser zoom level or device font size is increased? Core workflows should remain readable and operable without fixed-height clipping.
- What happens when the on-screen keyboard opens while editing a form field? The active field and submission/draft actions should not be permanently hidden or unreachable.
- What happens when a table, chart, PDF preview, or designer canvas cannot fully collapse to the viewport? The page should contain scrolling to the affected region and prevent full-page layout breakage.
- What happens when users rotate between portrait and landscape? Layouts should reflow without losing entered form data, selected filters, or menu state.
- What happens when a user switches from Classic to New, or New to Classic, while on a mobile viewport? The target theme should open the equivalent mobile-ready destination or a safe mobile-ready fallback.

### Assumptions

- The responsive scope covers production-reachable authenticated pages in both Classic and New themes, with priority on Desk, shared shell navigation, and representative data-heavy views.
- The baseline mobile acceptance viewports are 360px phone width and 768px tablet width, matching prior FormCraft mobile specifications.
- Arabic RTL and English LTR are both first-class acceptance contexts for this feature.
- Offline capability is not expanded by this feature; existing offline requirements remain governed by the Mobile and Offline Form Desk specification.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Both Classic and New themes MUST support responsive layouts for production-reachable authenticated pages at phone and tablet viewport sizes.
- **FR-002**: Supported responsive acceptance viewports MUST include 360px phone width and 768px tablet width in both Arabic RTL and English LTR.
- **FR-003**: Production-reachable pages in both themes MUST avoid full-page horizontal scrolling at supported mobile and tablet viewport sizes.
- **FR-004**: Theme shell controls in both themes MUST remain accessible on mobile, including primary navigation, module/mode navigation, theme switching, language switching, profile/account actions, notifications where available, and logout.
- **FR-005**: Mobile navigation in both themes MUST use touch-friendly patterns such as drawers, sheets, stacked menus, or collapsed toolbars when desktop navigation cannot fit.
- **FR-006**: Interactive controls on supported mobile views MUST meet touch-friendly sizing and spacing so users can activate controls without accidental neighboring taps.
- **FR-007**: Form Desk workflows in both themes MUST support mobile template search, template selection, form filling, validation, draft save/resume, submission, and confirmation states.
- **FR-008**: Form fields, labels, help text, validation messages, conditional sections, repeated groups, and action bars MUST remain readable and reachable on supported mobile viewports.
- **FR-009**: Mobile form validation MUST guide users to blocking errors without obscuring the relevant field or the next corrective action.
- **FR-010**: Data-heavy views in both themes MUST provide mobile-appropriate presentations for tables, cards, lists, dashboards, charts, filters, pagination, sorting, row actions, empty states, loading states, and error states.
- **FR-011**: Mobile table behavior MUST preserve key record identity, status, date, owner/customer/template context, and primary row actions even when secondary columns are hidden or collapsed.
- **FR-012**: Filters and search controls available on desktop MUST remain discoverable and usable on mobile unless a specific control is documented as unavailable with a clear explanation.
- **FR-013**: Dialogs, menus, drawers, sheets, popovers, date pickers, select lists, and confirmation prompts MUST fit within the mobile viewport and expose reachable dismiss and confirm actions.
- **FR-014**: Both themes MUST support responsive behavior in Arabic RTL and English LTR, including direction changes after language switching.
- **FR-015**: Responsive layouts MUST handle long localized labels, long record names, long identifiers, and translated status text without overlapping adjacent controls.
- **FR-016**: Responsive changes MUST preserve existing authentication, role-based access, organization scoping, theme preference, language preference, and route-equivalence behavior.
- **FR-017**: Switching themes on a supported mobile viewport MUST lead to the equivalent mobile-ready route when available, or to the nearest safe mobile-ready destination for the user's role.
- **FR-018**: Mobile layouts MUST preserve in-progress user state where applicable, including form values, selected filters, current page position, draft context, and selected records during normal navigation and viewport orientation changes.
- **FR-019**: Any production-reachable page that cannot meet mobile responsiveness requirements in this increment MUST be hidden from mobile navigation, routed to a safe equivalent, or show a clear unavailable state before users enter a broken workflow.
- **FR-020**: Responsive acceptance coverage MUST include representative pages from Desk, Studio/Designer, Admin/Analytics, profile/account, and shared shell navigation where those pages are production-reachable in either theme.

### Key Entities

- **Responsive Theme Shell**: The mobile-adapted top-level frame for Classic or New theme, including navigation, toolbar, account controls, language controls, and theme switch.
- **Mobile Workflow Surface**: A production-reachable page or sequence that users operate on phone or tablet, such as Form Desk, template lists, dashboards, customer records, submissions, reports, or designer screens.
- **Responsive Data View**: A table, list, card grid, chart, dashboard section, or detail view transformed for mobile while preserving key information and actions.
- **Mobile Action Surface**: A drawer, sheet, dialog, menu, sticky action area, or collapsed toolbar used to expose actions in constrained viewports.
- **Viewport Acceptance Matrix**: The set of theme, role, language direction, viewport size, and workflow combinations used to validate responsive behavior.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete the top 5 production Desk workflows in both Classic and New themes on 360px phone and 768px tablet viewports in Arabic RTL and English LTR without full-page horizontal scrolling.
- **SC-002**: 100% of production-reachable shell controls in both themes are reachable and operable on supported phone and tablet viewports.
- **SC-003**: 100% of required form-filling actions in both themes remain visible or reachable within two user interactions on supported mobile viewports.
- **SC-004**: Representative table/list/dashboard screens in both themes preserve record identity, status, primary action, and filtering/search access on supported mobile viewports.
- **SC-005**: Language switching between Arabic RTL and English LTR on mobile completes without visible overlap, clipped required actions, or full-page reload.
- **SC-006**: No production-reachable responsive acceptance page has full-page horizontal scrolling at 360px or 768px widths.
- **SC-007**: At least 90% of invited pilot users can complete assigned mobile validation tasks in both themes without needing desktop-only instructions.
- **SC-008**: Mobile-related support or QA defects for clipped controls, unreachable actions, or overlapping content are reduced by at least 80% after release compared with the pre-release responsive audit baseline.

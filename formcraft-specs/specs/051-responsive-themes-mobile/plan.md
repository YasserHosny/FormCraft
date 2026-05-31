# Implementation Plan: Responsive Classic and New Themes

**Branch**: `051-responsive-themes-mobile` | **Date**: 2026-06-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `formcraft-specs/specs/051-responsive-themes-mobile/spec.md`

## Summary

Add responsive mobile/tablet support to both Classic and New themes across all production-reachable authenticated pages. This is a CSS/template-only feature — no backend changes, no new API endpoints, no schema changes. Work spans: (1) shared responsive infrastructure (breakpoint mixins, responsive tokens), (2) shell/navigation responsiveness for both themes, (3) form-filling mobile adaptation, (4) data view responsiveness (tables, dashboards, cards), and (5) RTL/LTR verification across all changes.

## Technical Context

**Language/Version**: TypeScript / Angular 19 (standalone components for New theme, module-based for Classic)
**Primary Dependencies**: Angular Material, Angular CDK (BreakpointObserver, LayoutModule), RxJS, ngx-translate, existing direction mixins (`_direction-mixins.scss`, `_rtl.scss`)
**Storage**: No changes — existing Supabase PostgreSQL accessed via existing services
**Testing**: Jasmine/Karma (unit), Playwright (e2e — viewport-specific responsive tests)
**Target Platform**: Web browser (mobile-first responsive, RTL-primary)
**Project Type**: Web application (frontend-only SCSS/template changes)
**Performance Goals**: No additional JS bundles >5KB for responsive behavior; CSS-first approach preferred over JS-driven layout changes
**Constraints**: No backend work. No breaking changes to existing desktop layouts. Must work with both Classic (module-based) and New (standalone) component architectures.
**Scale/Scope**: ~25 SCSS files to modify/create, ~15 HTML templates to adapt, 1 shared responsive infrastructure file to create, 2 shell components to modify per theme.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arabic-First, RTL-Native | PASS | All responsive changes use logical properties (margin-inline-start/end, padding-inline) and existing direction mixins. RTL tested at every breakpoint. |
| II. Pixel-Perfect Print Fidelity | N/A | No print/PDF changes. Responsive styles scoped with `@media screen`. |
| III. AI Suggestion, Never Auto-Apply | N/A | No AI integration in this feature. |
| IV. Deterministic Over Probabilistic | PASS | Breakpoint behavior is deterministic CSS media queries. |
| V. Test-First Development | PASS | Playwright viewport tests written before responsive SCSS changes. |
| VI. Normalized Data Model | N/A | No schema changes. |
| VII. Translation-Key Architecture | PASS | No new hardcoded strings. Mobile-specific labels use existing translation keys. |
| VIII. Security and Auditability | PASS | No auth/RBAC changes. FR-016 explicitly preserves existing security behavior. |
| IX. Simplicity and YAGNI | PASS | CSS-first approach, no new components unless unavoidable. Reuse Angular Material responsive utilities. |

## Project Structure

### Documentation (this feature)

```text
formcraft-specs/specs/051-responsive-themes-mobile/
├── plan.md              # This file
├── spec.md              # Feature specification (clarified)
├── tasks.md             # Task breakdown
├── analysis.md          # Cross-artifact consistency analysis
└── checklists/
    └── requirements.md  # Quality checklist
```

### Source Code (repository root)

```text
formcraft-frontend/src/
├── styles/
│   ├── _direction-mixins.scss          # KEEP: existing RTL/LTR mixins
│   ├── _rtl.scss                       # KEEP: existing RTL overrides
│   └── _responsive.scss                # CREATE: shared breakpoint mixins & responsive tokens
├── app/
│   ├── shared/components/
│   │   └── app-shell/
│   │       └── app-shell.component.ts  # MODIFY: add mobile hamburger menu, drawer nav
│   ├── features/
│   │   ├── desk/
│   │   │   ├── dashboard/dashboard.component.scss    # MODIFY: normalize breakpoints, card reflow
│   │   │   ├── fill/fill.component.scss              # MODIFY: mobile form layout, sticky actions
│   │   │   ├── history/history.component.scss         # MODIFY: table→card on phone
│   │   │   ├── customers/customer-list.component.scss # MODIFY: table→card on phone
│   │   │   ├── customers/customer-detail.component.scss # MODIFY: stack layout
│   │   │   └── submission-detail/detail.component.scss  # MODIFY: stack layout
│   │   ├── ui-redesign/
│   │   │   ├── shell/
│   │   │   │   ├── toolbar.component.ts              # MODIFY: hamburger toggle for sidebar
│   │   │   │   ├── toolbar.component.scss            # MODIFY: extend existing media queries to phone
│   │   │   │   ├── sidebar.component.ts              # MODIFY: overlay drawer mode on mobile
│   │   │   │   └── sidebar.component.scss            # MODIFY: overlay drawer styles
│   │   │   ├── desk/
│   │   │   │   ├── dashboard.component.scss          # MODIFY: card reflow, KPI stack
│   │   │   │   ├── form-filler.component.scss        # MODIFY: mobile form layout
│   │   │   │   └── customers.component.scss          # MODIFY: table→card
│   │   │   ├── admin/
│   │   │   │   └── analytics.component.scss          # MODIFY: chart/card reflow
│   │   │   ├── studio/
│   │   │   │   ├── template-list.component.scss      # MODIFY: card grid→single column
│   │   │   │   └── designer.component.ts             # MODIFY: add mobile unavailable guard
│   │   │   └── shared/
│   │   │       ├── fc-tokens.scss                    # MODIFY: add responsive token overrides
│   │   │       └── components/
│   │   │           └── kpi-card.component.scss        # MODIFY: compact mobile sizing
│   │   ├── admin/                                     # MODIFY: responsive admin pages
│   │   ├── analytics/                                 # MODIFY: responsive chart layouts
│   │   └── auth/
│   │       └── profile/profile.component.scss         # MODIFY: stack layout
```

**Structure Decision**: Frontend-only changes. All responsive behavior added to existing SCSS/template files. One new shared file (`_responsive.scss`) for breakpoint mixins.

## Architecture

### Responsive Strategy

**CSS-first, progressive enhancement approach:**

1. **Shared breakpoint mixins** (`_responsive.scss`): Standardized mixins for phone/tablet/desktop breakpoints that all components import. Eliminates the current inconsistency (599px vs 768px vs 959px).

2. **Breakpoint definitions**:
   - `$fc-phone-max: 599px` — phone portrait/landscape
   - `$fc-tablet-min: 600px` / `$fc-tablet-max: 959px` — tablet
   - `$fc-desktop-min: 960px` — desktop (existing behavior)

3. **Angular CDK BreakpointObserver**: Used only where CSS alone is insufficient — specifically for:
   - Classic shell: toggling hamburger menu visibility and drawer mode
   - New theme shell: toggling sidebar between permanent and overlay
   - Designer: showing mobile-unavailable guard

4. **Logical properties everywhere**: All new responsive CSS uses `margin-inline-start/end`, `padding-inline`, `inset-inline-start/end` instead of physical left/right. This ensures RTL works automatically.

5. **No new components**: Responsive behavior is added to existing components via SCSS media queries and minimal template `@if` blocks driven by BreakpointObserver signals.

### Shell Responsiveness

**Classic Theme (`app-shell.component.ts`)**:
- Desktop (≥960px): Current toolbar + mode tabs (no change)
- Tablet (600–959px): Toolbar with collapsed tab labels (icons only), search hidden
- Phone (≤599px): Hamburger button → slide-out drawer with mode tabs stacked vertically, user chip shows avatar only

**New Theme (`toolbar + sidebar`)**:
- Desktop (≥960px): Current toolbar + permanent sidebar (no change)
- Tablet (600–959px): Toolbar with sidebar collapsed to icons-only rail (56px wide)
- Phone (≤599px): Toolbar with hamburger → sidebar as full overlay drawer, brand name hidden

### Data View Strategy

**Tables**: Conditional class `fc-table-responsive` applied via `@media`:
- ≤599px: Tables with >4 visible columns switch to card layout via CSS (`display: block` on rows, flexbox internal layout). Key columns (identity, status, date, action) always visible. Secondary columns in expandable section.
- 600–959px: Horizontal scroll within contained region for wide tables.
- ≥960px: Standard table (no change).

**Dashboards/KPIs**: CSS Grid with `auto-fit` and `minmax()` for natural reflow. No JS needed.

**Filters**: On phone, filters collapse into a slide-up bottom sheet triggered by a filter icon button. On tablet, filters stack vertically above content.

### Form Filling Strategy

- Form sections stack vertically on all viewports (already mostly the case)
- Multi-column field layouts (`grid-template-columns`) collapse to single column on phone
- Action bar (Submit, Save Draft, Print) becomes sticky bottom bar on phone
- Validation error scroll-to uses `scrollIntoView({ block: 'center' })` to account for sticky bars
- Date pickers use Angular Material's touch-optimized mode on phone viewports

### Mobile-Unavailable Routes

Routes that cannot be made responsive (Designer canvas) show a centered card with:
- Icon indicating desktop-required
- Translated message: "This feature requires a desktop screen"
- Button to navigate to the nearest mobile-ready route for the user's role

## Dependencies

### Internal
- Existing `_direction-mixins.scss` — reuse for RTL-aware responsive spacing
- Existing `_rtl.scss` — extend with responsive-specific RTL fixes if needed
- Existing `fc-tokens.scss` — add responsive token overrides (sidebar width, toolbar height on mobile)
- Angular CDK `BreakpointObserver` — already in Angular Material dependency tree

### External
- None — no new packages required

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Desktop layout regression from media query side effects | High | All new responsive CSS scoped inside `@media` blocks; Playwright desktop viewport tests added alongside mobile tests |
| Inconsistent breakpoint usage across classic theme | Medium | Shared `_responsive.scss` mixins normalize all breakpoints; existing ad-hoc breakpoints migrated in Phase 2 |
| RTL layout breaks on mobile only | High | Every responsive change tested in both `dir="rtl"` and `dir="ltr"` at each breakpoint; RTL-specific Playwright tests |
| Angular Material dialog/menu not fitting phone viewport | Medium | Global `.cdk-overlay-pane` max-width override for phone; dialog `maxWidth: '95vw'` default |
| Conflict with F052 parallel work | Low | F051 touches only SCSS/template files for responsive behavior; F052 scope confirmed non-overlapping |

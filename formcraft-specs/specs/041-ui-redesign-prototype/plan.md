# Implementation Plan: Dual Theme Experience and UI Redesign Rollout

**Branch**: `codex/fix-ui-redesign-templates` | **Date**: 2026-05-28 | **Spec**: `specs/041-ui-redesign-prototype/spec.md`
**Input**: Feature specification from `/specs/041-ui-redesign-prototype/spec.md` (rev 2)

## Summary

FormCraft requires a dual-theme system where users can switch between the existing Classic shell and a New redesigned shell. The New theme must achieve full feature parity with the Classic shell for production-reachable screens: theme preference persistence, context-aware route mapping, role-based navigation, language switching, real-time notifications, org branding, global search integration, and sidebar with live data. All mock data must be removed from production paths.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript / Angular 19 (frontend)
**Primary Dependencies**: FastAPI, Angular Material, Supabase (PostgreSQL + Auth), RxJS
**Storage**: localStorage (theme preference), Supabase PostgreSQL (all business data)
**Testing**: pytest (backend), Jasmine/Karma (frontend), manual browser verification
**Target Platform**: Web — desktop browsers (1280px–1920px), RTL-first
**Project Type**: Web application (polyrepo: frontend + backend + specs)
**Performance Goals**: Theme switch renders target shell within 2 seconds (NFR-005)
**Constraints**: No flash of wrong theme on refresh (NFR-002), no nested shells (FR-022)
**Scale/Scope**: 15 implementation items across P1/P2/P3 priorities

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arabic-First, RTL-Native | PASS | New theme adds dynamic `dir` switching via LanguageService; layout tested RTL+LTR |
| II. Pixel-Perfect Print Fidelity | N/A | No PDF/canvas changes in this feature |
| III. AI Suggestion, Never Auto-Apply | N/A | No AI behavior changes |
| IV. Deterministic Over Probabilistic | PASS | Route mapping is deterministic lookup table |
| V. Test-First Development | PASS | Unit tests for ThemePreferenceService, route mapper, role filtering |
| VI. Normalized Data Model | PASS | No schema changes; sidebar uses existing API data |
| VII. Translation-Key Architecture | PASS | New toolbar integrates LanguageService; all labels use translation keys where Classic does |
| VIII. Security and Auditability | PASS | Role-based tab filtering; RoleGuard on all New routes already in place |
| IX. Simplicity and YAGNI | PASS | Only implementing what the spec requires; no new business workflows |

## Project Structure

### Documentation (this feature)

```text
formcraft-specs/specs/041-ui-redesign-prototype/
├── spec.md              # Feature specification (rev 2)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (minimal — no schema changes)
├── contracts/           # Phase 1 output
│   └── route-equivalence.ts   # Route mapper interface contract
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
formcraft-frontend/src/app/
├── core/
│   └── services/
│       └── theme-preference.service.ts    # NEW: localStorage persistence + route mapper
├── shared/
│   └── components/
│       └── app-shell/
│           └── app-shell.component.ts     # MODIFY: use route mapper for theme switch
├── features/
│   └── ui-redesign/
│       ├── shell/
│       │   ├── layout.component.ts        # MODIFY: dynamic dir, LanguageService
│       │   ├── toolbar.component.ts       # MODIFY: role filtering, lang toggle, notifications, org logo, profile, search
│       │   ├── toolbar.component.html     # MODIFY: all control bindings
│       │   └── sidebar.component.ts       # MODIFY: remove mock-data import, use API data
│       └── shared/
│           └── mock-data.ts               # MODIFY: remove SIDEBAR_DATA (keep only test/demo exports)
├── app.component.ts                       # MODIFY: check theme preference on init
└── app-routing.module.ts                  # MODIFY: theme-aware default redirect

formcraft-frontend/src/app/core/services/
└── theme-preference.service.ts            # NEW FILE

formcraft-frontend/src/app/
└── tests for above files
```

**Structure Decision**: All changes are within the existing frontend polyrepo structure. One new service file (`theme-preference.service.ts`) is added to `core/services/`. No backend changes needed — all required APIs already exist.

## Design Decisions

### D1: Theme Preference Service (FR-034, FR-035, FR-036)

A single `ThemePreferenceService` in `core/services/` handles:
- **Persistence**: Read/write `fc_theme_preference` in localStorage
- **Route equivalence mapping**: A pure function `mapRouteToTheme(currentUrl, targetTheme)` that parses the URL, extracts params, and returns the equivalent route per the Route Equivalence Matrix
- **Theme-aware redirect**: Used by `AppComponent` and routing to resolve the correct landing page

**Rationale**: Centralizing in one service avoids duplicating route-mapping logic across both shells. The Classic shell's `getRedesignRoute()` and the New toolbar's hardcoded links both get replaced by calls to this service.

### D2: Toolbar Feature Parity (FR-037–FR-042)

The New toolbar component gains these injected services:
- `LanguageService` — for language toggle + dynamic `dir` on layout
- `AuthService` (already present) — for role-based tab filtering
- `OrgAdminService` — for org logo
- `MyFeedbackService` + `FeedbackRealtimeService` — for live notification count
- `ThemePreferenceService` — for context-aware theme switch

Each maps 1:1 to an existing Classic shell feature. No new APIs needed.

### D3: Sidebar Data Source (FR-043, FR-044)

The sidebar stops importing `SIDEBAR_DATA` from `mock-data.ts`. Instead:
- Navigation structure (icons, labels, routes) is defined inline in the component as a static config — these are UI structure, not business data
- Badge counts are fetched from existing APIs (template count, draft count, customer count) or omitted
- Items with `route: ''` get `[class.disabled]="true"` and `matTooltip="قريباً"`

### D4: Global Search Integration (FR-042)

The New toolbar replaces the non-functional `<input>` with the existing `<fc-global-search-bar>` component already used in the Classic shell. If `GlobalSearchBarComponent` has module dependencies, they are imported into the toolbar's standalone imports.

### D5: Layout Direction Switching (FR-037)

The layout component's hardcoded `dir="rtl"` becomes `[attr.dir]="currentDir"` bound to `LanguageService.getLanguage() === 'ar' ? 'rtl' : 'ltr'`, updating on language change subscription.

## Phases

### Phase 1: Core Theme Infrastructure (P1)
1. Create `ThemePreferenceService` with localStorage persistence and route mapper
2. Update `AppComponent` to check theme preference on init and redirect
3. Update `app-routing.module.ts` default/wildcard redirects to be theme-aware
4. Update Classic shell (`app-shell.component.ts`) to use route mapper for "switch to New" link
5. Update New toolbar theme-switch to use route mapper for "switch to Classic" link

### Phase 2: New Toolbar Feature Parity (P1)
6. Add role-based mode tab filtering to New toolbar
7. Add language toggle to New toolbar + dynamic `dir` on layout
8. Add real notification count to New toolbar (inject MyFeedbackService + realtime)
9. Add org logo to New toolbar (inject OrgAdminService)
10. Wire profile menu to `/auth/profile`

### Phase 3: Sidebar & Search (P1–P2)
11. Remove `mock-data.ts` sidebar import, define navigation structure inline
12. Add disabled styling + tooltip for unavailable sidebar items
13. Replace search input with `GlobalSearchBarComponent`

### Phase 4: Cleanup & Verification (P2–P3)
14. Remove hardcoded `unreadCount = 7` default
15. Verify no production component imports from `mock-data.ts`
16. Help menu: hide or add actionable item
17. Browser verification at 1280px, 1366px, 1440px, 1920px in RTL and LTR

## Complexity Tracking

No constitution violations. All changes use existing services and patterns already established in the Classic shell.

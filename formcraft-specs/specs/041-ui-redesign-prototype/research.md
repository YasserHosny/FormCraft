# Research: Dual Theme Experience

## R1: Theme Preference Storage Mechanism

**Decision**: `localStorage` under key `fc_theme_preference` with values `classic` | `new`
**Rationale**: Immediate availability without API round-trip on page load. Prevents flash of wrong theme (NFR-002). No backend migration needed. Already how `LanguageService` stores language preference.
**Alternatives considered**:
- Supabase user profile column: Requires migration, API call before rendering, slower cold start. Deferred to future increment for cross-device sync.
- Cookie: No advantage over localStorage for SPA; adds unnecessary HTTP overhead.

## R2: Route Equivalence Mapper Design

**Decision**: Pure function `mapRouteToTheme(currentUrl: string, target: 'classic' | 'new'): string` with a static lookup table matching the spec's Route Equivalence Matrix. Extracts `:pageId`, `:templateId`, and query params via regex/URL parsing.
**Rationale**: Deterministic, testable, no side effects. Both shells call the same function. Easy to extend when new routes are added to the matrix.
**Alternatives considered**:
- Router config metadata: Would require adding custom data to every route definition. More coupled, harder to test in isolation.
- Service with injected Router: Adds unnecessary DI complexity for what is fundamentally a string-to-string mapping.

## R3: Notification Integration in New Toolbar

**Decision**: Inject `MyFeedbackService` for initial count + `FeedbackRealtimeService` for live updates, matching the Classic shell's exact implementation.
**Rationale**: The services already exist and work. The Classic shell proves the pattern. No new API endpoints needed.
**Alternatives considered**:
- New notification API: Unnecessary — existing services cover the requirement.
- Shared notification state service: Over-engineering for this increment.

## R4: Sidebar Badge Count Sources

**Decision**: For production-ready sidebar items, fetch counts from existing services:
- Template count: `TemplateService.list()` response length (already loaded by template-list component)
- Other counts: Omit badge counts for prototype-only sections until APIs are wired
**Rationale**: Only the Studio templates route is production-ready. Other sections (Desk, Admin) are prototype-gated. Showing real counts only where data is real follows FR-030.
**Alternatives considered**:
- New sidebar-counts API endpoint: Over-engineering; the counts can be derived from existing list responses or omitted.

## R5: GlobalSearchBarComponent Integration

**Decision**: Import and render `GlobalSearchBarComponent` in New toolbar, matching Classic shell.
**Rationale**: Component already exists as a standalone component. Reusing it ensures feature parity with zero new code.
**Alternatives considered**:
- Rebuild search in New theme: Violates YAGNI and creates divergence.
- Show disabled placeholder: Acceptable fallback if integration has issues, but direct import is preferred.

## R6: Help Menu Content

**Decision**: Help menu shows "فتح الثيم الكلاسيكي" (switch to Classic) and a "اختصارات لوحة المفاتيح" (keyboard shortcuts) item that opens a simple dialog or is disabled with tooltip. If no shortcuts dialog exists, the help button shows a tooltip "المساعدة قريباً" and is visually muted.
**Rationale**: Spec (FR-023) requires help menu to have actionable items. Minimum viable: theme switch + one placeholder with clear unavailable state.
**Alternatives considered**:
- Full help center: Out of scope for this increment.
- Remove help button entirely: Violates FR-023 which lists it as a required control.

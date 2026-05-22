# Research: Mode Switching UX

**Date**: 2026-05-16

## Research Questions

No NEEDS CLARIFICATION items in the spec. Research focused on implementation approach validation.

## Findings

### 1. Angular Router Lazy Loading for Mode Prefixes

**Decision**: Use route groups with `loadChildren` per mode prefix.

**Rationale**: The existing codebase already uses lazy loading (`import('./features/designer/designer.module').then(m => m.DesignerModule)`). Wrapping these in parent route groups with prefixes (`/studio`, `/desk`, `/admin`) requires only routing configuration changes, not module restructuring.

**Key insight from existing code**: `app-routing.module.ts` already has role guards on routes. The mode prefix is an additional organizational layer on top of existing guards — not a replacement.

### 2. MatTabNav vs Custom Implementation

**Decision**: Use `MatTabNav` + `MatTabLink` from `@angular/material/tabs`.

**Rationale**: 
- Already in the project's dependency tree (Angular Material is the UI framework)
- `MatTabNavBar` is specifically designed for navigation (vs `MatTabGroup` which is for content panels)
- Provides: keyboard navigation, active ink bar, ARIA roles, RTL support out of the box
- Existing `app-shell.component.ts` already uses `mat-toolbar` and `mat-button` — adding `mat-tab-nav-bar` is consistent

### 3. Preferred Mode Storage

**Decision**: Add `preferred_mode` column to existing `profiles` table.

**Rationale**:
- `profiles` table already stores `language` preference — mode preference is the same pattern
- Single column addition via ALTER TABLE — minimal migration
- NULL means "use role default" — no need to backfill existing rows
- Supabase RLS on profiles already limits access to own profile

### 4. Backward Compatibility Strategy

**Decision**: Add redirect routes from old paths to new paths.

**Rationale**:
- Existing users may have bookmarked `/templates` or `/designer/123`
- Angular Router's `redirectTo` handles this without server changes
- Redirects can be removed in a future release once users have updated bookmarks
- No SEO impact (internal app, not public-facing)

## Alternatives Considered

| Option | Rejected Because |
|--------|-----------------|
| Micro-frontends per mode | Massive over-engineering for 3 modes; shared state (user, auth) becomes a distributed systems problem |
| URL query param for mode (`?mode=desk`) | Not SEO-friendly, doesn't work with Angular route guards, ugly URLs |
| Separate Angular apps | Same auth/session problem as micro-frontends; triple the build/deploy complexity |
| Mode stored in localStorage only | Doesn't sync across devices; cleared on browser reset |

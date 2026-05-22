# Implementation Plan: Mode Switching UX

**Branch**: `014-mode-switching-ux` | **Date**: 2026-05-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/014-mode-switching-ux/spec.md`

## Summary

Restructure FormCraft's frontend navigation from a flat route model (all routes under root) to a three-mode architecture with top-level mode tabs (Design Studio, Form Desk, Admin Console). Each mode has its own route prefix (`/studio/*`, `/desk/*`, `/admin/*`), role-based visibility, and persistent user preference. The existing app shell toolbar is extended with mode tabs, and route guards are enhanced to enforce mode-level access control.

## Technical Context

**Language/Version**: TypeScript / Angular 17 (frontend), Python 3.12 / FastAPI (backend — minor changes)
**Primary Dependencies**: Angular Router, Angular Material (MatToolbar, MatTabNav), @ngx-translate/core
**Storage**: Supabase PostgreSQL (profiles table — add preferred_mode column)
**Testing**: Jasmine + Karma (frontend), pytest (backend)
**Target Platform**: Modern browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (SPA)
**Performance Goals**: Mode switch < 200ms, route guard < 50ms, nav bar render < 100ms
**Constraints**: Must not break existing routes during migration; lazy-loaded modules
**Scale/Scope**: 5 role types, 3 modes, ~15 existing routes to reorganize

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|:------:|-------|
| I. Arabic-First, RTL-Native | PASS | Mode tabs use i18n JSON labels; nav bar already flips for RTL |
| II. mm-Precision Guarantee | N/A | No PDF or canvas changes |
| III. Deterministic-First Validation | N/A | No validation changes |
| IV. Two-Mode Architecture | PASS | This feature IS the implementation of Principle IV |
| V. Data Sovereignty & Multi-Tenancy | PASS | preferred_mode is per-user, no cross-org data |
| VI. Audit Everything | PASS | Mode preference change logged via existing audit middleware |
| VII. Template Versioning | N/A | No template changes |

## Project Structure

### Documentation (this feature)

```text
specs/014-mode-switching-ux/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
formcraft-backend/
├── app/
│   ├── api/users.py              # PATCH /api/users/me — accept preferred_mode field
│   ├── models/user.py            # Add preferred_mode to User model
│   └── schemas/user.py           # Add preferred_mode to UserUpdate schema
└── migrations/
    └── 015_add_preferred_mode.sql  # ALTER profiles ADD preferred_mode

formcraft-frontend/
├── src/app/
│   ├── app-routing.module.ts           # REWRITE: mode-based route structure
│   ├── core/
│   │   ├── auth/
│   │   │   ├── auth.guard.ts           # UPDATE: redirect to role-default mode
│   │   │   ├── role.guard.ts           # UPDATE: mode-aware redirects with toast
│   │   │   └── auth.service.ts         # UPDATE: add preferred_mode to User interface
│   │   └── navigation/
│   │       ├── mode.config.ts          # NEW: mode definitions (routes, labels, roles)
│   │       ├── mode.service.ts         # NEW: active mode tracking, preference save
│   │       └── mode.guard.ts           # NEW: mode-level route guard
│   ├── shared/
│   │   └── components/
│   │       ├── app-shell/
│   │       │   └── app-shell.component.ts  # UPDATE: add mode tabs
│   │       └── mode-tabs/
│   │           ├── mode-tabs.component.ts  # NEW: mode tab bar component
│   │           └── mode-tabs.component.html
│   └── features/
│       ├── studio/                     # NEW: wrapper module for /studio/*
│       │   └── studio-routing.module.ts
│       ├── desk/                       # NEW: wrapper module for /desk/*
│       │   └── desk-routing.module.ts
│       └── admin/                      # Existing admin routes reorganized
│           └── admin-routing.module.ts
└── src/assets/i18n/
    ├── ar.json                         # Add mode.studio, mode.desk, mode.admin keys
    └── en.json                         # Add mode.studio, mode.desk, mode.admin keys
```

**Structure Decision**: Extend existing polyrepo structure. New `core/navigation/` module owns mode-switching logic. Existing feature modules wrapped under mode route prefixes via re-export routing modules — no internal refactoring of existing features.

## Phase 0: Research

No NEEDS CLARIFICATION items. All technology already in use.

**Decision 1**: Use Angular Router's child route groups with lazy loading for each mode prefix.
- **Rationale**: Angular's `loadChildren` naturally maps to mode prefixes. Each mode is a route group.
- **Alternatives rejected**: Separate Angular apps (shared state too complex); flat routes with visual-only tabs (no real mode isolation).

**Decision 2**: Store `preferred_mode` in `profiles` table as an enum column.
- **Rationale**: Server-side persistence works across devices. The profiles table already has language preference.
- **Alternatives rejected**: localStorage only (doesn't sync across devices); separate preferences table (over-engineered for one field).

**Decision 3**: Use `MatTabNav` (Angular Material navigation tabs) for the mode tab bar.
- **Rationale**: Already using Angular Material. MatTabNav provides accessible keyboard nav, active ink bar, and is semantically correct for navigation (vs content) tabs.
- **Alternatives rejected**: Custom tab component (reinventing the wheel); MatButtonToggle (wrong semantics).

## Phase 1: Design

### Data Model

**Migration**: `015_add_preferred_mode.sql`

```sql
ALTER TABLE profiles
ADD COLUMN preferred_mode TEXT
CHECK (preferred_mode IN ('studio', 'desk', 'admin'))
DEFAULT NULL;

COMMENT ON COLUMN profiles.preferred_mode IS
  'Last-used product mode. NULL means use role default.';
```

No new tables. No RLS changes (preferred_mode is on the user's own profile, already gated by existing profile RLS).

### Contracts

**Backend API change** — `PATCH /api/users/me`:

Request body (existing endpoint, new optional field):
```json
{
  "preferred_mode": "desk"  // optional, enum: "studio" | "desk" | "admin" | null
}
```

Response (existing, extended):
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "role": "designer",
  "language": "ar",
  "display_name": "Ahmed",
  "preferred_mode": "desk"
}
```

Validation: If `preferred_mode` is set to a mode the user's role doesn't permit, return 422 with error `"Role '{role}' does not have access to mode '{mode}'"`.

**Frontend route architecture**:

Current → Target mapping:
| Current Path | Target Path | Redirect? |
|---|---|---|
| `/templates` | `/studio/templates` | Yes (301-style via Angular redirect) |
| `/designer/:pageId` | `/studio/designer/:pageId` | Yes |
| `/admin/feedback` | `/admin/feedback` | No change |
| `/my-feedback` | `/desk/my-feedback` | Yes |
| `/` | (role-default mode) | Dynamic |

### Mode Configuration

```typescript
export interface ModeConfig {
  id: 'studio' | 'desk' | 'admin';
  routePrefix: string;
  defaultRoute: string;
  labelKey: string;
  icon: string;
  permittedRoles: string[];
}

export const MODES: ModeConfig[] = [
  {
    id: 'studio',
    routePrefix: '/studio',
    defaultRoute: '/studio/templates',
    labelKey: 'modes.studio',
    icon: 'design_services',
    permittedRoles: ['admin', 'designer'],
  },
  {
    id: 'desk',
    routePrefix: '/desk',
    defaultRoute: '/desk',
    labelKey: 'modes.desk',
    icon: 'assignment',
    permittedRoles: ['admin', 'designer', 'operator', 'viewer'],
  },
  {
    id: 'admin',
    routePrefix: '/admin',
    defaultRoute: '/admin/feedback',
    labelKey: 'modes.admin',
    icon: 'admin_panel_settings',
    permittedRoles: ['admin'],
  },
];

export const ROLE_DEFAULT_MODE: Record<string, string> = {
  admin: 'admin',
  designer: 'studio',
  operator: 'desk',
  viewer: 'desk',
};
```

### Login Redirect Logic

```
On successful login:
  1. Load user profile (role, preferred_mode)
  2. If preferred_mode is set AND user's role permits that mode:
       -> navigate to that mode's defaultRoute
  3. Else:
       -> navigate to ROLE_DEFAULT_MODE[user.role]'s defaultRoute
  4. On mode tab click:
       -> navigate to clicked mode's defaultRoute
       -> PATCH /api/users/me { preferred_mode: newMode } (fire-and-forget, non-blocking)
```

### Route Guard Enhancement

Current `RoleGuard` redirects to `/templates`. Updated behavior:
- On unauthorized access: redirect to user's default mode root + show toast
- Toast message key: `errors.unauthorized_mode` (bilingual)
- New `ModeGuard` checks if current route prefix matches a mode the user's role permits

### i18n Keys

```json
// ar.json additions
{
  "modes": {
    "studio": "استوديو التصميم",
    "desk": "مكتب النماذج",
    "admin": "لوحة الإدارة"
  },
  "errors": {
    "unauthorized_mode": "غير مصرح بهذا القسم"
  }
}

// en.json additions
{
  "modes": {
    "studio": "Design Studio",
    "desk": "Form Desk",
    "admin": "Admin Console"
  },
  "errors": {
    "unauthorized_mode": "You don't have access to this section"
  }
}
```

## Complexity Tracking

No constitution violations. No unnecessary complexity.

| Decision | Justification |
|----------|--------------|
| Redirect routes for backward compat | Existing bookmarks and shared links must not break. Redirects are temporary (remove in v2) |
| Fire-and-forget preference save | NFR-004 requires non-blocking. If save fails, user simply sees role default next login — acceptable degradation |

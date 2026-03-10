# Tasks: Authentication & User Management

**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Format: `[ID] [Priority] [Story] Description`

## Phase 1: Setup (Shared Infrastructure)

- [ ] **T01-001** P1 Setup — Create Supabase project, configure Auth (email/password provider), get API keys
- [ ] **T01-002** P1 Setup — Create `supabase/migrations/001_create_profiles.sql` with profiles table schema, role check constraint, language check constraint
- [ ] **T01-003** P1 Setup — Create `supabase/migrations/002_create_audit_logs.sql` with audit_logs table schema
- [ ] **T01-004** P1 Setup — Create `supabase/seed.sql` with initial Admin user
- [ ] **T01-005** P1 Setup — Run migrations against Supabase Cloud via `supabase db push`

## Phase 2: Backend — Auth & User Service

- [ ] **T01-010** P1 S1 — Create `app/core/supabase.py` — Supabase client singleton, initialized from env vars
- [ ] **T01-011** P1 S1 — Create `app/core/config.py` — Settings class with `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY` validation
- [ ] **T01-012** P1 S2 — Create `app/core/security.py` — `verify_jwt()` function using Supabase JWT secret, extract user_id
- [ ] **T01-013** P1 S2 — Create `app/models/user.py` — User, UserProfile Pydantic models
- [ ] **T01-014** P1 S2 — Create `app/schemas/auth.py` — LoginRequest, LoginResponse, RegisterRequest, RefreshRequest schemas
- [ ] **T01-015** P1 S2 — Create `app/schemas/user.py` — UserProfileResponse, UpdateProfileRequest schemas
- [ ] **T01-016** P1 S2 — Create `app/services/user_service.py` — get_profile(), update_profile(), create_user(), list_users(), deactivate_user()
- [ ] **T01-017** P1 S3 — Create `app/api/deps.py` — `get_current_user` dependency (JWT → user_id → profile lookup), `require_role(roles)` dependency factory
- [ ] **T01-018** P1 S2 — Create `app/api/routes/auth.py` — POST /auth/login, POST /auth/register, POST /auth/refresh, POST /auth/logout
- [ ] **T01-019** P1 S1 — Create `app/api/routes/users.py` — GET /users/me, PUT /users/me, GET /users (admin), PUT /users/{id}/role (admin)

## Phase 3: Backend — Tests

- [ ] **T01-030** P1 S2 — Write unit tests: `tests/unit/test_security.py` — JWT verification, role extraction, tampered token rejection
- [ ] **T01-031** P1 S3 — Write unit tests: `tests/unit/test_deps.py` — require_role returns 403 for unauthorized roles
- [ ] **T01-032** P1 S1-S3 — Write integration tests: `tests/integration/test_auth_endpoints.py` — login, register, refresh, role-based access
- [ ] **T01-033** P1 S4 — Write integration tests: `tests/integration/test_user_profile.py` — get profile, update language preference

## Phase 4: Frontend — Auth Module

- [ ] **T01-040** P1 S2 — Create `src/app/core/auth/auth.service.ts` — login(), logout(), refresh(), isAuthenticated$, currentUser$
- [ ] **T01-041** P1 S2 — Create `src/app/core/auth/auth.interceptor.ts` — HTTP interceptor adding Authorization header
- [ ] **T01-042** P1 S3 — Create `src/app/core/auth/auth.guard.ts` — CanActivate guard checking authentication
- [ ] **T01-043** P1 S3 — Create `src/app/core/auth/role.guard.ts` — CanActivate guard checking user role
- [ ] **T01-044** P1 S2 — Create `src/app/core/models/user.model.ts` — User interface, Role enum
- [ ] **T01-045** P1 S2 — Create `src/app/features/auth/login/` — Login page with Angular Material form (email, password, submit)
- [ ] **T01-046** P1 S4 — Create `src/app/features/auth/profile/` — Profile page with language preference selector
- [ ] **T01-047** P1 S1 — Create `src/app/features/auth/register/` — Admin-only register page

## Phase 5: Frontend — Tests

- [ ] **T01-050** P1 S2 — Write unit tests: auth.service.spec.ts — login, logout, token storage
- [ ] **T01-051** P1 S3 — Write unit tests: auth.guard.spec.ts, role.guard.spec.ts — redirect behavior

## Dependencies & Execution Order

```
T01-001 → T01-002 → T01-003 → T01-004 → T01-005 (sequential: DB setup)
T01-005 → T01-010 → T01-011 (backend config depends on Supabase)
T01-011 → T01-012 → T01-017 (security → deps chain)
T01-013, T01-014, T01-015 (parallel: models/schemas)
T01-016 → T01-018, T01-019 (service → routes)
T01-030, T01-031 (parallel: unit tests after implementation)
T01-040 → T01-041 → T01-042, T01-043 (frontend auth chain)
T01-044, T01-045, T01-046, T01-047 (parallel after auth.service)
```

## Parallel Opportunities

- Backend models/schemas (T01-013, T01-014, T01-015) can be written in parallel
- Frontend components (T01-045, T01-046, T01-047) can be written in parallel after auth.service
- Backend tests (T01-030, T01-031) can be written in parallel

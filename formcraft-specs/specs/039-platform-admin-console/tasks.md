# Tasks: Platform Admin Console

**Feature**: Platform Admin Console  
**Spec**: [spec.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/039-platform-admin-console/spec.md)  
**Plan**: [plan.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/039-platform-admin-console/plan.md)  
**Branch**: `039-platform-admin-console`  
**Date**: 2026-05-26

## Dependencies & Execution Order

```text
Phase 1 (Setup)
    ↓
Phase 2 (Foundational)
    ↓
Phase 3 (User Story 1 — Organization List & Management)
    ↓
Phase 4 (User Story 2 — Create Organization)
    ↓
Phase 5 (User Story 3 — Organization Detail View)
    ↓
Phase 6 (User Story 4 — Platform Dashboard)
    ↓
Phase 7 (Polish & Cross-Cutting)
```

Parallel execution opportunities are marked with **[P]**.

---

## Phase 1: Setup

- [ ] T001 Run database migration `039_platform_admin_console.sql` adding `domain` to `organizations`, `status` enum, `tier_limits` table, and `platform_metrics_mv` materialized view.
- [ ] T002 Seed `tier_limits` table with starter/professional/enterprise/platform defaults.
- [ ] T003 Add translation keys for platform console to `formcraft-frontend/src/assets/i18n/en.json` and `ar.json`.

---

## Phase 2: Foundational

- [ ] T004 [P] Create backend schema DTOs in `formcraft-backend/app/schemas/platform.py` (OrganizationCreate, OrganizationUpdate, OrganizationSummary, OrganizationDetail, PlatformMetrics).
- [ ] T005 [P] Create `PlatformAdminGuard` in `formcraft-frontend/src/app/core/guards/platform-admin.guard.ts` checking `is_platform_admin`.
- [ ] T006 [P] Create `PlatformService` frontend service in `formcraft-frontend/src/app/core/services/platform.service.ts` with methods for org list, create, detail, suspend, reactivate, metrics.
- [ ] T007 Create Angular `platform` feature module and lazy-loaded routing in `formcraft-frontend/src/app/features/platform/platform.module.ts` and `platform-routing.module.ts`.
- [ ] T008 Create `ContextSwitcherComponent` in `formcraft-frontend/src/app/features/platform/platform-layout/context-switcher/` for dual-role users.
- [ ] T009 Update main navigation to show "Platform" tab conditionally and include context switcher when `is_platform_admin=true`.

---

## Phase 3: User Story 1 — Organization List & Management

**Goal**: Platform admin can list, search, filter, sort, suspend, and reactivate organizations.

**Independent Test**: Login as platform admin → `/platform/organizations` → verify table, search, filter, suspend, reactivate.

- [ ] T010 [P] [US1] Write failing backend contract tests for `GET /platform/organizations` (search, filter, sort, pagination) in `formcraft-backend/tests/integration/test_platform_routes.py`.
- [ ] T011 [P] [US1] Write failing backend unit tests for `PlatformService.list_organizations()` in `formcraft-backend/tests/unit/test_platform_service.py`.
- [ ] T012 [US1] Implement `list_organizations` query with search, tier/status/country filters, and sorting in `formcraft-backend/app/services/platform_service.py`.
- [ ] T013 [US1] Implement `GET /platform/organizations` endpoint in `formcraft-backend/app/api/routes/platform.py`.
- [ ] T014 [US1] Implement `suspend_organization` with immediate Supabase session revocation in `formcraft-backend/app/services/platform_service.py`.
- [ ] T015 [US1] Implement `POST /platform/organizations/{org_id}/suspend` endpoint in `formcraft-backend/app/api/routes/platform.py`.
- [ ] T016 [US1] Implement `reactivate_organization` in `formcraft-backend/app/services/platform_service.py`.
- [ ] T017 [US1] Implement `POST /platform/organizations/{org_id}/reactivate` endpoint in `formcraft-backend/app/api/routes/platform.py`.
- [ ] T018 [US1] Add audit logging for suspend and reactivate actions.
- [ ] T019 [US1] Create `OrganizationListComponent` in `formcraft-frontend/src/app/features/platform/organization-list/` with Angular Material table, search, filters, sort, and action buttons.
- [ ] T020 [US1] Implement suspend/reactivate confirmation dialogs and API integration in `organization-list.component.ts`.

---

## Phase 4: User Story 2 — Create Organization

**Goal**: Platform admin can create organizations with first-admin invitation, rate limiting, and domain validation.

**Independent Test**: Click "Create Organization" → fill form → submit → verify org created and invitation sent.

- [ ] T021 [P] [US2] Write failing backend unit tests for `create_organization` with rate limit and domain uniqueness in `formcraft-backend/tests/unit/test_platform_service.py`.
- [ ] T022 [P] [US2] Write failing backend contract tests for `POST /platform/organizations` and `POST /platform/organizations/{org_id}/invite-first-admin` in `formcraft-backend/tests/integration/test_platform_routes.py`.
- [ ] T023 [US2] Implement `create_organization` with rate-limit check (10/hour) and domain uniqueness validation in `formcraft-backend/app/services/platform_service.py`.
- [ ] T024 [US2] Implement `POST /platform/organizations` endpoint in `formcraft-backend/app/api/routes/platform.py`.
- [ ] T025 [US2] Implement `invite_first_admin` sending email invitation via existing notification infrastructure in `formcraft-backend/app/services/platform_service.py`.
- [ ] T026 [US2] Implement `POST /platform/organizations/{org_id}/invite-first-admin` endpoint in `formcraft-backend/app/api/routes/platform.py`.
- [ ] T027 [US2] Add audit logging for org creation, rate-limit warnings, and first-admin invitations.
- [ ] T028 [US2] Create `OrganizationCreateComponent` in `formcraft-frontend/src/app/features/platform/organization-create/` with form validation and async domain uniqueness check.
- [ ] T029 [US2] Implement first-admin invitation prompt on org detail page after creation.

---

## Phase 5: User Story 3 — Organization Detail View

**Goal**: Platform admin can view and edit org details across Profile, Subscription, Users, and Stats tabs.

**Independent Test**: Navigate to `/platform/organizations/:id` → verify all four tabs load correctly.

- [ ] T030 [P] [US3] Write failing backend contract tests for `GET /platform/organizations/{org_id}` and `PATCH /platform/organizations/{org_id}` in `formcraft-backend/tests/integration/test_platform_routes.py`.
- [ ] T031 [P] [US3] Write failing backend unit tests for `get_organization_detail` with computed fields in `formcraft-backend/tests/unit/test_platform_service.py`.
- [ ] T032 [US3] Implement `get_organization_detail` with computed counts (users, templates, submissions) in `formcraft-backend/app/services/platform_service.py`.
- [ ] T033 [US3] Implement `GET /platform/organizations/{org_id}` endpoint in `formcraft-backend/app/api/routes/platform.py`.
- [ ] T034 [US3] Implement `update_organization` with domain uniqueness check in `formcraft-backend/app/services/platform_service.py`.
- [ ] T035 [US3] Implement `PATCH /platform/organizations/{org_id}` endpoint in `formcraft-backend/app/api/routes/platform.py`.
- [ ] T036 [US3] Implement `DELETE /platform/organizations/{org_id}` with submission existence guard in `formcraft-backend/app/api/routes/platform.py`.
- [ ] T037 [US3] Add audit logging for update and delete attempts.
- [ ] T038 [US3] Create `OrganizationDetailComponent` with tab navigation in `formcraft-frontend/src/app/features/platform/organization-detail/`.
- [ ] T039 [P] [US3] Create `ProfileTabComponent` in `formcraft-frontend/src/app/features/platform/organization-detail/tabs/profile-tab/`.
- [ ] T040 [P] [US3] Create `SubscriptionTabComponent` in `formcraft-frontend/src/app/features/platform/organization-detail/tabs/subscription-tab/`.
- [ ] T041 [P] [US3] Create `UsersTabComponent` in `formcraft-frontend/src/app/features/platform/organization-detail/tabs/users-tab/`.
- [ ] T042 [P] [US3] Create `StatsTabComponent` in `formcraft-frontend/src/app/features/platform/organization-detail/tabs/stats-tab/`.

---

## Phase 6: User Story 4 — Platform Dashboard

**Goal**: Platform admin sees platform-wide metrics, charts, and tier-limit alerts on `/platform`.

**Independent Test**: Navigate to `/platform` → verify summary cards, pie chart, line chart, and alerts.

- [ ] T043 [P] [US4] Write failing backend unit tests for `PlatformMetricsService` in `formcraft-backend/tests/unit/test_platform_metrics_service.py`.
- [ ] T044 [P] [US4] Write failing backend contract tests for `GET /platform/metrics` in `formcraft-backend/tests/integration/test_platform_routes.py`.
- [ ] T045 [US4] Implement `PlatformMetricsService` reading from `platform_metrics_mv` and computing submission volume trend in `formcraft-backend/app/services/platform_metrics_service.py`.
- [ ] T046 [US4] Implement `GET /platform/metrics` endpoint in `formcraft-backend/app/api/routes/platform.py`.
- [ ] T047 [US4] Implement `POST /platform/metrics/refresh` manual refresh endpoint.
- [ ] T048 [US4] Create `PlatformDashboardComponent` in `formcraft-frontend/src/app/features/platform/platform-dashboard/` with summary cards, pie chart (org-by-tier), line chart (submission trend), and alerts list.
- [ ] T049 [US4] Integrate Chart.js/ng2-charts for dashboard visualizations.
- [ ] T050 [US4] Add scheduled materialized view refresh (APScheduler or cron) every 5 minutes.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T051 [P] Run full backend test suite: `pytest formcraft-backend/tests/unit/test_platform_service.py formcraft-backend/tests/unit/test_platform_metrics_service.py formcraft-backend/tests/integration/test_platform_routes.py -v`.
- [ ] T052 [P] Run frontend build and lint checks.
- [ ] T053 Verify all platform admin actions are recorded in `audit_logs`.
- [ ] T054 Verify `PlatformAdminGuard` blocks non-platform-admin users from `/platform` routes.
- [ ] T055 Verify context switcher works for dual-role users (platform + org admin).
- [ ] T056 Verify rate limit blocks 11th org creation and logs warning.
- [ ] T057 Verify suspension immediately redirects users to "Organization Suspended" page.
- [ ] T058 Update `AGENTS.md` with F039 technology additions if needed.

---

## Parallel Execution Examples

### Within User Story 1
- T010 (backend contract tests) and T011 (backend unit tests) can run in parallel.
- T019 (frontend list component) can start once T006/T007 are done, parallel with backend T012–T018.

### Within User Story 3
- T030/T031 (backend tests) and T038 (detail shell) can start in parallel.
- T039–T042 (four tab components) can be implemented in parallel once T038 is ready.

### Within User Story 4
- T043/T044 (backend tests) and T048 (frontend dashboard shell) can start in parallel.

---

## Implementation Strategy

**MVP Scope**: User Story 1 (Organization List & Management) alone provides core platform management. Deliver US1 first, then incrementally add US2 (Create), US3 (Detail), and US4 (Dashboard).

**Backend-Frontend Split**: Backend DTOs and service interfaces are established in Phase 2. Frontend can stub against these contracts while backend implementation proceeds in parallel for each user story.

**Testing**: TDD is enforced per the constitution. All test tasks are marked parallel and must be written before their corresponding implementation tasks.

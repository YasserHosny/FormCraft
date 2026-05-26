# Tasks: Granular Template Permissions

**Input**: `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-specs/specs/043-granular-template-permissions/plan.md`

## Phase 1: Setup

- [X] T001 Create normalized F043 migration in `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-backend/migrations/041_granular_template_permissions.sql`
- [X] T002 [P] Create permission Pydantic schemas in `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-backend/app/schemas/template_permissions.py`

## Phase 2: Foundational

- [X] T003 [P] Add service unit tests for deny precedence, imported admin-only fallback, custom role deactivation, and diagnostics in `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-backend/tests/unit/test_template_permission_service.py`
- [X] T004 [P] Add API contract tests for admin policy write and user decision diagnostics in `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-backend/tests/integration/test_template_permissions_route.py`

## Phase 3: User Story 1 - Restrict Template Visibility and Actions (P1)

**Independent Test**: Create scoped grants for a template and verify users outside scope cannot see or act on it from API decisions.

- [X] T005 [US1] Implement deterministic access evaluator in `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-backend/app/services/template_permission_service.py`
- [X] T006 [US1] Implement decision endpoint in `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-backend/app/api/routes/template_permissions.py`
- [X] T007 [US1] Register template permissions router in `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-backend/app/main.py`

## Phase 4: User Story 2 - Define Custom Role Capabilities (P2)

**Independent Test**: Assign an active custom role and confirm deactivation removes its capabilities on the next check.

- [X] T008 [US2] Add custom role capability loading and assignment filtering in `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-backend/app/services/template_permission_service.py`
- [X] T009 [US2] Implement admin policy replacement endpoint in `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-backend/app/api/routes/template_permissions.py`

## Phase 5: User Story 3 - Audit and Troubleshoot Access (P3)

**Independent Test**: Select a user-template pair and confirm diagnostics explain matched grants, restrictions, role sources, scopes, and final decision.

- [X] T010 [US3] Persist access decision records and denied-action audit events in `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-backend/app/services/template_permission_service.py`
- [X] T011 [US3] Implement admin diagnostics endpoint in `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-backend/app/api/routes/template_permissions.py`

## Final Phase: Polish

- [X] T012 Run targeted backend tests from `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-backend`
- [X] T013 Update task checkboxes after implementation in `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-specs/specs/043-granular-template-permissions/tasks.md`

## Dependencies

T001 and T002 can run first. T003 and T004 define expected behavior before T005-T011. T007 depends on T006. T009 depends on T005 and T008. T011 depends on T010.

## Parallel Opportunities

T002, T003, and T004 affect separate files and can be worked in parallel. Route and service edits should stay sequential because both define the shared contract.

## Implementation Strategy

Deliver the backend authorization core first, with API contracts and migration. Future frontend screens can consume the same endpoints without changing F043 semantics.

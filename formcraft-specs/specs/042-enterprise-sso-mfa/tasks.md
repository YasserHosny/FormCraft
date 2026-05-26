# Tasks: Enterprise SSO and MFA

**Input**: Design documents from `/specs/042-enterprise-sso-mfa/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included per Constitution V (Test-First Development).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add dependencies and scaffolding for SSO/MFA features

- [ ] T001 Add Python dependencies (`python-saml`, `authlib`, `pyotp`, `cryptography`) to `formcraft-backend/requirements.txt`
- [ ] T002 Add frontend dependencies (`angularx-qrcode`) to `formcraft-frontend/package.json`
- [ ] T003 [P] Create backend feature module directories: `formcraft-backend/app/services/`, `formcraft-backend/app/api/v1/`, `formcraft-backend/tests/unit/`, `formcraft-backend/tests/integration/`, `formcraft-backend/tests/contract/`
- [ ] T004 [P] Create frontend feature module directories: `formcraft-frontend/src/app/features/sso/`, `formcraft-frontend/src/app/features/mfa/`, `formcraft-frontend/src/app/core/guards/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create Supabase migration for `identity_provider`, `auth_policy`, `identity_mapping`, `mfa_enrollment`, `session_event` tables, enums, indexes, and RLS policies in `formcraft-backend/supabase/migrations/`
- [ ] T006 [P] Implement AES-256-GCM crypto service in `formcraft-backend/app/services/crypto_service.py`
- [ ] T007 [P] Create shared Pydantic schemas for SSO/MFA in `formcraft-backend/app/schemas/identity.py`
- [ ] T008 [P] Create frontend core service stubs in `formcraft-frontend/src/app/core/services/sso.service.ts` and `mfa.service.ts`
- [ ] T009 [P] Create frontend feature modules in `formcraft-frontend/src/app/features/sso/sso.module.ts` and `formcraft-frontend/src/app/features/mfa/mfa.module.ts`
- [ ] T010 Configure backend SSO/MFA settings in `formcraft-backend/app/core/config.py`

**Checkpoint**: Foundation ready — database tables, crypto, and module scaffolding exist

---

## Phase 3: User Story 1 - Configure Enterprise Sign-In (Priority: P1) 🎯 MVP

**Goal**: Org admins can configure SAML/OIDC identity providers and domain-based routing.

**Independent Test**: Configure a test IdP, verify a domain, and authenticate a matching user through the provider.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T011 [P] [US1] Contract test for IdP CRUD endpoints in `formcraft-backend/tests/contract/test_sso_api.py`
- [ ] T012 [P] [US1] Integration test for SAML ACS flow in `formcraft-backend/tests/integration/test_saml_flow.py`
- [ ] T013 [P] [US1] Integration test for OIDC callback flow in `formcraft-backend/tests/integration/test_oidc_flow.py`

### Implementation for User Story 1

- [ ] T014 [P] [US1] Create `IdentityProvider` SQLAlchemy model and Pydantic schemas in `formcraft-backend/app/models/identity.py`
- [ ] T015 [P] [US1] Implement `SsoService` with SAML metadata validation and OIDC discovery in `formcraft-backend/app/services/sso_service.py`
- [ ] T016 [US1] Implement IdP CRUD API in `formcraft-backend/app/api/v1/sso.py`
- [ ] T017 [US1] Implement domain verification and routing logic in `formcraft-backend/app/services/sso_service.py`
- [ ] T018 [P] [US1] Create `IdpConfigComponent` in `formcraft-frontend/src/app/features/sso/components/idp-config/idp-config.component.ts`
- [ ] T019 [P] [US1] Create `DomainVerifyComponent` in `formcraft-frontend/src/app/features/sso/components/domain-verify/domain-verify.component.ts`
- [ ] T020 [US1] Wire SSO routes and lazy-loaded module in `formcraft-frontend/src/app/features/sso/sso-routing.module.ts`

**Checkpoint**: User Story 1 is fully functional and testable independently

---

## Phase 4: User Story 2 - Enforce MFA and Session Policy (Priority: P2)

**Goal**: Admins can require MFA for sensitive roles and enforce session controls.

**Independent Test**: Enable MFA for the admin role, sign in as an admin, and verify enrollment/challenge before accessing protected areas.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T021 [P] [US2] Contract test for MFA enrollment/verify endpoints in `formcraft-backend/tests/contract/test_mfa_api.py`
- [ ] T022 [P] [US2] Unit test for TOTP generation/verification in `formcraft-backend/tests/unit/test_mfa_service.py`
- [ ] T023 [P] [US2] Unit test for session timeout enforcement in `formcraft-backend/tests/unit/test_session_service.py`

### Implementation for User Story 2

- [ ] T024 [P] [US2] Create `MfaEnrollment` and `AuthPolicy` SQLAlchemy models in `formcraft-backend/app/models/identity.py`
- [ ] T025 [P] [US2] Implement `MfaService` with TOTP and SMS/Email OTP in `formcraft-backend/app/services/mfa_service.py`
- [ ] T026 [US2] Implement MFA enrollment/challenge/recovery API in `formcraft-backend/app/api/v1/mfa.py`
- [ ] T027 [US2] Implement `SessionService` with timeout and concurrent limits in `formcraft-backend/app/services/session_service.py`
- [ ] T028 [US2] Implement `AuthPolicy` CRUD API in `formcraft-backend/app/api/v1/auth_policy.py`
- [ ] T029 [P] [US2] Create `EnrollComponent` for MFA enrollment in `formcraft-frontend/src/app/features/mfa/components/enroll/enroll.component.ts`
- [ ] T030 [P] [US2] Create `ChallengeComponent` for MFA challenge in `formcraft-frontend/src/app/features/mfa/components/challenge/challenge.component.ts`
- [ ] T031 [US2] Implement `MfaGuard` in `formcraft-frontend/src/app/core/guards/mfa.guard.ts`

**Checkpoint**: User Stories 1 AND 2 both work independently

---

## Phase 5: User Story 3 - Map Identity Groups to FormCraft Access (Priority: P3)

**Goal**: Admins map corporate identity groups to FormCraft roles, departments, and branches.

**Independent Test**: Sign in a test user with mapped identity groups and confirm their profile receives the expected role and org scope.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T032 [P] [US3] Contract test for identity mapping endpoints in `formcraft-backend/tests/contract/test_mapping_api.py`
- [ ] T033 [P] [US3] Integration test for JIT provisioning in `formcraft-backend/tests/integration/test_jit_provisioning.py`

### Implementation for User Story 3

- [ ] T034 [P] [US3] Create `IdentityMapping` and `SessionEvent` SQLAlchemy models in `formcraft-backend/app/models/identity.py`
- [ ] T035 [US3] Implement JIT provisioning service in `formcraft-backend/app/services/sso_service.py`
- [ ] T036 [US3] Implement identity mapping CRUD API in `formcraft-backend/app/api/v1/sso.py`
- [ ] T037 [US3] Implement audit logging for SSO/MFA/session events in `formcraft-backend/app/services/session_service.py`
- [ ] T038 [P] [US3] Create mapping admin UI component in `formcraft-frontend/src/app/features/sso/components/mapping-config/mapping-config.component.ts`

**Checkpoint**: All user stories are independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T039 [P] Add Arabic/English i18n keys for SSO/MFA UI strings in `formcraft-frontend/src/assets/i18n/ar.json` and `en.json`
- [ ] T040 [P] Run quickstart.md validation scenarios and fix gaps
- [ ] T041 Security review: verify AES-256 key management, secret rotation, and RLS policy correctness
- [ ] T042 [P] Add unit tests for crypto service in `formcraft-backend/tests/unit/test_crypto_service.py`
- [ ] T043 Update `AGENTS.md` with F042 technology stack additions if not already present

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) — Integrates with US1 sign-in flows but is independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) — Integrates with US1 SSO but is independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for IdP CRUD in formcraft-backend/tests/contract/test_sso_api.py"
Task: "Integration test for SAML ACS in formcraft-backend/tests/integration/test_saml_flow.py"
Task: "Integration test for OIDC callback in formcraft-backend/tests/integration/test_oidc_flow.py"

# Launch all models for User Story 1 together:
Task: "Create IdentityProvider model in formcraft-backend/app/models/identity.py"
Task: "Create SsoService in formcraft-backend/app/services/sso_service.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

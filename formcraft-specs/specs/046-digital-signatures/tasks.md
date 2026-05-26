# Tasks: Digital Signatures

**Input**: Design documents from `formcraft-specs/specs/046-digital-signatures/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included per Constitution Test-First Development requirement.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Database migration, base schema, and project structure for F046

- [ ] T001 Create migration `formcraft-backend/migrations/046_digital_signatures.sql` with signature_workflows, signature_requests, signature_recipients, signature_events, signed_evidence_packages tables and RLS policies
- [ ] T002 [P] Create Pydantic schema base `formcraft-backend/app/schemas/digital_signature.py` with workflow, request, recipient, event, and evidence DTOs
- [ ] T003 [P] Add i18n keys to `formcraft-frontend/src/assets/i18n/ar.json` and `en.json` for signature workflows

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core services that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Create `formcraft-backend/app/services/signature_token_service.py` for opaque token generation, hashing, and validation
- [ ] T005 [P] Create `formcraft-backend/app/services/signer_identity_service.py` for internal password re-auth and external email OTP generation/verification
- [ ] T006 [P] Create `formcraft-backend/app/services/signature_evidence_service.py` for evidence package creation, SHA-256 hashing, PDF sealing via WeasyPrint, and integrity verification
- [ ] T007 [P] Create `formcraft-backend/tests/unit/test_signature_token_service.py` with failing tests for token lifecycle
- [ ] T008 [P] Create `formcraft-backend/tests/unit/test_signer_identity_service.py` with failing tests for OTP and password flows
- [ ] T009 [P] Create `formcraft-backend/tests/unit/test_signature_evidence_service.py` with failing tests for hash and sealing
- [ ] T009b [P] Create `formcraft-backend/app/services/signature_guard_service.py` to enforce FR-007: block silent modification of submissions with pending/completed signatures
- [ ] T009c [P] Create `formcraft-backend/tests/unit/test_signature_guard_service.py` with failing tests for modification guards
- [ ] T010 Create `formcraft-frontend/src/app/core/services/digital-signature.service.ts` base service with workflow/list/request API wrappers
- [ ] T011 [P] Create `formcraft-frontend/src/app/features/digital-signatures/digital-signatures.module.ts` and routing module with lazy-loaded routes

**Checkpoint**: Foundation ready - services compile, migration applies, base tests exist and fail

---

## Phase 3: User Story 1 - Request Signatures on a Submission (Priority: P1) 🎯 MVP

**Goal**: Operators can create signature requests for submissions, send invitations to signers, and collect signatures with identity verification. External signers use email OTP; internal signers use password re-auth.

**Independent Test**: Create a workflow, submit a form, create a signature request with one internal and one external signer, send invitations, have both signers complete identity verification and sign, and confirm the submission shows as signed in history.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T012 [P] [US1] Contract test for workflow CRUD endpoints in `formcraft-backend/tests/integration/test_digital_signature_routes.py`
- [ ] T013 [P] [US1] Integration test for request creation and send flow in `formcraft-backend/tests/integration/test_digital_signature_routes.py`
- [ ] T014 [P] [US1] Unit test for `digital_signature_service.py` request orchestration in `formcraft-backend/tests/unit/test_digital_signature_service.py`

### Implementation for User Story 1

- [ ] T015 [P] [US1] Implement `formcraft-backend/app/api/routes/digital_signatures.py` workflow CRUD endpoints (GET/POST/PATCH /workflows)
- [ ] T016 [P] [US1] Implement `formcraft-backend/app/api/routes/digital_signatures.py` request creation and send endpoints (POST /requests, POST /requests/{id}/send)
- [ ] T017 [US1] Implement `formcraft-backend/app/services/digital_signature_service.py` core orchestration for create request, invite signers, process state transitions
- [ ] T018 [P] [US1] Implement public signer endpoints in `formcraft-backend/app/api/routes/digital_signatures.py` (GET /sign/{token}, POST /sign/{token}/otp/send, POST /sign/{token}/otp/verify, POST /sign/{token}/authenticate, POST /sign/{token}/sign, POST /sign/{token}/decline)
- [ ] T019 [P] [US1] Build `formcraft-frontend/src/app/features/digital-signatures/workflow-config/` admin workflow configuration component (enable, signer order, expiration, decline policy)
- [ ] T020 [P] [US1] Build `formcraft-frontend/src/app/features/digital-signatures/request-list/` operator request list component with status and progress
- [ ] T021 [US1] Build `formcraft-frontend/src/app/features/digital-signatures/request-detail/` operator request detail with timeline, resend, cancel actions
- [ ] T022 [P] [US1] Build `formcraft-frontend/src/app/features/digital-signatures/signer-portal/` public signer portal page (view document, OTP verification, sign/decline)
- [ ] T023 [US1] Integrate signature request creation into existing submission flow (operator can initiate signature from submission history or desk)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Manage Multi-Signer Approval (Priority: P2)

**Goal**: Admins configure ordered or parallel multi-signer workflows. Ordered signing unlocks the next signer only after the previous completes. Decline policies stop or continue the workflow.

**Independent Test**: Create a two-signer ordered workflow, submit a form, create a request, confirm the second signer is invited only after the first completes, and verify decline with `stop` policy halts the workflow.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T024 [P] [US2] Unit test for ordered workflow engine in `formcraft-backend/tests/unit/test_digital_signature_service.py`
- [ ] T025 [P] [US2] Integration test for decline policy behavior in `formcraft-backend/tests/integration/test_digital_signature_routes.py`

### Implementation for User Story 2

- [ ] T026 [US2] Extend `formcraft-backend/app/services/digital_signature_service.py` with ordered workflow engine (current_signer_index advancement, next signer invitation gating)
- [ ] T027 [P] [US2] Extend `formcraft-backend/app/services/digital_signature_service.py` with decline policy handlers (stop, continue_next, route_to_admin)
- [ ] T028 [P] [US2] Update `formcraft-frontend/src/app/features/digital-signatures/workflow-config/` to support ordered/parallel toggle and max 10 signer configuration UI
- [ ] T029 [US2] Update `formcraft-frontend/src/app/features/digital-signatures/request-detail/` to show ordered progress bar and locked/unlocked signer states
- [ ] T030 [P] [US2] Add admin notification on decline/route_to_admin events using existing `formcraft-backend/app/services/notification_service.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Verify Signed Evidence (Priority: P3)

**Goal**: Compliance users can view signed evidence packages, verify document integrity by re-computing SHA-256 hashes, and audit the complete signature event timeline.

**Independent Test**: Complete a signed submission, open the evidence viewer, confirm the evidence package shows signer events, timestamps, document hash, and integrity status, and trigger a re-verification that returns valid.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T031 [P] [US3] Unit test for evidence verification in `formcraft-backend/tests/unit/test_signature_evidence_service.py`
- [ ] T032 [P] [US3] Integration test for evidence retrieval and verification endpoints in `formcraft-backend/tests/integration/test_digital_signature_routes.py`

### Implementation for User Story 3

- [ ] T033 [US3] Implement evidence retrieval endpoint (GET /evidence/{request_id}) in `formcraft-backend/app/api/routes/digital_signatures.py`
- [ ] T034 [P] [US3] Implement evidence verification endpoint (POST /evidence/{request_id}/verify) in `formcraft-backend/app/api/routes/digital_signatures.py`
- [ ] T035 [P] [US3] Build `formcraft-frontend/src/app/features/digital-signatures/evidence-viewer/` component showing document hash, signer snapshot, event timeline, and integrity badge
- [ ] T036 [P] [US3] Add evidence reference and signature status to existing submission history and audit log views (minimal integration into existing history/audit components)
- [ ] T036b [P] [US3] Integrate signature events into existing `formcraft-backend/app/services/audit_service.py` so all signature lifecycle events are written to the centralized `audit_logs` table
- [ ] T037 [US3] Extend `formcraft-backend/app/services/signature_evidence_service.py` with duplicate event idempotency guards and out-of-order callback handling
- [ ] T037b [P] Add AES-256 encryption for sensitive JSONB evidence fields at rest using existing `formcraft-backend/app/services/crypto_service.py` or PostgreSQL pgcrypto
- [ ] T037c [P] Add migration update or policy note for 7-year audit retention of `signature_events` and `signed_evidence_packages`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T038 [P] Run backend tests: `cd formcraft-backend && pytest tests/unit/test_digital_signature_service.py tests/unit/test_signer_identity_service.py tests/unit/test_signature_evidence_service.py tests/unit/test_signature_token_service.py tests/integration/test_digital_signature_routes.py`
- [ ] T039 [P] Run ruff on new backend files: `cd formcraft-backend && ruff check app/api/routes/digital_signatures.py app/schemas/digital_signature.py app/services/digital_signature_service.py app/services/signer_identity_service.py app/services/signature_evidence_service.py app/services/signature_token_service.py`
- [ ] T040 [P] Verify Angular build has no F046-specific errors: `cd formcraft-frontend && npm run build`
- [ ] T041 Update `formcraft-specs/specs/046-digital-signatures/quickstart.md` with any validation notes discovered during implementation
- [ ] T042 Final RLS policy review on `formcraft-backend/migrations/046_digital_signatures.sql` to ensure cross-org leakage is impossible
- [ ] T043 Final i18n audit: all new frontend strings have Arabic and English keys in `ar.json` and `en.json`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Extends US1 workflow engine but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Consumes US1/US2 outputs but should be independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models (migration already in Phase 1) before services
- Services before endpoints
- Core backend before frontend
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Backend and frontend tasks within a story can run in parallel after service contracts are stable

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Contract test for workflow CRUD endpoints in tests/integration/test_digital_signature_routes.py"
Task: "Integration test for request creation and send flow in tests/integration/test_digital_signature_routes.py"
Task: "Unit test for digital_signature_service.py request orchestration in tests/unit/test_digital_signature_service.py"

# Launch backend endpoints and frontend components in parallel after services are ready:
Task: "Implement workflow CRUD endpoints in app/api/routes/digital_signatures.py"
Task: "Build admin workflow configuration component"
Task: "Build operator request list component"
Task: "Build public signer portal page"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
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
   - Developer A: User Story 1 (backend + frontend)
   - Developer B: User Story 2 (workflow engine + config UI)
   - Developer C: User Story 3 (evidence service + viewer)
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

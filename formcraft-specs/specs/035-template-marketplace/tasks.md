# Tasks: Template Marketplace

**Input**: Design documents from `formcraft-specs/specs/035-template-marketplace/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/marketplace-api.md, quickstart.md

**Tests**: Required by the FormCraft constitution. Backend contract/integration/unit tests must be written before implementation.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create shared marketplace schema, route registration points, and frontend module shell.

- [X] T001 Create marketplace database migration in `formcraft-backend/migrations/037_template_marketplace.sql`
- [X] T002 [P] Add marketplace backend schema models in `formcraft-backend/app/schemas/marketplace.py`
- [X] T003 [P] Add Angular marketplace shared models in `formcraft-frontend/src/app/shared/models/marketplace.models.ts`
- [X] T004 [P] Add Angular marketplace feature module and routing shell in `formcraft-frontend/src/app/features/marketplace/marketplace.module.ts` and `formcraft-frontend/src/app/features/marketplace/marketplace-routing.module.ts`
- [X] T005 Register `/marketplace` lazy route in `formcraft-frontend/src/app/app-routing.module.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared service boundaries and route wiring required by all stories.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T006 [P] Write unit tests for marketplace service browse/import/purchase/review helpers in `formcraft-backend/tests/unit/test_marketplace_service.py`
- [X] T007 [P] Write API contract/integration tests for marketplace endpoints in `formcraft-backend/tests/integration/test_marketplace_routes.py`
- [X] T008 Implement backend marketplace service skeleton, query helpers, payment adapter, audit helpers, and import dependency analysis in `formcraft-backend/app/services/marketplace_service.py`
- [X] T009 Implement backend marketplace API route skeleton in `formcraft-backend/app/api/routes/marketplace.py`
- [X] T010 Register marketplace routers in `formcraft-backend/app/main.py`
- [X] T011 [P] Implement Angular marketplace API client in `formcraft-frontend/src/app/core/services/marketplace.service.ts`
- [X] T012 [P] Add marketplace i18n keys in `formcraft-frontend/src/assets/i18n/ar.json` and `formcraft-frontend/src/assets/i18n/en.json`

**Checkpoint**: Schema, contracts, services, and routes are ready for story implementation.

---

## Phase 3: User Story 1 - Browse & Import Templates (Priority: P1) MVP

**Goal**: Admins browse/filter active listings, preview a listing, and import it as a new org-local draft with dependency remapping safeguards.

**Independent Test**: Navigate to `/marketplace`, filter by country/category, open detail, import a free listing, and verify a new draft template is created without publisher org identifiers.

### Tests for User Story 1

- [X] T013 [P] [US1] Add route tests for list/detail/import free listing in `formcraft-backend/tests/integration/test_marketplace_routes.py`
- [X] T014 [P] [US1] Add service tests for immutable snapshot cloning and dependency warnings in `formcraft-backend/tests/unit/test_marketplace_service.py`

### Implementation for User Story 1

- [X] T015 [US1] Implement list/detail/free import backend methods in `formcraft-backend/app/services/marketplace_service.py`
- [X] T016 [US1] Implement list/detail/import API endpoints in `formcraft-backend/app/api/routes/marketplace.py`
- [X] T017 [US1] Build marketplace browse component in `formcraft-frontend/src/app/features/marketplace/browse/marketplace-browse.component.ts`
- [X] T018 [US1] Build marketplace browse template/styles in `formcraft-frontend/src/app/features/marketplace/browse/marketplace-browse.component.html` and `formcraft-frontend/src/app/features/marketplace/browse/marketplace-browse.component.scss`
- [X] T019 [US1] Build marketplace detail/import component in `formcraft-frontend/src/app/features/marketplace/detail/marketplace-detail.component.ts`
- [X] T020 [US1] Build marketplace detail template/styles in `formcraft-frontend/src/app/features/marketplace/detail/marketplace-detail.component.html` and `formcraft-frontend/src/app/features/marketplace/detail/marketplace-detail.component.scss`

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Publish to Marketplace (Priority: P2)

**Goal**: Admins publish eligible templates to the marketplace, FormCraft admins moderate listings, and premium purchases record revenue share.

**Independent Test**: Submit a published template as a listing, approve it, purchase a premium listing, and verify transaction split is 70/30.

### Tests for User Story 2

- [X] T021 [P] [US2] Add route tests for publish/moderate/purchase listing in `formcraft-backend/tests/integration/test_marketplace_routes.py`
- [X] T022 [P] [US2] Add service tests for listing eligibility, suspension, and revenue share in `formcraft-backend/tests/unit/test_marketplace_service.py`

### Implementation for User Story 2

- [X] T023 [US2] Implement publish/moderate/purchase/suspension backend methods in `formcraft-backend/app/services/marketplace_service.py`
- [X] T024 [US2] Implement publish/moderate/purchase API endpoints in `formcraft-backend/app/api/routes/marketplace.py`
- [X] T025 [US2] Build marketplace publish component in `formcraft-frontend/src/app/features/marketplace/publish/marketplace-publish.component.ts`
- [X] T026 [US2] Build marketplace publish template/styles in `formcraft-frontend/src/app/features/marketplace/publish/marketplace-publish.component.html` and `formcraft-frontend/src/app/features/marketplace/publish/marketplace-publish.component.scss`

**Checkpoint**: User Stories 1 and 2 work independently.

---

## Phase 5: User Story 3 - Ratings & Reviews (Priority: P3)

**Goal**: Verified importing organizations can submit one review per listing and marketplace browse can sort by ratings/downloads.

**Independent Test**: Import a listing, submit a 4-star review, verify aggregate rating/review count update and browse sorting reflects the new score.

### Tests for User Story 3

- [X] T027 [P] [US3] Add route tests for create/update/list reviews in `formcraft-backend/tests/integration/test_marketplace_routes.py`
- [X] T028 [P] [US3] Add service tests for verified importer enforcement and aggregate recalculation in `formcraft-backend/tests/unit/test_marketplace_service.py`

### Implementation for User Story 3

- [X] T029 [US3] Implement review create/update/list backend methods in `formcraft-backend/app/services/marketplace_service.py`
- [X] T030 [US3] Implement review API endpoints in `formcraft-backend/app/api/routes/marketplace.py`
- [X] T031 [US3] Build marketplace review component in `formcraft-frontend/src/app/features/marketplace/review/marketplace-review.component.ts`
- [X] T032 [US3] Build marketplace review template/styles in `formcraft-frontend/src/app/features/marketplace/review/marketplace-review.component.html` and `formcraft-frontend/src/app/features/marketplace/review/marketplace-review.component.scss`

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation, and quality checks.

- [X] T033 [P] Update quickstart validation notes in `formcraft-specs/specs/035-template-marketplace/quickstart.md`
- [X] T034 Run backend tests for marketplace and fix failures in `formcraft-backend/tests/unit/test_marketplace_service.py` and `formcraft-backend/tests/integration/test_marketplace_routes.py`
- [X] T035 Run frontend build/tests for marketplace and fix failures in `formcraft-frontend/src/app/features/marketplace/`
- [X] T036 Verify all marketplace UI text uses translation keys in `formcraft-frontend/src/assets/i18n/ar.json` and `formcraft-frontend/src/assets/i18n/en.json`
- [X] T037 Mark completed F035 tasks in `formcraft-specs/specs/035-template-marketplace/tasks.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): no dependencies
- Foundational (Phase 2): depends on Setup completion and blocks all user stories
- User Story 1 (P1): depends on Foundational
- User Story 2 (P2): depends on Foundational; can be implemented after or alongside US1 service foundations
- User Story 3 (P3): depends on Foundational and is easiest after US1 import exists
- Polish: depends on selected user stories being complete

### User Story Dependencies

- User Story 1: MVP, no story dependency after foundation
- User Story 2: independent publish/purchase path, shares listing service with US1
- User Story 3: requires imports from US1 to verify reviews

### Parallel Opportunities

- T002, T003, and T004 can run in parallel.
- T006, T007, T011, and T012 can run in parallel after setup.
- Story-specific test tasks marked `[P]` can run before implementation work in the same story.
- Frontend component work can proceed in parallel with backend implementation once contracts are stable.

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete User Story 1 end to end.
3. Validate list/detail/import tests and manual `/marketplace` flow.
4. Continue with publish/purchase, then verified reviews.

### Coordination Note

This branch is scoped to F035 only. Avoid touching F036 specs, batch operation code, or shared files unless directly required by F035 route/module registration.

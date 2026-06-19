# Tasks: PayGateway Billing Integration

**Input**: Design documents from `formcraft-specs/specs/058-paygateway-billing/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are required by the FormCraft constitution and this feature plan. Write tests first and confirm they fail before implementing each story.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently after the shared billing foundation is complete.

## Phase 1: Setup

**Purpose**: Create shared billing files, configuration placeholders, and route/module scaffolding.

- [X] T001 Create billing migration skeleton for prices, purchases, fulfillments, refunds, marketplace splits, indexes, RLS enablement, and grants in `formcraft-backend/migrations/049_paygateway_billing.sql`
- [X] T002 [P] Create Pydantic billing schema placeholders for options, purchase creation, verification, history, webhook, and refund payloads in `formcraft-backend/app/schemas/billing.py`
- [X] T003 [P] Create PayGateway client skeleton with create/status/refund/signature methods in `formcraft-backend/app/services/paygateway_client.py`
- [X] T004 [P] Create billing service skeleton with price lookup, purchase creation, fulfillment, and refund method stubs in `formcraft-backend/app/services/billing_service.py`
- [X] T005 Create FastAPI billing router skeleton for `/api/billing/*`, `/api/billing/paygateway/webhook`, and `/api/platform/billing/*` in `formcraft-backend/app/api/routes/billing.py`
- [X] T006 Register the billing router import and include calls in `formcraft-backend/app/main.py`
- [X] T007 [P] Create Angular billing models for options, purchases, checkout state, verification, and refunds in `formcraft-frontend/src/app/shared/models/billing.models.ts`
- [X] T008 [P] Create Angular billing API service skeleton in `formcraft-frontend/src/app/core/services/billing.service.ts`
- [X] T009 Create Angular billing feature module and routing shell in `formcraft-frontend/src/app/features/billing/billing.module.ts` and `formcraft-frontend/src/app/features/billing/billing-routing.module.ts`
- [X] T010 Register Classic and Spark billing routes in `formcraft-frontend/src/app/app-routing.module.ts` and `formcraft-frontend/src/app/features/ui-redesign/ui-redesign.routes.ts`

---

## Phase 2: Foundational

**Purpose**: Implement shared storage, authorization, provider boundaries, and reusable UI before user stories.

**CRITICAL**: No user story implementation can begin until this phase is complete.

- [X] T011 Add billing enums, tables, constraints, active-price indexes, unique fulfillment/refund guards, audit action seed data, and RLS policies in `formcraft-backend/migrations/049_paygateway_billing.sql`
- [X] T012 Add organization `default_currency`, `purchased_seat_allowance`, and `ocr_scan_credit_balance` columns in `formcraft-backend/migrations/049_paygateway_billing.sql`
- [X] T013 [P] Add PayGateway settings for service URL, service key, webhook signing secret, timeout, and mode in `formcraft-backend/app/core/config.py`
- [X] T014 [P] Implement Pydantic enums and validators for billing purpose, target payloads, status lifecycle, currency, and full-refund requests in `formcraft-backend/app/schemas/billing.py`
- [X] T015 [P] Add backend contract tests for `GET /api/billing/options`, `POST /api/billing/purchases`, `POST /api/billing/purchases/{purchase_id}/verify`, `GET /api/billing/purchases`, `GET /api/billing/purchases/{purchase_id}`, `POST /api/billing/paygateway/webhook`, and `POST /api/platform/billing/purchases/{purchase_id}/refund` schemas in `formcraft-backend/tests/contract/test_billing_api.py`
- [X] T016 [P] Add backend unit tests for PayGateway client success, decline, authentication-required, unavailable, rate-limit, refund, and webhook-signature cases in `formcraft-backend/tests/unit/test_paygateway_client.py`
- [X] T017 [P] Add backend unit tests for price lookup, organization currency selection, target validation, non-admin rejection, cross-org isolation, and price tampering resistance in `formcraft-backend/tests/unit/test_billing_service.py`
- [X] T018 [P] Add backend integration tests for `/api/billing/options`, purchase history, single-purchase access, and cross-organization access in `formcraft-backend/tests/integration/test_billing_routes.py`
- [X] T019 [P] Add backend integration tests for PayGateway webhook/status recovery after browser close across tier, seat, OCR, and marketplace purchases in `formcraft-backend/tests/integration/test_billing_routes.py`
- [X] T020 [P] Implement PayGateway client request signing, timeout handling, provider error mapping, and webhook signature verification in `formcraft-backend/app/services/paygateway_client.py`
- [X] T021 Implement shared billing service helpers for org-admin checks, platform-admin checks, active price lookup, organization currency resolution, target validation, idempotency key generation, and audit writes in `formcraft-backend/app/services/billing_service.py`
- [X] T022 Implement shared route dependencies and error-to-message-key mapping in `formcraft-backend/app/api/routes/billing.py`
- [X] T023 [P] Implement Angular billing service methods for options, create purchase, verify purchase, get/list purchases, webhook return handling, and refund calls in `formcraft-frontend/src/app/core/services/billing.service.ts`
- [X] T024 [P] Create shared checkout dialog component with secure provider-token mount point, no raw card state, 3-D Secure state, errors, and loading states in `formcraft-frontend/src/app/features/billing/checkout-dialog/checkout-dialog.component.ts`, `formcraft-frontend/src/app/features/billing/checkout-dialog/checkout-dialog.component.html`, and `formcraft-frontend/src/app/features/billing/checkout-dialog/checkout-dialog.component.scss`
- [X] T025 [P] Create shared billing page and purchase history shells in `formcraft-frontend/src/app/features/billing/billing-page/billing-page.component.ts`, `formcraft-frontend/src/app/features/billing/billing-page/billing-page.component.html`, `formcraft-frontend/src/app/features/billing/billing-page/billing-page.component.scss`, `formcraft-frontend/src/app/features/billing/purchase-history/purchase-history.component.ts`, `formcraft-frontend/src/app/features/billing/purchase-history/purchase-history.component.html`, and `formcraft-frontend/src/app/features/billing/purchase-history/purchase-history.component.scss`
- [X] T026 Add Arabic and English billing translation keys for shared option labels, checkout statuses, provider errors, access errors, and history states in `formcraft-frontend/src/assets/i18n/ar.json` and `formcraft-frontend/src/assets/i18n/en.json`

**Checkpoint**: Billing foundation ready. User story phases can begin.

---

## Phase 3: User Story 1 - Upgrade the Organization's Subscription Tier (Priority: P1) MVP

**Goal**: Org admins can select a higher tier, pay with card, complete 3-D Secure if required, and see the organization tier updated exactly once after provider verification.

**Independent Test**: In test mode, upgrade an organization from starter to professional with a valid card; verify the tier changes, duplicate verification does not double-apply, decline leaves the tier unchanged, and localized messages appear.

### Tests for User Story 1

- [ ] T027 [P] [US1] Add backend unit tests for tier option filtering, missing-currency price unavailability, zero-amount tier fulfillment, previous tier snapshotting, and duplicate tier fulfillment in `formcraft-backend/tests/unit/test_billing_service.py`
- [ ] T028 [P] [US1] Add backend integration tests for tier checkout creation, 3-D Secure verification, declined card handling, duplicate verification, non-admin purchase rejection, and zero-amount fulfillment in `formcraft-backend/tests/integration/test_billing_routes.py`
- [ ] T029 [P] [US1] Add Angular billing service and checkout component tests for tier option loading, secure token handling, 3-D Secure state, decline message keys, and zero-amount response handling in `formcraft-frontend/src/app/core/services/billing.service.spec.ts` and `formcraft-frontend/src/app/features/billing/checkout-dialog/checkout-dialog.component.spec.ts`
- [ ] T030 [P] [US1] Add Angular billing page tests for Classic/Spark route retention and tier purchase success messaging in `formcraft-frontend/src/app/features/billing/billing-page/billing-page.component.spec.ts`

### Implementation for User Story 1

- [X] T031 [US1] Implement subscription tier option discovery, higher-tier-only filtering, missing-price unavailability, and organization currency pricing in `formcraft-backend/app/services/billing_service.py`
- [X] T032 [US1] Implement tier purchase creation with server-computed amount, zero-amount bypass, PayGateway checkout token creation, and pending purchase persistence in `formcraft-backend/app/services/billing_service.py`
- [X] T033 [US1] Implement idempotent tier fulfillment that verifies provider success, snapshots previous tier, updates `organizations.subscription_tier`, writes `billing_fulfillments`, and writes audit entries in `formcraft-backend/app/services/billing_service.py`
- [X] T034 [US1] Implement billing options, create purchase, verify purchase, get purchase, list purchases, and PayGateway webhook handlers for tier purchases in `formcraft-backend/app/api/routes/billing.py`
- [X] T035 [US1] Add OpenAPI response metadata for tier checkout endpoints in `formcraft-backend/app/api/routes/billing.py`
- [X] T036 [US1] Implement tier plan cards, current tier display, unavailable price state, zero-amount success path, and checkout launch in `formcraft-frontend/src/app/features/billing/billing-page/billing-page.component.ts` and `formcraft-frontend/src/app/features/billing/billing-page/billing-page.component.html`
- [ ] T037 [US1] Implement PayGateway checkout dialog orchestration for client token mounting, payment confirmation, 3-D Secure status, verify call, duplicate-safe completion, and localized errors in `formcraft-frontend/src/app/features/billing/checkout-dialog/checkout-dialog.component.ts` and `formcraft-frontend/src/app/features/billing/checkout-dialog/checkout-dialog.component.html`
- [X] T038 [US1] Implement purchase history rendering for tier purchase status lifecycle in `formcraft-frontend/src/app/features/billing/purchase-history/purchase-history.component.ts` and `formcraft-frontend/src/app/features/billing/purchase-history/purchase-history.component.html`
- [X] T039 [US1] Add billing navigation entry points for Classic shell and Spark shell while preserving route context on theme switch in `formcraft-frontend/src/app/shared/components/app-shell/app-shell.component.ts` and `formcraft-frontend/src/app/features/ui-redesign/shell/toolbar.component.ts`
- [X] T040 [US1] Add Platform Console Subscription tab action that starts the shared tier checkout experience in `formcraft-frontend/src/app/features/platform/organization-detail/tabs/subscription-tab/subscription-tab.component.ts`
- [X] T041 [US1] Add Arabic and English tier checkout, 3-D Secure, decline, confirmation, zero-amount, and unavailable-price translations in `formcraft-frontend/src/assets/i18n/ar.json` and `formcraft-frontend/src/assets/i18n/en.json`

**Checkpoint**: User Story 1 is fully functional and testable as the MVP.

---

## Phase 4: User Story 2 - Buy Additional Operator Seats (Priority: P2)

**Goal**: Org admins can buy extra operator seats, with quantity-based pricing and at-most-once additive allowance fulfillment.

**Independent Test**: Buy 10 seats with a valid test card and verify the effective allowance increases by 10; retry after a failed purchase and confirm seats are added only once for the successful purchase.

### Tests for User Story 2

- [ ] T042 [P] [US2] Add backend unit tests for seat quantity validation, server-side amount computation, zero-amount seat fulfillment, failed retry behavior, and duplicate seat fulfillment in `formcraft-backend/tests/unit/test_billing_service.py`
- [ ] T043 [P] [US2] Add backend integration tests for seat checkout creation, successful verification, declined seat purchase, and purchase history rendering in `formcraft-backend/tests/integration/test_billing_routes.py`
- [ ] T044 [P] [US2] Add Angular tests for seat quantity controls, computed price display, retry after failure, and localized errors in `formcraft-frontend/src/app/features/billing/billing-page/billing-page.component.spec.ts`

### Implementation for User Story 2

- [ ] T045 [US2] Implement seat add-on price lookup, quantity bounds, computed amount, and target validation in `formcraft-backend/app/services/billing_service.py`
- [ ] T046 [US2] Implement idempotent seat fulfillment that increments the organization's purchased seat allowance, writes `billing_fulfillments`, and writes audit entries in `formcraft-backend/app/services/billing_service.py`
- [ ] T047 [US2] Extend billing purchase and verification endpoints for `seats` purpose in `formcraft-backend/app/api/routes/billing.py`
- [ ] T048 [US2] Add seat quantity selector, computed price display, retry action, and success state to the billing page in `formcraft-frontend/src/app/features/billing/billing-page/billing-page.component.ts` and `formcraft-frontend/src/app/features/billing/billing-page/billing-page.component.html`
- [ ] T049 [US2] Add seat purchase history details and allowance delta display in `formcraft-frontend/src/app/features/billing/purchase-history/purchase-history.component.ts` and `formcraft-frontend/src/app/features/billing/purchase-history/purchase-history.component.html`
- [ ] T050 [US2] Add Arabic and English translations for seat quantities, pricing, retry, and allowance confirmation in `formcraft-frontend/src/assets/i18n/ar.json` and `formcraft-frontend/src/assets/i18n/en.json`

**Checkpoint**: User Story 2 is independently functional without requiring OCR, marketplace, or refund work.

---

## Phase 5: User Story 3 - Buy a One-Time OCR Onboarding Batch (Priority: P3)

**Goal**: Org admins can buy a fixed quantity of OCR form-scan credits and see credits applied once after payment success.

**Independent Test**: Buy a 300-form OCR batch with a valid test card and verify the organization receives 300 form-scan job credits with one purchase record.

### Tests for User Story 3

- [ ] T051 [P] [US3] Add backend unit tests for OCR package validation, quantity/price computation, zero-amount OCR fulfillment, and duplicate credit protection in `formcraft-backend/tests/unit/test_billing_service.py`
- [ ] T052 [P] [US3] Add backend integration tests for OCR batch purchase creation, verification, purchase history, and non-admin rejection in `formcraft-backend/tests/integration/test_billing_routes.py`
- [ ] T053 [P] [US3] Add Angular tests for OCR package selection, credit confirmation, and localized unavailable-price handling in `formcraft-frontend/src/app/features/billing/billing-page/billing-page.component.spec.ts`

### Implementation for User Story 3

- [ ] T054 [US3] Implement OCR batch price lookup, package validation, and computed credit quantity in `formcraft-backend/app/services/billing_service.py`
- [ ] T055 [US3] Implement idempotent OCR credit fulfillment that increments organization OCR credits, writes `billing_fulfillments`, and writes audit entries in `formcraft-backend/app/services/billing_service.py`
- [ ] T056 [US3] Extend billing purchase and verification endpoints for `ocr_batch` purpose in `formcraft-backend/app/api/routes/billing.py`
- [ ] T057 [US3] Add OCR package cards, credit quantities, checkout launch, and success state to the billing page in `formcraft-frontend/src/app/features/billing/billing-page/billing-page.component.ts` and `formcraft-frontend/src/app/features/billing/billing-page/billing-page.component.html`
- [ ] T058 [US3] Add Arabic and English translations for OCR packages, scan credits, and confirmation messages in `formcraft-frontend/src/assets/i18n/ar.json` and `formcraft-frontend/src/assets/i18n/en.json`

**Checkpoint**: User Story 3 is independently functional without requiring marketplace or refund work.

---

## Phase 6: User Story 4 - Purchase a Premium Marketplace Template (Priority: P3)

**Goal**: Org admins can pay for a premium marketplace template, receive a draft copy, and record publisher/FormCraft revenue split.

**Independent Test**: With a premium template listing, pay with a test card and verify a draft copy appears in the buyer organization and the split record is created.

### Tests for User Story 4

- [ ] T059 [P] [US4] Add backend unit tests for premium listing target validation, listing price authority, marketplace split calculation, and duplicate template-copy protection in `formcraft-backend/tests/unit/test_billing_service.py`
- [ ] T060 [P] [US4] Add backend integration tests for marketplace purchase creation, verification, draft copy creation, and split record creation in `formcraft-backend/tests/integration/test_billing_routes.py`
- [ ] T061 [P] [US4] Add Angular marketplace detail tests for premium checkout launch, post-payment import navigation, and localized payment failure handling in `formcraft-frontend/src/app/features/marketplace/detail/marketplace-detail.component.spec.ts`

### Implementation for User Story 4

- [ ] T062 [US4] Implement marketplace listing target validation, listing price/currency lookup, and platform/publisher split computation in `formcraft-backend/app/services/billing_service.py`
- [ ] T063 [US4] Implement idempotent marketplace fulfillment that calls existing marketplace template copy logic, writes `billing_marketplace_splits`, writes `billing_fulfillments`, and writes audit entries in `formcraft-backend/app/services/billing_service.py`
- [ ] T064 [US4] Extend billing purchase and verification endpoints for `marketplace_template` purpose in `formcraft-backend/app/api/routes/billing.py`
- [ ] T065 [US4] Replace direct premium marketplace purchase/import flow with shared billing checkout flow in `formcraft-frontend/src/app/features/marketplace/detail/marketplace-detail.component.ts` and `formcraft-frontend/src/app/features/marketplace/detail/marketplace-detail.component.html`
- [ ] T066 [US4] Add marketplace purchase result and split metadata display to purchase history in `formcraft-frontend/src/app/features/billing/purchase-history/purchase-history.component.ts` and `formcraft-frontend/src/app/features/billing/purchase-history/purchase-history.component.html`
- [ ] T067 [US4] Add Arabic and English translations for premium template checkout, paid import success, and split/status messages in `formcraft-frontend/src/assets/i18n/ar.json` and `formcraft-frontend/src/assets/i18n/en.json`

**Checkpoint**: User Story 4 is independently functional when a premium marketplace listing exists.

---

## Phase 7: User Story 5 - Reverse a Purchase via Refund (Priority: P3)

**Goal**: Platform admins can issue a full refund, call PayGateway refund, reverse tier/seat effects exactly once, and record the reversal.

**Independent Test**: Refund a successful tier upgrade and seat purchase; verify the tier reverts, seats are removed, duplicate refund is rejected, and audit records are written.

### Tests for User Story 5

- [ ] T068 [P] [US5] Add backend unit tests for full-only refund validation, already-refunded rejection, platform-admin authorization, provider refund failure, tier reversal over-limit behavior, OCR/template non-destructive reversal, and duplicate reversal protection in `formcraft-backend/tests/unit/test_billing_service.py`
- [ ] T069 [P] [US5] Add backend integration tests for `/api/platform/billing/purchases/{purchase_id}/refund` success, forbidden org-admin access, already-refunded conflict, and purchase history status in `formcraft-backend/tests/integration/test_billing_routes.py`
- [ ] T070 [P] [US5] Add Angular Platform Subscription tab tests for refund action visibility, confirmation, success, already-refunded, and localized provider error states in `formcraft-frontend/src/app/features/platform/organization-detail/tabs/subscription-tab/subscription-tab.component.spec.ts`

### Implementation for User Story 5

- [ ] T071 [US5] Implement full-only refund creation, PayGateway refund call, status transition, provider failure handling, and one-refund-per-purchase guard in `formcraft-backend/app/services/billing_service.py`
- [ ] T072 [US5] Implement tier reversal using `previous_effect_snapshot` without deleting/deactivating users or data in `formcraft-backend/app/services/billing_service.py`
- [ ] T073 [US5] Implement seat reversal that subtracts the purchased seat allowance once and records over-limit state without removing users in `formcraft-backend/app/services/billing_service.py`
- [ ] T074 [US5] Implement OCR/template non-destructive refund reversal that reverses payment/revenue status and audit state without deleting consumed OCR outputs or copied templates in `formcraft-backend/app/services/billing_service.py`
- [ ] T075 [US5] Implement `POST /api/platform/billing/purchases/{purchase_id}/refund` and platform-admin purchase lookup support in `formcraft-backend/app/api/routes/billing.py`
- [ ] T076 [US5] Add refund controls, confirmation dialog, status display, and error handling to Platform Console subscription tab in `formcraft-frontend/src/app/features/platform/organization-detail/tabs/subscription-tab/subscription-tab.component.ts`
- [ ] T077 [US5] Add platform-admin refund API method and types in `formcraft-frontend/src/app/core/services/billing.service.ts` and `formcraft-frontend/src/app/shared/models/billing.models.ts`
- [ ] T078 [US5] Add Arabic and English translations for refund confirmation, full-only warning, over-limit warning, already-refunded, and refund success/failure in `formcraft-frontend/src/assets/i18n/ar.json` and `formcraft-frontend/src/assets/i18n/en.json`

**Checkpoint**: User Story 5 is independently functional for platform-admin operational refunds.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, documentation, verification, and UX checks across all stories.

- [ ] T079 [P] Update `formcraft-specs/specs/058-paygateway-billing/quickstart.md` with any implementation-specific PayGateway test cards, environment variables, and route names
- [ ] T080 [P] Add seed data for EGP/SAR/AED tier, seat, and OCR prices in `formcraft-backend/supabase/seed.sql`
- [ ] T081 [P] Add billing feature notes and operational refund caveats in `docs/payment-gateway-integration.md`
- [ ] T082 Run timed validation for checkout token creation under 2 seconds, tier upgrade under 3 minutes, and platform refund under 3 minutes using `formcraft-specs/specs/058-paygateway-billing/quickstart.md`
- [ ] T083 Run backend focused tests with `cd formcraft-backend && pytest tests/contract/test_billing_api.py tests/unit/test_billing_service.py tests/unit/test_paygateway_client.py tests/integration/test_billing_routes.py`
- [ ] T084 Run backend lint with `cd formcraft-backend && ruff check app/schemas/billing.py app/services/billing_service.py app/services/paygateway_client.py app/api/routes/billing.py tests/contract/test_billing_api.py tests/unit/test_billing_service.py tests/unit/test_paygateway_client.py tests/integration/test_billing_routes.py`
- [ ] T085 Run frontend tests with `cd formcraft-frontend && npm test -- --watch=false`
- [ ] T086 Manually verify Classic/Spark, Arabic/English, RTL/LTR, light/dark, secure-token-only network traffic, and theme-switch route retention using `formcraft-specs/specs/058-paygateway-billing/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational; MVP.
- **User Story 2 (Phase 4)**: Depends on Foundational; can reuse shared checkout from US1 but remains independently testable.
- **User Story 3 (Phase 5)**: Depends on Foundational; can run after or alongside US2.
- **User Story 4 (Phase 6)**: Depends on Foundational and an available premium marketplace listing.
- **User Story 5 (Phase 7)**: Depends on at least one successful purchase from US1 or US2 for end-to-end refund validation.
- **Polish (Phase 8)**: Depends on all desired stories being complete.

### User Story Dependencies

- **US1 (P1)**: Independent MVP after foundation.
- **US2 (P2)**: Independent after foundation; shares purchase/checkout infrastructure.
- **US3 (P3)**: Independent after foundation; shares purchase/checkout infrastructure.
- **US4 (P3)**: Independent after foundation plus marketplace catalog/listing availability.
- **US5 (P3)**: Operationally depends on successful purchases to refund; tier/seat refund validation depends on US1/US2 purchase effects.

### Test Ordering

- Backend unit, integration, and frontend tests in each story must be written and confirmed failing before implementation tasks in that story.
- Shared foundational tests T015-T019 should fail before T020-T022 are completed.
- Run focused story tests at each checkpoint before starting the next priority story.

---

## Parallel Opportunities

- Setup tasks T002, T003, T004, T007, and T008 can run in parallel after T001 starts.
- Foundational tests T015-T019 can run in parallel.
- Frontend foundation tasks T023-T025 can run in parallel with backend provider/service work T020-T022.
- US1 tests T027-T030 can run in parallel before US1 implementation.
- US2 tests T042-T044 can run in parallel before US2 implementation.
- US3 tests T051-T053 can run in parallel before US3 implementation.
- US4 tests T059-T061 can run in parallel before US4 implementation.
- US5 tests T068-T070 can run in parallel before US5 implementation.
- Seed/docs updates T079-T081 can run in parallel during polish.

---

## Parallel Example: User Story 1

```bash
# Launch US1 tests together before implementation:
Task: "T027 [US1] Add backend unit tests for tier option filtering in formcraft-backend/tests/unit/test_billing_service.py"
Task: "T028 [US1] Add backend integration tests for tier checkout in formcraft-backend/tests/integration/test_billing_routes.py"
Task: "T029 [US1] Add Angular checkout tests in formcraft-frontend/src/app/features/billing/checkout-dialog/checkout-dialog.component.spec.ts"
Task: "T030 [US1] Add Angular billing page tests in formcraft-frontend/src/app/features/billing/billing-page/billing-page.component.spec.ts"
```

## Parallel Example: User Story 2

```bash
# Backend and frontend tests can be created in parallel:
Task: "T042 [US2] Add backend unit tests for seat quantity validation in formcraft-backend/tests/unit/test_billing_service.py"
Task: "T043 [US2] Add backend integration tests for seat checkout in formcraft-backend/tests/integration/test_billing_routes.py"
Task: "T044 [US2] Add Angular tests for seat quantity controls in formcraft-frontend/src/app/features/billing/billing-page/billing-page.component.spec.ts"
```

## Parallel Example: User Story 4

```bash
# Marketplace checkout work spans distinct files:
Task: "T059 [US4] Add backend unit tests for marketplace split calculation in formcraft-backend/tests/unit/test_billing_service.py"
Task: "T061 [US4] Add Angular marketplace detail tests in formcraft-frontend/src/app/features/marketplace/detail/marketplace-detail.component.spec.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 foundation.
3. Write and fail US1 tests T027-T030.
4. Implement US1 tasks T031-T041.
5. Validate tier upgrade, declined card, 3-D Secure, zero-amount purchase, duplicate verification, non-admin rejection, and audit record behavior.

### Incremental Delivery

1. Ship US1 to close the core tier-upgrade revenue gap.
2. Add US2 seat add-ons using the same checkout infrastructure.
3. Add US3 OCR credits.
4. Add US4 premium marketplace purchases.
5. Add US5 platform-admin refund/reversal operations.
6. Finish Phase 8 validation and visual/security checks.

### Notes

- Every task uses an exact target file path.
- `[P]` marks tasks that can be done in parallel because they touch different files or are independent test additions.
- User story labels map directly to the five stories in `spec.md`.
- Keep FormCraft as the source of truth for amount, currency, purchase status, fulfillment, and audit records.
- Never expose PayGateway service keys or raw card data to the browser.

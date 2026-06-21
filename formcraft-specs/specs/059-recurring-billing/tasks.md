# Tasks: Recurring Subscription Billing with Proration and Self-Serve Downgrade

**Branch**: `059-recurring-billing`  
**Input**: Design documents from `formcraft-specs/specs/059-recurring-billing/`  
**Prerequisites**: plan.md ✓ spec.md ✓ research.md ✓ data-model.md ✓ contracts/api.md ✓ quickstart.md ✓

**Tests**: Included — TDD is mandatory per FormCraft Constitution §V. Write test files before implementation; ensure they FAIL before writing production code.

**Organization**: Tasks grouped by user story. Each user story (US1–US5) is independently testable and deliverable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no shared dependencies)
- **[Story]**: User story label maps to spec.md user stories

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Migration, shared schemas, PayGateway client extension, and i18n — required by all user stories.

- [ ] T001 Write `formcraft-backend/migrations/051_recurring_billing.sql`: CREATE TABLE `billing_subscriptions` (see data-model.md), ADD COLUMN `billing_prices.provider_price_id`, ADD COLUMN `organizations.stripe_customer_id`, enable RLS, add indexes, seed placeholder `provider_price_id` values
- [ ] T002 Apply migration `051_recurring_billing.sql` to local Supabase dev instance: run `supabase db push` (or `supabase migration up` if using CLI v1) from `formcraft-backend/`; confirm `billing_subscriptions` table, `billing_prices.provider_price_id` column, and `organizations.stripe_customer_id` column all exist via `supabase db diff`
- [ ] T003 [P] Add subscription Pydantic schemas to `formcraft-backend/app/schemas/billing.py`: `SubscriptionStatus` enum, `BillingIntervalEnum`, `SubscriptionResponse`, `CreateSubscriptionRequest`, `CreateSubscriptionResponse`, `UpgradeSubscriptionRequest`, `UpgradeSubscriptionResponse`, `DowngradeScheduleRequest`, `DowngradeScheduleResponse`, `CancelSubscriptionResponse`, `ReactivateSubscriptionResponse`, `SubscriptionWebhookRequest`, `SubscriptionWebhookResponse`, `PortalUrlResponse`
- [ ] T004 [P] Add PayGateway client subscription methods to `formcraft-backend/app/services/paygateway_client.py`: `create_customer(email: str, name: str)`, `create_subscription(customer_id: str, price_id: str, metadata: dict)`, `get_subscription(subscription_id: str)`, `upgrade_subscription(subscription_id: str, new_price_id: str)`, `cancel_subscription(subscription_id: str)`, `reactivate_subscription(subscription_id: str)`, `get_portal_url(customer_id: str, return_url: str)` — each as async methods following the existing `_request()` pattern
- [ ] T005 [P] Add 22 new i18n keys to `formcraft-frontend/src/assets/i18n/en.json` (see contracts/api.md §New i18n Keys)
- [ ] T006 [P] Add 22 corresponding i18n keys (Arabic translations) to `formcraft-frontend/src/assets/i18n/ar.json`
- [ ] T061 [P] Add Zod schemas for subscription API types to `formcraft-frontend/src/app/features/billing/billing.schemas.ts` (create file if it does not exist, following the Zod + Pydantic contract discipline from Constitution §VIII): `SubscriptionResponseSchema`, `CreateSubscriptionRequestSchema`, `UpgradeSubscriptionRequestSchema`, `DowngradeScheduleRequestSchema`, `CancelSubscriptionResponseSchema`, `PortalUrlRequestSchema`, `PortalUrlResponseSchema` — these must match the response shapes in contracts/api.md and are used to validate HTTP responses in `BillingService`

**Checkpoint**: Migration applied, schemas defined, PayGateway methods stubbed, i18n keys in place, Zod schemas defined. No user story can begin before T001–T002 are complete.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core subscription service skeleton and route scaffolding that all user story phases extend.

**⚠️ CRITICAL**: No user story implementation begins until T001–T006 are complete and this phase is scaffolded.

- [ ] T062 Coordinate PayGateway service extension with the PayGateway team: confirm that `POST /api/v1/customers`, `POST /api/v1/subscriptions`, `GET /api/v1/subscriptions/{id}`, `POST /api/v1/subscriptions/{id}/upgrade`, `POST /api/v1/subscriptions/{id}/cancel`, `POST /api/v1/subscriptions/{id}/reactivate`, and `POST /api/v1/customers/{id}/portal` endpoints are implemented and reachable in the dev environment before any task that calls `PayGatewayClient` subscription methods (T015, T025, T040, T041, T051). Document the PayGateway dev base URL and update `.env.local` / `docker-compose.override.yml` accordingly.
- [ ] T007 Create `formcraft-backend/app/services/subscription_service.py` with class `SubscriptionService(supabase_client)`, helper `_get_active_subscription(org_id)`, helper `_get_dunning_threshold(org_id)` (reads from `org_settings` key `billing.dunning_max_failures`, default 3), and `compute_proration_preview(org_id, new_tier)` (pure math, no PayGateway call)
- [ ] T008 Add subscription router to `formcraft-backend/app/api/routes/billing.py`: `subscription_router = APIRouter(prefix="/billing/subscriptions")`, stub all 8 new endpoints returning `HTTP 501`, register `subscription_router` in the app
- [ ] T009 [P] Add `POST /api/billing/paygateway/subscription-webhook` stub route to `formcraft-backend/app/api/routes/billing.py`: verify HMAC signature via `PayGatewayClient().verify_webhook_signature()`, dispatch to `SubscriptionService` based on `event_type`, return `{"received": true}`
- [ ] T010 [P] Add `BillingService` and `SubscriptionService` dependency helper `_subscription_service()` in `formcraft-backend/app/api/routes/billing.py`

**Checkpoint**: All endpoints exist (501 stubs), webhook route verifies signatures. Can now implement user stories without routing conflicts.

---

## Phase 3: User Story 1 — Subscribe to a Paid Tier (Priority: P1) 🎯 MVP

**Goal**: Org admin can create a recurring monthly or annual subscription; billing page shows subscription status, renewal date, and amount.

**Independent Test**: From billing page → select tier + interval → complete card → org tier updated → billing page shows "Active · renews [date] · [amount]".

### Tests for User Story 1 ⚠️ Write first — must FAIL before T015

- [ ] T011 [P] [US1] Write contract test for `GET /api/billing/subscriptions/current` in `formcraft-backend/app/api/tests/test_billing_subscriptions.py`: assert 200 with subscription fields when active sub exists; assert 404 when no subscription; assert 403 when called by a non-admin org member
- [ ] T012 [P] [US1] Write contract test for `POST /api/billing/subscriptions` in `formcraft-backend/app/api/tests/test_billing_subscriptions.py`: assert 201 with subscription_id; assert 409 when active subscription already exists; assert 403 when non-admin calls; assert that any `amount_minor` field included in the request body is silently ignored (server computes all amounts)
- [ ] T013 [P] [US1] Write unit test for `SubscriptionService.compute_proration_preview()` in `formcraft-backend/app/services/tests/test_subscription_service.py`: verify formula output for known inputs; verify zero result when days_remaining=0

### Implementation for User Story 1

- [ ] T014 [US1] Implement `SubscriptionService.get_current_subscription(org_id)` in `formcraft-backend/app/services/subscription_service.py`: query `billing_subscriptions` WHERE `org_id=? AND status IN ('active','past_due')` ORDER BY `created_at DESC` LIMIT 1; return None if not found
- [ ] T015 [US1] Implement `SubscriptionService.create_subscription(org_id, actor_id, tier, billing_interval, return_url)` in `formcraft-backend/app/services/subscription_service.py`: (1) assert no active/past_due subscription; (2) if `organizations.stripe_customer_id` is null, fetch the org admin's email + name from `profiles` table, then call `PayGatewayClient.create_customer(email, name)` and persist the returned `cus_...` ID on the org record; (3) look up `billing_prices.provider_price_id` for tier+interval; (4) call `PayGatewayClient.create_subscription(customer_id, price_id, metadata)`; (5) do NOT insert `billing_subscriptions` row here — the row is created by `handle_invoice_paid()` when the first `invoice.paid` webhook is received; (6) return subscription provider ID + checkout token for 3DS if `requires_action`
- [ ] T016 [US1] Implement `SubscriptionService.handle_invoice_paid(event)` in `formcraft-backend/app/services/subscription_service.py` — initial version: find subscription by `provider_subscription_id`; if `invoice_id == last_invoice_id`, return (idempotent); update `current_period_start/end`, reset `failed_payment_count=0`, set `status='active'`, update `last_invoice_id`; apply any `scheduled_downgrade_tier` (clear after applying); write `billing_fulfillments` row with `source='webhook'`
- [ ] T017 [US1] Wire up `GET /api/billing/subscriptions/current` route in `formcraft-backend/app/api/routes/billing.py`: call `_subscription_service().get_current_subscription(ctx.org_id)`; return 404 if None
- [ ] T018 [US1] Wire up `POST /api/billing/subscriptions` route in `formcraft-backend/app/api/routes/billing.py`: call `_subscription_service().create_subscription(...)` with validated body
- [ ] T019 [US1] Wire up `invoice.paid` case in `POST /api/billing/paygateway/subscription-webhook` handler in `formcraft-backend/app/api/routes/billing.py`
- [ ] T020 [P] [US1] Extend `formcraft-frontend/src/app/features/billing/checkout-dialog/checkout-dialog.component.ts`: add `MatButtonToggleGroup` for interval selection (Monthly / Annual); bind selection to `billingInterval` field; pass interval in the subscription create request (not in amount field)
- [ ] T021 [US1] Extend `formcraft-frontend/src/app/features/billing/billing-page/billing-page.component.ts`: call `BillingService.getCurrentSubscription()` on load; store `currentSubscription$`; derive display values (status label, renewal date, renewal amount)
- [ ] T022 [US1] Extend `formcraft-frontend/src/app/features/billing/billing-page/billing-page.component.html`: add subscription info panel showing status badge (`billing.subscription_status.*`), next renewal date (`billing.subscription_renews_on`), and next renewal amount; panel is hidden when no active subscription

**Checkpoint**: Org admin can subscribe, billing page shows renewal info. Tests pass. This is a shippable MVP.

---

## Phase 4: User Story 2 — Upgrade Mid-Cycle with Proration (Priority: P2)

**Goal**: Org admin on an active subscription can upgrade to a higher tier and is charged only the prorated delta for the remaining days.

**Independent Test**: With active Professional subscription (15 days remaining), call upgrade → Enterprise → verify proration charge matches formula (±1 minor unit); verify tier updated on org.

### Tests for User Story 2 ⚠️ Write first — must FAIL before T026

- [ ] T023 [P] [US2] Write contract test for `POST /api/billing/subscriptions/upgrade` in `formcraft-backend/app/api/tests/test_billing_subscriptions.py`: assert 200 with `proration_amount_minor`; assert 409 when downgrading; assert 409 when interval differs; assert 404 when no active subscription
- [ ] T024 [P] [US2] Write unit test for proration math edge cases in `formcraft-backend/app/services/tests/test_subscription_service.py`: 0 days remaining → 0 proration; same-price tiers → 0 charge; last day of period → 1-day proration

### Implementation for User Story 2

- [ ] T025 [US2] Implement `SubscriptionService.upgrade_subscription(org_id, new_tier)` in `formcraft-backend/app/services/subscription_service.py`: (1) assert active subscription exists; (2) assert new tier is higher-priced than current; (3) assert interval is same (else 409); (4) compute proration preview; (5) call `PayGatewayClient.upgrade_subscription(sub_id, new_price_id)`; (6) update `billing_subscriptions.tier` optimistically (confirmed on `invoice.paid`)
- [ ] T026 [US2] Wire up `POST /api/billing/subscriptions/upgrade` route in `formcraft-backend/app/api/routes/billing.py`
- [ ] T027 [US2] Extend `formcraft-frontend/src/app/features/billing/billing-page/billing-page.component.ts`: when `currentSubscription` exists and org admin clicks a higher tier, call `BillingService.upgradeSubscription()` instead of the F058 one-off purchase flow; show proration amount in a confirmation step before calling upgrade

**Checkpoint**: Upgrading mid-cycle charges correctly. Tests pass.

---

## Phase 5: User Story 3 — Schedule a Downgrade (Priority: P2)

**Goal**: Org admin can schedule a downgrade to a lower tier, effective at the next renewal. The current tier is retained until then. The schedule can be cancelled.

**Independent Test**: With active Enterprise subscription → schedule downgrade to Professional → billing page shows "Downgrade to Professional scheduled for [date]" → on next renewal (simulated via webhook replay) → tier becomes Professional.

### Tests for User Story 3 ⚠️ Write first — must FAIL before T031

- [ ] T028 [P] [US3] Write contract test for `POST /api/billing/subscriptions/downgrade-schedule` in `formcraft-backend/app/api/tests/test_billing_subscriptions.py`: assert 200 with `scheduled_downgrade_tier`; assert 409 when new tier is higher; assert 409 when scheduling downgrade to Starter (must cancel instead)
- [ ] T029 [P] [US3] Write contract test for `DELETE /api/billing/subscriptions/downgrade-schedule` in `formcraft-backend/app/api/tests/test_billing_subscriptions.py`: assert 200 with `scheduled_downgrade_tier: null`; assert 409 when no schedule exists
- [ ] T030 [P] [US3] Write webhook replay test for scheduled downgrade in `formcraft-backend/app/api/tests/test_subscription_webhook.py`: simulate `invoice.paid` when `scheduled_downgrade_tier` is set → assert org tier downgraded and schedule cleared

### Implementation for User Story 3

- [ ] T031 [US3] Implement `SubscriptionService.schedule_downgrade(org_id, new_tier)` in `formcraft-backend/app/services/subscription_service.py`: assert new tier is lower; set `billing_subscriptions.scheduled_downgrade_tier = new_tier`
- [ ] T032 [US3] Implement `SubscriptionService.cancel_downgrade_schedule(org_id)` in `formcraft-backend/app/services/subscription_service.py`: assert `scheduled_downgrade_tier IS NOT NULL`; set to NULL
- [ ] T033 [US3] Wire up `POST /api/billing/subscriptions/downgrade-schedule` route in `formcraft-backend/app/api/routes/billing.py`
- [ ] T034 [US3] Wire up `DELETE /api/billing/subscriptions/downgrade-schedule` route in `formcraft-backend/app/api/routes/billing.py`
- [ ] T035 [US3] Extend `formcraft-frontend/src/app/features/billing/billing-page/billing-page.component.ts`: add `scheduleDowngrade()` and `cancelDowngradeSchedule()` methods; bind to `BillingService.scheduleDowngrade()` / `cancelDowngradeSchedule()`
- [ ] T036 [US3] Extend `formcraft-frontend/src/app/features/billing/billing-page/billing-page.component.html`: add "Downgrade scheduled for [date]" chip using `billing.subscription_downgrade_scheduled`; add "Cancel scheduled downgrade" link; add downgrade action buttons on lower-tier cards when subscription is active

**Checkpoint**: Downgrade scheduling and cancellation work. Webhook replay confirms tier change at renewal. Tests pass.

---

## Phase 6: User Story 4 — Cancel a Subscription (Priority: P3)

**Goal**: Org admin can cancel so the subscription does not renew. Org retains current tier until period end. Org admin can reactivate before period end.

**Independent Test**: Cancel active subscription → billing page shows "Subscription ending on [date]" → simulate `customer.subscription.deleted` webhook → org reverts to Starter; separately test reactivate before period end.

### Tests for User Story 4 ⚠️ Write first — must FAIL before T040

- [ ] T037 [P] [US4] Write contract test for `POST /api/billing/subscriptions/cancel` in `formcraft-backend/app/api/tests/test_billing_subscriptions.py`: assert 200 with `cancel_at_period_end: true`; assert 409 when already cancelled; assert 404 when no subscription
- [ ] T038 [P] [US4] Write contract test for `POST /api/billing/subscriptions/reactivate` in `formcraft-backend/app/api/tests/test_billing_subscriptions.py`: assert 200 with `cancel_at_period_end: false`; assert 409 when not cancelling; assert 409 when period already ended
- [ ] T039 [P] [US4] Write webhook replay test for `customer.subscription.deleted` in `formcraft-backend/app/api/tests/test_subscription_webhook.py`: simulate event → assert org tier set to Starter and subscription `status='cancelled'`

### Implementation for User Story 4

- [ ] T040 [US4] Implement `SubscriptionService.cancel_subscription(org_id)` in `formcraft-backend/app/services/subscription_service.py`: call `PayGatewayClient.cancel_subscription(sub_id)`; set `billing_subscriptions.cancel_at_period_end=TRUE`
- [ ] T041 [US4] Implement `SubscriptionService.reactivate_subscription(org_id)` in `formcraft-backend/app/services/subscription_service.py`: assert `cancel_at_period_end=TRUE` and `current_period_end > now()`; call `PayGatewayClient.reactivate_subscription(sub_id)`; set `cancel_at_period_end=FALSE`
- [ ] T042 [US4] Implement `SubscriptionService.handle_subscription_deleted(event)` in `formcraft-backend/app/services/subscription_service.py`: find subscription; set `status='cancelled'`; if org still on elevated tier, revert to Starter; write `billing_fulfillments` row with `source='webhook'`
- [ ] T043 [US4] Wire up `POST /api/billing/subscriptions/cancel` and `POST /api/billing/subscriptions/reactivate` routes in `formcraft-backend/app/api/routes/billing.py`
- [ ] T044 [US4] Wire up `customer.subscription.deleted` case in subscription webhook handler in `formcraft-backend/app/api/routes/billing.py`
- [ ] T045 [US4] Extend `formcraft-frontend/src/app/features/billing/billing-page/billing-page.component.ts`: add `cancelSubscription()` (opens MatDialog confirmation); add `reactivateSubscription()`; bind to service calls
- [ ] T046 [US4] Extend `formcraft-frontend/src/app/features/billing/billing-page/billing-page.component.html`: add "Cancel subscription" button (visible when `cancel_at_period_end=false`); add "Subscription ending on [date]" notice and "Reactivate" button (visible when `cancel_at_period_end=true`)

**Checkpoint**: Cancellation and reactivation work end-to-end. Tests pass.

---

## Phase 7: User Story 5 — Handle Failed Renewal Payment / Dunning (Priority: P3)

**Goal**: Failed renewal triggers email notification and "past due" status. After N consecutive failures the org auto-downgrades to Starter. Past-due org admin can access payment method update via hosted Customer Portal link.

**Independent Test**: Simulate `invoice.payment_failed` (3×) → org on Starter, audit log entry. Simulate `GET /portal-url` when past_due → returns valid URL string. Replay same invoice_id → no double-processing.

### Tests for User Story 5 ⚠️ Write first — must FAIL before T050

- [ ] T047 [P] [US5] Write webhook replay test for `invoice.payment_failed` idempotency in `formcraft-backend/app/api/tests/test_subscription_webhook.py`: send same `invoice_id` twice → assert `failed_payment_count` incremented only once
- [ ] T048 [P] [US5] Write webhook replay test for dunning exhaustion in `formcraft-backend/app/api/tests/test_subscription_webhook.py`: send N `invoice.payment_failed` events → assert org tier reverted to Starter and `billing_fulfillments` row written with `source='webhook'`
- [ ] T049 [P] [US5] Write contract test for `POST /api/billing/subscriptions/portal-url` in `formcraft-backend/app/api/tests/test_billing_subscriptions.py`: assert 200 with `portal_url` string when past_due (with `return_url` in request body); assert 409 when status is active (not past_due)

### Implementation for User Story 5

- [ ] T050 [US5] Implement `SubscriptionService.handle_payment_failed(event)` in `formcraft-backend/app/services/subscription_service.py`: (1) look up subscription by `provider_subscription_id`; (2) if `event.invoice_id == last_invoice_id` return (idempotent); (3) increment `failed_payment_count`, set `status='past_due'`, update `last_invoice_id`; (4) dispatch email via `NotificationService` using event key `billing.subscription_payment_failed` (must be registered in `notification_service.py`'s event registry before this task runs); (5) if `failed_payment_count >= threshold` → revert org to Starter, set `status='cancelled'`, write `billing_fulfillments` with `source='webhook'`, write audit log entry attributed to platform-initiated action
- [ ] T051 [US5] Implement `SubscriptionService.get_portal_url(org_id, return_url)` in `formcraft-backend/app/services/subscription_service.py`: assert subscription exists and `status='past_due'`; call `PayGatewayClient.get_portal_url(stripe_customer_id, return_url)`; return `{ portal_url, expires_at }`
- [ ] T052 [US5] Wire up `invoice.payment_failed` case in subscription webhook handler in `formcraft-backend/app/api/routes/billing.py`
- [ ] T063 [US5] Implement `SubscriptionService.handle_subscription_updated(event)` in `formcraft-backend/app/services/subscription_service.py`: sync `current_period_start`, `current_period_end`, `status`, and `next_renewal_amount_minor` from the incoming `customer.subscription.updated` event payload; use `last_invoice_id` pattern to remain idempotent; wire up `customer.subscription.updated` case in subscription webhook handler
- [ ] T053 [US5] Wire up `POST /api/billing/subscriptions/portal-url` route in `formcraft-backend/app/api/routes/billing.py`: accept `{ return_url: str }` body; call `_subscription_service().get_portal_url(ctx.org_id, return_url)`
- [ ] T054 [US5] Extend `formcraft-frontend/src/app/features/billing/billing-page/billing-page.component.ts`: add `openPaymentPortal()` method that calls `BillingService.getPortalUrl()` and opens the returned URL in a new tab
- [ ] T055 [US5] Extend `formcraft-frontend/src/app/features/billing/billing-page/billing-page.component.html`: add "Update payment method" button (visible only when `status='past_due'`); bind to `openPaymentPortal()`; add failed payment notice banner using `billing.subscription_status.past_due`

**Checkpoint**: Dunning flow works end-to-end. Idempotency verified by replay tests. Customer Portal link appears only when past_due. Tests pass.

---

## Phase 8: Polish & Cross-Cutting Concerns

- [ ] T056 [P] Run full backend test suite: `cd formcraft-backend && pytest -k "billing or subscription" -v` and fix any failures
- [ ] T057 [P] Run frontend tests: `cd formcraft-frontend && ng test --include="**/billing/**"` and fix any failures
- [ ] T058 Update `docs/058-billing-gap-analysis.md`: mark G-4 (recurring billing), G-9 (proration), G-10 (self-serve downgrade) as ✅ CLOSED with reference to F059
- [ ] T059 Verify RLS policies on `billing_subscriptions`: confirm org admin can SELECT/UPDATE their own org's row; confirm other orgs cannot; confirm platform admin can read all
- [ ] T060 [P] Verify all 22 i18n keys render correctly in RTL layout (Arabic) on the billing page — check status badge, renewal date, downgrade chip, cancel notice, past_due banner

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Start immediately — no prerequisites
- **Phase 2 (Foundational)**: Requires T001 (migration applied) and T003–T004 (schemas + client)
- **Phase 3 (US1)**: Requires Phase 1 + 2 complete — BLOCKS Phases 4–7 (subscription must exist before upgrade/downgrade/cancel/dunning)
- **Phase 4 (US2) + Phase 5 (US3)**: Both require Phase 3; can run in parallel with each other
- **Phase 6 (US4) + Phase 7 (US5)**: Both require Phase 3; can run in parallel with each other and with Phases 4–5
- **Phase 8 (Polish)**: Requires all desired user story phases complete

### User Story Dependencies

- **US1 (P1)**: Depends only on Phases 1–2. Core MVP.
- **US2 (P2)**: Depends on US1 (subscription must exist to upgrade). Shares `handle_invoice_paid`.
- **US3 (P2)**: Depends on US1 (subscription must exist to schedule downgrade). Extends `handle_invoice_paid`.
- **US4 (P3)**: Depends on US1 (subscription must exist to cancel). Independent of US2/US3.
- **US5 (P3)**: Depends on US1 (subscription must exist for dunning). Independent of US2/US3/US4.

### Within Each User Story

1. Tests written → verified failing
2. Service methods implemented
3. Routes wired up
4. Frontend extended
5. End-to-end verification

---

## Parallel Opportunities

```bash
# Phase 1 — all can run in parallel after T001+T002:
T003  # Pydantic schemas
T004  # PayGateway client methods
T005  # en.json i18n keys
T006  # ar.json i18n keys

# Phase 3 — tests can run in parallel (T011, T012, T013)

# Phases 4 + 5 in parallel (if two developers available):
Developer A: T023–T027 (US2 upgrade + proration)
Developer B: T028–T036 (US3 downgrade scheduling)

# Phases 6 + 7 in parallel:
Developer A: T037–T046 (US4 cancellation)
Developer B: T047–T055 (US5 dunning + portal)

# Phase 8 — T056 and T057 can run in parallel
```

---

## Implementation Strategy

### MVP First (US1 Only — Phases 1–3)

1. Phase 1: Migration + schemas + PayGateway methods + i18n
2. Phase 2: Service skeleton + route stubs
3. Phase 3: Full US1 (create subscription, webhook, billing page)
4. **STOP and VALIDATE**: Org can subscribe; billing page shows renewal date and amount
5. Ship MVP

### Incremental Delivery

- Phases 1–3 → MVP: recurring subscriptions working
- + Phase 4 → Prorated upgrades working
- + Phase 5 → Downgrade scheduling working
- + Phase 6 → Self-serve cancellation working
- + Phase 7 → Dunning + Customer Portal working
- + Phase 8 → Fully polished and verified

### Task Count Summary

| Phase | Tasks | User Story |
|-------|-------|------------|
| Phase 1: Setup | T001–T006, T061 | — |
| Phase 2: Foundational | T062, T007–T010 | — |
| Phase 3: Subscribe | T011–T022 | US1 (P1) |
| Phase 4: Upgrade | T023–T027 | US2 (P2) |
| Phase 5: Downgrade | T028–T036 | US3 (P2) |
| Phase 6: Cancel | T037–T046 | US4 (P3) |
| Phase 7: Dunning | T047–T055, T063 | US5 (P3) |
| Phase 8: Polish | T056–T060 | — |
| **Total** | **63 tasks** | |

---

## Notes

- `[P]` tasks operate on different files and have no shared incomplete dependencies — safe to parallelise
- Each user story's test tasks MUST be written and confirmed failing before implementation tasks in the same story begin (Constitution §V)
- Commit after each phase checkpoint at minimum
- The `last_invoice_id` idempotency pattern (T050) is critical — do not skip it
- `billing_subscriptions` RLS must be verified (T059) before shipping US5 (dunning auto-downgrade touches org data)
- Run `ruff check .` on backend files before each commit

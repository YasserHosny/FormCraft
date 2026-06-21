# Research: 059 Recurring Subscription Billing

**Branch**: `059-recurring-billing` | **Date**: 2026-06-20

---

## Decision 1: Webhook Verification for Subscription Events

**Decision**: Reuse the existing HMAC-SHA256 signature verification already in `PayGatewayClient.verify_webhook_signature()`. Subscription webhook events from PayGateway will be signed with the same `PAYGATEWAY_WEBHOOK_SECRET`. A new endpoint `POST /api/billing/paygateway/subscription-webhook` will verify using the same mechanism before processing.

**Rationale**: F058 already implements and tests this mechanism. Reusing it avoids duplicate secret management and keeps the security contract consistent.

**Alternatives considered**: Separate per-event-type secrets — rejected (operational overhead, no added security when both endpoints are in the same service).

---

## Decision 2: Proration Computation Strategy

**Decision**: Use Stripe's `proration_behavior=create_prorations` when calling the PayGateway upgrade endpoint. FormCraft backend computes the expected proration amount server-side for display/preview (using FR-006 formula). The actual charge amount for the prorated invoice comes from Stripe and is confirmed via the `invoice.paid` webhook — FormCraft does NOT charge a separate payment intent for the proration delta.

**Rationale**: Stripe's proration invoice is the authoritative source for the actual charge; computing it independently risks rounding divergence. FormCraft's formula is used only for UI preview (showing the user what they'll pay before confirming). This matches the security constraint: client never supplies an amount.

**Alternatives considered**: FormCraft creates a separate one-off payment intent for the proration amount and upgrades the subscription at zero additional charge — rejected (two charges per upgrade, complex reconciliation, harder audit trail).

---

## Decision 3: Subscription Webhook Endpoint Architecture

**Decision**: Add a separate endpoint `POST /api/billing/paygateway/subscription-webhook` for subscription lifecycle events (`invoice.paid`, `invoice.payment_failed`, `customer.subscription.updated`, `customer.subscription.deleted`). This endpoint is distinct from the existing `POST /api/billing/paygateway/webhook` which handles payment intent events.

**Rationale**: The existing payment webhook schema (`PayGatewayWebhookRequest`) requires `purchase_reference: UUID` — this field doesn't exist for subscription events. Separating concerns avoids a brittle schema union and allows each webhook to evolve independently.

**Alternatives considered**: Unified webhook with discriminated union — rejected (makes `purchase_reference` optional, complicating existing payment handler logic and test assertions).

---

## Decision 4: Customer Portal URL Generation

**Decision**: Add `POST /api/billing/subscriptions/portal-url` endpoint in FormCraft that calls a new PayGateway endpoint `POST /api/v1/customers/{id}/portal` (which calls `stripe.billing_portal.Session.create()`). The response contains a short-lived URL (Stripe default: 5-minute TTL) returned to the Angular client. The client opens it in a new browser tab.

**Rationale**: Card details must never pass through FormCraft — the hosted Customer Portal satisfies FR-015a without building a card form. The URL is generated server-side (org admin's Stripe customer ID never exposed to client).

**Alternatives considered**: Redirect the current tab to Stripe's portal — rejected (breaks SPA navigation state; new tab is better UX).

---

## Decision 5: Billing Interval Validation on Upgrade

**Decision**: Interval switching (monthly ↔ annual) on an existing active subscription is rejected with `HTTP 409 billing.interval_change_not_supported`. The client should use the cancel + resubscribe flow. This is enforced in `SubscriptionService.upgrade()`.

**Rationale**: Per clarification Q3: out of scope for 059. Explicit rejection with a clear error code is better than silent failure.

---

## Decision 6: `billing_subscriptions` Uniqueness Rule

**Decision**: A partial unique index `ON billing_subscriptions (org_id) WHERE status IN ('active', 'past_due')` enforces one active/past_due subscription per org. Cancelled subscriptions are allowed to linger as historical records.

**Rationale**: Allows historical record-keeping without blocking future subscriptions after cancellation. Matches the assumption in spec that "each org has at most one active subscription at a time."

---

## Decision 7: Dunning Threshold Configuration

**Decision**: The dunning threshold (default: 3) is read from `org_settings` table key `billing.dunning_max_failures`. If not set for an org, the platform-level default of 3 is used. This uses the existing `org_settings` key-value infrastructure already in production.

**Rationale**: Avoids adding a new column to `organizations` just for this value; the existing `org_settings` table is designed exactly for this purpose.

---

## Decision 8: Subscription Event Idempotency

**Decision**: Each subscription webhook handler checks if the event was already processed by looking up `billing_subscriptions.provider_subscription_id` + expected state. For `invoice.paid`, the idempotency check verifies that `failed_payment_count` is already 0 before resetting (no-op on re-delivery). For `invoice.payment_failed`, the check verifies the event's `invoice_id` was not already processed (store last-processed invoice ID on the subscription row as `last_invoice_id TEXT`).

**Rationale**: FR-019 requires idempotent handlers. Storing `last_invoice_id` is the minimal change to guarantee idempotency for the payment failure flow without a separate event log table.

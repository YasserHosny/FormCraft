# Feature Specification: Recurring Subscription Billing with Proration and Self-Serve Downgrade

**Feature Branch**: `059-recurring-billing`  
**Created**: 2026-06-20  
**Status**: Draft  
**Source**: `docs/058-billing-gap-analysis.md` — Gaps G-4, G-9, G-10  
**Depends on**: F058 (PayGateway Billing — `billing_purchases`, `billing_prices`, `billing_fulfillments`, PayGateway service)

---

## Overview

FormCraft's billing system (F058) allows organisations to purchase tier upgrades as one-off payments. This feature replaces one-off tier charges with recurring monthly or annual subscriptions that auto-renew, supports mid-cycle prorated upgrades, lets org admins schedule downgrades at the next renewal, and handles failed-payment dunning automatically. Add-on purchases (seats, OCR batch) remain one-off; only tier subscriptions are recurring.

---

## Clarifications

### Session 2026-06-20

- Q: Who controls the dunning retry schedule — FormCraft or the payment provider? → A: The payment provider (Stripe) retries automatically on its own schedule. FormCraft only counts received `invoice.payment_failed` events and downgrades when the count reaches the configured threshold.
- Q: How does a past-due org admin update their payment method to allow recovery? → A: The billing page shows an "Update payment method" link when subscription status is past_due. This link opens the payment provider's hosted Customer Portal. Building a card-entry form inside FormCraft is out of scope.
- Q: Is switching billing interval (monthly ↔ annual) on an existing subscription in scope? → A: Out of scope for 059. Interval is selected only when creating a new subscription. Changing interval requires cancelling the current subscription and subscribing again.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Subscribe to a Paid Tier (Priority: P1)

An org admin on the Starter tier wants to move to Professional and have it auto-renew each month instead of having to re-purchase manually.

**Why this priority**: This is the primary revenue flow. Without it, every subscription is a one-off payment and churns silently at the end of a billing period.

**Independent Test**: Navigate to Billing page as org admin → choose Professional → complete card entry → verify org is on Professional tier, billing page shows next renewal date and amount.

**Acceptance Scenarios**:

1. **Given** an org is on the Starter tier with no active subscription, **When** the org admin selects a paid tier and completes payment, **Then** a recurring subscription is created, the org's tier is updated immediately, and the billing page shows the next renewal date and renewal amount.
2. **Given** an org has an active subscription, **When** the billing page loads, **Then** the subscription status, current tier, next renewal date, and next renewal amount are displayed.
3. **Given** a subscription is active, **When** the renewal date arrives and payment succeeds, **Then** the org's tier remains unchanged and the billing page reflects the new period start/end dates.

---

### User Story 2 — Upgrade Mid-Cycle with Proration (Priority: P2)

An org admin on Professional (monthly) wants to upgrade to Enterprise on day 15 of a 30-day cycle and only pay for the remaining days of the new tier minus a credit for unused days of the old tier.

**Why this priority**: Without proration, customers are discouraged from upgrading mid-cycle because they feel they are paying double. Proration is a standard SaaS expectation.

**Independent Test**: With an active Professional subscription (simulate 15 days remaining), upgrade to Enterprise → verify the charge equals (Enterprise_price × 15/30) − (Professional_price × 15/30).

**Acceptance Scenarios**:

1. **Given** an org has an active paid subscription with days remaining in the current period, **When** the org admin upgrades to a higher tier, **Then** the charge is computed as `(new_tier_amount × days_remaining/period_days) − (old_tier_amount × days_remaining/period_days)`, rounded to the nearest currency minor unit.
2. **Given** an upgrade is in progress, **When** the system computes the proration amount, **Then** the computation uses the server-recorded period end date — the client never supplies or influences the amount.
3. **Given** a prorated upgrade succeeds, **When** the next renewal date arrives, **Then** the org is charged the full new-tier amount with no proration applied.

---

### User Story 3 — Schedule a Downgrade (Priority: P2)

An org admin on Enterprise wants to move back to Professional but keep the Enterprise tier until the current billing period ends.

**Why this priority**: Without a downgrade path, org admins must contact support or wait for a platform-admin refund, creating friction and support load.

**Independent Test**: With an active Enterprise subscription, schedule downgrade to Professional → verify org stays on Enterprise until period end → verify org moves to Professional on the next renewal.

**Acceptance Scenarios**:

1. **Given** an org has an active subscription, **When** the org admin schedules a downgrade to a lower tier, **Then** no immediate charge or tier change occurs, and the billing page shows "Downgrade to [tier] scheduled for [date]".
2. **Given** a downgrade is scheduled, **When** the renewal date arrives and payment succeeds, **Then** the org's tier is updated to the scheduled lower tier and the downgrade schedule is cleared.
3. **Given** a downgrade is scheduled, **When** the org admin cancels the scheduled downgrade before the renewal date, **Then** the subscription renews at the current tier as normal.
4. **Given** a downgrade is scheduled, **When** the org admin schedules another downgrade while one is already pending, **Then** the new scheduled downgrade replaces the previous one.

---

### User Story 4 — Cancel a Subscription (Priority: P3)

An org admin wants to cancel the subscription so the org will not be charged next cycle, while still retaining the current tier until the period ends.

**Why this priority**: Self-serve cancellation prevents chargebacks and negative reviews from unexpected renewal charges.

**Independent Test**: Cancel an active subscription → verify billing page shows "Subscription ends on [date]" → verify org is downgraded to Starter on the renewal date with no charge.

**Acceptance Scenarios**:

1. **Given** an active subscription, **When** the org admin cancels it via a confirmation dialog, **Then** the org retains the current tier until the period end date, and the billing page shows "Subscription ending on [date]".
2. **Given** a cancellation is scheduled, **When** the period end date arrives, **Then** the org's tier is set to Starter at no charge.
3. **Given** a cancellation is scheduled, **When** the org admin reactivates the subscription before the period end, **Then** the cancellation is reversed and the subscription renews normally at the next cycle.

---

### User Story 5 — Handle Failed Renewal Payment (Dunning) (Priority: P3)

A renewal payment fails because the card on file was declined. The org admin should be notified and given a chance to update their payment method before the tier is revoked.

**Why this priority**: Silent tier revocation on first failure is a poor experience. Dunning with a grace period recovers revenue and reduces churn.

**Independent Test**: Simulate a failed renewal webhook → verify org admin receives email → verify org status shows "past due" → simulate N consecutive failures (N = configured threshold) → verify org is downgraded to Starter.

**Acceptance Scenarios**:

1. **Given** a renewal payment fails, **When** the failure event is received, **Then** the subscription status is set to "past due", the org retains its current tier, and an email notification is sent to the org admin.
2. **Given** a subscription is past due, **When** the org admin clicks the "Update payment method" link on the billing page and updates their card via the payment provider's hosted portal, and the payment provider's next automatic retry succeeds, **Then** the subscription returns to active status and the failed payment count resets.
3. **Given** a subscription has failed payment N consecutive times where N equals the configured threshold (default: 3), **When** the Nth failure is received, **Then** the org is automatically downgraded to the Starter tier and the event is written to the audit log.
4. **Given** an org was downgraded due to dunning exhaustion, **When** the org admin later subscribes to a new paid tier, **Then** the failed payment count resets and the new subscription starts cleanly.

---

### Edge Cases

- What happens when a subscription lapses and the org admin tries to upgrade again? → Falls back to the F058 new-subscription flow as if no prior subscription existed.
- What if a proration calculation results in a zero or negative charge (e.g., equal-priced tiers)? → The fulfillment still completes; a zero-amount event is recorded and no card interaction occurs.
- What if a webhook event is delivered out of order or duplicated? → All webhook handlers must be idempotent; reprocessing an already-processed event must produce no additional state changes.
- What if an org has a scheduled downgrade but then upgrades to an even higher tier mid-cycle? → The scheduled downgrade is cleared; the upgrade takes effect immediately with proration.
- What if the payment infrastructure service is temporarily unavailable when a webhook arrives? → The webhook endpoint returns a retriable error; the payment provider retries automatically per its retry policy.
- What if an org is on an annual subscription and the first renewal fails? → The same dunning flow applies; the retry count and grace period follow the same configurable threshold.
- What if an org wants to switch from monthly to annual billing (or vice versa) mid-subscription? → Not supported in 059. The org must cancel the current subscription, wait for period end (retaining current tier), then subscribe again with the new interval.

---

## Requirements *(mandatory)*

### Functional Requirements

**Subscription Lifecycle**

- **FR-001**: The system MUST allow an org admin to choose between monthly and annual billing intervals when subscribing to a paid tier.
- **FR-002**: The system MUST create a recurring subscription via the payment infrastructure; the org admin never interacts with the payment provider directly.
- **FR-003**: The system MUST record the active subscription in a dedicated store tracking: org, tier, billing interval, current period start/end, status, scheduled downgrade tier, consecutive failed payment count, next renewal amount, and currency.
- **FR-004**: The system MUST lazily create a payment-provider customer record for an org on first subscription and persist the customer reference on the org record.
- **FR-005**: The billing page MUST display subscription status, current tier, next renewal date, and next renewal amount for any org with an active subscription.

**Proration**

- **FR-006**: The system MUST compute upgrade proration server-side using: `charge = (new_tier_amount × days_remaining / period_days) − (old_tier_amount × days_remaining / period_days)`, where `days_remaining` and `period_days` derive solely from the server-stored subscription record. Both the new and old tier amounts are prorated; the client never influences either value.
- **FR-007**: Proration MUST apply only on upgrades (moving to a higher-priced tier). Downgrades are always scheduled for the next renewal date and never prorated.

**Downgrade**

- **FR-008**: The system MUST allow an org admin to schedule a tier downgrade effective at the end of the current billing period.
- **FR-009**: On the renewal event, if a downgrade is scheduled, the system MUST apply the downgrade tier instead of renewing at the current tier, then clear the schedule.
- **FR-010**: An org admin MUST be able to cancel a pending scheduled downgrade before it takes effect.

**Cancellation**

- **FR-011**: The system MUST allow an org admin to cancel an active subscription (with confirmation) so it does not renew. The org retains its current tier until period end.
- **FR-012**: When a cancelled subscription's period ends, the system MUST automatically downgrade the org to the Starter tier.
- **FR-013**: An org admin MUST be able to reactivate a cancelled subscription that has not yet expired.

**Dunning**

- **FR-014**: When a renewal payment fails (signalled by a received `invoice.payment_failed` event from the payment provider), the system MUST set subscription status to "past due" and dispatch an email notification to the org admin via the existing notification service. The payment provider controls the retry schedule and timing; FormCraft does not schedule retries.
- **FR-015**: An org MUST retain its current tier while the subscription is in a "past due" status.
- **FR-015a**: When the subscription status is "past due", the billing page MUST display an "Update payment method" link that opens the payment provider's hosted Customer Portal so the org admin can update their card details.
- **FR-016**: After a configurable number of consecutive received `invoice.payment_failed` events (platform-level default: 3), the system MUST automatically downgrade the org to Starter, write a `billing_fulfillments` row with `source='webhook'` for billing reconciliation, and write an entry to the general `audit_logs` table attributed to a platform-initiated action (so the event is visible in the Platform Admin Console).
- **FR-017**: The consecutive failed payment count MUST reset to zero when an `invoice.paid` event is subsequently received.

**Webhook Handling**

- **FR-018**: The webhook endpoint MUST handle `invoice.paid`, `invoice.payment_failed`, `customer.subscription.updated`, and `customer.subscription.deleted` events.
- **FR-019**: All webhook handlers MUST be idempotent — re-delivery of any event must produce no duplicate fulfillment or state change.

**Security**

- **FR-020**: The payment provider's secret credentials MUST never be exposed to the web client at any point.
- **FR-021**: Subscription creation, upgrade, downgrade scheduling, and cancellation MUST be restricted to the org admin role. Automated dunning downgrades MUST be recorded as platform-initiated audit events.
- **FR-022**: All monetary amounts (proration charges, renewal amounts) MUST be computed entirely server-side. The client MUST NOT supply any monetary value for subscription operations.

**Payment Infrastructure Extension**

- **FR-023**: The payment infrastructure service MUST expose operations for: creating a subscription, fetching subscription state, upgrading a subscription price with proration, and cancelling a subscription at period end.
- **FR-024**: The price catalogue MUST include a provider price reference field linking each tier-and-interval combination to its corresponding object in the payment provider's system.

### Key Entities

- **Subscription**: One active recurring subscription per org. Attributes: org reference, provider subscription ID, tier, billing interval (monthly/annual), period start, period end, status (active/past_due/cancelled), scheduled downgrade tier (nullable), consecutive failed payment count, next renewal amount (minor currency units), currency.
- **Billing Price (extended)**: Extends the F058 price catalogue with a provider price reference for each tier + interval combination.
- **Organisation (extended)**: Extends the existing org record with a provider customer reference, created lazily on first subscription.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An org admin can initiate a recurring subscription and see the updated tier and next renewal date within 10 seconds of payment confirmation.
- **SC-002**: A prorated upgrade charge matches the server-computed formula (±1 minor currency unit for rounding) in 100% of tested upgrade scenarios.
- **SC-003**: A scheduled downgrade takes effect at the correct renewal date in 100% of tested renewal cycles.
- **SC-004**: A failed renewal triggers an email notification to the org admin within 5 minutes of the failure event.
- **SC-005**: After the configured failure threshold, an org is automatically downgraded to Starter with no manual intervention required.
- **SC-006**: All webhook handlers process duplicate event deliveries without any duplicate state change or fulfillment — verified by replay testing.
- **SC-007**: The billing page displays subscription status, renewal date, and renewal amount within 2 seconds for any org.
- **SC-008**: In 100% of tested subscription operations, no monetary amount originates from the client — all amounts are server-computed.

---

## Assumptions

- The PayGateway service already handles payment provider communication for one-off payments (F058) and will be extended with subscription-specific operations.
- Each org has at most one active tier subscription at a time.
- Billing intervals are limited to monthly and annual in this iteration.
- The dunning threshold (default: 3 consecutive failures) is configurable at the platform level via the existing org_settings infrastructure.
- Annual subscriptions follow the same dunning flow as monthly subscriptions; retry timing is controlled entirely by the payment provider's built-in retry schedule (FormCraft does not schedule its own retries).
- Proration uses calendar days, not billing-cycle business days.
- The Starter tier is free and requires no subscription; downgrading to Starter results in subscription cancellation rather than a lower-priced subscription.
- A `billing_purchases` record is still created for each subscription lifecycle event to maintain audit continuity from F058.
- Email notifications for dunning use the existing notification service already in production.

---

## Out of Scope

- Recurring billing for add-ons (seats, OCR batch credits remain one-off purchases).
- Trial periods or free-trial subscriptions.
- Multi-currency mid-cycle FX conversion.
- Tax/VAT calculation and tax-compliant invoice generation (separate gap G-7, future spec).
- Custom/negotiated pricing for Enterprise and Platform tiers (contract management, future gap G-12).
- Building a card-entry form inside FormCraft for payment method updates — the billing page provides a link to the payment provider's hosted Customer Portal instead (FR-015a).
- Switching billing interval (monthly ↔ annual) on an existing active subscription — interval is selected only when creating a new subscription.
- The payment provider's Customer Portal configuration and branding.

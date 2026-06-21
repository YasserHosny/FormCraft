# API Contracts: 059 Recurring Subscription Billing

**Branch**: `059-recurring-billing` | **Date**: 2026-06-20  
**Auth**: All endpoints require valid Supabase JWT. Subscription endpoints require `require_org_admin()`.

---

## FormCraft Backend — New Subscription Endpoints

All new endpoints are under the existing billing router. Prefix: `/api/billing/subscriptions`.

---

### GET `/api/billing/subscriptions/current`

Returns the current active or past_due subscription for the caller's org. Returns 404 if no active subscription exists (org is on free Starter tier).

**Auth**: `require_org_admin()`

**Response 200**:
```json
{
  "id": "uuid",
  "org_id": "uuid",
  "tier": "professional",
  "billing_interval": "monthly",
  "status": "active",
  "current_period_start": "2026-06-01T00:00:00Z",
  "current_period_end": "2026-07-01T00:00:00Z",
  "next_renewal_amount_minor": 4900,
  "currency": "SAR",
  "scheduled_downgrade_tier": null,
  "cancel_at_period_end": false,
  "failed_payment_count": 0
}
```

**Response 404**: `{ "detail": "billing.subscription_not_found" }`

---

### POST `/api/billing/subscriptions`

Creates a new recurring subscription. Only valid when the org has no active/past_due subscription. Lazily creates a Stripe Customer if `stripe_customer_id` is not set on the org.

**Auth**: `require_org_admin()`

**Request body**:
```json
{
  "tier": "professional",
  "billing_interval": "monthly",
  "return_url": "https://app.formcraft.io/billing"
}
```

**Response 201**:
```json
{
  "subscription_id": "uuid",
  "status": "active",
  "checkout": {
    "provider": "paygateway",
    "client_token": "pi_..._secret_...",
    "requires_action": true,
    "expires_at": "2026-06-20T16:50:00Z"
  }
}
```

**Errors**:
- `409 billing.subscription_already_active` — org already has active/past_due subscription

---

### POST `/api/billing/subscriptions/upgrade`

Upgrades an existing active subscription to a higher tier with proration. Rejected if the new tier is lower (use downgrade-schedule instead) or if the billing interval differs (use cancel + resubscribe).

**Auth**: `require_org_admin()`

**Request body**:
```json
{
  "tier": "enterprise"
}
```

**Response 200**:
```json
{
  "subscription_id": "uuid",
  "previous_tier": "professional",
  "new_tier": "enterprise",
  "proration_amount_minor": 2450,
  "currency": "SAR",
  "status": "active"
}
```

**Errors**:
- `404 billing.subscription_not_found`
- `409 billing.downgrade_requires_schedule` — new tier is lower; use downgrade-schedule endpoint
- `409 billing.interval_change_not_supported` — tier is same but interval differs

---

### POST `/api/billing/subscriptions/downgrade-schedule`

Schedules a downgrade to a lower tier, effective at the next renewal. Replaces any existing scheduled downgrade.

**Auth**: `require_org_admin()`

**Request body**:
```json
{
  "tier": "professional"
}
```

**Response 200**:
```json
{
  "subscription_id": "uuid",
  "current_tier": "enterprise",
  "scheduled_downgrade_tier": "professional",
  "effective_date": "2026-07-01T00:00:00Z"
}
```

**Errors**:
- `404 billing.subscription_not_found`
- `409 billing.upgrade_requires_immediate` — new tier is higher; use upgrade endpoint

---

### DELETE `/api/billing/subscriptions/downgrade-schedule`

Cancels a pending scheduled downgrade. The subscription renews at the current tier.

**Auth**: `require_org_admin()`

**Response 200**:
```json
{
  "subscription_id": "uuid",
  "current_tier": "enterprise",
  "scheduled_downgrade_tier": null
}
```

**Errors**:
- `404 billing.subscription_not_found`
- `409 billing.no_downgrade_scheduled`

---

### POST `/api/billing/subscriptions/cancel`

Schedules the subscription to not renew. The org retains the current tier until `current_period_end`. Requires confirmation (enforced client-side via dialog; no extra server field needed).

**Auth**: `require_org_admin()`

**Request body**: `{}` (empty — no amount or reason needed)

**Response 200**:
```json
{
  "subscription_id": "uuid",
  "tier": "professional",
  "cancel_at_period_end": true,
  "period_end": "2026-07-01T00:00:00Z"
}
```

**Errors**:
- `404 billing.subscription_not_found`
- `409 billing.already_cancelled`

---

### POST `/api/billing/subscriptions/reactivate`

Reverses a pending cancellation (`cancel_at_period_end = true`). Only valid while the period has not yet ended.

**Auth**: `require_org_admin()`

**Response 200**:
```json
{
  "subscription_id": "uuid",
  "tier": "professional",
  "cancel_at_period_end": false,
  "next_renewal_date": "2026-07-01T00:00:00Z"
}
```

**Errors**:
- `404 billing.subscription_not_found`
- `409 billing.subscription_not_cancelling` — no pending cancellation to reverse
- `409 billing.subscription_already_expired` — period already ended; must subscribe again

---

### POST `/api/billing/subscriptions/portal-url`

Returns a short-lived URL to the payment provider's hosted Customer Portal. Only available when subscription status is `past_due`. The Angular client opens this URL in a new tab. POST is used because this operation creates a Stripe Billing Portal session (server-side state).

**Auth**: `require_org_admin()`

**Request body**:
```json
{
  "return_url": "https://app.formcraft.io/billing"
}
```

**Response 200**:
```json
{
  "portal_url": "https://billing.stripe.com/session/...",
  "expires_at": "2026-06-20T17:05:00Z"
}
```

**Errors**:
- `404 billing.subscription_not_found`
- `409 billing.subscription_not_past_due` — portal link only needed when past_due

---

### POST `/api/billing/paygateway/subscription-webhook` (new)

Receives subscription lifecycle events from PayGateway. Verified with HMAC-SHA256 (`X-PayGateway-Signature` header, same mechanism as the existing payment webhook). Returns 200 with `{"received": true}` for all known events; 204 for unknown events (not an error — Stripe sends many event types).

**Auth**: `X-PayGateway-Signature` HMAC verification (no JWT required — server-to-server)

**Request body** (PayGateway subscription event format):
```json
{
  "event_id": "evt_...",
  "event_type": "invoice.paid",
  "subscription_id": "sub_...",
  "invoice_id": "in_...",
  "amount_paid_minor": 4900,
  "currency": "SAR",
  "period_start": "2026-07-01T00:00:00Z",
  "period_end": "2026-08-01T00:00:00Z",
  "metadata": {}
}
```

Supported `event_type` values:
- `invoice.paid` — renewal succeeded or initial payment succeeded
- `invoice.payment_failed` — renewal payment failed
- `customer.subscription.updated` — tier/interval/status changed on Stripe side
- `customer.subscription.deleted` — subscription was deleted from Stripe

**Response 200**: `{ "received": true, "event_type": "invoice.paid" }`
**Response 401**: `{ "detail": "billing.webhook_invalid" }` — signature mismatch

---

## PayGateway Extension — New Endpoints

These endpoints are implemented in the PayGateway service (port 8001) and are called only by the FormCraft backend. They wrap Stripe APIs. Auth: `Authorization: Bearer {PAYGATEWAY_SERVICE_KEY}`.

### POST `/api/v1/customers`
Creates a Stripe Customer. Returns `{ "id": "cus_...", "email": "..." }`.

### POST `/api/v1/subscriptions`
Creates a Stripe Subscription using `stripe.Subscription.create()`.
- Body: `{ "customer_id": "cus_...", "price_id": "price_...", "metadata": {} }`
- Returns: `{ "id": "sub_...", "status": "active", "current_period_start": ..., "current_period_end": ..., "latest_invoice": { "payment_intent": { "client_secret": "pi_..._secret_..." } } }`

### GET `/api/v1/subscriptions/{id}`
Retrieves a Stripe Subscription. Returns full Stripe subscription object subset.

### POST `/api/v1/subscriptions/{id}/upgrade`
Modifies the subscription's price using `stripe.Subscription.modify()` with `proration_behavior="create_prorations"`.
- Body: `{ "new_price_id": "price_..." }`
- Returns: `{ "id": "sub_...", "status": "active", "proration_amount_minor": 2450 }`

### POST `/api/v1/subscriptions/{id}/cancel`
Sets `cancel_at_period_end=True` on the Stripe Subscription.
- Returns: `{ "id": "sub_...", "cancel_at_period_end": true, "current_period_end": ... }`

### POST `/api/v1/subscriptions/{id}/reactivate`
Sets `cancel_at_period_end=False` on the Stripe Subscription.

### POST `/api/v1/customers/{id}/portal`
Creates a Stripe Billing Portal session.
- Body: `{ "return_url": "https://app.formcraft.io/billing" }`
- Returns: `{ "portal_url": "https://billing.stripe.com/session/...", "expires_at": ... }`

---

## Angular Service Changes

The existing `BillingService` in the frontend gets new methods:

```typescript
// New methods on BillingService
getCurrentSubscription(): Observable<SubscriptionResponse | null>
createSubscription(req: CreateSubscriptionRequest): Observable<CreateSubscriptionResponse>
upgradeSubscription(req: UpgradeSubscriptionRequest): Observable<UpgradeSubscriptionResponse>
scheduleDowngrade(req: ScheduleDowngradeRequest): Observable<DowngradeScheduleResponse>
cancelDowngradeSchedule(): Observable<DowngradeScheduleResponse>
cancelSubscription(): Observable<CancelSubscriptionResponse>
reactivateSubscription(): Observable<ReactivateSubscriptionResponse>
getPortalUrl(returnUrl: string): Observable<PortalUrlResponse>
```

---

## New i18n Keys (EN + AR required)

```
billing.subscription_status.active
billing.subscription_status.past_due
billing.subscription_status.cancelled
billing.subscription_renews_on
billing.subscription_ends_on
billing.subscription_downgrade_scheduled
billing.subscription_cancel_confirm_title
billing.subscription_cancel_confirm_body
billing.update_payment_method
billing.interval.monthly
billing.interval.annual
billing.subscription_already_active
billing.subscription_not_found
billing.downgrade_requires_schedule
billing.interval_change_not_supported
billing.upgrade_requires_immediate
billing.no_downgrade_scheduled
billing.already_cancelled
billing.subscription_not_cancelling
billing.subscription_already_expired
billing.subscription_not_past_due
billing.portal_url_error
```

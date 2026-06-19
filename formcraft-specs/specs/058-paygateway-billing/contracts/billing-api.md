# API Contract: PayGateway Billing Integration

All endpoints require Supabase JWT authentication unless noted. Org-admin purchase endpoints use the caller's organization context. Platform-admin refund endpoints require `is_platform_admin=true`. Responses use translation keys for user-facing messages.

## GET `/api/billing/options`

List purchasable tiers and add-ons for the caller's organization.

**Query Parameters**

- `purpose` optional enum: `subscription_tier`, `seats`, `ocr_batch`, `marketplace_template`
- `listing_id` optional UUID for marketplace template pricing

**Response 200**

```json
{
  "currency": "EGP",
  "current_tier": "starter",
  "tiers": [
    {
      "tier": "professional",
      "amount_minor": 250000,
      "currency": "EGP",
      "available": true,
      "unavailable_reason_key": null
    }
  ],
  "addons": [
    {
      "purpose": "seats",
      "unit_amount_minor": 10000,
      "currency": "EGP",
      "min_quantity": 1,
      "max_quantity": 500,
      "available": true
    }
  ]
}
```

**Rules**

- Subscription options include only tiers higher than the current tier.
- Missing price in organization currency returns `available=false`.

## POST `/api/billing/purchases`

Create a purchase intent, compute price server-side, and either return a PayGateway checkout token or immediately fulfill zero-amount purchases.

**Request**

```json
{
  "purpose": "subscription_tier",
  "target": {
    "tier": "professional"
  },
  "quantity": null,
  "return_url": "https://app.formcraft.example/billing/return"
}
```

**Response 201: provider checkout required**

```json
{
  "purchase_id": "7a9b94d3-f330-4d2b-a44a-1a4ea0f227e5",
  "status": "created",
  "amount_minor": 250000,
  "currency": "EGP",
  "checkout": {
    "provider": "paygateway",
    "client_token": "single-purchase-token",
    "requires_action": false,
    "expires_at": "2026-06-19T15:30:00Z"
  }
}
```

**Response 201: zero-amount fulfilled**

```json
{
  "purchase_id": "7a9b94d3-f330-4d2b-a44a-1a4ea0f227e5",
  "status": "succeeded",
  "amount_minor": 0,
  "currency": "EGP",
  "checkout": null,
  "message_key": "billing.purchase.fulfilled"
}
```

**Errors**

- `400 billing.price_unavailable`
- `400 billing.invalid_target`
- `403 billing.org_admin_required`
- `409 billing.duplicate_pending_purchase`
- `503 billing.provider_unavailable`

## POST `/api/billing/purchases/{purchase_id}/verify`

Authoritatively verify provider status and run idempotent fulfillment when payment succeeded.

**Request**

```json
{
  "provider_payment_id": "pgw_pay_123",
  "client_reference": "optional-return-reference"
}
```

**Response 200**

```json
{
  "purchase_id": "7a9b94d3-f330-4d2b-a44a-1a4ea0f227e5",
  "status": "succeeded",
  "fulfilled": true,
  "message_key": "billing.purchase.fulfilled"
}
```

**Rules**

- Provider status is fetched server-side from PayGateway.
- Repeated calls return the same final status and never duplicate fulfillment.
- `requires_action` returns a localized authentication message key and no fulfillment.

## GET `/api/billing/purchases/{purchase_id}`

Fetch one purchase visible to the caller's organization, or to platform admins.

**Response 200**

```json
{
  "id": "7a9b94d3-f330-4d2b-a44a-1a4ea0f227e5",
  "organization_id": "368f568a-5ed6-4a81-bb0d-03ef3a8c6f07",
  "purpose": "subscription_tier",
  "target": { "tier": "professional" },
  "amount_minor": 250000,
  "currency": "EGP",
  "status": "succeeded",
  "fulfilled_at": "2026-06-19T15:06:00Z",
  "created_at": "2026-06-19T15:02:00Z"
}
```

## GET `/api/billing/purchases`

List caller organization purchases. Platform admins may pass `organization_id`.

**Query Parameters**

- `organization_id` optional UUID, platform-admin only
- `status` optional enum
- `purpose` optional enum
- `limit` default 50
- `cursor` optional opaque cursor

## POST `/api/billing/paygateway/webhook`

PayGateway server-to-server event receiver. Uses PayGateway signature verification and never trusts unsigned events.

**Request**

```json
{
  "event_id": "pgw_evt_123",
  "event_type": "payment.succeeded",
  "payment_id": "pgw_pay_123",
  "purchase_reference": "7a9b94d3-f330-4d2b-a44a-1a4ea0f227e5"
}
```

**Response 200**

```json
{
  "received": true,
  "purchase_id": "7a9b94d3-f330-4d2b-a44a-1a4ea0f227e5",
  "status": "succeeded"
}
```

## POST `/api/platform/billing/purchases/{purchase_id}/refund`

Issue a full refund and reverse the original effect. Platform-admin only.

**Request**

```json
{
  "reason": "Customer requested cancellation"
}
```

**Response 200**

```json
{
  "refund_id": "0edfdab5-3470-4f49-9c72-c03b3916a888",
  "purchase_id": "7a9b94d3-f330-4d2b-a44a-1a4ea0f227e5",
  "status": "succeeded",
  "reversal_status": "applied",
  "amount_minor": 250000,
  "currency": "EGP",
  "message_key": "billing.refund.applied"
}
```

**Errors**

- `403 billing.platform_admin_required`
- `404 billing.purchase_not_found`
- `409 billing.purchase_not_refundable`
- `409 billing.already_refunded`
- `503 billing.provider_unavailable`

## Frontend Contract

The Angular billing service exposes:

- `getOptions(purpose?, listingId?)`
- `createPurchase(request)`
- `verifyPurchase(purchaseId, providerPaymentId?)`
- `getPurchase(purchaseId)`
- `listPurchases(filters)`
- `refundPurchase(purchaseId, reason)` for platform-admin UI only

The checkout component must support:

- Provider secure card element mounting with no raw card values in FormCraft state.
- 3-D Secure / additional action status.
- Theme switch retention on `/billing` and Spark equivalent routes.
- Error keys for decline, authentication, provider unavailable, rate limit, price unavailable, and access denied.

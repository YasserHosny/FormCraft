# Quickstart: 059 Recurring Subscription Billing

**Branch**: `059-recurring-billing`

---

## How This Feature Fits the Existing System

F059 extends the F058 billing system. The key change: when an org admin buys a tier, instead of a one-off payment intent, a Stripe Subscription is created. The existing `billing_purchases` / `billing_fulfillments` tables remain in use for the initial subscription payment and for proration charges. A new `billing_subscriptions` table tracks the recurring state.

**Touch points:**
- `formcraft-backend/app/services/paygateway_client.py` — add 7 new PayGateway methods
- `formcraft-backend/app/services/billing_service.py` — add `SubscriptionService` methods (or extend existing class)
- `formcraft-backend/app/schemas/billing.py` — add subscription request/response schemas
- `formcraft-backend/app/api/routes/billing.py` — add 7 new routes + 1 new webhook route
- `formcraft-backend/migrations/051_recurring_billing.sql` — new table + column extensions
- `formcraft-frontend/.../billing-page/` — extend to show subscription state
- `formcraft-frontend/.../checkout-dialog/` — add interval picker (monthly/annual)
- `formcraft-frontend/src/assets/i18n/en.json` + `ar.json` — new translation keys

---

## Implementation Order (dependency-safe)

```
1. Migration 051 → creates billing_subscriptions, extends billing_prices + organizations
2. PayGateway extension → adds subscription + customer + portal endpoints
3. PayGatewayClient extension → new methods in paygateway_client.py
4. Subscription schemas → new Pydantic models in billing.py
5. SubscriptionService → backend business logic
6. Billing routes → new FastAPI routes + subscription webhook handler
7. Frontend subscription service → new Angular service methods
8. Frontend billing page → extend to display subscription state
9. Frontend checkout dialog → add interval picker
10. i18n keys → EN + AR for all new strings
11. Tests → contract tests for all new endpoints; unit tests for proration math; webhook replay tests
```

---

## Key Invariants to Preserve

- **One active subscription per org**: enforced by partial unique index in DB and validated in service before creating.
- **Server-side amounts only**: `SubscriptionService.compute_proration_preview()` is purely informational; never passed to PayGateway as the charge amount.
- **Idempotent webhook handlers**: check `last_invoice_id` before processing `invoice.payment_failed` or `invoice.paid`.
- **Audit trail**: every tier change triggered by a webhook (downgrade at renewal, dunning downgrade) must write a `billing_fulfillments` row with `source='webhook'`.
- **RLS**: `billing_subscriptions` must have RLS enabled matching the pattern from `billing_purchases`.

---

## Testing Reference

```bash
# Backend unit tests
cd formcraft-backend && pytest app/services/tests/test_subscription_service.py -v

# Contract tests for new endpoints
pytest app/api/tests/test_billing_subscriptions.py -v

# Webhook replay tests (idempotency)
pytest app/api/tests/test_subscription_webhook.py -v

# Run all billing tests
pytest -k "billing" -v
```

```typescript
// Frontend
cd formcraft-frontend && ng test --include="**/billing/**"
```

---

## Environment Variables Needed

| Variable | Purpose | Where |
|---|---|---|
| `PAYGATEWAY_BASE_URL` | PayGateway service URL (already set from F058) | Backend |
| `PAYGATEWAY_SERVICE_KEY` | Service-to-service JWT (already set from F058) | Backend |
| `PAYGATEWAY_WEBHOOK_SECRET` | HMAC key for webhook verification (already set from F058) | Backend |
| Stripe `provider_price_id` seed values | Populate `billing_prices.provider_price_id` after migration | DB seed |

No new environment variables are needed in the Angular frontend.

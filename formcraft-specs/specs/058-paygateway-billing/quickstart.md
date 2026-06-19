# Quickstart: PayGateway Billing Integration

## Prerequisites

- PayGateway test environment is reachable from the FastAPI backend.
- Backend has PayGateway service URL, service key, webhook signing secret, and mode configured as environment variables.
- Supabase migrations are applied, including `formcraft-backend/migrations/049_paygateway_billing.sql`.
- Seed billing prices exist for supported organization default currencies: `EGP`, `SAR`, and `AED`.

## Backend Test Flow

1. Create failing tests first:

   ```bash
   cd /media/yasserhosny/My\ Passport/Work/Projects/FormCraft/formcraft-backend
   pytest tests/contract/test_billing_api.py tests/unit/test_billing_service.py tests/unit/test_paygateway_client.py tests/integration/test_billing_routes.py
   ```

2. Implement the billing migration, schemas, service, PayGateway adapter, and routes.

3. Re-run focused tests:

   ```bash
   cd /media/yasserhosny/My\ Passport/Work/Projects/FormCraft/formcraft-backend
   pytest tests/contract/test_billing_api.py tests/unit/test_billing_service.py tests/unit/test_paygateway_client.py tests/integration/test_billing_routes.py
   ```

4. Run backend lint and wider tests before handoff:

   ```bash
   cd /media/yasserhosny/My\ Passport/Work/Projects/FormCraft/formcraft-backend
   ruff check .
   pytest
   ```

## Frontend Test Flow

1. Create billing service/component tests for option loading, zero-amount fulfillment, provider errors, 3-D Secure state, and theme-route retention.

2. Run focused Angular tests:

   ```bash
   cd /media/yasserhosny/My\ Passport/Work/Projects/FormCraft/formcraft-frontend
   npm test -- --watch=false
   ```

3. Manually verify these UI combinations:

   - Classic + Arabic RTL + light
   - Classic + English LTR + dark
   - Spark + Arabic RTL + dark
   - Spark + English LTR + light

## End-to-End Acceptance Checks

1. As an org admin, open `/billing`, select a tier higher than the current tier, and pay with a PayGateway test card.
2. Confirm the organization `subscription_tier` changes immediately after verified success.
3. Repeat purchase verification for the same purchase and confirm no duplicate fulfillment or audit record appears.
4. Attempt a purchase as a non-admin and confirm `403`.
5. Attempt cross-organization purchase access and confirm `404` or `403` without leaking record details.
6. Seed a zero-amount price, create the purchase, and confirm no PayGateway request is made while fulfillment and audit still occur.
7. Use a declined test card and confirm the tier/add-on effect is not applied.
8. Use a 3-D Secure test card and confirm the authentication step completes before fulfillment.
9. As a platform admin, refund a successful tier purchase and confirm the prior tier is restored and the refund audit entry is written.
10. Switch between Classic and Spark while on billing and confirm the route remains in billing checkout context.

## Timing Validation

- Confirm checkout token creation completes under 2 seconds excluding PayGateway latency.
- Confirm test-mode tier upgrade completes in under 3 minutes from billing page open to active tier display.
- Confirm platform-admin refund completes in under 3 minutes from confirmation to refunded purchase status and audit entry.

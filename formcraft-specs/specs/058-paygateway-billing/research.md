# Research: PayGateway Billing Integration

## Decision: Treat FormCraft as the purchase source of truth and PayGateway as the payment processor

**Rationale**: FormCraft owns organization tier, add-on allowance, OCR credit, marketplace template copy, audit trail, RBAC, and RLS. PayGateway should create/confirm/refund charges, but fulfillment must occur only after FormCraft verifies provider status server-side. This satisfies FR-002, FR-006, FR-007, and FR-012 while avoiding any browser exposure of provider secrets.

**Alternatives considered**: Letting PayGateway call FormCraft directly for fulfillment was rejected because FormCraft still needs org-scoped authorization, price authority, audit records, and idempotency. Trusting client payment status was rejected by FR-006.

## Decision: Persist `billing_purchases` before provider checkout token creation

**Rationale**: A durable purchase record gives every provider request an internal idempotency key, stores the authoritative amount/currency/purpose/target, and allows recovery if the buyer closes the browser before returning. It also supports status inspection and retry without recomputing mutable intent data.

**Alternatives considered**: Creating PayGateway charges first and then inserting a local purchase was rejected because a database failure after charge creation could orphan paid transactions. Creating purchases only after payment success was rejected because it cannot support recovery or status inspection.

## Decision: Use one idempotent fulfillment service for all confirmation paths

**Rationale**: Browser return, explicit status polling, scheduled reconciliation, and webhooks may all observe the same provider success. A single `fulfill_purchase_once(purchase_id, actor_id, source)` method with a unique fulfillment row and transactional status update enforces SC-002.

**Alternatives considered**: Separate fulfillment logic in each route was rejected because duplicate confirmations are an explicit edge case. Relying only on provider idempotency was rejected because the business effect inside FormCraft must also be idempotent.

## Decision: Store prices as normalized price list rows with organization default currency

**Rationale**: The spec requires system-computed amounts, no client-supplied amount trust, and charge currency from the organization record. Normalized price rows for tiers and add-ons make missing currency explicit and make unavailable options easy to explain in localized UI.

**Alternatives considered**: Hardcoded price constants were rejected because operators must maintain prices over time. Client-provided prices were rejected by FR-002 and SC-003. Buyer-selected currency was rejected by FR-002b.

## Decision: Fulfill zero-amount purchases through the same idempotency path without calling PayGateway

**Rationale**: FR-002a requires bypassing card collection and the provider when amount is zero, while preserving status, audit, and at-most-once behavior. Marking the purchase `succeeded` with `provider_status=not_required` and running the same fulfillment method keeps the behavior uniform.

**Alternatives considered**: Hiding zero-priced options was rejected because free promotions or seeded prices may be valid. Sending zero charges to PayGateway was rejected because the requirement says bypass the provider entirely.

## Decision: Model full-only refunds as separate refund records with reversal effects

**Rationale**: Full refunds need platform-admin authorization, a provider refund call, purchase status transition to `refunded`, and one reversal of the original effect. Separate refund records retain actor, reason, provider refund id, reversal status, and auditability while enforcing one refund per purchase.

**Alternatives considered**: Mutating the purchase row only was rejected because it loses refund-specific actor/provider metadata. Partial refund state was rejected by FR-016a.

## Decision: Tier refunds restore the stored previous tier even if usage is now over limit

**Rationale**: The clarification requires reversal even when current usage exceeds the reverted limits, without removing users or data. The purchase must therefore snapshot `previous_tier` at fulfillment time and use that value during reversal.

**Alternatives considered**: Blocking reversal when over limit was rejected by FR-015a. Auto-deactivating users/data was rejected by FR-015a and would create unrelated enforcement behavior.

## Decision: Marketplace premium purchases call existing marketplace clone logic after payment success

**Rationale**: Feature 035 already owns listing metadata, template copy semantics, and revenue split concepts. Billing should orchestrate paid access and record the split, then reuse marketplace service behavior to create the buyer draft.

**Alternatives considered**: Duplicating marketplace import logic in billing was rejected because it risks diverging clone rules and RLS protections. Treating all marketplace imports as free was rejected because this feature explicitly adds premium purchase.

## Decision: Implement checkout as shared Angular billing components reachable from Classic, Spark, Platform Console, and Marketplace

**Rationale**: The same purchase flow must work in both themes and both directions. A single billing module with shared state and theme-compatible shells reduces duplicate behavior and makes theme-switch persistence testable.

**Alternatives considered**: Separate Classic and Spark checkout implementations were rejected because they would duplicate payment-state logic and increase the chance of inconsistent localization or 3-D Secure handling.

# Data Model: PayGateway Billing Integration

## Entity: Billing Price

Authoritative sellable price row used to compute purchase amounts.

**Fields**

- `id` UUID primary key
- `price_type` enum: `tier`, `seat`, `ocr_batch`
- `target_key` text: tier name, `seat`, or OCR package key
- `currency` char(3): organization default currency such as `EGP`, `SAR`, `AED`
- `billing_interval` enum nullable: `one_time`, `monthly`, `annual`; this feature charges one-time, tier rows still retain interval metadata for future compatibility
- `unit_amount_minor` integer: amount in minor currency units
- `min_quantity` integer nullable
- `max_quantity` integer nullable
- `is_active` boolean
- `starts_at` timestamptz
- `ends_at` timestamptz nullable
- `created_at`, `updated_at`, `created_by`

**Validation Rules**

- `(price_type, target_key, currency, billing_interval, is_active active window)` must identify at most one active price.
- `unit_amount_minor >= 0`.
- Tier prices exist only for `starter`, `professional`, `enterprise`, `platform`, but checkout offers only tiers above the current tier.
- Seat/OCR purchases require a positive quantity within configured bounds unless amount resolves to zero through price.

## Entity: Billing Purchase

Single purchase intent and lifecycle record, isolated by organization.

**Fields**

- `id` UUID primary key
- `organization_id` UUID foreign key to `organizations`
- `created_by` UUID foreign key to `profiles`
- `purpose` enum: `subscription_tier`, `seats`, `ocr_batch`, `marketplace_template`
- `target` jsonb: purpose-specific target payload
- `quantity` integer nullable
- `currency` char(3)
- `amount_minor` integer
- `status` enum: `created`, `requires_action`, `succeeded`, `failed`, `refunded`, `cancelled`
- `provider` text default `paygateway`
- `provider_payment_id` text nullable
- `provider_checkout_token_hash` text nullable
- `provider_status` text nullable
- `idempotency_key` text unique
- `failure_code` text nullable
- `failure_message_key` text nullable
- `previous_effect_snapshot` jsonb nullable
- `fulfilled_at` timestamptz nullable
- `created_at`, `updated_at`

**Validation Rules**

- `amount_minor` and `currency` are computed server-side and never accepted from client request bodies.
- `organization_id` always comes from authenticated org context unless platform-admin refund views are used.
- `target` must match `purpose`.
- Missing active price in the organization currency prevents purchase creation.
- `amount_minor = 0` skips provider fields and moves through `succeeded` plus fulfillment.

**State Transitions**

```text
created -> requires_action -> succeeded -> refunded
created -> succeeded -> refunded
created -> failed
created -> cancelled
requires_action -> failed
requires_action -> succeeded -> refunded
```

## Entity: Billing Fulfillment

At-most-once business effect application for a purchase.

**Fields**

- `id` UUID primary key
- `purchase_id` UUID unique foreign key to `billing_purchases`
- `organization_id` UUID foreign key
- `effect_type` enum: `tier_changed`, `seats_added`, `ocr_credited`, `template_copied`
- `effect_payload` jsonb: target/effect details
- `applied_by` UUID nullable: user or system actor
- `source` enum: `checkout_return`, `status_poll`, `webhook`, `reconciliation`, `zero_amount`
- `applied_at` timestamptz

**Validation Rules**

- Unique `purchase_id` enforces one fulfillment per purchase.
- Fulfillment can run only for purchases verified as `succeeded` or zero-amount purchases.
- Every fulfillment writes exactly one organization audit log entry.

## Entity: Billing Refund

Full-only refund and reversal record.

**Fields**

- `id` UUID primary key
- `purchase_id` UUID unique foreign key to `billing_purchases`
- `organization_id` UUID foreign key
- `requested_by` UUID foreign key to platform-admin profile
- `reason` text
- `provider_refund_id` text nullable
- `amount_minor` integer
- `currency` char(3)
- `status` enum: `requested`, `succeeded`, `failed`
- `reversal_status` enum: `pending`, `applied`, `failed`
- `reversal_payload` jsonb nullable
- `created_at`, `updated_at`, `applied_at`

**Validation Rules**

- One refund per purchase.
- Refunds are full-only; `amount_minor` equals the purchase amount.
- Platform-admin role is required.
- Refund reversal always applies for tier and seat purchases even if resulting usage exceeds limits.
- OCR/template refunds apply a non-destructive reversal: payment, revenue split, purchase status, and audit state are reversed, but already-consumed OCR outputs and copied templates are not deleted automatically.

## Entity: Billing Marketplace Split

Revenue split for paid marketplace purchases.

**Fields**

- `id` UUID primary key
- `purchase_id` UUID unique foreign key
- `listing_id` UUID foreign key to marketplace listing
- `publisher_org_id` UUID foreign key to organizations
- `buyer_org_id` UUID foreign key to organizations
- `gross_amount_minor` integer
- `platform_share_minor` integer
- `publisher_share_minor` integer
- `currency` char(3)
- `created_at`

**Validation Rules**

- Created only for `marketplace_template` purchases.
- Shares sum to gross amount.
- Split uses listing price and configured platform share at purchase time.

## Existing Entity Extensions

### Organization

- Uses existing `subscription_tier`.
- Adds `purchased_seat_allowance` and `ocr_scan_credit_balance` additive allowance columns.
- Adds `default_currency` char(3) for charge currency selection.

### Audit Record

New action types:

- `billing.purchase.fulfilled`
- `billing.purchase.failed`
- `billing.purchase.refunded`
- `billing.purchase.refund_failed`
- `billing.purchase.zero_amount_fulfilled`

### Marketplace Listing

- Paid listings provide price/currency metadata for checkout.
- Billing purchase fulfillment creates a draft template copy through marketplace service and records the split.

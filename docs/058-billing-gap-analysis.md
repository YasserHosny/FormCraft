# Gap Analysis: Revenue Model Vision vs. 058-PayGateway-Billing Specification

**Date**: 2026-06-20
**Source A**: `system-critique-and-vision.md` §Revenue Model (L2064–L2099)
**Source B**: `formcraft-specs/specs/058-paygateway-billing/` (spec, plan, data-model, research, contracts)

---

## Executive Summary

Feature 058 covers the **"Sellable"** half of the revenue blocker — turning tiers and add-ons into purchasable products via card payment. It deliberately leaves out the **"Enforced"** half (blocking over-limit usage) and several revenue-model line items. This report maps every vision-doc revenue item to the 058 spec to identify what is covered, what is deferred, and what is absent from any known spec.

---

## 1. Tier Subscription Coverage

| Vision Tier | Vision Pricing Model | 058 Coverage | Gap |
|-------------|---------------------|--------------|-----|
| **Starter** | Monthly subscription | **Partial** — purchasable as a tier row in `billing_prices`; interval metadata stored but charges are one-off | No recurring/auto-renewal billing; no monthly charge cycle |
| **Professional** | Annual subscription | **Partial** — same as Starter | No annual auto-renewal; no proration on mid-cycle upgrade |
| **Enterprise** | Custom pricing, annual contract | **Partial** — a tier price row can exist, but "custom pricing" implies negotiated/offline deals | No contract management, no offline/invoice payment path |
| **Platform** | Custom pricing | **Partial** — same as Enterprise | Same gaps as Enterprise |

### Key tier gaps

- **Recurring billing**: The vision doc describes monthly and annual subscriptions. 058 explicitly scopes out recurring/auto-renewing charges (spec §Out of Scope). Every purchase is a one-off "pay to change tier" charge.
- **Self-serve downgrade**: Vision implies tiers are fluid (up and down). 058 supports upgrades only; downgrades happen only via platform-admin refund/reversal.
- **Custom/contract pricing**: Enterprise and Platform tiers use "custom pricing, annual contract" — no contract workflow, negotiated pricing, or invoice-based payment exists in 058.
- **Proration**: No credit or proration when upgrading mid-billing-period (explicitly out of scope).

---

## 2. Add-on Coverage

| Vision Add-on | Vision Price Model | 058 Coverage | Gap |
|---------------|-------------------|--------------|-----|
| **Additional operators beyond tier limit** | Per seat / month | **Covered (purchase)** — Story 2 buys N seats; `purchased_seat_allowance` incremented on org. **Not covered (recurring)** — seats are a one-time add; no monthly seat billing cycle | No recurring per-seat/month charge |
| **OCR batch onboarding (one-time)** | Per form scanned | **Covered** — Story 3 buys N form-scan credits; `ocr_scan_credit_balance` incremented | Fully aligned with vision (one-time purchase model matches) |
| **Template Marketplace premium publishing** | Revenue share (70/30) | **Covered** — Story 4 purchases a premium template; `billing_marketplace_splits` records gross/platform/publisher shares | Split ratio is configurable at purchase time; vision says 70/30 but 058 doesn't hardcode the ratio — needs seed data alignment |
| **Custom integration connector** | One-time setup + monthly | **Not covered** — no purchase purpose for connectors exists in 058 | Entirely missing; no `connector` purpose in the billing system |
| **Priority support + SLA** | % of subscription | **Not covered** — no purchase purpose for support/SLA tiers | Entirely missing; no support-tier purchase flow |

---

## 3. Tier Limit Enforcement

| Vision Requirement | 058 Coverage | Gap |
|-------------------|--------------|-----|
| Starter: 1 designer + 3 operators + 100 submissions/month | **Not enforced** — 058 records `purchased_seat_allowance` but does not gate invites or submissions | Enforcement is explicitly out of scope (spec §Out of Scope, vision L2097) |
| Professional: 5 designers + 25 operators + unlimited submissions | Same | Same |
| Enterprise: Unlimited designers + operators | Same | Same |
| DB `tier_limits` mismatch (Starter = 10 users vs. vision = 4 users) | **Not addressed** — 058 does not modify `tier_limits` values | Reconciliation of `tier_limits` values is called out in vision L2092 but not in any spec |
| Submission volume cap (Starter = 100/month) | **Not addressed** — submission cap is not part of `tier_limits` table and is not enforced | Vision L2092 flags this; no spec covers it |
| Storage limits (5 GB / 25 GB / 100 GB / 500 GB per tier) | **Not addressed** | Not mentioned in 058 or any billing context |

---

## 4. Feature-Capability Coverage Matrix

| Capability | Vision Mentions | 058 Spec | 058 Data Model | 058 API Contract | Status |
|-----------|:-:|:-:|:-:|:-:|--------|
| Tier upgrade by card payment | Yes | FR-001, FR-008, Story 1 | `billing_purchases` | `POST /api/billing/purchases` | **Fully specified** |
| Seat add-on purchase | Yes | FR-009, Story 2 | `billing_purchases` + org column | `POST /api/billing/purchases` | **Fully specified** |
| OCR batch purchase | Yes | FR-010, Story 3 | `billing_purchases` + org column | `POST /api/billing/purchases` | **Fully specified** |
| Marketplace template purchase | Yes | FR-011, Story 4 | `billing_marketplace_splits` | `POST /api/billing/purchases` | **Fully specified** |
| Full + partial refund + reversal | Yes | FR-015–016a, Story 5 | `billing_refunds` | `POST /api/platform/billing/.../refund` | **Fully implemented** (was 501 stub; now live with optional partial amount) |
| Zero-amount fulfillment | Implicit | FR-002a | Same tables | Same endpoints | **Fully specified** |
| 3-D Secure / SCA support | Implicit | FR-004 | `requires_action` status | Verify endpoint | **Fully specified** |
| Recurring subscription billing | Yes (monthly/annual) | **Out of scope** | `billing_interval` stored but unused | — | **Gap** |
| Proration / credits | Implied | **Out of scope** | — | — | **Gap** |
| Self-serve downgrade | Implied | **Out of scope** | — | — | **Gap** |
| Tier limit enforcement gates | Yes (L2097) | **Out of scope** | — | — | **Gap (tracked separately)** |
| Custom connector purchase | Yes | **Not mentioned** | — | — | **Gap (no spec)** |
| Priority support purchase | Yes | **Not mentioned** | — | — | **Gap (no spec)** |
| Invoicing / tax / VAT | Implied for enterprise | **Out of scope** | — | — | **Gap** |
| Dunning / failed-renewal retry | Implied | **Out of scope** | — | — | **Gap** |
| Self-serve price admin UI | Operational need | **Out of scope** | — | — | **Gap** |

---

## 5. Data Model Alignment

| Vision Concept | 058 Data Model | Design Doc (`payment-gateway-integration.md`) | Delta |
|---------------|---------------|----------------------------------------------|-------|
| Price table | `billing_prices` — normalized with `price_type`, `target_key`, `currency`, `billing_interval`, quantity bounds | `tier_prices` — simpler, tier-only, single currency | 058 spec supersedes design doc; more complete |
| Purchase record | `billing_purchases` — 4 purposes, full lifecycle, idempotency key, provider fields, previous-effect snapshot | `billing_intents` — simpler, no snapshot, no idempotency key column | 058 spec supersedes; addresses more edge cases |
| Fulfillment record | `billing_fulfillments` — separate table, unique per purchase, effect type + source enum | Inline in `billing_intents.fulfilled_at` | 058 spec is more robust (separate audit-grade record) |
| Refund record | `billing_refunds` — separate table, reversal status, platform-admin only | Brief mention in design doc §4.5 | 058 spec is substantially more detailed |
| Marketplace split | `billing_marketplace_splits` — dedicated table with configurable shares | Inline `_clone_template` mention | 058 spec formalizes the 70/30 split recording |
| Org extensions | `default_currency`, `purchased_seat_allowance`, `ocr_scan_credit_balance` | `subscription_tier` mutation only | 058 adds currency + additive allowance columns |

**Assessment**: The 058 data model is a significant evolution of the design doc's simpler `tier_prices` / `billing_intents` sketch. The migration `049_paygateway_billing.sql` has been applied and matches the 058 data model.

---

## 6. API Contract Alignment

| Design Doc Endpoint | 058 Contract Endpoint | Alignment |
|--------------------|-----------------------|-----------|
| `POST /api/billing/create` | `POST /api/billing/purchases` | Renamed; 058 is RESTful |
| `POST /api/billing/confirm` | `POST /api/billing/purchases/{id}/verify` | Merged confirm + verify into one idempotent verify step |
| `GET /api/billing/{id}/status` | `GET /api/billing/purchases/{id}` | Simplified; status is a field on the purchase |
| — | `GET /api/billing/options` | **New in 058** — discovery endpoint for available tiers/add-ons |
| — | `GET /api/billing/purchases` | **New in 058** — purchase history list |
| — | `POST /api/billing/paygateway/webhook` | **New in 058** — server-to-server event receiver |
| (admin UI mention) | `POST /api/platform/billing/purchases/{id}/refund` | **New in 058** — formalized platform-admin refund endpoint |

**Assessment**: 058 API contract is more complete and RESTful than the design doc sketch. The design doc should be considered superseded by the 058 contracts.

---

## 7. Prioritized Gap Summary

### Critical Gaps (revenue blockers not addressed by 058)

| # | Gap | Impact | Status |
|---|-----|--------|--------|
| G-1 | **Tier enforcement gates** — invite and submission blocking | Tiers are purchasable but not enforced | ✅ **CLOSED** — `invitation_service._check_user_limit()` raises 402 when profiles+pending ≥ tier limit; `submission_service._check_submission_limit()` raises 402 when monthly count ≥ cap |
| G-2 | **`tier_limits` value mismatch** — DB Starter = 10 users vs. vision = 4 | Enforcement used wrong limits | ✅ **CLOSED** — migration `050_tier_limits_reconcile.sql` corrects starter→4, professional→30, enterprise→9999 |
| G-3 | **Submission volume cap** — not tracked in `tier_limits` | Starter's 100/month cap was untrackable | ✅ **CLOSED** — migration `050_tier_limits_reconcile.sql` adds `submissions_per_month_limit` column; Starter gets 100, others -1 (unlimited) |

### High Gaps (revenue model items with no spec)

| # | Gap | Impact | Recommended Next Step |
|---|-----|--------|----------------------|
| G-4 | **Recurring subscription billing** — monthly/annual auto-renewal, dunning | Every tier purchase is a one-off; no subscription continuity | Future feature spec; requires PayGateway subscription support |
| G-5 | **Custom integration connector purchase** — one-time setup + monthly | Revenue line item with no purchase path | Add `connector` purpose to billing or spec separately |
| G-6 | **Priority support + SLA purchase** — % of subscription | Revenue line item with no purchase path | Add `support_tier` purpose or spec separately |

### Medium Gaps (operational needs)

| # | Gap | Impact | Recommended Next Step |
|---|-----|--------|----------------------|
| G-7 | **Invoicing / tax / VAT** — enterprise customers typically require invoices | Cannot serve enterprise customers who need tax-compliant invoices | Future feature; depends on regional tax requirements |
| G-8 | **Self-serve price admin UI** — prices must be seeded/maintained manually | Operational burden; price changes require DB access | Future admin UI feature |
| G-9 | **Proration / mid-cycle credits** — upgrading mid-period gives no credit for unused time | Customer confusion on upgrade timing | Future enhancement to recurring billing |
| G-10 | **Self-serve downgrade** — only platform-admin refund can lower a tier | Friction for customers who want to scale down | Future feature; requires proration math |

### Low Gaps (nice-to-have)

| # | Gap | Impact | Recommended Next Step |
|---|-----|--------|----------------------|
| G-11 | **Partial refunds** — only full refunds supported | Cannot handle "refund 5 of 10 seats" | ✅ **CLOSED** — `billing_service.refund_purchase()` accepts optional `amount_minor`; partial refunds skip fulfillment reversal; full refunds reverse tier/seat/OCR effects |
| G-12 | **Contract management** — Enterprise/Platform use "annual contract" | No contract lifecycle tracking | ⏳ Future feature for enterprise sales |
| G-13 | **70/30 split ratio + marketplace fulfillment** — marketplace_template purpose raised 400, no split recorded | Marketplace purchases were broken end-to-end | ✅ **CLOSED** — `_compute_amount()` now handles `marketplace_template` via listing price; `fulfill_purchase_once()` clones template via `MarketplaceService.import_listing()` and records 70/30 in `billing_marketplace_splits` |

---

## 8. Conclusion

Feature 058 effectively closes the **"Sellable"** half of the revenue blocker: tiers and the three documented add-ons (seats, OCR batch, marketplace templates) become purchasable by card. The data model, API contracts, and security design are substantially more mature than the earlier design doc sketch.

The **three critical gaps** (G-1 through G-3) must be addressed in parallel or immediately after 058 implementation to make tier differentiation meaningful. The **recurring billing gap** (G-4) is the largest long-term revenue risk — without it, every subscription is a manual one-off payment.

Two vision-doc add-ons — **custom connectors** (G-5) and **priority support** (G-6) — have no purchase path in any spec and need dedicated feature work when those products are ready to sell.

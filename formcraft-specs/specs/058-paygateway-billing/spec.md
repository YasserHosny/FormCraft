# Feature Specification: PayGateway Billing Integration

**Feature Branch**: `058-paygateway-billing`
**Created**: 2026-06-19
**Status**: Draft
**Input**: Embed the already-built PayGateway service into FormCraft so organizations can pay by card for subscription tier upgrades and add-ons, closing the revenue gap where subscription tiers are display-only and not sellable.

## Overview

FormCraft sells access in tiers (starter / professional / enterprise / platform) plus add-ons,
but today a tier is only a stored label — there is no way for a customer to **pay to change it**,
and no purchase path for add-ons. This feature adds card payment so an organization administrator
can buy a tier upgrade or an add-on from inside FormCraft, with the purchase taking effect
automatically once payment succeeds. Payments are processed through the organization's
already-deployed PayGateway service; FormCraft never handles raw card data or payment secrets.

The checkout experience must work identically in both FormCraft UI themes (Classic and Spark),
in Arabic (RTL) and English (LTR), and be reachable both from a dedicated billing page and from
the Platform Console's organization Subscription view.

## Clarifications

### Session 2026-06-19

- Q: Can an org admin select a *lower* tier (self-serve downgrade) through checkout, or only upgrade? → A: Upgrades only; lowering a tier is possible only via a platform-admin refund/reversal (Story 5). No self-serve downgrade UI, no proration/credit math.
- Q: What happens when the computed charge amount is 0 (free tier / zero-quantity)? → A: Skip the card/payment step entirely and fulfill immediately — still record the purchase as succeeded and write the audit entry.
- Q: On refund, what if current usage exceeds the reverted tier/seat limit (e.g., 40 users when reverting to a 10-user tier)? → A: Always perform the reversal; the org may sit over-limit and no users/data are removed. Over-limit handling is left to the separate enforcement work.
- Q: Which currency is a purchase charged in? → A: The organization's configured default currency (from the org record); the buyer cannot change it. If no price exists for that currency, the option is unavailable.
- Q: Are partial refunds supported, or full-only? → A: Full refunds only — each refund reverses the entire purchase. No partial/proportional refunds.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upgrade the organization's subscription tier (Priority: P1)

An organization administrator who has hit (or anticipates) the limits of their current tier wants
to move to a higher tier. They open billing, see the available tiers and prices, choose a tier,
enter card details, and pay. On success the organization is immediately on the new tier and its
new limits apply.

**Why this priority**: This is the core revenue path and the direct fix for the documented
"tiers are display-only" gap. Without it, FormCraft cannot monetize differentially by tier. It is
a complete, valuable slice on its own.

**Independent Test**: In test mode, an org admin upgrades from starter to professional with a
test card; verify the organization's tier is updated, the new limits are in effect, and the change
is recorded — all without any other billing purpose being implemented.

**Acceptance Scenarios**:

1. **Given** an org admin viewing the billing page, **When** they select a higher tier and pay with a valid test card, **Then** the payment succeeds, the organization's tier is updated to the selected tier, and a confirmation is shown.
2. **Given** a successful tier purchase, **When** the admin returns to the billing/subscription view, **Then** the organization shows the new tier and the new tier limits are active.
3. **Given** a card that is declined, **When** the admin attempts payment, **Then** a clear, localized error is shown, no charge is recorded, and the tier is unchanged.
4. **Given** a card that requires additional bank authentication (3-D Secure), **When** the admin pays, **Then** the authentication step is presented and, once completed, the purchase proceeds normally.
5. **Given** the payment provider confirms success, **When** the same confirmation is processed more than once, **Then** the tier is changed exactly once (no double application).

---

### User Story 2 - Buy additional operator seats (Priority: P2)

An organization that has reached its seat limit but does not want to change tier buys a number of
extra operator seats. After payment, the organization can invite that many additional users.

**Why this priority**: Seats are the primary "expand" add-on in the revenue model and the most
common purchase after the initial tier. It reuses the entire payment flow from Story 1.

**Independent Test**: An org admin buys 10 extra seats with a test card; verify the organization's
effective user allowance increases by 10 and the purchase is recorded.

**Acceptance Scenarios**:

1. **Given** an org admin on the billing page, **When** they choose a seat quantity and pay, **Then** the price reflects the quantity, the payment succeeds, and the organization's effective seat allowance increases by that quantity.
2. **Given** a seat purchase that fails, **When** the admin retries with a different card, **Then** seats are added only once and only for the successful payment.

---

### User Story 3 - Buy a one-time OCR onboarding batch (Priority: P3)

An organization with a library of paper forms buys a one-time batch to OCR-digitize N forms. After
payment, the organization has credit for N form-scan jobs.

**Why this priority**: A one-time, high-value onboarding add-on that strengthens enterprise sales,
but not required for the core subscription revenue loop.

**Independent Test**: An org admin buys a 300-form OCR batch with a test card; verify the
organization is credited 300 form-scan jobs and the purchase is recorded.

**Acceptance Scenarios**:

1. **Given** an org admin selects an OCR batch of N forms, **When** they pay successfully, **Then** the organization is credited N form-scan jobs and the purchase is recorded.

---

### User Story 4 - Purchase a premium marketplace template (Priority: P3)

An organization admin buys a premium template from the marketplace. After payment, the template is
copied into their organization as an editable draft, and the revenue is split between the
publishing organization and FormCraft.

**Why this priority**: Enables marketplace monetization, but depends on the marketplace catalog
(separate feature) and is the least central to the subscription revenue model.

**Independent Test**: With a premium template reference, an org admin pays with a test card; verify
a copy of the template appears in the buyer organization as a draft and the split is recorded.

**Acceptance Scenarios**:

1. **Given** a premium template, **When** an org admin pays the listed price, **Then** a draft copy is created in the buyer organization and a revenue-split record is created.

---

### User Story 5 - Reverse a purchase via refund (Priority: P3)

A platform administrator refunds a purchase (e.g., customer request, duplicate, fraud). The refund
reverses the reversible effect of the original purchase and is recorded. Tier and seat refunds
restore the previous tier/allowance. OCR and marketplace refunds reverse the payment state and
audit/revenue records without deleting already-consumed OCR work or copied templates; any follow-up
service recovery is handled operationally outside this feature.

**Why this priority**: Required for operational correctness and dispute handling, but lower volume
and platform-admin-only.

**Acceptance Scenarios**:

1. **Given** a successful tier upgrade, **When** a platform admin issues a refund, **Then** the payment is refunded, the tier is reverted to its prior value, and the reversal is recorded.
2. **Given** a successful seat purchase, **When** it is refunded, **Then** the added seats are removed and the reversal is recorded.
3. **Given** a successful OCR or marketplace purchase, **When** it is refunded, **Then** the payment and purchase status are refunded, revenue/audit records reflect the refund, and already-consumed OCR output or copied templates are not deleted automatically.

---

### Edge Cases

- **Client tampers with the price**: the amount a client sends is ignored; the charged amount is always computed by the system from the price list.
- **Payment succeeds but the user closes the browser before confirmation**: the purchase is still applied when the system next verifies the payment status (fulfillment is not dependent on the client staying on the page).
- **Duplicate confirmation / retry of the same purchase**: the effect is applied at most once.
- **Cross-organization access attempt**: an admin of one organization cannot view, pay, or fulfill another organization's purchase.
- **Non-admin attempts to purchase**: blocked.
- **Provider temporarily unavailable / rate limited**: the user sees a clear, localized "try again shortly" message and no partial effect is applied.
- **Refund of an already-refunded purchase**: rejected or no-ops without double-reversing.
- **Theme switch mid-checkout**: switching between Classic and Spark keeps the user on the billing page rather than dropping them elsewhere.
- **Missing price for a requested tier/currency**: purchase cannot be initiated and the admin is told the option is unavailable.

## Requirements *(mandatory)*

### Functional Requirements

**Purchasing**

- **FR-001**: The system MUST allow an organization administrator to initiate a purchase for one of four purposes: subscription tier upgrade, additional seats, one-time OCR batch, or premium marketplace template.
- **FR-001a**: For subscription purchases the system MUST offer only tiers *higher* than the organization's current tier; it MUST NOT provide a self-serve path to a lower tier. Lowering a tier occurs only as the reversal of a platform-admin refund (FR-015).
- **FR-002**: The system MUST compute the charge amount itself from a maintained price list and MUST NOT trust any amount supplied by the client.
- **FR-002a**: When the computed amount is 0, the system MUST bypass card collection and the payment provider entirely, fulfill the purchase immediately, record it as succeeded, and write the audit entry (preserving the same at-most-once fulfillment guarantee).
- **FR-002b**: The charge currency MUST be the organization's configured default currency; the buyer MUST NOT be able to choose it. If the price list has no entry for the requested target in that currency, the option MUST be unavailable for purchase.
- **FR-003**: The system MUST collect card details only through the payment provider's secure input, never receiving or storing raw card numbers.
- **FR-004**: The system MUST support cards that require additional bank authentication (3-D Secure) and complete the purchase after authentication succeeds.
- **FR-005**: The system MUST present clear, localized (Arabic + English) messages for declines, authentication, provider errors, and rate limiting.

**Fulfillment & integrity**

- **FR-006**: The system MUST apply the purchased change (tier set, seats added, OCR credited, template copied) only after authoritatively verifying with the payment provider that payment succeeded — never based on a client-reported status.
- **FR-007**: The system MUST apply each purchase's effect at most once, even if confirmation/verification happens multiple times.
- **FR-008**: On a successful subscription purchase, the organization's tier MUST be updated and the corresponding tier limits MUST take effect immediately.
- **FR-009**: On a successful seat purchase, the organization's effective user allowance MUST increase by the purchased quantity.
- **FR-010**: On a successful OCR batch purchase, the organization MUST be credited the purchased number of form-scan jobs.
- **FR-011**: On a successful marketplace purchase, a draft copy of the template MUST be created in the buyer organization and a publisher/FormCraft revenue-split record MUST be created.

**Security & access**

- **FR-012**: Payment provider credentials and secrets MUST never be exposed to the browser; the client MUST only ever receive a single-purchase token that cannot create new charges.
- **FR-013**: Only organization administrators MUST be able to initiate purchases; refunds MUST be restricted to platform administrators.
- **FR-014**: Purchase records MUST be isolated per organization; one organization MUST NOT be able to read or act on another organization's purchases.

**Refunds**

- **FR-015**: A platform administrator MUST be able to refund a purchase, which MUST reverse the reversible original effect (revert tier, remove purchased seats, reverse payment/revenue state for OCR and marketplace purchases) and be recorded.
- **FR-015a**: A refund reversal MUST always be applied even if the organization's current usage exceeds the reverted limit (e.g., more active users than the reverted tier allows). The reversal MUST NOT remove or deactivate existing users or data; resulting over-limit states are handled by the separate enforcement work, not by this feature.
- **FR-015b**: For OCR and marketplace refunds, the system MUST NOT automatically delete already-consumed OCR outputs or copied templates; it MUST record the full refund, mark revenue/audit state as reversed, and leave operational recovery to platform-admin follow-up.
- **FR-016**: The system MUST prevent a refund from reversing the same purchase more than once.
- **FR-016a**: Refunds MUST be full-only — a refund reverses the entire purchase. The system MUST NOT support partial or proportional refunds (e.g., refunding some but not all purchased seats).

**Auditability**

- **FR-017**: Every fulfillment and every refund MUST be recorded in the organization's audit trail with a distinct action type and the acting user.
- **FR-018**: Each purchase MUST retain its status lifecycle (created → succeeded/failed → refunded) for later inspection.

**Experience (dual theme & localization)**

- **FR-019**: The checkout experience MUST be available and visually correct in both the Classic and Spark themes, in both light and dark appearance, and in both RTL (Arabic) and LTR (English) directions.
- **FR-020**: The billing entry point MUST be reachable in both themes, and switching themes while on the billing page MUST keep the user on the billing page.
- **FR-021**: The Platform Console organization Subscription view MUST offer an action to start a tier purchase using the same checkout experience.
- **FR-022**: All user-facing text MUST be provided in both Arabic and English.

### Key Entities *(include if feature involves data)*

- **Purchase (Billing Intent)**: A single attempt to buy something. Belongs to one organization; has a purpose (subscription/seats/OCR/marketplace), a target (which tier, how many seats/forms, which template), a system-computed amount and currency, a link to the payment provider's record, a status, who created it, and when it was fulfilled. Isolated per organization.
- **Tier Price**: The price for a given tier in a given currency (and billing interval). Source of truth for subscription amounts.
- **Add-on Price**: The unit prices for seats and OCR forms; the per-template price comes from the marketplace listing.
- **Audit Record**: An immutable log entry recording each fulfillment and refund (action type, organization, actor, target, timestamp) within the existing audit trail.
- **Organization**: The paying entity whose tier, seat allowance, OCR credit, and template library are changed by fulfillment.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An organization administrator can complete a tier upgrade end-to-end (open billing → pay → see new tier active) in under 3 minutes in test mode.
- **SC-002**: 100% of successful payments result in exactly one application of the purchased change, with zero double-applications across retries and repeated verifications.
- **SC-003**: A client-supplied amount that differs from the official price is never charged; the official price is charged in 100% of cases.
- **SC-004**: Card declines and bank-authentication prompts are handled with a localized message in 100% of those cases, with no partial change applied on failure.
- **SC-005**: The checkout renders correctly across all four combinations of {Classic, Spark} × {RTL, LTR} and in both light and dark appearance, with no layout breakage.
- **SC-006**: Switching theme while on the billing page keeps the user on the billing page in 100% of attempts.
- **SC-007**: Attempts by non-administrators to purchase, and attempts to access another organization's purchases, are blocked in 100% of attempts.
- **SC-008**: Payment provider secrets never appear in any client-visible network traffic or storage (verified by inspection).
- **SC-009**: Every fulfillment and refund produces exactly one audit record with the correct action type and actor.
- **SC-010**: A platform administrator can refund a purchase and have its effect reversed, with the reversal recorded, in under 3 minutes.

## Assumptions

- The PayGateway service is already deployed, reachable, and configured with its payment provider (test and live), and a service-role API key has been issued for FormCraft's backend.
- Prices are maintained by an internal operator (no self-serve price editing UI is part of this feature); the price list is seeded for all sellable tiers and the supported currencies (EGP/SAR/AED at minimum).
- Subscription purchases in this feature are one-off "pay to change" charges; automatic recurring renewal is out of scope (see below).
- The charge currency is the organization's configured default currency (from the org record), not chosen by the buyer (see FR-002b).
- Seat and OCR allowances are tracked as additive credits on the organization; the actual *enforcement* of those limits at invite/submit time is handled by the separate enforcement work (see Dependencies).
- The marketplace listing and its pricing already exist (or will, via feature 035); this feature only adds the purchase-and-copy step.

## Dependencies

- **PayGateway service** (external, already built): payment create/confirm/status/refund.
- **Multi-tenancy / organizations & tier limits** (existing): organizations, tier limits lookup, audit trail.
- **Platform Console** (existing): the organization Subscription view that gains the upgrade action.
- **Dual-theme shell** (existing): Classic and Spark layouts, theme preference + route mapping, the localization framework, and the shared theme tokens the checkout relies on.
- **Tier/seat/submission enforcement gates** (separate revenue-track work): this feature records allowances; blocking overruns at invite/submit time is tracked separately and is a prerequisite for the allowances to have a user-visible effect.
- **Marketplace catalog** (feature 035): required for the marketplace purchase story to be reachable by users.

## Out of Scope

- Enforcement gates that block invitations or submissions when an organization exceeds its tier/seat/submission allowance (tracked in the vision doc's revenue section).
- Recurring / auto-renewing subscription billing, proration, and dunning.
- Building the marketplace premium-template catalog and listing management (feature 035); only the purchase/copy step is included here.
- Self-serve price administration UI.
- Invoicing, tax/VAT calculation, and accounting-system integration.
- Self-serve tier downgrades (tier lowering happens only via platform-admin refund/reversal).
- Partial / proportional refunds and downgrade proration or credits.

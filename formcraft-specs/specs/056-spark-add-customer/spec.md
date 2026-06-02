# Feature Specification: Spark Theme — Add Customer

**Feature Branch**: `056-spark-add-customer`  
**Created**: 2026-06-02  
**Status**: Draft  

## Clarifications

### Session 2026-06-02

- Q: How should the duplicate identifier error (HTTP 409) be displayed to the operator? → A: Inline field-level error shown directly beneath the Identifier field, matching the same visual pattern used for required-field validation errors elsewhere on the form.
- Q: What column layout should the form use for field pairs? → A: Two-column layout for pairs: Identifier Type + Identifier on one row, Phone + Email on one row. Arabic Name, English Name, and Address each occupy the full form width.
- Q: Should the Phone field enforce any format validation? → A: No phone format validation — any string is accepted, matching Classic theme behavior.

---

## Overview

Desk operators currently see a placeholder when navigating to the "Add Customer" route in the Spark theme, instructing them to switch to Classic mode to complete the action. This creates friction and breaks the Spark-native workflow. This feature delivers a fully functional Add Customer form within the Spark theme, eliminating the need to leave the new interface.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Create a New Customer (Priority: P1)

A desk operator in the Spark theme wants to register a new customer. They click "Add Customer" from the customer directory, fill in the customer's details, and save. The new customer record appears in the directory immediately.

**Why this priority**: This is the core unblocked capability. Without it, Spark-theme users must abandon the new interface every time they onboard a new customer — the primary gap this feature closes.

**Independent Test**: Navigate to `/ui/desk/customers/new`, fill in Arabic Name + Identifier Type + Identifier, click Save, and confirm the customer appears in the Customer Directory list — this alone delivers the feature's full value.

**Acceptance Scenarios**:

1. **Given** an operator is on the Spark Customer Directory, **When** they click "Add Customer", **Then** the browser navigates to `/ui/desk/customers/new` and displays the Add Customer form within the Spark layout (no placeholder, no redirect to Classic).
2. **Given** the form is displayed, **When** the operator fills in Arabic Name, selects an Identifier Type, and enters an Identifier then clicks Save, **Then** the customer record is created and the operator is redirected to the customer's detail page.
3. **Given** the form is displayed, **When** the operator clicks Cancel, **Then** they are returned to the Customer Directory without creating any record.
4. **Given** the form is displayed with no data entered, **When** the operator clicks Save, **Then** validation errors are shown inline for the required fields (Arabic Name, Identifier Type, Identifier) and the form is not submitted.

---

### User Story 2 — Duplicate Customer Detection (Priority: P2)

An operator attempts to add a customer whose identifier (e.g., National ID) already exists in the system. Rather than silently failing or creating a duplicate, the form clearly informs the operator that a customer with this identifier already exists.

**Why this priority**: Duplicate records corrupt the customer directory and cause downstream issues (wrong form pre-fill, merged confusion). Detection at creation time is cheaper than deduplication later.

**Independent Test**: Attempt to save a customer with an identifier that already exists in the system and confirm a clear, actionable error message is shown without leaving the form.

**Acceptance Scenarios**:

1. **Given** a customer with identifier "12345678" already exists, **When** the operator submits the form with the same identifier, **Then** an error message is shown indicating a duplicate was found, and the form remains open with all entered data preserved.

---

### User Story 3 — Optional Fields Flexibility (Priority: P3)

An operator wants to register a customer with only the minimum required data (Arabic Name, Identifier Type, Identifier) and skip optional fields (English Name, Phone, Email, Address) for now, with the ability to fill them in later on the customer detail page.

**Why this priority**: Forced-complete forms slow down intake. Operators often onboard customers at the counter with limited information at hand.

**Independent Test**: Submit the form with only the three required fields populated and verify the customer is created successfully without validation errors on optional fields.

**Acceptance Scenarios**:

1. **Given** only Arabic Name, Identifier Type, and Identifier are filled, **When** the operator clicks Save, **Then** the customer is created successfully with null/empty values for Phone, Email, English Name, and Address.
2. **Given** all seven fields are filled, **When** the operator clicks Save, **Then** all values (including optional ones) are persisted correctly.

---

### Edge Cases

- What happens when the Arabic Name contains only whitespace? The form should treat it as empty and show a required-field validation error.
- What happens when the Email field contains a syntactically invalid email? The form should show an inline format validation error before submission.
- What happens when the network is unavailable during Save? The operator sees an error message and the form data is preserved so they can retry.
- What happens when the operator navigates away mid-form (e.g., browser back)? Standard browser/router navigation occurs with no special unsaved-changes prompt (acceptable for v1).
- What happens if the Identifier Type dropdown has no selection? The form should treat it as empty and show a required-field error.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The Spark theme MUST render a native Add Customer form at the `/ui/desk/customers/new` route, replacing the current `SparkFeatureBridgeComponent` placeholder entirely.
- **FR-002**: The form MUST include the following fields matching the Classic implementation: Arabic Name (required, full-width), English Name (optional, full-width), Identifier Type (required, dropdown, half-width paired with Identifier), Identifier (required, half-width paired with Identifier Type), Phone (optional, half-width paired with Email), Email (optional, half-width paired with Phone), Address (optional, multi-line text, full-width). Phone accepts any string without format validation.
- **FR-003**: The Identifier Type dropdown MUST default to "National ID" and offer the same options as the Classic theme: National ID, Iqama, Commercial Register, Passport, Other.
- **FR-004**: The form MUST prevent submission and show inline validation errors when any required field (Arabic Name, Identifier Type, Identifier) is empty or whitespace-only.
- **FR-005**: The form MUST call the existing customer creation API using the same `CustomerService` already used in the Classic theme.
- **FR-006**: On successful save, the system MUST redirect the operator to the new customer's detail page.
- **FR-007**: On duplicate identifier (HTTP 409), the form MUST display an inline error message directly beneath the Identifier field and keep the form open with all entered data intact.
- **FR-008**: The Cancel button MUST navigate back to the Customer Directory without creating any record.
- **FR-009**: The form MUST display a loading/saving state during the API call to prevent double-submission.
- **FR-010**: The form MUST be rendered within the Spark layout shell (header, sidebar) consistent with all other Spark pages.
- **FR-011**: The form MUST support both Arabic and English interface languages using the existing ngx-translate i18n infrastructure.

### Key Entities

- **Customer**: The customer record being created. Required attributes: `name_ar`, `identifier_type`, `identifier`. Optional: `name_en`, `contact_phone`, `contact_email`, `address`.
- **Identifier Type**: An enumerated type (National ID, Iqama, Commercial Register, Passport, Other) that classifies the customer's identifier document.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A desk operator can complete the Add Customer flow (open form → fill required fields → save → land on customer detail) in under 60 seconds.
- **SC-002**: 100% of customers created via the Spark Add Customer form appear correctly in the Customer Directory immediately after creation.
- **SC-003**: Zero customers can be submitted with empty required fields — all required-field validation prevents submission before any network call is made.
- **SC-004**: Duplicate identifier attempts are caught and communicated to the operator without data loss (form retains all entered values on error).
- **SC-005**: The Add Customer page is no longer reachable via the `SparkFeatureBridgeComponent` placeholder — the route renders the native Spark form in all supported roles (admin, branch_manager, operator).

---

## Assumptions

- The `CustomerService` (including `create()`, observable error handling, and HTTP 409 duplicate detection) is already implemented and stable — no backend changes are needed.
- After successful creation, the redirect target is the customer detail page (Classic route `/desk/customers/:id`) until a Spark-native customer detail page exists; this follows the same pattern used for other customer detail links in the Spark theme.
- No unsaved-changes confirmation dialog is required for v1 (parity with Classic behavior).
- The form does not need to support custom fields in v1; the `custom_fields` payload will be sent as an empty object `{}`.
- Role-based access control (admin, branch_manager, operator) is handled by the existing `RoleGuard` on the route and requires no changes.

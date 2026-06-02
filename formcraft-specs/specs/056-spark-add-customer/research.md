# Research: Spark Theme — Add Customer (F056)

**Date**: 2026-06-02 | **Branch**: `056-spark-add-customer`

## Decision Log

### D-001: Component Architecture

**Decision**: Single new standalone Angular component `AddCustomerComponent` in `ui-redesign/desk/`.  
**Rationale**: All Spark desk pages follow this exact pattern (`CustomersComponent`, `DashboardComponent`, `FormFillerComponent`). A single component with Reactive Forms keeps the footprint minimal and testable.  
**Alternatives considered**: Shared/reused Classic `CustomerDetailComponent` — rejected because Classic component uses `ActivatedRoute` to detect `new` vs `edit` mode, imports MatCard/MatChips not used in Spark, and would couple the two themes.

### D-002: Form Management Strategy

**Decision**: Angular Reactive Forms (`FormGroup` / `FormControl`) with synchronous validators.  
**Rationale**: Reactive Forms offer testable validator composition, easy programmatic error-state access (needed for the inline duplicate error on Identifier field), and clear disabled-state management during the saving phase. Template-driven forms would make duplicate-error injection awkward.  
**Alternatives considered**: Template-driven (NgModel) — rejected because injecting server-side error state onto a specific control is cleaner with Reactive Forms.

### D-003: Duplicate Error Display

**Decision**: Inject a custom error key (`'duplicate'`) onto the `FormControl` for `identifier` after receiving HTTP 409, display via `mat-error` beneath the field — same visual pattern as built-in validators.  
**Rationale**: Keeps error display entirely within the Angular Material form field, consistent with required-field errors. No additional banner component needed.  
**Alternatives considered**: Snackbar toast — rejected (less discoverable, auto-dismisses); top-of-form banner — rejected (breaks visual proximity principle).

### D-004: Layout Strategy

**Decision**: CSS Grid two-column layout for field pairs (Identifier Type + Identifier, Phone + Email); single-column full-width for Arabic Name, English Name, Address.  
**Rationale**: Matches the Classic theme's visual layout (confirmed by screenshot). CSS Grid is already used elsewhere in Spark theme SCSS. No Angular Material Grid dependency needed.  
**Alternatives considered**: Angular Material `mat-grid-list` — rejected (overkill for a simple form); flexbox row wrapping — rejected (harder to control pair sizing precisely with Angular Material form fields).

### D-005: Post-Save Redirect

**Decision**: Redirect to Classic customer detail page `/desk/customers/:id` after successful creation.  
**Rationale**: Spark-native customer detail page (`/ui/desk/customers/:id`) does not yet exist. This follows the established `ClassicRedirectComponent` pattern for unimplemented Spark pages — the operator still lands on the correct customer record.  
**Alternatives considered**: Redirect to Spark Customer Directory — considered but rejected because the operator expects to immediately see the created record's full detail after save, not the list.

### D-006: i18n Key Namespace

**Decision**: Use the namespace `add_customer.*` for all new keys (e.g., `add_customer.title`, `add_customer.field_name_ar`, `add_customer.error_duplicate`).  
**Rationale**: Existing customer-related keys use `customers.*` for list-view strings. A dedicated `add_customer.*` namespace avoids key collision and is unambiguous.

### D-007: Loading/Saving State

**Decision**: Disable the Save button and show a `mat-spinner` (inline, small) inside it during the API call. All form controls remain enabled (readable) during save.  
**Rationale**: Least disruptive — operator can still read their input. Prevents double-submission without locking the whole form. Consistent with how other Spark pages handle async operations.

### D-008: RTL Compliance

**Decision**: Apply `dir="auto"` to Arabic Name and Address `<input>`/`<textarea>` elements. English Name, Phone, Email, Identifier are LTR-only fields (dir="ltr"). The overall form container inherits RTL/LTR from the Spark layout shell.  
**Rationale**: Constitution I requires correct mixed-direction rendering. `dir="auto"` on Arabic-content fields lets the browser detect script direction. Fixed `dir="ltr"` on numeric/identifier fields prevents right-alignment of latin strings in RTL mode.

### D-009: Phone Validation

**Decision**: No phone format validation — any string accepted.  
**Rationale**: Classic theme applies no phone validation. The `CustomerCreate` interface types `contact_phone` as `string | undefined`. Adding a constraint not present in Classic would break parity without a business requirement.

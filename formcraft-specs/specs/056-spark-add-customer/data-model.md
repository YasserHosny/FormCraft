# Data Model: Spark Theme — Add Customer (F056)

**Date**: 2026-06-02 | **Branch**: `056-spark-add-customer`

## Entities Used

No new entities or database tables are introduced by this feature. The feature writes to the existing `Customer` entity via the existing `CustomerService`.

---

## Customer (existing)

**Source**: `formcraft-frontend/src/app/features/desk/customers/customer.models.ts`

| Field | Type | Required | Validation | Notes |
|-------|------|----------|-----------|-------|
| `name_ar` | `string` | Yes | Non-empty, non-whitespace | Arabic Name field; `dir="auto"` |
| `name_en` | `string \| undefined` | No | None | English Name field; `dir="ltr"` |
| `identifier_type` | `string` | Yes | One of enum values | Dropdown; default `national_id` |
| `identifier` | `string` | Yes | Non-empty | Identifier field; duplicate check via HTTP 409 |
| `contact_phone` | `string \| undefined` | No | None (any string) | Phone field |
| `contact_email` | `string \| undefined` | No | RFC 5322 format if provided | Email field |
| `address` | `string \| undefined` | No | None | Multi-line textarea; `dir="auto"` |
| `custom_fields` | `Record<string, any>` | No | N/A | Sent as `{}` (v1 deferral) |

---

## Identifier Type Enum

| Value | Display Label (EN) | Display Label (AR) |
|-------|-------------------|-------------------|
| `national_id` | National ID | الهوية الوطنية |
| `iqama` | Iqama | الإقامة |
| `commercial_register` | Commercial Register | السجل التجاري |
| `passport` | Passport | جواز السفر |
| `other` | Other | أخرى |

---

## Form State Machine

```
IDLE
  → (user types) → DIRTY
  → (user clicks Save with invalid fields) → INVALID (validation errors shown)
  → (user clicks Save with valid fields) → SAVING (button disabled, spinner shown)
    → (API success) → navigate to /desk/customers/:id
    → (API 409) → DUPLICATE_ERROR (inline error on identifier field, form re-editable)
    → (API other error) → ERROR (snackbar notification, form re-editable)
  → (user clicks Cancel at any state) → navigate to /ui/desk/customers
```

---

## Reactive Form Structure

```typescript
FormGroup {
  name_ar: FormControl<string>     // Validators: required, notWhitespace
  name_en: FormControl<string>     // Validators: none
  identifier_type: FormControl<string> // Validators: required; default: 'national_id'
  identifier: FormControl<string>  // Validators: required; custom error key 'duplicate' injected on 409
  contact_phone: FormControl<string>   // Validators: none
  contact_email: FormControl<string>   // Validators: email (Angular built-in, optional)
  address: FormControl<string>     // Validators: none
}
```

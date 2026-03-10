# Feature Specification: Arabic-Specific Validation Library

**Feature Branch**: `07-arabic-validators`
**Created**: 2026-02-21
**Status**: Draft
**Input**: FormCraft PRD Phase 5 – Arabic-Specific Validation Library

## User Scenarios & Testing

### User Story 1 - Egyptian Document Validation (Priority: P1)

The system provides deterministic validators for Egyptian documents: National ID (14 digits with checksum semantics), IBAN (EG + 27 characters), and phone numbers (+20 prefix with 10 digits).

**Why this priority**: Egypt is a primary target market. These validators override AI suggestions per Constitution Principle IV.

**Independent Test**: Can be tested by passing valid and invalid Egyptian document numbers to each validator and verifying pass/fail results.

**Acceptance Scenarios**:

1. **Given** an Egyptian National ID "29901011234567", **When** validated, **Then** the validator returns valid (14 digits, starts with 2 or 3).
2. **Given** an Egyptian National ID "1234", **When** validated, **Then** the validator returns invalid with error "National ID must be exactly 14 digits".
3. **Given** an Egyptian IBAN "EG380019000500000000263180002", **When** validated, **Then** the validator returns valid (starts with EG, correct length).
4. **Given** an Egyptian phone "+201012345678", **When** validated, **Then** the validator returns valid (+20 prefix, 10 digits after prefix).
5. **Given** an Egyptian phone "01012345678", **When** validated, **Then** the validator returns valid (local format accepted, normalized to +20).

---

### User Story 2 - Saudi Document Validation (Priority: P1)

The system provides deterministic validators for Saudi documents: National ID / Iqama (10 digits, starts with 1 or 2), IBAN (SA + 22 alphanumeric), and VAT number (15 digits starting with 3 and ending with 3).

**Why this priority**: Saudi Arabia is a primary target market.

**Independent Test**: Can be tested by passing valid and invalid Saudi document numbers.

**Acceptance Scenarios**:

1. **Given** a Saudi National ID "1234567890", **When** validated, **Then** the validator returns valid (10 digits, starts with 1).
2. **Given** a Saudi Iqama "2123456789", **When** validated, **Then** the validator returns valid (10 digits, starts with 2).
3. **Given** a Saudi National ID "3123456789", **When** validated, **Then** the validator returns invalid (must start with 1 or 2).
4. **Given** a Saudi IBAN "SA0380000000608010167519", **When** validated, **Then** the validator returns valid (SA + 22 characters).
5. **Given** a Saudi VAT "300012345600003", **When** validated, **Then** the validator returns valid (15 digits, starts with 3, ends with 3).
6. **Given** a Saudi VAT "400012345600003", **When** validated, **Then** the validator returns invalid (must start with 3).

---

### User Story 3 - UAE Document Validation (Priority: P1)

The system provides deterministic validators for UAE documents: IBAN (AE + 21 characters) and TRN (Tax Registration Number, 15 digits).

**Why this priority**: UAE is a primary target market.

**Independent Test**: Can be tested by passing valid and invalid UAE document numbers.

**Acceptance Scenarios**:

1. **Given** a UAE IBAN "AE070331234567890123456", **When** validated, **Then** the validator returns valid (AE + 21 characters).
2. **Given** a UAE IBAN "AE123", **When** validated, **Then** the validator returns invalid (incorrect length).
3. **Given** a UAE TRN "100234567890003", **When** validated, **Then** the validator returns valid (15 digits).
4. **Given** a UAE TRN "12345", **When** validated, **Then** the validator returns invalid (must be 15 digits).

---

### User Story 4 - Validator Integration with AI Suggestion (Priority: P1)

When the AI suggestion endpoint processes a field label, it first checks if the label matches a known document type for the given country. If a deterministic validator matches, the response uses the validator's rules instead of the LLM output, with confidence set to 1.0.

**Why this priority**: This is the integration point between specs 05 and 07, ensuring deterministic rules always win.

**Independent Test**: Can be tested by calling the AI suggestion endpoint with known document labels and verifying deterministic rules are returned.

**Acceptance Scenarios**:

1. **Given** label "رقم الهوية الوطنية" with country "EG", **When** the suggestion endpoint responds, **Then** controlType is "national_id", confidence is 1.0, and validation.regex matches the 14-digit Egyptian ID pattern.
2. **Given** label "IBAN" with country "SA", **When** the suggestion endpoint responds, **Then** the validation uses the SA IBAN pattern regardless of what the LLM would return.
3. **Given** label "رقم التسجيل الضريبي" with country "AE", **When** the suggestion responds, **Then** it returns TRN validation (15 digits).

---

### Edge Cases

- What happens when the country is not EG, SA, or AE? → No deterministic validators apply; AI suggestion is used as-is.
- What happens when a field matches multiple validators (e.g., "رقم" could be ID or phone)? → Match by most specific label pattern; if ambiguous, use AI suggestion.
- What happens with non-standard formatting (spaces, dashes in IDs)? → Validators strip non-alphanumeric characters before validation.
- What happens when an IBAN has correct prefix but wrong checksum? → Phase 1 validates format only (prefix + length). Checksum validation is deferred to Phase 2.

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide a `ValidatorRegistry` that maps (country, field_type) → Validator.
- **FR-002**: Egyptian National ID validator: exactly 14 digits, first digit is 2 or 3.
- **FR-003**: Egyptian IBAN validator: starts with "EG", total length 29 characters.
- **FR-004**: Egyptian phone validator: +20 prefix, 10 digits after country code. Accepts local format (0xx) and normalizes.
- **FR-005**: Saudi National ID validator: exactly 10 digits, first digit is 1 (citizen) or 2 (iqama).
- **FR-006**: Saudi IBAN validator: starts with "SA", total length 24 characters.
- **FR-007**: Saudi VAT validator: exactly 15 digits, starts with 3, ends with 3.
- **FR-008**: UAE IBAN validator: starts with "AE", total length 23 characters.
- **FR-009**: UAE TRN validator: exactly 15 digits.
- **FR-010**: All validators MUST strip whitespace, dashes, and spaces before validation.
- **FR-011**: All validators MUST return a structured result: `{ valid: bool, error: str | None, normalized: str }`.
- **FR-012**: ValidatorRegistry MUST be checked in the AI suggestion pipeline before returning LLM results.
- **FR-013**: Deterministic matches MUST set confidence to 1.0 in the suggestion response.
- **FR-014**: Each validator MUST expose a `regex` property that can be included in the suggestion response for frontend validation.
- **FR-015**: Validators MUST be stateless pure functions with no external dependencies.

### Label Matching Patterns

| Country | Field Type | Arabic Label Patterns | English Label Patterns |
|---------|-----------|----------------------|----------------------|
| EG | national_id | رقم الهوية, الرقم القومي, رقم البطاقة | National ID, ID Number |
| EG | iban | IBAN, رقم الحساب الدولي | IBAN |
| EG | phone | رقم الهاتف, رقم الموبايل, الهاتف | Phone, Mobile |
| SA | national_id | رقم الهوية, رقم الإقامة, الهوية الوطنية | National ID, Iqama |
| SA | iban | IBAN, رقم الحساب الدولي, آيبان | IBAN |
| SA | vat_number | الرقم الضريبي, رقم ضريبة القيمة المضافة | VAT Number, Tax Number |
| AE | iban | IBAN, رقم الحساب الدولي | IBAN |
| AE | vat_number | رقم التسجيل الضريبي, TRN | TRN, Tax Registration |

### Key Entities

- **Validator**: Pure function `validate(value: str) → ValidationResult`.
- **ValidatorRegistry**: Maps (country, field_type) → Validator. Also maps label patterns → (country, field_type).
- **ValidationResult**: `{ valid: bool, error: str | None, normalized: str }`.
- **LabelMatcher**: Fuzzy matching of field labels to known document types using pattern matching (not ML).

## Success Criteria

### Measurable Outcomes

- **SC-001**: All validators correctly identify valid documents (100% true positive rate on test corpus).
- **SC-002**: All validators correctly reject invalid documents (100% true negative rate on test corpus).
- **SC-003**: Validator execution completes within 1ms per field (pure computation, no I/O).
- **SC-004**: Label matching correctly maps known Arabic labels to document types with ≥95% accuracy.
- **SC-005**: Deterministic override is triggered for all known document fields when the correct country is specified.

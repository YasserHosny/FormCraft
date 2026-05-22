# Feature Specification: Advanced Form Validation & Conditional Logic

**Feature Branch**: `021-advanced-form-validation`  
**Created**: 2026-05-17  
**Status**: Draft  
**Input**: DS-13 — Conditional Visibility, Dynamic Defaults & Computed Values; Roadmap 1.10

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Conditional Element Visibility (Priority: P1)

A designer configures a form element to be visible only when a condition is met (e.g., "Show spouse name field only when marital_status = 'married'"). During form filling, the element appears/disappears dynamically as the operator changes values. Hidden elements are excluded from validation and their values are not included in the final submission.

**Why this priority**: Most government/banking forms have conditional sections (e.g., guarantor info only if loan > 50K, spouse details only if married). Without conditional visibility, designers must create multiple template variants or rely on instructions operators ignore.

**Independent Test**: Create template with dropdown "marital_status" (single/married) + text "spouse_name" with visible_when: {field: "marital_status", operator: "equals", value: "married"} → open Form Desk → verify spouse_name hidden initially → select "married" → verify spouse_name appears → select "single" → verify spouse_name hidden again → submit → verify spouse_name not in submission data.

**Acceptance Scenarios**:

1. **Given** a designer opens element properties, **When** they click "Add Visibility Condition", **Then** a condition builder appears with: source field (dropdown of other elements), operator (equals, not_equals, contains, greater_than, less_than, is_empty, is_not_empty), and value input
2. **Given** a visibility condition is set, **When** the form renders in Form Desk, **Then** the element is hidden by default unless the condition is met
3. **Given** an operator changes a field that triggers a visibility condition, **When** the dependent field becomes visible, **Then** it smoothly appears (CSS transition) and is now included in validation
4. **Given** a hidden field has a value from a previous state, **When** the form is submitted, **Then** the hidden field's value is NOT included in the submission data
5. **Given** multiple conditions on one element (AND logic), **When** ALL conditions are true, **Then** the element is visible; if any is false, the element is hidden

---

### User Story 2 - Conditional Required Validation (Priority: P1)

A designer configures an element to be required only when a condition is met (e.g., "Guarantor phone is required only when loan_amount > 50000"). This allows fields to be optional in some scenarios and mandatory in others.

**Why this priority**: Fixed required/optional status forces designers to either make fields always required (frustrating for simple cases) or always optional (risking incomplete data in complex cases). Conditional required solves both.

**Independent Test**: Create template with number "loan_amount" + text "guarantor_phone" with required_when: {field: "loan_amount", operator: "greater_than", value: 50000} → fill loan_amount=30000 → submit without guarantor_phone → succeeds → change loan_amount=60000 → submit without guarantor_phone → fails with "required" error.

**Acceptance Scenarios**:

1. **Given** a designer opens element properties, **When** they configure "Required When" condition, **Then** the condition builder works identically to visibility conditions
2. **Given** a field with required_when condition, **When** the condition evaluates to true, **Then** the field shows a required asterisk and validation enforces non-empty
3. **Given** the triggering field value changes to make required_when false, **When** the element updates, **Then** the required asterisk disappears and the field is valid even if empty
4. **Given** a field is both conditionally visible AND conditionally required, **When** the field is hidden (invisible), **Then** the required condition is irrelevant — hidden fields are never validated

---

### User Story 3 - Computed Values (Priority: P2)

A designer configures an element to auto-compute its value from other fields using a formula (e.g., "total = subtotal * (1 + tax_rate / 100)"). Computed fields are read-only in Form Desk and update live as source fields change.

**Why this priority**: Financial forms require calculated fields (tax amounts, totals, net values). Without computed values, operators must calculate manually — prone to errors and slow.

**Independent Test**: Create template with number "subtotal" + number "tax_rate" + number "total" with computed_value: "subtotal * (1 + tax_rate / 100)" → fill subtotal=1000, tax_rate=14 → verify total auto-computes to 1140 → change subtotal=2000 → verify total updates to 2280.

**Acceptance Scenarios**:

1. **Given** a designer configures a computed_value expression, **When** the expression references other element keys, **Then** the system validates that referenced elements exist on the same template
2. **Given** a computed field is rendered in Form Desk, **When** it appears, **Then** it is read-only with a "calculated" indicator and its value is auto-populated
3. **Given** a source field changes, **When** the computed expression re-evaluates, **Then** the computed field updates within 100ms (perceived instant)
4. **Given** a computed expression references a field that is currently hidden, **When** the hidden field has no value, **Then** the computed field treats it as 0 (for numbers) or empty string (for text)

---

### User Story 4 - Default Values & Placeholders (Priority: P2)

A designer configures default values (pre-populated when form loads) and placeholder text (shown when field is empty) per element. Defaults can be static or dynamic (e.g., "today's date", "current user name").

**Why this priority**: Reduces repetitive typing for operators. Common defaults (today's date, branch name, officer name) save 5-10 seconds per form × hundreds of forms daily.

**Independent Test**: Create template with date "application_date" default_value: "{{today}}" + text "officer" placeholder: "Enter officer name" → open Form Desk → verify date pre-filled with today → verify officer shows placeholder → fill officer → verify placeholder disappears.

**Acceptance Scenarios**:

1. **Given** a designer sets default_value to "{{today}}", **When** the form loads in Form Desk, **Then** the date field is pre-populated with today's date (local timezone)
2. **Given** a designer sets default_value to a static value "Egypt", **When** the form loads, **Then** the field shows "Egypt" as its initial value
3. **Given** a designer sets placeholder_text, **When** the field is empty, **Then** the placeholder is shown in grey; when the operator types, the placeholder disappears
4. **Given** the operator clears a field that had a default, **When** submitting, **Then** the empty value is stored (default is not re-applied on submit)

---

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Designer can set visible_when condition on any element (condition builder UI) | P1 |
| FR-02 | Visibility condition supports operators: equals, not_equals, contains, greater_than, less_than, is_empty, is_not_empty | P1 |
| FR-03 | Multiple conditions on one element use AND logic | P1 |
| FR-04 | Hidden elements excluded from validation and submission data | P1 |
| FR-05 | Designer can set required_when condition on any element | P1 |
| FR-06 | Required_when dynamically toggles the required asterisk and validation in Form Desk | P1 |
| FR-07 | Designer can set computed_value expression on numeric/text elements | P2 |
| FR-08 | Computed fields are read-only in Form Desk and update live | P2 |
| FR-09 | Computed expression supports: +, -, *, /, (), field references by key | P2 |
| FR-10 | Designer can set default_value (static or dynamic: {{today}}, {{user_name}}) | P2 |
| FR-11 | Designer can set placeholder_text (ar/en) on text-like elements | P2 |
| FR-12 | ConditionEngine evaluates all conditions on form value changes (reactive) | P1 |
| FR-13 | Circular dependency detection at design time (prevent infinite loops) | P1 |

## Non-Functional Requirements

| ID | Requirement | Metric |
|----|-------------|--------|
| NFR-01 | Condition evaluation completes within 50ms for forms with up to 100 elements | < 50ms per evaluation cycle |
| NFR-02 | Computed value updates perceived as instant (< 100ms) | < 100ms feedback |
| NFR-03 | Dependency graph built once on form load, not reconstructed per change | O(1) lookup per field change |
| NFR-04 | Form remains responsive during complex condition cascades (chained dependencies) | No UI freeze > 16ms |

## Edge Cases

| # | Case | Handling |
|---|------|----------|
| 1 | Circular dependency: A visible when B, B visible when A | Detected at design time; designer shown error "Circular dependency detected between A and B" |
| 2 | Computed value divides by zero | Result set to 0; show "Cannot compute" indicator |
| 3 | Cascading visibility: A shows B, B shows C — A hidden | B and C both hidden (cascade evaluation) |
| 4 | Draft save includes hidden field values | Yes — drafts save ALL values including hidden; only final submission strips hidden values |
| 5 | Operator manually edits computed field | Not possible — computed fields are read-only in Form Desk |
| 6 | Default value {{today}} — which timezone? | Server returns UTC; frontend converts to user's local timezone for display |
| 7 | Condition references a field on a different page | Supported — ConditionEngine evaluates across all pages in the template |

## Success Criteria

- Designer can configure visibility/required conditions in under 30 seconds per field
- Form with 10 conditional fields evaluates all conditions without perceptible delay
- Computed fields calculate correctly for all basic arithmetic operations
- Circular dependencies are caught 100% of the time at design time
- Draft saves preserve all values; final submission correctly excludes hidden values

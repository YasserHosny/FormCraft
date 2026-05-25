# Feature Specification: Form Desk Search & Quick Fill

**Feature Branch**: `037-desk-search-quickfill`  
**Created**: 2026-05-25  
**Status**: Draft  
**Vision Reference**: FD-07

## User Scenarios & Testing

### User Story 1 - Global Search Bar (Priority: P1)

As an operator, I need a global search bar at the top of the Form Desk that can search across templates, submissions (by reference number), and customers (by name) with instant filtered results, so I can quickly find what I need without navigating through multiple pages.

**Why this priority**: Speed is the primary operator concern — a unified search eliminates the need to know which page holds what data.

**Independent Test**: Type a template name in the search bar, see instant results; type a reference number, jump to submission detail; type a customer name, see customer's recent forms.

**Acceptance Scenarios**:

1. **Given** operator focuses the global search bar, **When** they type a template name, **Then** matching published templates appear as selectable results within 300ms.
2. **Given** operator types a submission reference number (e.g., "FC-2026-05-0042"), **When** a match is found, **Then** clicking the result navigates directly to the submission detail view.
3. **Given** customer profiles are enabled and operator types a customer name, **When** matches are found, **Then** customer results show with their recent form activity count.
4. **Given** operator types a query that matches multiple types (template + customer), **When** results display, **Then** they are grouped by type with clear section headers: "Templates", "Submissions", "Customers".

---

### User Story 2 - Quick Fill Mode (Priority: P2)

As an operator, I need to select a template and optionally a customer profile to enter Quick Fill mode where the customer's known data is auto-populated into matching fields, so I can fill forms for repeat customers in seconds instead of minutes.

**Why this priority**: Core productivity feature — repeat customer scenarios (bank tellers, government counters) represent 60%+ of daily form filling.

**Independent Test**: Select a template, select a customer, form opens with customer data pre-filled in matching fields, fill remaining fields, print.

**Acceptance Scenarios**:

1. **Given** operator selects a template from search or dashboard, **When** they click "Quick Fill", **Then** a customer search dialog appears with a search bar.
2. **Given** operator selects a customer from the dialog, **When** the form loads, **Then** all matching fields are auto-populated: name from customer.name_ar/name_en, ID from customer.identifier, phone from customer.contact_phone, address from customer.address.
3. **Given** auto-populated fields are displayed, **When** the operator reviews them, **Then** auto-filled fields are visually distinguished (e.g., light blue background) and editable.
4. **Given** operator finishes filling remaining fields, **When** they print the form, **Then** the submission is linked to the customer profile for history tracking.

---

### Edge Cases

- What happens when a customer profile has fields that don't match any template field?
- How does the search handle Arabic and English text simultaneously (mixed-script queries)?
- What happens when the operator modifies auto-populated data — does it update the customer profile?
- How does search ranking work when a query matches both a template name and a customer name?

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide a global search bar on the Form Desk that searches across templates, submissions, and customers.
- **FR-002**: Search results MUST appear within 300ms of typing (debounced at 200ms).
- **FR-003**: Results MUST be grouped by type (Templates, Submissions, Customers) with clear section headers.
- **FR-004**: Submission search by reference number MUST navigate directly to the submission detail.
- **FR-005**: System MUST support a Quick Fill mode that auto-populates customer data into matching template fields.
- **FR-006**: Auto-populated fields MUST be visually distinguished and remain editable.
- **FR-007**: Submissions created via Quick Fill MUST be linked to the customer profile.
- **FR-008**: Search MUST handle mixed Arabic/English queries correctly.
- **FR-009**: Customer search in Quick Fill dialog MUST search across name_ar, name_en, identifier, and contact_phone.

### Key Entities

- **Search Index**: Unified search across templates (name, description, tags), submissions (reference number, field values), and customers (name, identifier, contact).
- **Quick Fill Mapping**: Automatic field-to-customer-attribute mapping based on field key conventions (e.g., field key "national_id" maps to customer.identifier).

## Success Criteria

### Measurable Outcomes

- **SC-001**: Global search returns results within 300ms for 95% of queries.
- **SC-002**: Quick Fill reduces form completion time by 50%+ for repeat customers.
- **SC-003**: Auto-populated fields have 95%+ accuracy in field-to-customer mapping.
- **SC-004**: Operators can find any submission by reference number in under 5 seconds.
- **SC-005**: Search handles 50 concurrent operator queries without degradation.

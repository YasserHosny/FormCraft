# Feature Specification: Customer Profiles & Auto-Populate

**Feature Branch**: `030-customer-profiles`
**Created**: 2026-05-25
**Status**: Draft
**Input**: User description: "Customer Profiles & Auto-Populate — Operator address book of known customers/entities with auto-populate into form fields during filling. Covers customer CRUD, search, auto-populate during form filling, customer form history, and admin merge/delete. Includes privacy controls and audit logging for customer data access. Based on FD-08 from the system vision."

---

## Clarifications

### Session 2026-05-25

- Q: How are template fields mapped to customer profile fields for auto-populate? → A: Convention with designer override — default key-name matching (e.g., field key `national_id` auto-maps to customer identifier) plus a per-template mapping configuration panel where designers can explicitly map any element to any customer field.
- Q: How do admins define the custom field schema for customer profiles? → A: Admin schema builder in org settings — admin adds/removes custom fields with name, type (text, number, date, dropdown), and required flag. All customers in the org share the same schema. Consistent with the reference data list schema pattern (F24).

---

## User Scenarios & Testing

### User Story 1 — Customer CRUD & Search (Priority: P1)

Operators need a centralized customer directory to avoid re-entering the same customer data across multiple form submissions. An operator navigates to the customer profiles section, creates a new customer record with identifying information (name in Arabic and English, national ID or commercial register, phone, email, address), and saves it. Later, the operator searches for the customer by name or identifier and finds the record instantly. The operator can also edit existing customer details when information changes.

**Why this priority**: Without the ability to create and find customer records, no other customer-related feature (auto-populate, history) can function. This is the foundational data layer.

**Independent Test**: Create a customer profile with full details, search for it by name and by identifier, edit a field, verify the update persists.

**Acceptance Scenarios**:

1. **Given** an authenticated operator, **When** they navigate to the customer profiles section and fill in customer details (name_ar, name_en, identifier, identifier_type, phone), **Then** a new customer record is created and visible in the customer list.
2. **Given** an existing customer "Ahmed Hassan" with national ID "29001011234567", **When** the operator types "Ahmed" in the search bar, **Then** the customer appears in filtered results within 1 second.
3. **Given** an existing customer "Ahmed Hassan", **When** the operator searches by national ID "29001011234567", **Then** the customer appears in filtered results.
4. **Given** an existing customer record, **When** the operator edits the phone number and saves, **Then** the updated phone number is shown on the customer detail view.
5. **Given** a customer list with 500+ records, **When** the operator opens the customer profiles page, **Then** the list loads with pagination (25 per page) within 1 second.

---

### User Story 2 — Auto-Populate During Form Filling (Priority: P1)

When filling a form in Form Desk, operators frequently enter the same customer's details (name, ID, phone, address) across different form types. Auto-populate lets the operator select an existing customer and have all matching fields pre-filled automatically. The operator clicks "Select Customer" in the form filler toolbar, searches for or picks a customer, and all template fields whose keys match customer profile fields are populated. The operator can override any auto-filled value before submission.

**Why this priority**: This is the primary value proposition — reducing form fill time from minutes to seconds for repeat customers. Without auto-populate, customer profiles are just an address book with limited operational value.

**Independent Test**: Create a customer with full details, open a published template in Form Desk, click "Select Customer", pick the customer, verify matching fields are pre-filled, override one field, submit the form successfully.

**Acceptance Scenarios**:

1. **Given** a customer "Ahmed Hassan" with name_ar, national ID, and phone, **When** the operator selects this customer while filling a template that has name, national_id, and phone fields, **Then** all three fields are pre-filled with the customer's data.
2. **Given** an auto-populated form, **When** the operator edits the phone number field to a different value, **Then** the form accepts the overridden value and submits successfully.
3. **Given** a template with fields that do not match any customer profile fields, **When** the operator selects a customer, **Then** no fields are populated, and the operator sees a message indicating no matching fields were found.
4. **Given** the operator is in the form filler, **When** they click "Select Customer", **Then** a searchable dialog appears with recently used customers at the top and a search input for finding others.
5. **Given** an auto-populated form, **When** the operator clears the customer selection, **Then** all auto-populated fields are reset to empty (unless the operator has manually edited them).

---

### User Story 3 — Customer Form History (Priority: P2)

Admins and operators need to see all forms ever filled for a specific customer — across all template types — to support customer service, compliance review, and relationship management. From a customer's profile page, the user sees a cross-template submission history showing every form submitted with that customer's data.

**Why this priority**: Provides significant operational value for customer service scenarios ("show me everything we've done for this customer") but is not required for the core fill-and-print workflow.

**Independent Test**: Create a customer, submit 3 different forms with that customer selected, navigate to the customer's profile, verify all 3 submissions appear in the history view.

**Acceptance Scenarios**:

1. **Given** a customer with 5 form submissions across 2 different templates, **When** the operator opens the customer's profile and clicks the "Form History" tab, **Then** all 5 submissions appear grouped by template type.
2. **Given** a customer's form history, **When** the operator clicks on a submission row, **Then** they are navigated to the read-only submission detail view.
3. **Given** a customer's form history with 100+ submissions, **When** the operator filters by template name or date range, **Then** only matching submissions are shown.

---

### User Story 4 — Auto-Create Customer Profiles from Submissions (Priority: P2)

To reduce manual data entry, the system can automatically create customer profiles from form submission data. When an operator submits a form containing customer-identifying fields (national ID, name, phone) and no matching customer profile exists, the system offers to create one. This is controlled by an organization-level setting.

**Why this priority**: Reduces the friction of building the customer database — profiles accumulate naturally as operators fill forms, rather than requiring a separate data entry step.

**Independent Test**: Enable auto-create in org settings, fill and submit a form with new customer data (name + national ID), verify a customer profile is auto-created with the submitted data.

**Acceptance Scenarios**:

1. **Given** auto-create is enabled in org settings, **When** an operator submits a form with a national ID that doesn't match any existing customer, **Then** the system prompts "Create customer profile from this submission?" with a confirm/dismiss option.
2. **Given** the operator confirms auto-creation, **Then** a new customer profile is created with the data extracted from the submitted form fields.
3. **Given** auto-create is disabled in org settings, **When** an operator submits a form with new customer data, **Then** no auto-create prompt appears.
4. **Given** auto-create is enabled and the operator submits a form whose national ID matches an existing customer, **Then** no auto-create prompt appears (the customer already exists).

---

### User Story 5 — Admin Customer Management (Priority: P3)

Admins need tools to maintain customer data quality: merge duplicate profiles, deactivate profiles for customers no longer served, and delete profiles when required by data retention policies. Merging combines two customer records into one, preserving all form submission history from both records under the surviving profile.

**Why this priority**: Administrative housekeeping features are important for long-term data quality but not required for day-to-day form filling operations.

**Independent Test**: Create two duplicate customer profiles, merge them via the admin interface, verify the surviving profile has the combined submission history. Deactivate a customer and verify they no longer appear in search results.

**Acceptance Scenarios**:

1. **Given** two customer profiles with the same national ID but different names (typo), **When** the admin selects both and clicks "Merge", **Then** a merge dialog shows both profiles side-by-side for field-by-field selection of which value to keep.
2. **Given** a merge operation is confirmed, **Then** all form submissions from both profiles are linked to the surviving profile, and the duplicate profile is deleted.
3. **Given** an admin deactivates a customer profile, **Then** the customer no longer appears in operator search results but their form history remains accessible to admins.
4. **Given** an admin wants to delete a customer profile, **Then** the system requires confirmation and warns about the number of linked form submissions that will lose their customer reference.

---

### User Story 6 — Privacy & Audit Controls (Priority: P3)

All access to customer data must be logged for compliance. Every time a user views, creates, edits, searches, or auto-populates from a customer profile, the action is recorded in the audit log. Admins can review who accessed which customer data and when.

**Why this priority**: Essential for banking and government compliance but does not affect the core user workflow. Can be added as a cross-cutting concern after the main features work.

**Independent Test**: View a customer profile, verify an audit log entry is created with the action type, user, and customer ID. Search for customers, verify a search audit entry exists.

**Acceptance Scenarios**:

1. **Given** an operator views a customer profile, **Then** an audit log entry of type "CUSTOMER_ACCESSED" is recorded with the operator's ID, customer ID, and timestamp.
2. **Given** an operator selects a customer during form filling (auto-populate), **Then** an audit log entry of type "CUSTOMER_AUTO_POPULATED" is recorded.
3. **Given** an admin merges two customer profiles, **Then** an audit log entry of type "CUSTOMER_MERGED" is recorded with both source and target customer IDs.
4. **Given** an admin navigates to the audit log and filters by customer-related actions, **Then** all customer access events are listed with user name, action type, customer identifier, and timestamp.

---

### Edge Cases

- What happens when two operators create a customer with the same national ID simultaneously? The system prevents duplicates by enforcing uniqueness on (org_id, identifier_type, identifier) and returns the existing record to the second operator.
- How does the system handle a customer whose identifier type changes (e.g., from passport to national ID after obtaining citizenship)? The operator edits the profile to update identifier_type and identifier; the old values are preserved in audit history.
- What happens when a template's field keys don't match the standard customer field mapping? No fields are auto-populated; the operator sees a brief message and fills manually.
- What happens when a merged customer's submission history references a deleted duplicate? All submission customer_id references are updated to point to the surviving profile before the duplicate is deleted.
- What happens when auto-create detects partial customer data (e.g., name but no identifier)? Auto-create requires at least an identifier (national ID, commercial register, etc.) to proceed; without one, no prompt is shown.
- How does the system handle deactivated customers in existing form drafts that reference them? The draft retains the customer data already filled but the customer's name shows "(Deactivated)" in the customer selection dialog if re-opened.

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST allow operators and admins to create customer profiles with: name in Arabic, name in English, identifier (national ID, commercial register, passport, iqama, or other), identifier type, contact phone, contact email, and address.
- **FR-002**: System MUST enforce uniqueness of customer profiles within an organization based on the combination of identifier type and identifier value — duplicate creation attempts must return the existing record.
- **FR-003**: System MUST support org-configurable custom fields on customer profiles via an admin schema builder in org settings. Admins define custom fields with a name, type (text, number, date, dropdown), and required flag. All customers in the org share the same custom field schema. Custom field values are validated against the schema on create/edit.
- **FR-004**: System MUST provide a searchable customer list with full-text search across name (Arabic and English), identifier, phone, and email, returning results within 1 second for up to 50,000 customer records.
- **FR-005**: System MUST provide paginated customer list (default 25 per page) with sorting by name, creation date, and last update date (updated_at — updated on any profile edit or status change; serves as proxy for last activity).
- **FR-006**: System MUST support auto-populate during form filling — when an operator selects a customer, fields are pre-filled using a two-tier mapping: (1) default convention-based matching by field key name (e.g., element key `national_id` maps to customer identifier), and (2) optional per-template designer-configured mappings that override or supplement the defaults. Designers configure custom mappings via a mapping panel in Design Studio.
- **FR-007**: System MUST allow operators to override any auto-populated field value before submission without affecting the customer profile.
- **FR-008**: System MUST support clearing a customer selection, resetting auto-populated fields (unless the operator has manually edited them) back to empty.
- **FR-009**: System MUST link form submissions to customer profiles via a customer_id reference, enabling cross-template submission history per customer.
- **FR-010**: System MUST display a customer's cross-template form submission history on their profile page, grouped by template type, with filters for template name and date range.
- **FR-011**: System MUST support admin-initiated profile merging: side-by-side comparison, field-by-field value selection, automatic re-linking of all form submissions to the surviving profile.
- **FR-012**: System MUST support customer profile deactivation — deactivated customers are hidden from operator search but remain accessible to admins and retain their submission history.
- **FR-013**: System MUST support customer profile deletion with confirmation showing the count of linked submissions that will lose their customer reference.
- **FR-014**: System MUST support an organization-level toggle for auto-creating customer profiles from form submissions when the submitted identifier doesn't match any existing customer.
- **FR-015**: System MUST log all customer data access events (view, create, edit, search, auto-populate, merge, deactivate, delete) in the audit trail with user ID, action type, customer ID, and timestamp.
- **FR-016**: System MUST scope all customer data by organization — operators and admins can only access customers belonging to their organization.
- **FR-017**: System MUST display recently used customers (last 5) at the top of the customer selection dialog in the form filler for quick access.
- **FR-018**: System MUST provide a customer field mapping configuration panel in Design Studio where designers can view the default field-key-to-customer-attribute mappings for a template and override or add custom mappings per template.

### Key Entities

- **Customer Profile**: Represents a known customer or entity. Key attributes: name (Arabic + English), identifier, identifier type, contact info, org-specific custom fields, active/deactivated status. Scoped to a single organization.
- **Customer-Submission Link**: The reference from a form submission record to the customer profile it was filled for. Enables cross-template history views.
- **Customer Field Mapping**: The mapping between standard customer profile fields and template element keys, used to determine which fields to auto-populate when a customer is selected.

---

## Non-Functional Requirements

- **NFR-001**: Customer search must return results within 1 second for organizations with up to 50,000 customer profiles.
- **NFR-002**: Auto-populate must complete (all matched fields filled) within 500 milliseconds of customer selection.
- **NFR-003**: Customer data must be isolated by organization — no cross-org data leakage under any query path.
- **NFR-004**: All customer data access must be audit-logged with no silent read paths.
- **NFR-005**: Customer profile merge must be an atomic operation — either all submissions are re-linked and the duplicate deleted, or none of it happens.

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: Operators can create and find a customer profile in under 30 seconds.
- **SC-002**: Auto-populate reduces average form fill time by at least 40% for repeat customers (measured as time from form open to submission for forms with 5+ auto-populated fields).
- **SC-003**: 95% of customer searches return results within 1 second for organizations with up to 50,000 profiles.
- **SC-004**: 100% of customer data access events are captured in the audit log (zero silent read paths).
- **SC-005**: Customer profile merge correctly re-links all historical submissions with zero data loss.
- **SC-006**: Organizations can serve 500+ repeat customers daily using auto-populate without performance degradation.

---

## Assumptions

- The existing Form Desk form filler (F17) supports adding toolbar actions (the "Select Customer" button) without requiring a redesign of the filler component.
- The existing form_submissions table can be extended with an optional customer_id foreign key column without breaking current submission workflows.
- Auto-populate uses a two-tier field mapping strategy: (1) a built-in default mapping table that matches common field key names (e.g., `national_id`, `customer_name_ar`, `phone`) to customer profile attributes, and (2) a per-template mapping configuration panel in Design Studio where designers can override defaults or map non-standard field keys to customer fields.
- Org settings (F25) already support adding new configuration flags (e.g., `auto_create_customer_profiles`).
- The existing audit logging infrastructure (F08) can accommodate new event types without migration changes.
- Custom fields on customer profiles are org-level configured via an admin schema builder in org settings (all customers in an org share the same custom field schema). The schema builder follows the same pattern as reference data list schemas (F24): field name, type (text/number/date/dropdown), and required flag.

---

## Dependencies

- **F01 (Auth & Users)**: User authentication and role-based access control for operators and admins.
- **F08 (Security & Audit)**: Audit logging infrastructure for customer data access events.
- **F17 (Form Filler)**: Form Desk filler where auto-populate is triggered during form filling.
- **F18 (Submission History)**: Form submission records that link to customer profiles.
- **F25 (Multi-Tenancy)**: Organization scoping and RLS isolation for customer data.

---

## Out of Scope

- Bulk customer import from CSV/Excel (planned for a future enhancement).
- Customer-facing portal or self-service profile management.
- Customer data encryption at rest (column-level encryption is a separate infrastructure concern).
- Integration with external CRM systems or core banking customer databases.
- Customer profile photo or document attachments.

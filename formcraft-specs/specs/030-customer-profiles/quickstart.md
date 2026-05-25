# Quickstart: Customer Profiles & Auto-Populate

**Feature**: 030-customer-profiles
**Date**: 2026-05-25

---

## Prerequisites

- FormCraft backend and frontend running
- At least one organization with `customer_profiles_enabled: true`
- At least one operator user and one admin user
- At least one published template with fields using standard key names (e.g., `national_id`, `customer_name_ar`, `phone`)

---

## Test Scenarios

### Scenario 1: Customer CRUD & Search (US1 — P1)

**Goal**: Verify operators can create, search, edit, and list customer profiles.

1. Log in as operator
2. Navigate to Customer Profiles section (Desk → Customers)
3. Click "Add Customer"
4. Fill in: name_ar = "أحمد حسن محمد", name_en = "Ahmed Hassan", identifier_type = "national_id", identifier = "29001011234567", phone = "+966501234567"
5. Save — verify customer appears in list
6. Search "أحمد" — verify customer appears within 1 second
7. Search "29001011234567" — verify customer appears
8. Click customer → Edit phone to "+966509876543" → Save
9. Verify updated phone shows on detail view
10. Try creating another customer with same national_id "29001011234567" — verify error/existing record returned

**Pass criteria**: Customer created, searchable by name and ID, editable, duplicate prevented.

---

### Scenario 2: Auto-Populate During Form Filling (US2 — P1)

**Goal**: Verify selecting a customer auto-fills matching form fields.

1. Ensure a published template exists with elements keyed: `national_id`, `customer_name_ar`, `phone`
2. Log in as operator → navigate to Form Desk → open the template for filling
3. Click "Select Customer" button in the filler toolbar
4. Verify the customer selection dialog appears with search input and recent customers
5. Search for "Ahmed" → select "أحمد حسن محمد"
6. Verify fields auto-populate: `national_id` = "29001011234567", `customer_name_ar` = "أحمد حسن محمد", `phone` = "+966509876543"
7. Manually override the phone field to "+966500000000"
8. Submit the form — verify submission saves with overridden phone value
9. Re-open a new form → select same customer → clear customer selection
10. Verify auto-populated fields reset to empty (except any manually edited)

**Pass criteria**: Auto-populate fills matching fields, overrides allowed, clear resets fields.

---

### Scenario 3: Customer Form History (US3 — P2)

**Goal**: Verify cross-template submission history on customer profile.

1. Create customer "شركة الابتكار" (Innovation Company) with commercial_register
2. Submit 2 forms of Template A and 1 form of Template B with this customer selected
3. Navigate to customer detail → click "Form History" tab
4. Verify all 3 submissions appear, grouped by template type
5. Click on a submission row → verify navigation to read-only submission detail
6. Filter by Template A → verify only 2 submissions shown
7. Filter by date range covering only today → verify 3 submissions shown

**Pass criteria**: All linked submissions visible, filterable by template and date.

---

### Scenario 4: Auto-Create Customer from Submission (US4 — P2)

**Goal**: Verify auto-create prompt when submitting with new customer data.

1. Log in as admin → go to Org Settings
2. Enable "Auto-create customer profiles from submissions" toggle
3. Log in as operator → fill a form with national_id = "29002021234567", name_ar = "سارة أحمد"
4. Submit the form
5. Verify a prompt appears: "Create customer profile from this submission?"
6. Click "Confirm" → verify new customer profile created with the submitted data
7. Navigate to Customer Profiles → search "سارة" → verify the auto-created customer exists
8. Fill another form with the same national_id "29002021234567" → submit
9. Verify NO auto-create prompt (customer already exists)
10. Disable auto-create in org settings → submit a form with new data
11. Verify NO auto-create prompt appears

**Pass criteria**: Prompt appears for new identifiers, not for existing ones, respects org toggle.

---

### Scenario 5: Admin Merge Customers (US5 — P3)

**Goal**: Verify admin can merge duplicate profiles with combined history.

1. Create Customer A: name_ar = "محمد علي", national_id = "29003031234567", phone = "+966501111111"
2. Create Customer B: name_ar = "محمد علي أحمد", national_id = "29003031234568", phone = "+966502222222"
3. Submit 2 forms with Customer A, 1 form with Customer B
4. Log in as admin → navigate to Customer Management
5. Select both customers → click "Merge"
6. Verify side-by-side comparison dialog shows both profiles
7. Select: keep name_ar from B ("محمد علي أحمد"), keep phone from A ("+966501111111")
8. Confirm merge
9. Verify surviving customer has name_ar = "محمد علي أحمد", phone = "+966501111111"
10. Verify all 3 submissions now linked to surviving customer
11. Verify duplicate customer B no longer exists

**Pass criteria**: Merge combines fields per selection, re-links all submissions, deletes duplicate.

---

### Scenario 6: Deactivate/Delete Customer (US5 — P3)

**Goal**: Verify deactivation hides from search; deletion warns about submissions.

1. Create a customer and submit 3 forms with them
2. Log in as admin → deactivate the customer
3. Log in as operator → search for the customer → verify NOT found in results
4. Log in as admin → search for the customer with is_active=false filter → verify found
5. Reactivate the customer → verify operator can find them again
6. Log in as admin → attempt to delete the customer
7. Verify confirmation dialog shows "3 submissions will lose their customer reference"
8. Confirm deletion
9. Verify customer is deleted
10. Verify the 3 submissions still exist but have no customer_id

**Pass criteria**: Deactivation hides from operators only, deletion warns and unlinks.

---

### Scenario 7: Audit Logging (US6 — P3)

**Goal**: Verify all customer data access is logged.

1. Perform these actions: view customer, create customer, edit customer, search, auto-populate, merge, deactivate, delete
2. Log in as admin → navigate to Audit Log
3. Filter by customer-related actions
4. Verify an audit entry exists for each action with: user name, action type, customer identifier, timestamp
5. Verify CUSTOMER_ACCESSED logged for profile views
6. Verify CUSTOMER_AUTO_POPULATED logged for auto-populate selections
7. Verify CUSTOMER_MERGED logged with both source and target IDs

**Pass criteria**: 100% of customer access events captured in audit log.

---

## API Smoke Tests

### Customer CRUD

```bash
# Create customer
curl -X POST /api/customers \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name_ar":"تست","identifier_type":"national_id","identifier":"11111111111111"}'
# Expected: 201, customer object

# List customers
curl /api/customers?search=تست \
  -H "Authorization: Bearer $TOKEN"
# Expected: 200, items array with the created customer

# Get customer detail
curl /api/customers/$CUSTOMER_ID \
  -H "Authorization: Bearer $TOKEN"
# Expected: 200, full customer object

# Update customer
curl -X PATCH /api/customers/$CUSTOMER_ID \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"contact_phone":"+966500000000"}'
# Expected: 200, updated customer object

# Duplicate check
curl -X POST /api/customers \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name_ar":"مكرر","identifier_type":"national_id","identifier":"11111111111111"}'
# Expected: 409, existing customer returned
```

### Auto-Populate

```bash
# Get auto-populate mappings
curl /api/customers/$CUSTOMER_ID/auto-populate?template_id=$TEMPLATE_ID \
  -H "Authorization: Bearer $TOKEN"
# Expected: 200, mappings array with element_key/value pairs
```

### Field Mappings (Designer)

```bash
# Get template mappings
curl /api/templates/$TEMPLATE_ID/customer-field-mappings \
  -H "Authorization: Bearer $TOKEN"
# Expected: 200, default_mappings + override_mappings

# Set override mappings
curl -X PUT /api/templates/$TEMPLATE_ID/customer-field-mappings \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"mappings":[{"element_key":"applicant_phone","customer_field":"contact_phone"}]}'
# Expected: 200, updated mappings
```

### Merge

```bash
# Merge customers
curl -X POST /api/customers/merge \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"surviving_id":"$ID_A","duplicate_id":"$ID_B","field_selections":{"name_ar":"surviving","contact_phone":"duplicate"}}'
# Expected: 200, merged_customer + submissions_relinked count
```

### Recently Used

```bash
# Get recent customers
curl /api/customers/recent \
  -H "Authorization: Bearer $TOKEN"
# Expected: 200, items array (max 5)
```

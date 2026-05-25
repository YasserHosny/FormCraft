# Tasks: Customer Profiles & Auto-Populate

**Input**: Design documents from `/specs/030-customer-profiles/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/customer-api.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `formcraft-backend/`
- **Frontend**: `formcraft-frontend/src/app/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Database migration, enums, and shared models

- [ ] T001 Create database migration `formcraft-backend/migrations/032_customer_profiles.sql` — create `customers` table with all columns (id, org_id, name_ar, name_en, identifier_type, identifier, contact_phone, contact_email, address, custom_fields JSONB, is_active, search_vector tsvector GENERATED, created_by, created_at, updated_at), UNIQUE constraint on (org_id, identifier_type, identifier), GIN index on search_vector, indexes on (org_id, is_active) and (org_id, updated_at DESC), RLS policies for SELECT/INSERT/UPDATE/DELETE, updated_at trigger
- [ ] T002 Extend migration `formcraft-backend/migrations/032_customer_profiles.sql` — create `customer_field_mappings` table (id, template_id FK, element_key, customer_field CHECK constraint, created_at), UNIQUE on (template_id, element_key), RLS policies, index on template_id
- [ ] T003 Extend migration `formcraft-backend/migrations/032_customer_profiles.sql` — add `customer_id UUID REFERENCES customers(id) ON DELETE SET NULL` nullable column to `form_submissions` table, create index on form_submissions(customer_id)
- [ ] T004 Add `IdentifierType` StrEnum to `formcraft-backend/app/models/enums.py` with values: national_id, iqama, commercial_register, passport, other

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Backend schemas, service skeleton, and router registration that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create Pydantic schemas in `formcraft-backend/app/schemas/customer.py` — CustomerBase (name_ar, name_en, identifier_type, identifier, contact_phone, contact_email, address, custom_fields), CustomerCreate(CustomerBase), CustomerUpdate (all optional), CustomerResponse (with id, org_id, is_active, created_by, created_at, updated_at), CustomerListResponse (items, total, page, page_size), CustomerSearchParams (page, page_size, search, is_active, sort_by, sort_order)
- [ ] T006 Create customer service skeleton in `formcraft-backend/app/services/customer_service.py` — CustomerService class with __init__(self, db: AsyncClient) and placeholder methods: create, get_by_id, list_customers, search, update, delete, deactivate, reactivate, merge, get_auto_populate_data, get_recent
- [ ] T007 Create customer router skeleton in `formcraft-backend/app/api/routes/customers.py` — FastAPI APIRouter with all endpoint stubs returning 501, import deps (get_current_user, require_role)
- [ ] T008 Register customers router in `formcraft-backend/app/main.py` — add `from app.api.routes.customers import router as customers_router` and `app.include_router(customers_router, prefix="/api")` following existing pattern
- [ ] T009 [P] Create TypeScript interfaces in `formcraft-frontend/src/app/features/desk/customers/customer.models.ts` — Customer, CustomerCreate, CustomerUpdate, CustomerListResponse, CustomerSearchParams, AutoPopulateMapping, CustomerFieldMapping, CustomerMergeRequest
- [ ] T010 [P] Create Angular customer API service in `formcraft-frontend/src/app/features/desk/services/customer.service.ts` — CustomerService with HttpClient, methods: list, getById, create, update, delete, search, deactivate, reactivate, merge, getAutoPopulateData, getRecentCustomers, getFieldMappings, updateFieldMappings
- [ ] T011 Extend `formcraft-backend/app/schemas/submission.py` — add optional `customer_id: UUID | None = None` field to CreateSubmissionRequest schema

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 — Customer CRUD & Search (Priority: P1) 🎯 MVP

**Goal**: Operators can create, search, edit, list, and view customer profiles with full-text search across 50K records in <1s.

**Independent Test**: Create a customer with full details, search by name and identifier, edit a field, verify pagination works at 25/page, verify duplicate prevention on (identifier_type, identifier).

- [ ] T012 [US1] Implement `create_customer` method in `formcraft-backend/app/services/customer_service.py` — insert into customers table with org_id from current user, validate custom_fields against org settings schema, handle 409 duplicate (return existing on UNIQUE violation), audit log CUSTOMER_CREATED
- [ ] T013 [US1] Implement `list_customers` method in `formcraft-backend/app/services/customer_service.py` — paginated query with sort_by (name_ar, name_en, created_at, updated_at) and sort_order (asc, desc), filter by is_active, org_id scoping via RLS
- [ ] T014 [US1] Implement `search_customers` method in `formcraft-backend/app/services/customer_service.py` — full-text search using `plainto_tsquery('simple', query)` against search_vector with `ts_rank` ordering, ILIKE fallback for queries <3 chars, audit log CUSTOMER_SEARCH
- [ ] T015 [US1] Implement `get_by_id` method in `formcraft-backend/app/services/customer_service.py` — fetch single customer by id with org_id scoping, audit log CUSTOMER_ACCESSED, raise 404 if not found
- [ ] T016 [US1] Implement `update_customer` method in `formcraft-backend/app/services/customer_service.py` — partial update, validate custom_fields if provided, handle 409 on identifier conflict, audit log CUSTOMER_UPDATED with changed fields
- [ ] T017 [US1] Wire up customer CRUD endpoints in `formcraft-backend/app/api/routes/customers.py` — implement POST /api/customers (create), GET /api/customers (list+search), GET /api/customers/{customer_id} (detail), PATCH /api/customers/{customer_id} (update) with role guards (operator, admin, org_admin)
- [ ] T018 [P] [US1] Create customer list component in `formcraft-frontend/src/app/features/desk/customers/customer-list.component.ts` + `.html` + `.scss` — paginated table (25/page) with search input, columns: name_ar, name_en, identifier, phone, status, actions. Use Angular Material table + paginator. Debounced search input calling CustomerService.list with search param
- [ ] T019 [P] [US1] Create customer detail component in `formcraft-frontend/src/app/features/desk/customers/customer-detail.component.ts` + `.html` + `.scss` — view/edit form with all customer fields (name_ar, name_en, identifier_type dropdown, identifier, phone, email, address, custom_fields dynamic form based on org schema), save button calling CustomerService.update, "Add Customer" mode for create via CustomerService.create
- [ ] T020 [US1] Add customers route and navigation in `formcraft-frontend/src/app/features/desk/desk.module.ts` and desk routing — add lazy-loaded route `/desk/customers` → CustomerListComponent, `/desk/customers/:id` → CustomerDetailComponent, `/desk/customers/new` → CustomerDetailComponent in create mode. Add "Customers" nav item to desk sidebar/menu
- [ ] T021 [US1] Handle duplicate customer error in customer-detail.component — on 409 response from create, show MatSnackBar with "Customer already exists" and offer to navigate to existing customer (use returned customer data from 409 response body)

---

## Phase 4: User Story 2 — Auto-Populate During Form Filling (Priority: P1)

**Goal**: Operators select a customer from a dialog during form filling, and matching template fields are pre-filled automatically. Overrides allowed, clear resets fields.

**Independent Test**: Create a customer with full details, open a published template, click "Select Customer", pick the customer, verify matching fields are pre-filled, override one, submit successfully, clear selection and verify reset.

**Depends on**: US1 (customer data must exist)

- [ ] T022 [US2] Implement `get_auto_populate_data` method in `formcraft-backend/app/services/customer_service.py` — accept customer_id + template_id, load customer data, load Tier 2 overrides from customer_field_mappings for this template, apply Tier 1 default mapping table (match element keys against hardcoded patterns per research.md R2), merge Tier 2 over Tier 1, return list of {element_key, value, source} mappings, audit log CUSTOMER_AUTO_POPULATED
- [ ] T023 [US2] Implement `get_recent_customers` method in `formcraft-backend/app/services/customer_service.py` — query audit_logs for CUSTOMER_AUTO_POPULATED events by current user, group by customer_id, return last 5 distinct customers with their basic info (id, name_ar, name_en, identifier, last_used_at)
- [ ] T024 [US2] Wire up auto-populate and recent endpoints in `formcraft-backend/app/api/routes/customers.py` — implement GET /api/customers/{customer_id}/auto-populate?template_id=uuid, GET /api/customers/recent (must be registered BEFORE /{customer_id} path to avoid route conflict)
- [ ] T025 [P] [US2] Create customer selection dialog in `formcraft-frontend/src/app/shared/components/customer-select-dialog/customer-select-dialog.component.ts` + `.html` + `.scss` — MatDialog with search input (debounced), recent customers section (top 5), search results list showing name_ar, name_en, identifier. Append "(غير نشط)" / "(Deactivated)" suffix to name for customers with is_active=false if they appear in results (e.g. from draft re-open). On select, return customer object. Declare in SharedModule exports
- [ ] T026 [US2] Extend form filler toolbar in `formcraft-frontend/src/app/features/desk/fill/` — add "Select Customer" button (mat-icon-button with person icon) to filler toolbar, on click open CustomerSelectDialogComponent, on customer selected call CustomerService.getAutoPopulateData(customerId, templateId), apply returned mappings to form field values, track which fields were auto-populated vs manually edited
- [ ] T027 [US2] Implement auto-populate field application logic in the form filler — iterate mappings from auto-populate response, for each mapping find the matching form element by element_key and set its value, track auto-populated fields in a Set<string>, show MatSnackBar with count of fields populated (or "No matching fields found" if zero)
- [ ] T028 [US2] Implement clear customer selection in form filler — add "Clear Customer" button (visible when customer selected), on click reset all auto-populated fields to empty (only fields in the auto-populated Set that haven't been manually edited since), clear the selected customer reference, remove "Clear Customer" button
- [ ] T029 [US2] Extend submission creation to include customer_id — when submitting a form with a customer selected, pass customer_id in the CreateSubmissionRequest body. Update `formcraft-backend/app/services/submission_service.py` to save customer_id to form_submissions table

---

## Phase 5: User Story 3 — Customer Form History (Priority: P2)

**Goal**: Customer profile shows cross-template submission history with filters by template and date range.

**Independent Test**: Create a customer, submit 3 forms across 2 templates with that customer, view customer profile, verify all 3 submissions appear in history tab, filter by template, filter by date.

**Depends on**: US1 (customer exists), US2 (submissions linked to customer)

- [ ] T030 [US3] Implement `get_customer_submissions` method in `formcraft-backend/app/services/customer_service.py` — paginated query joining form_submissions + templates where customer_id matches, filter by template_id and date range, return submission id, template_id, template_name, status, created_at, created_by_name, audit log CUSTOMER_HISTORY_ACCESSED
- [ ] T031 [US3] Wire up customer submissions endpoint in `formcraft-backend/app/api/routes/customers.py` — implement GET /api/customers/{customer_id}/submissions with query params: page, page_size, template_id, date_from, date_to
- [ ] T032 [US3] Add "Form History" tab to customer detail component in `formcraft-frontend/src/app/features/desk/customers/customer-detail.component.ts` + `.html` — MatTabGroup with "Details" and "Form History" tabs, history tab shows paginated table of submissions (template name, status, date, operator), filter controls for template dropdown and date range picker, clicking a row navigates to /desk/submissions/:id

---

## Phase 6: User Story 4 — Auto-Create Customer from Submission (Priority: P2)

**Goal**: After form submission with new identifier data, system prompts operator to create a customer profile from the submission data (when org setting enabled).

**Independent Test**: Enable auto-create in org settings, submit form with new national_id + name, verify prompt appears, confirm creation, verify customer exists. Submit again with same ID — no prompt. Disable setting — no prompt.

**Depends on**: US1 (customer create), US2 (submission flow)

- [ ] T033 [US4] Add auto-create org setting support — verify `auto_create_customer_profiles` is read from org settings in backend (no new endpoint needed, org settings already loaded by frontend). If not present in existing org settings schema, add it to `formcraft-backend/app/schemas/organization.py` with default false
- [ ] T034 [US4] Add auto-create toggle to org settings UI in `formcraft-frontend/src/app/features/admin/org-settings/` — add MatSlideToggle for "Auto-create customer profiles from submissions" under a "Customer Profiles" section, bind to org settings auto_create_customer_profiles field
- [ ] T035 [US4] Implement auto-create prompt in form filler post-submission flow in `formcraft-frontend/src/app/features/desk/fill/` — after successful submission, if (1) auto_create_customer_profiles is enabled in org settings, (2) submitted form has an identifier-type field with a value, (3) no customer_id was set (not already selecting existing customer): call CustomerService.list with search=identifier_value, if no match found show MatDialog "Create customer profile from this submission?" with pre-filled data extracted from submitted field_values using the default mapping table (reverse lookup), on confirm call CustomerService.create
- [ ] T036 [US4] Implement identifier field detection utility in `formcraft-frontend/src/app/features/desk/services/customer.service.ts` — add method `extractIdentifierFromSubmission(fieldValues, templateElements)` that scans field keys for identifier-pattern matches (national_id, iqama, commercial_register, passport_number, customer_id_number) and returns {identifier_type, identifier, mapped_fields} or null if no identifier found

---

## Phase 7: User Story 5 — Admin Customer Management (Priority: P3)

**Goal**: Admins can merge duplicate profiles (side-by-side field selection, re-link submissions), deactivate profiles (hide from operators), and delete profiles (with submission unlink warning).

**Independent Test**: Create 2 duplicate customers with submissions, merge them, verify combined history on survivor. Deactivate a customer, verify hidden from operator search. Delete a customer, verify submissions retain data but lose customer_id.

**Depends on**: US1 (customer CRUD), US3 (submission history for merge verification)

- [ ] T037 [US5] Implement `delete_customer` method in `formcraft-backend/app/services/customer_service.py` — count linked submissions, delete customer (ON DELETE SET NULL handles unlinking), return deleted=true + submissions_unlinked count, audit log CUSTOMER_DELETED
- [ ] T038 [US5] Implement `deactivate_customer` and `reactivate_customer` methods in `formcraft-backend/app/services/customer_service.py` — update is_active flag, audit log CUSTOMER_DEACTIVATED or CUSTOMER_REACTIVATED
- [ ] T039 [US5] Implement `merge_customers` method in `formcraft-backend/app/services/customer_service.py` — atomic transaction: (1) build surviving profile from field_selections picking values from each source, (2) UPDATE form_submissions SET customer_id = surviving_id WHERE customer_id = duplicate_id, (3) DELETE duplicate, return merged customer + submissions_relinked count, audit log CUSTOMER_MERGED with both source IDs and field selections
- [ ] T040 [US5] Wire up admin management endpoints in `formcraft-backend/app/api/routes/customers.py` — implement DELETE /api/customers/{customer_id} (admin only), PATCH /api/customers/{customer_id}/status (admin only), POST /api/customers/merge (admin only, must be registered BEFORE /{customer_id} routes)
- [ ] T041 [P] [US5] Create customer merge component in `formcraft-frontend/src/app/features/admin/customer-management/customer-merge.component.ts` + `.html` + `.scss` — side-by-side display of two customer profiles, radio buttons for each field to select "keep from A" or "keep from B", preview of merged result, confirm button calling CustomerService.merge, success shows merged profile with re-linked submission count
- [ ] T042 [P] [US5] Create admin customer management page in `formcraft-frontend/src/app/features/admin/customer-management/` — list of all customers (including deactivated) with bulk select, toolbar actions: Merge (enabled when exactly 2 selected), Deactivate/Reactivate, Delete with confirmation dialog showing submission count warning
- [ ] T043 [US5] Add admin customer management route in `formcraft-frontend/src/app/features/admin/admin.module.ts` and admin routing — add route `/admin/customer-management` → admin customer list, add "Customer Management" item to admin menu/nav

---

## Phase 8: User Story 6 — Privacy & Audit Controls (Priority: P3)

**Goal**: All customer data access is audit-logged. Admins can review customer access events in the audit log.

**Independent Test**: View, create, edit, search, auto-populate, merge, deactivate, delete customers — verify each action creates an audit log entry with correct action type, user, customer ID, timestamp.

**Depends on**: US1-US5 (audit events fire from all customer operations)

- [ ] T044 [US6] Verify and complete audit logging across all customer service methods in `formcraft-backend/app/services/customer_service.py` — ensure every method calls AuditLogger.log_event with: CUSTOMER_CREATED, CUSTOMER_ACCESSED, CUSTOMER_UPDATED, CUSTOMER_DELETED, CUSTOMER_SEARCH, CUSTOMER_AUTO_POPULATED, CUSTOMER_HISTORY_ACCESSED, CUSTOMER_MERGED, CUSTOMER_DEACTIVATED, CUSTOMER_REACTIVATED. Include customer_id and relevant metadata (changed fields, search query, merge source IDs, submission counts)
- [ ] T045 [US6] Add customer audit event types filter to admin audit log view — extend existing audit log filtering in `formcraft-frontend/src/app/features/admin/` to include a "Customer Events" category filter that shows all CUSTOMER_* action types, displaying user name, action type, customer identifier (resolve from metadata), and timestamp

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Designer field mapping config, custom fields schema builder, and integration polish

- [ ] T046 Implement designer field mapping configuration panel — create customer field mapping section in Design Studio template editor `formcraft-frontend/src/app/features/designer/` that shows default mappings (read-only) and allows adding/editing/removing override mappings. On save, call PUT /api/templates/{template_id}/customer-field-mappings
- [ ] T047 Wire up template field mapping endpoints in `formcraft-backend/app/api/routes/customers.py` or a new route file — implement GET /api/templates/{template_id}/customer-field-mappings and PUT /api/templates/{template_id}/customer-field-mappings with designer/admin role guard
- [ ] T048 Implement custom fields schema builder in org settings admin UI `formcraft-frontend/src/app/features/admin/org-settings/` — dynamic form to add/remove/edit custom field definitions (key, label_ar, label_en, type dropdown [text/number/date/dropdown], required toggle, options list for dropdown type). Save to org settings under customer_custom_fields key
- [ ] T049 Implement custom fields validation in `formcraft-backend/app/services/customer_service.py` — on create/update, load org's customer_custom_fields schema from settings, validate each custom_field value against declared type, check required fields present, reject unknown keys, validate dropdown values against options list
- [ ] T050 Implement custom fields dynamic form rendering in customer detail component `formcraft-frontend/src/app/features/desk/customers/customer-detail.component.ts` — load org's custom field schema, render dynamic form inputs (text input, number input, date picker, dropdown) for each defined custom field, bind to customer.custom_fields object
- [ ] T051 Validate full-text search performance at scale — create a seed script in `formcraft-backend/scripts/seed_test_customers.py` that generates 50,000 realistic customer records (mixed Arabic/English names, unique identifiers, varied phone/email) for a test org. Run search queries against the seeded data and verify results return in <1s. Validate GIN index is used via EXPLAIN ANALYZE. Remove seed data after validation.

---

## Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US1: CRUD & Search)
                                            ↓
                                     Phase 4 (US2: Auto-Populate) → Phase 5 (US3: History)
                                            ↓                              ↓
                                     Phase 6 (US4: Auto-Create)     Phase 7 (US5: Admin Mgmt)
                                                                           ↓
                                                                    Phase 8 (US6: Audit)
                                                                           ↓
                                                                    Phase 9 (Polish)
```

**Story dependency order**:
1. US1 (Customer CRUD) — no dependencies, MVP standalone
2. US2 (Auto-Populate) — depends on US1
3. US3 (Form History) — depends on US1 + US2 (needs linked submissions)
4. US4 (Auto-Create) — depends on US1 + US2
5. US5 (Admin Management) — depends on US1, benefits from US3
6. US6 (Audit) — depends on all stories (verifies audit logging)

---

## Parallel Execution Opportunities

**Phase 2**: T009 and T010 (frontend models + service) can run parallel to T005-T008 (backend)
**Phase 3 (US1)**: T018 and T019 (frontend components) can run parallel with each other and with backend tasks T012-T017
**Phase 4 (US2)**: T025 (dialog component) can run parallel with T022-T024 (backend)
**Phase 7 (US5)**: T041 and T042 (merge + admin components) can run parallel with each other

---

## Implementation Strategy

1. **MVP** (US1 only): Customer CRUD & Search — delivers standalone value, operators can manage customer directory
2. **Core Value** (US1 + US2): Add auto-populate — delivers the primary 40%+ time savings
3. **Enhanced** (+ US3 + US4): History and auto-create — reduces friction and adds cross-template value
4. **Complete** (+ US5 + US6 + Polish): Admin tools, audit compliance, designer config — full feature set

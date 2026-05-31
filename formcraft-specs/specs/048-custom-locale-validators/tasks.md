# Feature 048: Implementation Tasks

## Phase 1: Data Model & API (Backend)

### Task 1.1: Create custom_validators Table
- [ ] Write PostgreSQL migration to create `custom_validators` table
- [ ] Add columns: id, org_id, name, description, regex_pattern, error_message_ar, error_message_en, created_at, updated_at, created_by, updated_by, deleted_at
- [ ] Add UNIQUE constraint on (org_id, name)
- [ ] Add CHECK constraints for non-empty fields
- [ ] Create indexes on (org_id, deleted_at) for fast org queries
- [ ] Create indexes on (org_id, name) for dropdown population

### Task 1.2: Modify elements Table
- [ ] Add `custom_validators_ids UUID[]` column with default empty array
- [ ] Add migration to handle existing elements (set to empty array)

### Task 1.3: Implement RLS Policies
- [ ] Create RLS policy: users can read custom_validators only for their org
- [ ] Create RLS policy: users can write (insert/update/delete) only if org_id matches their profile org_id
- [ ] Test RLS isolation (user from Org A cannot see Org B validators)

### Task 1.4: Build Validator CRUD API Endpoints
- [ ] `GET /admin/validators` — List validators with pagination, search by name
- [ ] `POST /admin/validators` — Create validator with validation (regex test, required fields)
- [ ] `GET /admin/validators/:id` — Get single validator
- [ ] `PUT /admin/validators/:id` — Update validator
- [ ] `DELETE /admin/validators/:id` — Soft delete (set deleted_at)
- [ ] Add input validation: regex pattern, required bilingual messages
- [ ] Add rate limiting to prevent regex DoS attacks

### Task 1.5: Build Validator Query API for Designers
- [ ] `GET /api/validators/org` — Return all active (not deleted) custom validators for user's org
- [ ] Format response with: id, name, description, regex_pattern (for validation display)
- [ ] Add caching for quick dropdown population

### Task 1.6: Implement Template Usage Endpoint
- [ ] `GET /admin/validators/:id/templates` — Return list of templates using this validator
- [ ] Include: template_id, template_name, last_used_date, is_active
- [ ] Add pagination for validators with many template uses

### Task 1.7: Add Audit Logging
- [ ] Create audit log entries for VALIDATOR_CREATED event
- [ ] Create audit log entries for VALIDATOR_UPDATED event (with before/after values)
- [ ] Create audit log entries for VALIDATOR_DELETED event
- [ ] Test audit trail completeness

### Task 1.8: Implement Validator Update Handler
- [ ] When validator is updated, broadcast change to all templates using it
- [ ] No need to modify templates themselves (reference by ID maintains consistency)
- [ ] Log audit event with before/after values

---

## Phase 2: Admin UI (Frontend)

### Task 2.1: Create Validators Admin Page Layout
- [ ] Create `/admin/validators` route in Admin Console
- [ ] Design page layout: list + detail panel
- [ ] Add toolbar with search, filter, create button

### Task 2.2: Implement Validators List Component
- [ ] Display table/list of org's custom validators
- [ ] Columns: name, description, pattern (truncated), created_by, updated_at
- [ ] Pagination (20 per page)
- [ ] Search by name and description
- [ ] Sort by name, created_at, updated_at

### Task 2.3: Implement Create Validator Modal
- [ ] Form fields: name, description, regex_pattern, error_message_ar, error_message_en
- [ ] Regex pattern validator: test pattern before save
- [ ] Bilingual input: side-by-side AR/EN fields
- [ ] Submit button creates validator via POST endpoint
- [ ] Show success/error toast

### Task 2.4: Implement Edit Validator Modal
- [ ] Load validator details from API
- [ ] Pre-populate all fields
- [ ] Regex pattern validator (test before save)
- [ ] Submit updates validator via PUT endpoint
- [ ] Show warning: "Changes will apply to all templates using this validator"

### Task 2.5: Implement Delete Confirmation Dialog
- [ ] Show validator name and count of templates using it
- [ ] Confirmation text: "This will remove the validator, but existing references will remain (showing the old rules)"
- [ ] Delete via DELETE endpoint (soft delete)

### Task 2.6: Implement Usage Tab
- [ ] Show list of templates using this validator
- [ ] Display: template name, last used date, edit link
- [ ] Pagination for validators used by many templates

### Task 2.7: Add Admin Audit Trail View
- [ ] Create `/admin/audit?entity=validator` filter
- [ ] Display VALIDATOR_CREATED, VALIDATOR_UPDATED, VALIDATOR_DELETED events
- [ ] Show operator, timestamp, before/after values

---

## Phase 3: Designer UI Integration (Frontend)

### Task 3.1: Extend Element Properties Panel
- [ ] Add "Custom Validators" section to validation rules panel
- [ ] Position below built-in validation rules

### Task 3.2: Implement Custom Validators Dropdown
- [ ] Fetch org's validators via GET /api/validators/org on panel open
- [ ] Display: validator name, description in dropdown
- [ ] Support search/filter by name
- [ ] Handle loading state and empty state

### Task 3.3: Add Validator Tags/Chips UI
- [ ] Selected validators appear as removable chips below dropdown
- [ ] Clicking X removes validator from element
- [ ] Visual indication of multiple validators applied

### Task 3.4: Persist Validator Selections
- [ ] Save selected custom_validators_ids array to element.custom_validators_ids
- [ ] Ensure array is properly serialized/deserialized in element model
- [ ] Handle undo/redo for validator additions/removals

### Task 3.5: Update Element Preview
- [ ] Show custom validators in element metadata during canvas preview
- [ ] Validation rules clearly indicate "uses custom validator X"

### Task 3.6: Add Validator Description Tooltip
- [ ] Hover tooltip shows full validator description and regex pattern
- [ ] Helps designer understand what the validator checks

---

## Phase 4: Form Filler Integration (Frontend)

### Task 4.1: Extend Validation Engine
- [ ] Modify form fill validator to check custom_validators_ids array
- [ ] For each custom validator: fetch validator definition, test regex against field value
- [ ] Return validation error if regex fails

### Task 4.2: Implement Bilingual Error Messages
- [ ] Fetch operator's language preference from profile
- [ ] Display error_message_ar if operator language is AR, else error_message_en
- [ ] Show error inline next to field (consistent with built-in validation)

### Task 4.3: Add Real-Time Validation UI
- [ ] As operator types, check against custom validators in real-time
- [ ] Show error immediately when regex matches failure condition
- [ ] Hide error when field becomes valid

### Task 4.4: Update Form Submission Handler
- [ ] Before submit, validate all custom validators
- [ ] Prevent submission if any custom validator fails
- [ ] Show all validation errors together

### Task 4.5: Test Validator Evaluation
- [ ] Unit tests for regex evaluation logic
- [ ] E2E tests: operator enters invalid data, sees bilingual error, corrects, form submits

---

## Phase 5: Testing & Documentation

### Task 5.1: Unit Tests - Backend
- [ ] Test validator CRUD operations
- [ ] Test regex pattern validation before storage
- [ ] Test RLS policies (isolation between orgs)
- [ ] Test audit logging
- [ ] Test regex evaluation logic

### Task 5.2: Unit Tests - Frontend
- [ ] Test dropdown population from API
- [ ] Test regex pattern validation UI
- [ ] Test bilingual message selection
- [ ] Test validator removal/addition from element

### Task 5.3: Integration Tests
- [ ] Admin creates validator, designer uses it, operator validates against it
- [ ] Validator update propagates to all templates
- [ ] Audit trail records all operations

### Task 5.4: E2E Tests
- [ ] Playwright: Admin creates custom validator
- [ ] Designer applies to form field
- [ ] Operator submits form with invalid data, sees error in AR/EN
- [ ] Operator corrects field, submits successfully
- [ ] Admin updates validator message, new operator sees new message

### Task 5.5: Performance Testing
- [ ] Load test with 100+ validators per org
- [ ] Measure dropdown load time
- [ ] Measure form submit validation time with 10+ validators per field

### Task 5.6: API Documentation
- [ ] Document all endpoints: request/response format, error codes
- [ ] Add example regexes for common use cases (commercial reg, tax ID, etc.)
- [ ] Document RLS behavior and org isolation

### Task 5.7: User Documentation
- [ ] Guide for Org Admins: how to create and manage validators
- [ ] Guide for Designers: how to use validators in templates
- [ ] Guide for Operators: bilingual error messages and validation feedback

---

## Dependencies & Ordering

1. **Phase 1 must complete before Phases 2-4** (data model is prerequisite)
2. **Phase 2 (Admin UI) can start as soon as Phase 1.6 is done** (POST endpoint available)
3. **Phase 3 (Designer UI) requires Phase 1.5 to be done** (GET /api/validators/org endpoint)
4. **Phase 4 (Form Filler) requires Phase 1 complete** (custom_validators_ids must be stored)
5. **Phase 5 (Testing) can begin after Phases 1-3 are feature-complete**

---

## Estimated Effort

- Phase 1: 16 hours (5 developers: 1 migrations specialist, 1 RLS expert, 1 API dev, 1 queries dev, 1 QA)
- Phase 2: 12 hours (2 frontend developers)
- Phase 3: 10 hours (2 frontend developers)
- Phase 4: 8 hours (2 frontend developers)
- Phase 5: 12 hours (1 QA engineer, 1 test automation engineer)

**Total: ~58 hours of development**

---

## Success Criteria

- [x] All CRUD endpoints working with org isolation
- [x] RLS policies prevent cross-org access
- [x] Admin can create/edit/delete validators
- [x] Designer can apply validators to elements
- [x] Form filler validates against custom validators
- [x] Bilingual error messages display correctly
- [x] Audit trail complete for all operations
- [x] 95%+ test coverage for custom validator code paths
- [x] Dropdown load time < 200ms with 100 validators
- [x] Form submission validation < 100ms with 10 validators/field

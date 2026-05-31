# Feature 048: Implementation Tasks

## Test-First Discipline (Constitution Principle V)

Every implementation task below is **gated by a preceding test task**:

- `Task X.Y.T` — failing tests land first (Red)
- `Task X.Y.I` — implementation makes tests pass (Green)
- `Task X.Y.R` — refactor with tests still green (Refactor)

No `.I` task may merge unless its `.T` peer was demonstrably red beforehand (CI gate via PR labels). Phase 5 retains only end-to-end / performance / cross-system tests that cannot be authored before the feature is integrated.

## Precedence & Scope Reminders

- **Deterministic validators always run before custom validators** (Constitution Principle IV + spec.md "Validator Precedence Rule"). Implementation must wire custom validators into the existing validation engine **after** the deterministic chain, not in parallel.
- All new UI strings use i18n translation keys (`admin.validators.*`, `designer.validators.*`) — no hardcoded labels.

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
- [ ] **1.4.T** Contract tests for each endpoint (GET list, GET one, POST, PUT, DELETE) — including rate-limit headers, 400 on bad regex, 403 cross-org, 404 missing, and unique-name constraint
- [ ] **1.4.I** `GET /admin/validators` — paginated, `ILIKE` search across `name || ' ' || COALESCE(description, '')` (FR-8)
- [ ] **1.4.I** `POST /admin/validators` — create with validation (required bilingual messages, regex compiled in sandbox + nested-quantifier check + 100ms probe timeout per FR-9)
- [ ] **1.4.I** `GET /admin/validators/:id`
- [ ] **1.4.I** `PUT /admin/validators/:id` — same FR-9 regex checks on changed pattern; emit `VALIDATOR_UPDATED` with changed-field diff
- [ ] **1.4.I** `DELETE /admin/validators/:id` — soft delete; cascade behavior: existing element references remain but validator is skipped at runtime
- [ ] **1.4.I** Rate limiting: 30 req/min/org on POST and PUT (FR-1)
- [ ] **1.4.I** Enforce hard cap: reject POST if `COUNT(* WHERE org_id=? AND deleted_at IS NULL) >= 500`

### Task 1.4b: Regex Safety Sandbox
- [ ] **1.4b.T** Tests: ReDoS probe set must reject `(a+)+$`, `(.*a){10}b`, `(x+x+)+y`; benign patterns must pass; timeout returns specific 400 code
- [ ] **1.4b.I** Implement compile-time pre-check (length ≤ 500, no `(...+)+` / `(...*)*` chains via AST scan)
- [ ] **1.4b.I** Implement compile-time probe runner with 100ms hard timeout (Python `signal.SIGALRM` or subprocess)
- [ ] **1.4b.I** Implement runtime 50ms per-pattern timeout with fail-open + `VALIDATOR_TIMEOUT` audit event

### Task 1.5: Build Validator Query API for Designers
- [ ] **1.5.T** Contract test asserts response shape (`{id, name, description, regex_pattern}[]`), org isolation, `ORDER BY name ASC`, and dropdown payload ≤ 200ms at 500 validators
- [ ] **1.5.I** `GET /api/validators/org` — return active validators sorted `ORDER BY name ASC` (US-3)
- [ ] **1.5.I** In-process cache keyed by `org_id`, TTL 60s, explicit invalidation hook called from POST/PUT/DELETE on `/admin/validators`
- [ ] **1.5.I** Cache miss path measured: target ≤ 100ms for 500 validators (use `(org_id, deleted_at)` partial index)

### Task 1.6: Implement Template Usage Endpoint
- [ ] **1.6.T** Contract test: returns templates that reference validator via `elements.custom_validators_ids` (GIN-indexed); paginated 50/page; sorted `last_submission_at DESC NULLS LAST`; org-scoped
- [ ] **1.6.I** `GET /admin/validators/:id/templates` — derived join: `templates → pages → elements WHERE :validator_id = ANY(elements.custom_validators_ids)`
- [ ] **1.6.I** `last_submission_at` computed via correlated subquery `MAX(submissions.created_at) WHERE submissions.template_id = templates.id` (FR-6, U1 resolved)
- [ ] **1.6.I** Response fields: `template_id`, `template_name`, `template_status`, `last_submission_at` (nullable)

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

### Task 4.1: Extend Validation Engine (Deterministic-First per Constitution Principle IV)
- [ ] **4.1.T** Test the precedence rule: deterministic validator for a national-ID-typed element MUST run and short-circuit before any custom validator; if deterministic fails, no custom validator is evaluated and the deterministic error message is shown
- [ ] **4.1.T** Test: soft-deleted validators (`deleted_at IS NOT NULL`) are skipped silently — they do NOT produce an error
- [ ] **4.1.T** Test: per-pattern 50ms timeout returns "pass" and emits `VALIDATOR_TIMEOUT` audit event (fail-open per FR-9)
- [ ] **4.1.I** Modify form-fill validator pipeline to: deterministic_chain → custom_chain (per `element.custom_validators_ids` in order)
- [ ] **4.1.I** Fetch validator definitions via the cached `GET /api/validators/org` data loaded at form open; refresh cache on page navigation and at submit (FR-7 in-flight semantics)
- [ ] **4.1.I** Return structured error: `{validator_id, error_message_ar, error_message_en}`

### Task 4.2: Implement Bilingual Error Messages (with fallback chain — FR-2)
- [ ] **4.2.T** Test fallback order: internal operator → `profiles.preferred_language`; external portal user → `template.language`; unsupported / missing → `error_message_en`
- [ ] **4.2.I** Implement selector function `pickErrorMessage(validator, context) → string` honoring the chain
- [ ] **4.2.I** Show error inline next to field; use existing built-in validator UI component (no duplicate styling)

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

## Phase 5: System-Level Tests & Documentation

(Per Constitution Principle V, unit/integration tests for each component were written in Phases 1–4 alongside their `.I` implementations. Phase 5 retains only tests that require the full system end-to-end.)

### ~~Task 5.1: Unit Tests - Backend~~ — MOVED into Phase 1 `.T` tasks
### ~~Task 5.2: Unit Tests - Frontend~~ — MOVED into Phases 2/3/4 `.T` tasks
### ~~Task 5.3: Integration Tests~~ — MOVED into Phase 1 `.T` and Phase 4 `.T` tasks

### Task 5.4: E2E Tests
- [ ] Playwright: Admin creates custom validator
- [ ] Designer applies to form field; deterministic validator on same field still runs first
- [ ] Operator submits form with invalid data, sees error in AR/EN per fallback chain
- [ ] Operator corrects field, submits successfully
- [ ] Admin updates validator message; in-flight fill picks up new message at next-page navigation or submit
- [ ] Cross-org isolation: User in Org A cannot fetch Org B validator by ID (HTTP 403/404)
- [ ] Soft-deleted validator: referenced by element → element validates as if validator were absent (no error raised)

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

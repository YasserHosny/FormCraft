# Tasks: Data Export & Integration

**Input**: Design documents from `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-specs/specs/032-data-export-integration/`
**Prerequisites**: [plan.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/032-data-export-integration/plan.md), [spec.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/032-data-export-integration/spec.md), [research.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/032-data-export-integration/research.md), [data-model.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/032-data-export-integration/data-model.md), [contracts/openapi.yaml](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/032-data-export-integration/contracts/openapi.yaml), [quickstart.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/032-data-export-integration/quickstart.md)

**Tests**: Required by the FormCraft Constitution. Test tasks must be written first and fail before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup

**Purpose**: Prepare shared files, route slots, service placeholders, and frontend entry points.

- [X] T001 Create backend export route placeholder in `formcraft-backend/app/api/routes/admin_export.py`
- [X] T002 Create backend integrations route placeholder in `formcraft-backend/app/api/routes/integrations.py`
- [X] T003 Register admin export and integrations routers in `formcraft-backend/app/main.py`
- [X] T004 [P] Create export schema placeholder in `formcraft-backend/app/schemas/export.py`
- [X] T005 [P] Create integration schema placeholder in `formcraft-backend/app/schemas/integration.py`
- [X] T006 [P] Create template package schema placeholder in `formcraft-backend/app/schemas/template_package.py`
- [X] T007 [P] Create export service placeholder in `formcraft-backend/app/services/export_service.py`
- [X] T008 [P] Create template package service placeholder in `formcraft-backend/app/services/template_package_service.py`
- [X] T009 [P] Create integration credential service placeholder in `formcraft-backend/app/services/integration_credential_service.py`
- [X] T010 [P] Create webhook service placeholder in `formcraft-backend/app/services/webhook_service.py`
- [X] T011 [P] Create frontend data export API service placeholder in `formcraft-frontend/src/app/core/services/data-export.service.ts`
- [X] T012 [P] Create frontend integration API service placeholder in `formcraft-frontend/src/app/core/services/integration.service.ts`
- [X] T013 [P] Create shared integration/export model placeholder in `formcraft-frontend/src/app/shared/models/integration.models.ts`
- [X] T014 Add admin child routes for `/admin/export`, `/admin/export/schedules`, and `/admin/integrations` in `formcraft-frontend/src/app/features/admin/admin.module.ts`

---

## Phase 2: Foundational

**Purpose**: Shared persistence, schemas, security helpers, and translation keys required before user stories.

**Critical**: No user story implementation should begin until this phase is complete.

- [X] T015 Write failing migration validation tests for export and integration tables, indexes, audit fields, and RLS policies in `formcraft-backend/tests/integration/test_data_export_integration_routes.py`
- [X] T016 Create Supabase migration for `export_requests`, `export_schedules`, `export_deliveries`, `integration_credentials`, `webhook_subscriptions`, `webhook_deliveries`, indexes, RLS policies, and audit fields in `formcraft-backend/migrations/034_data_export_integration.sql`
- [X] T017 Implement shared Pydantic DTOs for export preview/download/history/schedules/deliveries in `formcraft-backend/app/schemas/export.py`
- [X] T018 Implement shared Pydantic DTOs for integration credentials, webhook subscriptions, and webhook deliveries in `formcraft-backend/app/schemas/integration.py`
- [X] T019 Implement shared Pydantic DTOs for template package manifest, import review, import request, and import result in `formcraft-backend/app/schemas/template_package.py`
- [X] T020 [P] Implement frontend Zod schemas and TypeScript types for export, package, credential, webhook, and delivery contracts in `formcraft-frontend/src/app/shared/models/integration.models.ts`
- [X] T021 [P] Add Arabic and English i18n keys for export, recurring schedules, package import/export, credentials, webhooks, and delivery logs in `formcraft-frontend/src/assets/i18n/en.json`
- [X] T022 [P] Add Arabic and English i18n keys for export, recurring schedules, package import/export, credentials, webhooks, and delivery logs in `formcraft-frontend/src/assets/i18n/ar.json`
- [X] T023 Implement credential secret generation, hashing, prefixing, and one-time secret helpers in `formcraft-backend/app/services/integration_credential_service.py`
- [X] T024 Implement webhook signature generation and verification helper for timestamp plus payload HMAC in `formcraft-backend/app/services/webhook_service.py`
- [X] T025 Add admin navigation entries for Data Export and Integrations in `formcraft-frontend/src/app/shared/components/app-shell/app-shell.component.ts`

**Checkpoint**: Database, DTOs, security helpers, frontend models, translations, and routing are ready.

---

## Phase 3: User Story 1 - Export Submission Data (Priority: P1)

**Goal**: Admins can preview filtered submission exports, directly download allowed CSV/XLSX/JSON files, and receive clear rejection for oversized exports.

**Independent Test**: Choose submission filters, preview the matching count, download flattened CSV and structured JSON, verify records match filters, and verify oversized exports are rejected before generation.

### Tests for User Story 1

- [X] T026 [P] [US1] Write failing contract tests for `POST /api/admin/export/preview` count, warning, admin-only access, and oversized rejection metadata in `formcraft-backend/tests/integration/test_data_export_integration_routes.py`
- [X] T027 [P] [US1] Write failing contract tests for `POST /api/admin/export/download` CSV, XLSX, JSON, empty export, and HTTP 413 oversized responses in `formcraft-backend/tests/integration/test_data_export_integration_routes.py`
- [X] T028 [P] [US1] Write failing unit tests for submission filter query construction and org scoping in `formcraft-backend/tests/unit/test_export_service.py`
- [X] T029 [P] [US1] Write failing unit tests for flattened field-key columns, structured JSON, Arabic/mixed text preservation, and spreadsheet formula escaping in `formcraft-backend/tests/unit/test_export_service.py`
- [ ] T030 [P] [US1] Write failing frontend service tests for export preview and direct download calls in `formcraft-frontend/src/app/core/services/data-export.service.spec.ts`

### Implementation for User Story 1

- [X] T031 [US1] Implement org-scoped submission filtering by template, date range, department, branch, operator, and status in `formcraft-backend/app/services/export_service.py`
- [X] T032 [US1] Implement export preview matching count, estimated file size, unavailable-field warnings, and allowed-limit rejection logic in `formcraft-backend/app/services/export_service.py`
- [X] T033 [US1] Implement flattened CSV and XLSX generation with field-key headers, UTF-8 Arabic support, mixed-direction value preservation, and formula escaping in `formcraft-backend/app/services/export_service.py`
- [X] T034 [US1] Implement structured JSON export generation preserving submission field data and metadata in `formcraft-backend/app/services/export_service.py`
- [X] T035 [US1] Persist export request history and audit event `DATA_EXPORTED` or `DATA_EXPORT_REJECTED` in `formcraft-backend/app/services/export_service.py`
- [X] T036 [US1] Expose `POST /api/admin/export/preview`, `POST /api/admin/export/download`, and `GET /api/admin/export/history` with admin-only guards in `formcraft-backend/app/api/routes/admin_export.py`
- [X] T037 [US1] Implement Angular export preview, direct download, and history API methods in `formcraft-frontend/src/app/core/services/data-export.service.ts`
- [X] T038 [P] [US1] Create data export component class with filters, format/scope selection, preview state, rejection state, and download handlers in `formcraft-frontend/src/app/features/admin/data-export/data-export.component.ts`
- [X] T039 [P] [US1] Create data export template with translated filters, preview count, warnings, empty-state, oversized rejection, and download controls in `formcraft-frontend/src/app/features/admin/data-export/data-export.component.html`
- [X] T040 [P] [US1] Create data export styles with RTL/LTR-safe spacing, responsive filter layout, and stable table/action sizing in `formcraft-frontend/src/app/features/admin/data-export/data-export.component.scss`
- [X] T041 [US1] Wire Data Export component into `formcraft-frontend/src/app/features/admin/admin.module.ts`

**Checkpoint**: User Story 1 is functional and independently testable as the MVP.

---

## Phase 4: User Story 2 - Schedule Recurring Exports (Priority: P2)

**Goal**: Admins can create daily/weekly email-only export schedules, run them manually, and inspect delivery history/failures.

**Independent Test**: Create a weekly export schedule with email recipients, run it now, verify delivery history and no-data behavior, and confirm SFTP/file-transfer options are absent.

### Tests for User Story 2

- [ ] T042 [P] [US2] Write failing contract tests for `GET/POST/PATCH/DELETE /api/admin/export/schedules` email-only schedules and admin-only access in `formcraft-backend/tests/integration/test_data_export_integration_routes.py`
- [ ] T043 [P] [US2] Write failing contract tests for `POST /api/admin/export/schedules/{schedule_id}/run-now` delivery creation and failure response shape in `formcraft-backend/tests/integration/test_data_export_integration_routes.py`
- [ ] T044 [P] [US2] Write failing unit tests for daily/weekly next-run calculation, no-data behavior, email recipient validation, and SFTP rejection in `formcraft-backend/tests/unit/test_export_service.py`
- [ ] T045 [P] [US2] Write failing unit tests for recurring export email delivery summaries and failure history in `formcraft-backend/tests/unit/test_export_service.py`
- [ ] T046 [P] [US2] Write failing frontend service tests for export schedule CRUD and run-now calls in `formcraft-frontend/src/app/core/services/data-export.service.spec.ts`

### Implementation for User Story 2

- [X] T047 [US2] Implement export schedule CRUD with active/paused/disabled transitions, email-only validation, no-data behavior, and org scoping in `formcraft-backend/app/services/export_service.py`
- [X] T048 [US2] Implement recurring export execution using shared export generation and email delivery integration in `formcraft-backend/app/services/export_service.py`
- [X] T049 [US2] Implement export delivery records with queued/sent/failed status, attempt count, failure reason, sent timestamp, and audit events in `formcraft-backend/app/services/export_service.py`
- [X] T050 [US2] Expose schedule list/create/update/disable/run-now endpoints with admin-only guards in `formcraft-backend/app/api/routes/admin_export.py`
- [X] T051 [US2] Implement Angular export schedule CRUD, run-now, and delivery history methods in `formcraft-frontend/src/app/core/services/data-export.service.ts`
- [X] T052 [P] [US2] Create export schedules component class with schedule list, form state, frequency, recipients, no-data behavior, and run-now handling in `formcraft-frontend/src/app/features/admin/export-schedules/export-schedules.component.ts`
- [X] T053 [P] [US2] Create export schedules template with translated schedule table, email recipients, status controls, run-now action, and delivery history in `formcraft-frontend/src/app/features/admin/export-schedules/export-schedules.component.html`
- [X] T054 [P] [US2] Create export schedules styles with RTL/LTR-safe forms, tables, and status chips in `formcraft-frontend/src/app/features/admin/export-schedules/export-schedules.component.scss`
- [X] T055 [US2] Wire Export Schedules component into `formcraft-frontend/src/app/features/admin/admin.module.ts`

**Checkpoint**: User Story 2 is functional and independently testable without package or webhook work.

---

## Phase 5: User Story 3 - Move Templates Between Environments (Priority: P3)

**Goal**: Designers/admins can export `.formcraft` packages, review imports, create new drafts or new versions, and handle remapping warnings safely.

**Independent Test**: Export a template package, import it into a target org as a new draft when no match exists, import a matching package as a new version, and verify invalid packages are rejected without partial creation.

### Tests for User Story 3

- [ ] T056 [P] [US3] Write failing contract tests for `GET /api/templates/{template_id}/package` package response and template access rules in `formcraft-backend/tests/integration/test_data_export_integration_routes.py`
- [ ] T057 [P] [US3] Write failing contract tests for `POST /api/templates/package/import-review` and `POST /api/templates/package/import` new draft, new version, warning, and invalid package cases in `formcraft-backend/tests/integration/test_data_export_integration_routes.py`
- [ ] T058 [P] [US3] Write failing unit tests for package manifest, checksum, unsupported version rejection, and mm coordinate preservation in `formcraft-backend/tests/unit/test_template_package_service.py`
- [ ] T059 [P] [US3] Write failing unit tests for lineage/name match new-version import, new-draft import, missing reference warnings, and no partial creation on failure in `formcraft-backend/tests/unit/test_template_package_service.py`
- [ ] T060 [P] [US3] Write failing frontend service tests for package export, import review, and import calls in `formcraft-frontend/src/app/core/services/template.service.spec.ts`

### Implementation for User Story 3

- [X] T061 [US3] Implement template package export assembly with template, pages, elements, validators, conditions, reference bindings, manifest metadata, and checksum in `formcraft-backend/app/services/template_package_service.py`
- [X] T062 [US3] Implement package validation for checksum, package version, required sections, authorized access, and corrupted package rejection in `formcraft-backend/app/services/template_package_service.py`
- [X] T063 [US3] Implement package import review with lineage/name match detection, missing department/branch/reference/validator warnings, and remapping requirements in `formcraft-backend/app/services/template_package_service.py`
- [X] T064 [US3] Implement package import as new draft or new template version without replacing the currently published version in `formcraft-backend/app/services/template_package_service.py`
- [X] T065 [US3] Add audit events `TEMPLATE_PACKAGE_EXPORTED`, `TEMPLATE_PACKAGE_IMPORT_REVIEWED`, and `TEMPLATE_PACKAGE_IMPORTED` in `formcraft-backend/app/services/template_package_service.py`
- [X] T066 [US3] Expose package export, import-review, and import endpoints in `formcraft-backend/app/api/routes/templates.py`
- [X] T067 [US3] Extend Angular template API methods for package export, import review, and import in `formcraft-frontend/src/app/core/services/template.service.ts`
- [ ] T068 [P] [US3] Add package export action to existing template list or designer toolbar in `formcraft-frontend/src/app/features/templates/template-list/template-list.component.ts`
- [ ] T069 [P] [US3] Add package import review UI state and remapping warnings to template creation/import flow in `formcraft-frontend/src/app/features/templates/template-create-dialog/template-create-dialog.component.ts`
- [ ] T070 [P] [US3] Add translated package export/import controls and warning display in `formcraft-frontend/src/app/features/templates/template-list/template-list.component.html`
- [ ] T071 [P] [US3] Add translated package import review template in `formcraft-frontend/src/app/features/templates/template-create-dialog/template-create-dialog.component.html`

**Checkpoint**: User Story 3 is functional and independently testable without webhooks/API credentials.

---

## Phase 6: User Story 4 - Connect External Systems (Priority: P4)

**Goal**: Admins can create/revoke scoped integration credentials, configure signed webhook subscriptions, trigger/test deliveries, and inspect full-payload delivery logs.

**Independent Test**: Create a credential and verify the secret is shown once, revoke it and verify access stops, configure a signed webhook, trigger/test a delivery, and verify retries plus full payload preview in admin-only logs.

### Tests for User Story 4

- [ ] T072 [P] [US4] Write failing contract tests for credential list/create/rotate/revoke, one-time secret response, and admin-only access in `formcraft-backend/tests/integration/test_data_export_integration_routes.py`
- [ ] T073 [P] [US4] Write failing contract tests for webhook list/create/update/test/delivery-log endpoints, required signing secret, and full payload preview response in `formcraft-backend/tests/integration/test_data_export_integration_routes.py`
- [ ] T074 [P] [US4] Write failing unit tests for credential hashing, prefixing, scope checks, expiry, last-used updates, and immediate revoke in `formcraft-backend/tests/unit/test_webhook_service.py`
- [ ] T075 [P] [US4] Write failing unit tests for webhook HMAC signature, active-secret requirement, retry backoff, three-attempt failure, and admin-only payload preview access in `formcraft-backend/tests/unit/test_webhook_service.py`
- [ ] T076 [P] [US4] Write failing frontend service tests for credential and webhook API calls in `formcraft-frontend/src/app/core/services/integration.service.spec.ts`

### Implementation for User Story 4

- [X] T077 [US4] Implement integration credential create/list/rotate/revoke with hashed secrets, scopes, expiry, last-used tracking, immediate revocation, and audit events in `formcraft-backend/app/services/integration_credential_service.py`
- [ ] T078 [US4] Implement integration credential authentication/scope dependency for future external API access in `formcraft-backend/app/api/deps.py`
- [X] T079 [US4] Implement webhook subscription create/list/update with signing-secret requirement, HTTPS URL validation, active/paused/disabled states, and audit events in `formcraft-backend/app/services/webhook_service.py`
- [X] T080 [US4] Implement webhook payload construction for form submitted, form printed, template published, and batch completed events in `formcraft-backend/app/services/webhook_service.py`
- [X] T081 [US4] Implement signed webhook delivery dispatch, delivery log persistence with full payload preview, response summary capture, and retry scheduling in `formcraft-backend/app/services/webhook_service.py`
- [ ] T082 [US4] Hook `form_submitted` webhook dispatch into submission creation flow in `formcraft-backend/app/services/submission_service.py`
- [ ] T083 [US4] Hook `template_published` webhook dispatch into template status transition flow in `formcraft-backend/app/services/template_service.py`
- [X] T084 [US4] Expose credential, webhook subscription, test delivery, and delivery-log endpoints with admin-only guards in `formcraft-backend/app/api/routes/integrations.py`
- [X] T085 [US4] Implement Angular integration credential and webhook API methods in `formcraft-frontend/src/app/core/services/integration.service.ts`
- [X] T086 [P] [US4] Create integration credentials component with list, create, one-time secret reveal, rotate, and revoke flows in `formcraft-frontend/src/app/features/admin/integrations/integration-credentials.component.ts`
- [X] T087 [P] [US4] Create webhook subscriptions component with list, create/update, signing secret, pause/disable, and test delivery flows in `formcraft-frontend/src/app/features/admin/integrations/webhook-subscriptions.component.ts`
- [X] T088 [P] [US4] Create webhook deliveries component with full payload preview, response summary, retry status, and admin-only warning states in `formcraft-frontend/src/app/features/admin/integrations/webhook-deliveries.component.ts`
- [X] T089 [P] [US4] Create integrations styles with RTL/LTR-safe tables, secret reveal panels, payload preview, and status chips in `formcraft-frontend/src/app/features/admin/integrations/integrations.component.scss`
- [X] T090 [US4] Wire Integrations components into `formcraft-frontend/src/app/features/admin/admin.module.ts`

**Checkpoint**: User Story 4 is functional and independently testable.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validate constitution compliance, security, performance, documentation, and full quickstart flow.

- [ ] T091 [P] Verify no hardcoded user-facing strings were introduced in `formcraft-frontend/src/app/features/admin/data-export/`
- [ ] T092 [P] Verify no hardcoded user-facing strings were introduced in `formcraft-frontend/src/app/features/admin/export-schedules/`
- [ ] T093 [P] Verify no hardcoded user-facing strings were introduced in `formcraft-frontend/src/app/features/admin/integrations/`
- [ ] T094 [P] Verify RTL and LTR layouts for export filters, schedules, package import review, credentials, and webhook delivery logs in `formcraft-frontend/src/app/features/admin/`
- [ ] T095 [P] Add or update quickstart API smoke examples and implementation notes in `formcraft-specs/specs/032-data-export-integration/quickstart.md`
- [ ] T096 Run backend F32 tests in `formcraft-backend/tests/unit/test_export_service.py`, `formcraft-backend/tests/unit/test_template_package_service.py`, `formcraft-backend/tests/unit/test_webhook_service.py`, and `formcraft-backend/tests/integration/test_data_export_integration_routes.py`
- [ ] T097 Run backend lint with `ruff check .` in `formcraft-backend/`
- [ ] T098 Run frontend build with `npm run build` in `formcraft-frontend/`
- [ ] T099 Manually validate all quickstart scenarios from direct export through recurring email, package import/export, credentials, and signed webhooks using `formcraft-specs/specs/032-data-export-integration/quickstart.md`
- [ ] T100 Update implementation status and any known gaps in `formcraft-specs/specs/032-data-export-integration/tasks.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational; recommended MVP.
- **User Story 2 (Phase 4)**: Depends on Foundational and reuses export generation from US1 service concepts, but remains testable through schedule run-now.
- **User Story 3 (Phase 5)**: Depends on Foundational and can run independently of US1/US2 after schemas and template routes exist.
- **User Story 4 (Phase 6)**: Depends on Foundational and can run independently of exports/packages after shared integration schemas exist.
- **Polish (Phase 7)**: Depends on desired user stories being complete.

### User Story Dependencies

- **US1 Export Submission Data**: MVP; no dependency on other stories.
- **US2 Schedule Recurring Exports**: Reuses export generation concepts from US1 but can be implemented after Foundational with a run-now path.
- **US3 Move Templates Between Environments**: Independent template-package slice.
- **US4 Connect External Systems**: Independent integrations slice, with event hooks added to existing services.

### Within Each User Story

- Write tests first and confirm they fail.
- Implement backend schemas before services.
- Implement services before routes.
- Implement Angular models/services before components.
- Add i18n keys before final UI validation.
- Audit logging must be added before story checkpoint validation.

---

## Parallel Execution Examples

### User Story 1

```bash
Task: "T026 contract tests for POST /api/admin/export/preview"
Task: "T027 contract tests for POST /api/admin/export/download"
Task: "T028 unit tests for submission filter query construction"
Task: "T029 unit tests for file generation and Arabic/formula handling"
Task: "T030 frontend service tests for export calls"
```

```bash
Task: "T038 data export component class"
Task: "T039 data export component template"
Task: "T040 data export component styles"
```

### User Story 2

```bash
Task: "T042 schedule CRUD contract tests"
Task: "T043 run-now contract tests"
Task: "T044 schedule calculation and validation unit tests"
Task: "T045 email delivery history unit tests"
Task: "T046 frontend schedule service tests"
```

```bash
Task: "T052 export schedules component class"
Task: "T053 export schedules template"
Task: "T054 export schedules styles"
```

### User Story 3

```bash
Task: "T056 package export contract tests"
Task: "T057 package import contract tests"
Task: "T058 package manifest/checksum unit tests"
Task: "T059 package import mode/remapping unit tests"
Task: "T060 frontend package service tests"
```

```bash
Task: "T068 template list package export action"
Task: "T069 package import review UI state"
Task: "T070 package export/import controls"
Task: "T071 package import review template"
```

### User Story 4

```bash
Task: "T072 credential contract tests"
Task: "T073 webhook contract tests"
Task: "T074 credential security unit tests"
Task: "T075 webhook signing/retry unit tests"
Task: "T076 frontend integration service tests"
```

```bash
Task: "T086 credential component"
Task: "T087 webhook subscription component"
Task: "T088 webhook delivery component"
Task: "T089 integrations styles"
```

---

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 for User Story 1.
3. Validate export preview, direct CSV/XLSX/JSON downloads, empty exports, oversized rejection, Arabic/mixed text preservation, formula escaping, export history, and audit logs.
4. Stop for review/demo before adding recurring schedules, packages, or external integrations.

### Incremental Delivery

1. Deliver US1: Direct submission exports.
2. Deliver US2: Email-only recurring export schedules.
3. Deliver US3: Template package export/import portability.
4. Deliver US4: Scoped integration credentials and signed webhooks.
5. Run Phase 7 checks after each story if shipping incrementally.

### Constitution Reminders

- Keep all UI strings in `en.json` and `ar.json`.
- Test RTL and LTR layouts before merge.
- Preserve exact mm positions in template packages.
- Do not add AI, OCR, SFTP, file-transfer destinations, pre-built connectors, custom connector builder, or a general automation engine.
- Store integration credentials and signing secrets only as hashes/prefix metadata.
- Restrict full webhook payload previews to authorized org admins.
- Preserve Supabase RLS, authenticated admin-only access, org scoping, and audit logs for all F32 actions.

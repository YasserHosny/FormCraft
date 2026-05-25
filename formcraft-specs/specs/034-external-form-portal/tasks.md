# Tasks: External Form Portal

**Input**: Design documents from `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-specs/specs/034-external-form-portal/`
**Prerequisites**: [plan.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/034-external-form-portal/plan.md), [spec.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/034-external-form-portal/spec.md), [research.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/034-external-form-portal/research.md), [data-model.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/034-external-form-portal/data-model.md), [contracts/openapi.yaml](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/034-external-form-portal/contracts/openapi.yaml), [quickstart.md](/media/yasserhosny/My%20Passport/Work/Projects/FormCraft/formcraft-specs/specs/034-external-form-portal/quickstart.md)

**Tests**: Required by the FormCraft Constitution. Test tasks must be written first and fail before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup

**Purpose**: Create route, schema, service, model, and UI placeholders for the portal surface.

- [ ] T001 Create public portal backend route placeholder in `formcraft-backend/app/api/routes/public_portal.py`
- [ ] T002 Create admin portal backend route placeholder in `formcraft-backend/app/api/routes/admin_portal.py`
- [ ] T003 Register public portal and admin portal routers in `formcraft-backend/app/main.py`
- [ ] T004 [P] Create portal schema placeholder in `formcraft-backend/app/schemas/portal.py`
- [ ] T005 [P] Create portal orchestration service placeholder in `formcraft-backend/app/services/portal_service.py`
- [ ] T006 [P] Create portal OTP service placeholder in `formcraft-backend/app/services/portal_otp_service.py`
- [ ] T007 [P] Create portal rate limit service placeholder in `formcraft-backend/app/services/portal_rate_limit_service.py`
- [ ] T008 [P] Create CAPTCHA service placeholder in `formcraft-backend/app/services/captcha_service.py`
- [ ] T009 [P] Create frontend portal API service placeholder in `formcraft-frontend/src/app/core/services/portal.service.ts`
- [ ] T010 [P] Create frontend portal Zod model placeholder in `formcraft-frontend/src/app/shared/models/portal.models.ts`
- [ ] T011 Create public portal Angular module and route shell in `formcraft-frontend/src/app/features/public-portal/public-portal.module.ts`
- [ ] T012 Create admin portal component placeholder in `formcraft-frontend/src/app/features/admin/portal/portal-admin.component.ts`
- [ ] T013 Wire public portal and admin portal routes in `formcraft-frontend/src/app/app-routing.module.ts` and `formcraft-frontend/src/app/features/admin/admin.module.ts`

---

## Phase 2: Foundational

**Purpose**: Shared persistence, DTOs, security helpers, provider adapters, translations, and contract scaffolding required by all stories.

**Critical**: No user story implementation should begin until this phase is complete.

- [ ] T014 Write failing migration validation tests for portal configuration, session, OTP, rate-limit, metadata tables, indexes, audit fields, and RLS policies in `formcraft-backend/tests/integration/test_external_form_portal_routes.py`
- [ ] T015 Create Supabase migration for `portal_configurations`, `portal_sessions`, `portal_otp_verifications`, `portal_rate_limit_events`, and `public_submission_metadata` in `formcraft-backend/migrations/035_external_form_portal.sql`
- [ ] T016 Implement Pydantic DTOs for public form load, portal-session-token errors, OTP, submission, email confirmation, admin configuration, QR, and analytics contracts in `formcraft-backend/app/schemas/portal.py`
- [ ] T017 [P] Implement frontend Zod schemas and TypeScript types for public form, portal-session-token errors, OTP, submission, email confirmation, admin configuration, QR, and analytics contracts in `formcraft-frontend/src/app/shared/models/portal.models.ts`
- [ ] T018 [P] Add Arabic i18n keys for public portal, OTP gate, confirmation, email confirmation status, admin portal, QR actions, errors, and rate-limit messages in `formcraft-frontend/src/assets/i18n/ar.json`
- [ ] T019 [P] Add English i18n keys for public portal, OTP gate, confirmation, email confirmation status, admin portal, QR actions, errors, and rate-limit messages in `formcraft-frontend/src/assets/i18n/en.json`
- [ ] T020 Implement hashing helpers and validation dependencies for session tokens, contacts, IP addresses, browser/session keys, OTP codes, and PDF tokens in `formcraft-backend/app/services/portal_service.py`
- [ ] T021 Implement portal configuration lookup, public URL slug resolution, and enabled/published-template guards in `formcraft-backend/app/services/portal_service.py`
- [ ] T022 Implement session creation with pinned template version, expiry, status transitions, and duplicate-submit guard in `formcraft-backend/app/services/portal_service.py`
- [ ] T023 Implement CAPTCHA verification adapter with hCaptcha/reCAPTCHA provider selection and mocked provider support in `formcraft-backend/app/services/captcha_service.py`
- [ ] T024 Implement portal rate-limit key derivation and event recording helpers for pre-OTP and verified-contact limits in `formcraft-backend/app/services/portal_rate_limit_service.py`
- [ ] T025 Add backend audit helpers for public portal events with bounded/redacted field summaries in `formcraft-backend/app/services/portal_service.py`
- [ ] T026 Add admin navigation entry for Portal in `formcraft-frontend/src/app/shared/components/app-shell/app-shell.component.ts`
- [ ] T027 Create frontend public portal shared layout styles with RTL/LTR-safe responsive Flow Layout primitives in `formcraft-frontend/src/app/features/public-portal/public-portal.scss`
- [ ] T028 Validate `formcraft-specs/specs/034-external-form-portal/contracts/openapi.yaml` against generated DTO names, route prefixes, portal-session-token requirements, QR fields, and email confirmation fields in `formcraft-specs/specs/034-external-form-portal/contracts/openapi.yaml`

**Checkpoint**: Database, schemas, translations, providers, route shells, and shared portal infrastructure are ready.

---

## Phase 3: User Story 1 - Public Form Access & Submission (Priority: P1) MVP

**Goal**: External users can open a public form URL, fill a responsive Arabic-first Flow Layout form with validation/conditions/tafqeet parity, submit once, and receive a confirmation reference number with optional PDF download and email confirmation status.

**Independent Test**: Open a public form URL in an incognito browser, fill all fields, submit, receive confirmation with reference number, and verify pinned template version and public source metadata.

### Tests for User Story 1

- [ ] T029 [P] [US1] Write failing contract tests for `GET /api/public/forms/{org_slug}/{public_slug}` success, disabled form, unpublished template, opaque session token, and pinned version in `formcraft-backend/tests/integration/test_external_form_portal_routes.py`
- [ ] T030 [P] [US1] Write failing contract tests for `POST /api/public/forms/{session_token}/submit` validation errors, invalid/expired session token, duplicate submit conflict, CAPTCHA-required failure, email confirmation status, and confirmation response in `formcraft-backend/tests/integration/test_external_form_portal_routes.py`
- [ ] T031 [P] [US1] Write failing contract tests for `GET /api/public/submissions/{reference_number}/pdf` enabled, disabled, invalid download token, and pinned-version PDF responses in `formcraft-backend/tests/integration/test_external_form_portal_routes.py`
- [ ] T032 [P] [US1] Write failing unit tests for public form config lookup, session version pinning, duplicate-submit protection, and public URL slug resolution in `formcraft-backend/tests/unit/test_portal_service.py`
- [ ] T033 [P] [US1] Write failing unit tests for validation parity, conditional visibility, tafqeet computation, audit-safe field summary, email confirmation status/failure persistence, and public submission metadata persistence in `formcraft-backend/tests/unit/test_portal_service.py`
- [ ] T034 [P] [US1] Write failing frontend service tests for public form load, submit, and PDF download methods in `formcraft-frontend/src/app/core/services/portal.service.spec.ts`
- [ ] T035 [P] [US1] Write failing frontend component tests for Flow Layout rendering, Arabic/LTR toggle, validation display, tafqeet display, and confirmation state in `formcraft-frontend/src/app/features/public-portal/public-form-page/public-form-page.component.spec.ts`

### Implementation for User Story 1

- [ ] T036 [US1] Implement public form load contract and response shaping in `formcraft-backend/app/api/routes/public_portal.py`
- [ ] T037 [US1] Implement public form session creation, pinned template read model assembly, and cache-safe response metadata in `formcraft-backend/app/services/portal_service.py`
- [ ] T038 [US1] Implement public submission orchestration with portal-session-token validation, validation/condition/tafqeet parity, and single-submit session transition in `formcraft-backend/app/services/portal_service.py`
- [ ] T039 [US1] Implement public submission insert plus `public_submission_metadata` persistence with `source = public_portal`, email confirmation status, and email confirmation failure reason in `formcraft-backend/app/services/portal_service.py`
- [ ] T040 [US1] Implement bounded/redacted audit event creation for public submission success, validation failures, and email confirmation failures in `formcraft-backend/app/services/portal_service.py`
- [ ] T041 [US1] Implement optional PDF download token creation and pinned-version PDF route in `formcraft-backend/app/api/routes/public_portal.py`
- [ ] T042 [US1] Implement public form load, submit, and PDF download API methods in `formcraft-frontend/src/app/core/services/portal.service.ts`
- [ ] T043 [P] [US1] Create public form page component class with session state, language toggle, validation state, tafqeet state, submit state, and duplicate-submit handling in `formcraft-frontend/src/app/features/public-portal/public-form-page/public-form-page.component.ts`
- [ ] T044 [P] [US1] Create public form page template with translated Flow Layout fields, validation messages, language toggle, submit controls, and responsive empty/error states in `formcraft-frontend/src/app/features/public-portal/public-form-page/public-form-page.component.html`
- [ ] T045 [P] [US1] Create public form page styles with Arabic-first responsive layout, `dir="auto"` field values, stable controls, and mobile constraints in `formcraft-frontend/src/app/features/public-portal/public-form-page/public-form-page.component.scss`
- [ ] T046 [P] [US1] Create confirmation page component class and route handling for reference number and optional PDF link in `formcraft-frontend/src/app/features/public-portal/confirmation-page/confirmation-page.component.ts`
- [ ] T047 [P] [US1] Create confirmation page template and styles with translated reference number, PDF action, email confirmation status, and support guidance in `formcraft-frontend/src/app/features/public-portal/confirmation-page/confirmation-page.component.html` and `formcraft-frontend/src/app/features/public-portal/confirmation-page/confirmation-page.component.scss`
- [ ] T048 [US1] Wire public form and confirmation child routes in `formcraft-frontend/src/app/features/public-portal/public-portal.module.ts`

**Checkpoint**: User Story 1 is functional and independently testable as the MVP.

---

## Phase 4: User Story 2 - OTP Verification for External Submissions (Priority: P2)

**Goal**: Admin-enabled OTP gates force external users to choose an allowed SMS/email mode, verify successfully, fail closed during provider outages, and lock after three invalid attempts.

**Independent Test**: Open an OTP-gated form, choose an allowed contact mode, request OTP, verify successfully to access the form, and confirm invalid attempts/provider outages block access.

### Tests for User Story 2

- [ ] T049 [P] [US2] Write failing contract tests for `POST /api/public/forms/{session_token}/otp/send` allowed modes, disallowed modes, invalid/expired session token, provider failure, and locked-session responses in `formcraft-backend/tests/integration/test_external_form_portal_routes.py`
- [ ] T050 [P] [US2] Write failing contract tests for `POST /api/public/forms/{session_token}/otp/verify` valid code, invalid code, invalid/expired session token, expiry, third-failure lockout, and verified session state in `formcraft-backend/tests/integration/test_external_form_portal_routes.py`
- [ ] T051 [P] [US2] Write failing unit tests for OTP generation, hashing, expiry, latest-challenge selection, three-attempt lockout, and provider failure status in `formcraft-backend/tests/unit/test_portal_otp_service.py`
- [ ] T052 [P] [US2] Write failing frontend service tests for OTP send and verify calls in `formcraft-frontend/src/app/core/services/portal.service.spec.ts`
- [ ] T053 [P] [US2] Write failing frontend component tests for allowed-mode selection, invalid-code errors, lockout timer, provider outage message, and verified transition in `formcraft-frontend/src/app/features/public-portal/otp-gate/otp-gate.component.spec.ts`

### Implementation for User Story 2

- [ ] T054 [US2] Implement SMS/email OTP provider interface, development mock provider, and provider unavailable result handling in `formcraft-backend/app/services/portal_otp_service.py`
- [ ] T055 [US2] Implement OTP send flow with allowed-mode validation, contact hashing, code hashing, expiry, provider failure persistence, and audit event in `formcraft-backend/app/services/portal_otp_service.py`
- [ ] T056 [US2] Implement OTP verify flow with latest pending challenge, attempt increment, three-attempt 15-minute lockout, and session transition to `otp_verified` in `formcraft-backend/app/services/portal_otp_service.py`
- [ ] T057 [US2] Expose OTP send and verify endpoints with fail-closed provider outage behavior in `formcraft-backend/app/api/routes/public_portal.py`
- [ ] T058 [US2] Enforce OTP-gated session access before public form submit in `formcraft-backend/app/services/portal_service.py`
- [ ] T059 [US2] Implement frontend OTP send and verify API methods in `formcraft-frontend/src/app/core/services/portal.service.ts`
- [ ] T060 [P] [US2] Create OTP gate component class with allowed-mode selection, contact input, send state, verify state, lockout state, and provider outage state in `formcraft-frontend/src/app/features/public-portal/otp-gate/otp-gate.component.ts`
- [ ] T061 [P] [US2] Create OTP gate template with translated SMS/email mode selection, code entry, retry/support messages, and lockout timer in `formcraft-frontend/src/app/features/public-portal/otp-gate/otp-gate.component.html`
- [ ] T062 [P] [US2] Create OTP gate styles with RTL/LTR-safe form controls and mobile-friendly spacing in `formcraft-frontend/src/app/features/public-portal/otp-gate/otp-gate.component.scss`
- [ ] T063 [US2] Integrate OTP gate before public form rendering in `formcraft-frontend/src/app/features/public-portal/public-form-page/public-form-page.component.ts`

**Checkpoint**: User Story 2 is functional and independently testable with US1.

---

## Phase 5: User Story 3 - Admin Portal Configuration (Priority: P3)

**Goal**: Admins can enable/disable public access per template, configure OTP/CAPTCHA/rate limits/PDF/email options, view generated public URLs and QR codes, and inspect portal analytics.

**Independent Test**: Navigate to `/admin/portal`, configure a published template with OTP + CAPTCHA + rate limits, verify public behavior changes, preview/download the QR code, and view portal analytics.

### Tests for User Story 3

- [ ] T064 [P] [US3] Write failing contract tests for `GET /api/admin/portal/templates` list, admin-only access, URL generation, QR code field, and configuration shape in `formcraft-backend/tests/integration/test_external_form_portal_routes.py`
- [ ] T065 [P] [US3] Write failing contract tests for `GET/PATCH /api/admin/portal/templates/{template_id}` enabled/disabled transitions, published-template guard, OTP modes, CAPTCHA provider, rate-limit validation, and slug uniqueness in `formcraft-backend/tests/integration/test_external_form_portal_routes.py`
- [ ] T066 [P] [US3] Write failing contract tests for `GET /api/admin/portal/analytics` submission counts, OTP failures, email confirmation failures, and rate-limited counts in `formcraft-backend/tests/integration/test_external_form_portal_routes.py`
- [ ] T067 [P] [US3] Write failing unit tests for portal configuration validation, custom-domain/default URL generation, derived QR code generation, slug uniqueness, and admin audit events in `formcraft-backend/tests/unit/test_portal_service.py`
- [ ] T068 [P] [US3] Write failing unit tests for pre-OTP and verified-contact rate-limit counters, shared-IP false-positive avoidance, burst denial, and event persistence in `formcraft-backend/tests/unit/test_portal_rate_limit_service.py`
- [ ] T069 [P] [US3] Write failing frontend service tests for admin portal list, update, and analytics calls in `formcraft-frontend/src/app/core/services/portal.service.spec.ts`
- [ ] T070 [P] [US3] Write failing frontend component tests for admin portal configuration form, generated URL display, QR preview/download, OTP/CAPTCHA/rate-limit controls, and analytics panels in `formcraft-frontend/src/app/features/admin/portal/portal-admin.component.spec.ts`

### Implementation for User Story 3

- [ ] T071 [US3] Implement admin portal list, get, update, derived QR generation, and analytics service methods including email confirmation failure counts in `formcraft-backend/app/services/portal_service.py`
- [ ] T072 [US3] Implement configuration validation for published templates, slug uniqueness, OTP modes, CAPTCHA provider, PDF/email flags, and rate-limit bounds in `formcraft-backend/app/services/portal_service.py`
- [ ] T073 [US3] Implement custom-domain/default public URL generation and derived QR code generation in `formcraft-backend/app/services/portal_service.py`
- [ ] T074 [US3] Implement admin audit events for portal enable, disable, and configuration changes in `formcraft-backend/app/services/portal_service.py`
- [ ] T075 [US3] Expose admin portal list, get, update, and analytics endpoints with admin-only guards in `formcraft-backend/app/api/routes/admin_portal.py`
- [ ] T076 [US3] Enforce public load, OTP send, and submit rate-limit checks using portal configuration limits in `formcraft-backend/app/services/portal_rate_limit_service.py` and `formcraft-backend/app/services/portal_service.py`
- [ ] T077 [US3] Implement CAPTCHA verification on public submit when enabled in `formcraft-backend/app/services/captcha_service.py` and `formcraft-backend/app/services/portal_service.py`
- [ ] T078 [US3] Implement frontend admin portal list, update, QR display/download, and analytics API methods in `formcraft-frontend/src/app/core/services/portal.service.ts`
- [ ] T079 [P] [US3] Create admin portal component class with template list, configuration form, URL generation display, QR preview/download state, analytics state, and save validation in `formcraft-frontend/src/app/features/admin/portal/portal-admin.component.ts`
- [ ] T080 [P] [US3] Create admin portal template with translated enable toggle, OTP modes, CAPTCHA provider, PDF/email options, rate-limit controls, URL display, QR preview/download, and analytics panels in `formcraft-frontend/src/app/features/admin/portal/portal-admin.component.html`
- [ ] T081 [P] [US3] Create admin portal styles with RTL/LTR-safe dense admin layout, stable controls, and responsive analytics panels in `formcraft-frontend/src/app/features/admin/portal/portal-admin.component.scss`
- [ ] T082 [US3] Wire admin portal child route into `formcraft-frontend/src/app/features/admin/admin.module.ts`

**Checkpoint**: User Story 3 is functional and independently testable with US1/US2.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate constitution compliance, security, performance, documentation, and full quickstart flow.

- [ ] T083 [P] Verify no hardcoded user-facing strings were introduced in `formcraft-frontend/src/app/features/public-portal/`
- [ ] T084 [P] Verify no hardcoded user-facing strings were introduced in `formcraft-frontend/src/app/features/admin/portal/`
- [ ] T085 [P] Verify RTL and LTR layouts for public form, OTP gate, confirmation page, and admin portal in `formcraft-frontend/src/app/features/public-portal/` and `formcraft-frontend/src/app/features/admin/portal/`
- [ ] T086 [P] Verify public submission audit entries contain metadata plus bounded/redacted summaries, email confirmation failure metadata, and no full raw field payloads in `formcraft-backend/tests/unit/test_portal_service.py`
- [ ] T087 [P] Add or update quickstart smoke examples and implementation notes in `formcraft-specs/specs/034-external-form-portal/quickstart.md`
- [ ] T088 Run backend F034 tests in `formcraft-backend/tests/unit/test_portal_service.py`, `formcraft-backend/tests/unit/test_portal_otp_service.py`, `formcraft-backend/tests/unit/test_portal_rate_limit_service.py`, and `formcraft-backend/tests/integration/test_external_form_portal_routes.py`
- [ ] T089 Run backend lint with `ruff check .` in `formcraft-backend/`
- [ ] T090 Run frontend build with `npm run build` in `formcraft-frontend/`
- [ ] T091 Manually validate all quickstart scenarios from public access through OTP, rate limits, template update pinning, QR download, email confirmation, and admin configuration using `formcraft-specs/specs/034-external-form-portal/quickstart.md`
- [ ] T092 Update implementation status and any known gaps in `formcraft-specs/specs/034-external-form-portal/tasks.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational; recommended MVP.
- **User Story 2 (Phase 4)**: Depends on Foundational and integrates into public form access, but OTP send/verify is independently testable.
- **User Story 3 (Phase 5)**: Depends on Foundational; admin configuration can be implemented after US1 or in parallel once route/service shells exist.
- **Polish (Phase 6)**: Depends on desired user stories being complete.

### User Story Dependencies

- **US1 Public Form Access & Submission**: MVP; no dependency on other stories.
- **US2 OTP Verification**: Builds on portal sessions from Foundational and gates US1 form access.
- **US3 Admin Portal Configuration**: Controls settings consumed by US1/US2 and can be tested with mocked settings or after US1.

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
Task: "T029 contract tests for public form load"
Task: "T030 contract tests for public submit"
Task: "T031 contract tests for public PDF download"
Task: "T032 unit tests for config lookup and session pinning"
Task: "T033 unit tests for validation parity and metadata"
Task: "T034 frontend service tests for load/submit/PDF"
Task: "T035 frontend component tests for Flow Layout"
```

```bash
Task: "T043 public form component class"
Task: "T044 public form template"
Task: "T045 public form styles"
Task: "T046 confirmation component class"
Task: "T047 confirmation template and styles"
```

### User Story 2

```bash
Task: "T049 OTP send contract tests"
Task: "T050 OTP verify contract tests"
Task: "T051 OTP service unit tests"
Task: "T052 OTP frontend service tests"
Task: "T053 OTP gate component tests"
```

```bash
Task: "T060 OTP gate component class"
Task: "T061 OTP gate template"
Task: "T062 OTP gate styles"
```

### User Story 3

```bash
Task: "T064 admin portal list contract tests"
Task: "T065 admin portal update contract tests"
Task: "T066 admin portal analytics contract tests"
Task: "T067 portal configuration unit tests"
Task: "T068 rate-limit service unit tests"
Task: "T069 admin portal frontend service tests"
Task: "T070 admin portal component tests"
```

```bash
Task: "T079 admin portal component class"
Task: "T080 admin portal template"
Task: "T081 admin portal styles"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Stop and validate incognito public URL load, validation parity, submit, reference confirmation, optional PDF, pinned template version, and public source metadata.

### Incremental Delivery

1. Deliver US1 to prove accountless public submission end to end.
2. Add US2 to secure sensitive public forms with OTP and fail-closed provider behavior.
3. Add US3 so admins can manage exposure, abuse controls, and portal analytics without developer intervention.

### Team Parallelism

- Backend and frontend test tasks can be split by story after Phase 2.
- US2 OTP services/components can proceed in parallel with US3 admin UI once shared portal DTOs and translations are in place.

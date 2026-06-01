# Tasks: New-Theme Admin Pages - Export, Portal, Integration

**Input**: Design documents from `formcraft-specs/specs/055-spark3-missing-pages/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/admin-pages-contract.md`, `quickstart.md`

## Phase 1: Setup

- [ ] T001 Inspect existing Spark 3 admin route/navigation patterns in `formcraft-frontend/src/app/features/ui-redesign/ui-redesign.routes.ts`
- [ ] T002 Inspect existing Spark 3 Analytics styling conventions in `formcraft-frontend/src/app/features/ui-redesign/admin/analytics.component.scss`
- [ ] T003 Inspect classic Export/Portal/Integrations behavior for parity in `formcraft-frontend/src/app/features/admin/`
- [ ] T004 Confirm available translation key namespaces in `formcraft-frontend/src/assets/i18n/en.json`

## Phase 2: Foundational

- [ ] T005 Add failing route coverage for `/ui/admin/export`, `/ui/admin/portal`, and `/ui/admin/integrations` in `formcraft-frontend/src/app/features/ui-redesign/ui-redesign.routes.spec.ts`
- [ ] T006 Add failing toolbar navigation coverage for Export, Portal, and Integration tabs targeting `/ui/admin/*` in `formcraft-frontend/src/app/features/ui-redesign/shell/toolbar.component.spec.ts`
- [ ] T007 Add Spark 3 admin translation keys for shared loading/error/empty/action states in `formcraft-frontend/src/assets/i18n/en.json`
- [ ] T008 Add matching Arabic Spark 3 admin translation keys in `formcraft-frontend/src/assets/i18n/ar.json`
- [ ] T009 Replace classic admin toolbar routes with `/ui/admin/export`, `/ui/admin/portal`, and `/ui/admin/integrations` in `formcraft-frontend/src/app/features/ui-redesign/shell/toolbar.component.ts`
- [ ] T010 Add failing non-admin redirect expectation to `/ui/dashboard` for F055 admin routes in `formcraft-frontend/src/app/features/ui-redesign/ui-redesign.routes.spec.ts`

## Phase 3: User Story 1 - Data Export Page (Priority: P1)

**Goal**: Admins can preview, download, and review export history from a new-theme `/ui/admin/export` page.

**Independent Test**: Navigate to `/ui/admin/export` as admin, preview filtered export data, verify oversized results disable Download, download an eligible result, and see export history in the new-theme layout.

- [ ] T011 [P] [US1] Add failing component tests for export initial load, preview success, oversized disablement, download, history empty/error states in `formcraft-frontend/src/app/features/ui-redesign/admin/export.component.spec.ts`
- [ ] T012 [P] [US1] Add Export page translation keys for filters, formats, scopes, preview, download, history, warnings, and errors in `formcraft-frontend/src/assets/i18n/en.json`
- [ ] T013 [P] [US1] Add Arabic Export page translation keys in `formcraft-frontend/src/assets/i18n/ar.json`
- [ ] T014 [US1] Implement Export page component state and `DataExportService` interactions in `formcraft-frontend/src/app/features/ui-redesign/admin/export.component.ts`
- [ ] T015 [US1] Implement Export page template with filter form, preview panel, download controls, history table, loading/error/empty states in `formcraft-frontend/src/app/features/ui-redesign/admin/export.component.html`
- [ ] T016 [US1] Implement Export page Spark 3/RTL responsive styles in `formcraft-frontend/src/app/features/ui-redesign/admin/export.component.scss`
- [ ] T017 [US1] Wire Export page lazy route to `ExportComponent` in `formcraft-frontend/src/app/features/ui-redesign/ui-redesign.routes.ts`
- [ ] T018 [US1] Verify Export page tests pass and no raw translation keys render in `formcraft-frontend/src/app/features/ui-redesign/admin/export.component.spec.ts`

## Phase 4: User Story 2 - Public Portal Management Page (Priority: P2)

**Goal**: Admins can manage existing public portal settings per template from a new-theme `/ui/admin/portal` page.

**Independent Test**: Navigate to `/ui/admin/portal` as admin, select a template, edit portal settings, save successfully, verify URL/QR/analytics display, and see inline translated failures.

- [ ] T019 [P] [US2] Add failing component tests for portal template list, selection, save success/failure, OTP visibility, URL/QR, analytics, empty/error states in `formcraft-frontend/src/app/features/ui-redesign/admin/portal.component.spec.ts`
- [ ] T020 [P] [US2] Add Portal page translation keys for template list, configuration fields, OTP/captcha/rate-limit, URL/QR, analytics, save states in `formcraft-frontend/src/assets/i18n/en.json`
- [ ] T021 [P] [US2] Add Arabic Portal page translation keys in `formcraft-frontend/src/assets/i18n/ar.json`
- [ ] T022 [US2] Implement Portal page component state and `PortalService` interactions in `formcraft-frontend/src/app/features/ui-redesign/admin/portal.component.ts`
- [ ] T023 [US2] Implement Portal page template with template list, configuration panel, URL copy, QR rendering, analytics, loading/error/empty states in `formcraft-frontend/src/app/features/ui-redesign/admin/portal.component.html`
- [ ] T024 [US2] Implement Portal page Spark 3/RTL responsive styles in `formcraft-frontend/src/app/features/ui-redesign/admin/portal.component.scss`
- [ ] T025 [US2] Wire Portal page lazy route to `PortalComponent` in `formcraft-frontend/src/app/features/ui-redesign/ui-redesign.routes.ts`
- [ ] T026 [US2] Verify Portal page tests pass and save failure preserves edited form state in `formcraft-frontend/src/app/features/ui-redesign/admin/portal.component.spec.ts`

## Phase 5: User Story 3 - Integrations Page (Priority: P3)

**Goal**: Admins can view existing API credentials and webhooks, revoke active credentials, and pause/resume webhooks from a new-theme `/ui/admin/integrations` page.

**Independent Test**: Navigate to `/ui/admin/integrations` as admin, verify credentials/webhooks render, revoke an active credential, pause/resume a webhook, and see empty/loading/error states.

- [ ] T027 [P] [US3] Add failing component tests for credential list, revoke active only, webhook list, toggle active/paused only, and empty/error states in `formcraft-frontend/src/app/features/ui-redesign/admin/integrations.component.spec.ts`
- [ ] T028 [P] [US3] Add Integrations page translation keys for API keys, scopes, statuses, revoke, webhooks, toggles, empty/error states in `formcraft-frontend/src/assets/i18n/en.json`
- [ ] T029 [P] [US3] Add Arabic Integrations page translation keys in `formcraft-frontend/src/assets/i18n/ar.json`
- [ ] T030 [US3] Implement Integrations page component state and `IntegrationService` interactions in `formcraft-frontend/src/app/features/ui-redesign/admin/integrations.component.ts`
- [ ] T031 [US3] Implement Integrations page template with API credentials, webhooks, revoke/toggle actions, loading/error/empty states in `formcraft-frontend/src/app/features/ui-redesign/admin/integrations.component.html`
- [ ] T032 [US3] Implement Integrations page Spark 3/RTL responsive styles in `formcraft-frontend/src/app/features/ui-redesign/admin/integrations.component.scss`
- [ ] T033 [US3] Wire Integrations page lazy route to `IntegrationsComponent` in `formcraft-frontend/src/app/features/ui-redesign/ui-redesign.routes.ts`
- [ ] T034 [US3] Verify Integrations page does not expose create-credential or create-webhook controls in `formcraft-frontend/src/app/features/ui-redesign/admin/integrations.component.spec.ts`

## Phase 6: Polish & Cross-Cutting

- [ ] T035 [P] Add no-classic-redirect regression assertions for Export, Portal, and Integrations routes in `formcraft-frontend/src/app/features/ui-redesign/ui-redesign.routes.spec.ts`
- [ ] T036 [P] Audit F055 English translation keys for raw-string coverage in `formcraft-frontend/src/assets/i18n/en.json`
- [ ] T037 [P] Audit F055 Arabic translation keys for parity with English keys in `formcraft-frontend/src/assets/i18n/ar.json`
- [ ] T038 Run frontend unit tests for F055 route/component coverage from `formcraft-frontend/`
- [ ] T039 Perform quickstart RTL/LTR manual verification for all three pages using `formcraft-specs/specs/055-spark3-missing-pages/quickstart.md`
- [ ] T040 Confirm no F055 implementation touched backend code or unrelated spec paths from the repository root

## Dependencies

- Phase 1 must complete before route/component edits.
- Phase 2 must complete before user story route wiring.
- US1 is the MVP and can be implemented before US2/US3.
- US2 and US3 can proceed after Phase 2 independently of each other.
- Phase 6 runs after the selected user-story phases are complete.

## Parallel Execution Examples

- After Phase 2, one agent can work US1 files under `features/ui-redesign/admin/export.*` while another works US2 files under `features/ui-redesign/admin/portal.*`.
- Translation tasks T012/T013, T020/T021, and T028/T029 can be paired by locale but must be reconciled to keep key shapes identical.
- Styling tasks T016, T024, and T032 are parallelizable after their corresponding templates exist.

## Implementation Strategy

1. Complete Phase 1 and Phase 2 to establish guarded routes and corrected navigation.
2. Deliver MVP with US1 Export page first because it is P1 and operationally critical.
3. Add US2 Portal page using the same loading/error/empty state patterns.
4. Add US3 Integrations page with manage-existing-only behavior.
5. Finish with i18n polish, RTL/LTR verification, and test execution.

## Summary

- Total tasks: 40
- Setup tasks: 4
- Foundational tasks: 6
- User Story 1 tasks: 8
- User Story 2 tasks: 8
- User Story 3 tasks: 8
- Polish tasks: 6
- Parallel opportunities: 13 tasks marked `[P]`
- Suggested MVP scope: Phase 1 + Phase 2 + User Story 1
- Format validation: All tasks use checkbox, sequential task ID, optional `[P]`, required user-story labels for story phases, and explicit file paths.

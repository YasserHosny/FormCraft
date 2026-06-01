# Research: New-Theme Admin Pages - Export, Portal, Integration

## Decision: Build native Spark 3 standalone components

**Rationale**: The issue is a theme break caused by toolbar/admin routes landing on classic-theme pages. Native standalone components under `features/ui-redesign/admin/` preserve the new-theme shell, direction handling, and visual tokens while enabling page-specific parity.

**Alternatives considered**:

- Keep `ClassicRedirectComponent`: rejected because it preserves the broken UX.
- Wrap classic components in the new shell: rejected because classic templates/styles can leak old layout assumptions.

## Decision: Reuse existing frontend services and shared models

**Rationale**: `DataExportService`, `PortalService`, and `IntegrationService` already expose the required backend operations. Reusing them keeps this feature frontend-only and avoids API/schema drift.

**Alternatives considered**:

- Add new backend endpoints: rejected by spec and unnecessary for parity.
- Create facade services first: rejected as premature abstraction.

## Decision: Route all F055 pages through `/ui/admin/*`

**Rationale**: The new-theme shell is mounted under `/ui/`, and the existing Analytics page uses `/ui/admin/analytics`. Export, Portal, and Integration should use the same route family and `RoleGuard` admin-only enforcement.

**Alternatives considered**:

- Preserve `/admin/*` toolbar links: rejected because those paths resolve to classic-theme admin pages.
- Use nested child routes under Analytics: rejected because these are peer admin pages.

## Decision: Disable export download above 50,000 records

**Rationale**: The spec success criterion sets supported export size at up to 50,000 records. The UI should use backend `can_download` when available and present 50,000 records as the explicit user-facing threshold.

**Alternatives considered**:

- Hardcode only a frontend threshold: rejected because backend remains source of truth for actual download eligibility.
- Leave threshold vague: rejected because tests need deterministic expected behavior.

## Decision: Integrations page is read-and-manage only

**Rationale**: Creating credentials and webhooks is out of scope. The page lists credentials/webhooks, revokes active credentials, and toggles webhooks between active and paused.

**Alternatives considered**:

- Include create forms because the service supports credential creation: rejected because it expands scope.
- Hide revoke/toggle actions: rejected because existing manage operations are required for parity.

## Decision: Use translation keys for all visible states

**Rationale**: The constitution requires zero hardcoded UI strings and Arabic-first RTL behavior. The new pages must add keys to both `en.json` and `ar.json` for titles, filters, table headers, actions, success/error states, and empty states.

**Alternatives considered**:

- Reuse existing classic keys only: partially useful but insufficient where Spark 3 copy/state names are missing.
- Inline strings in snackbars/confirmations: rejected by Translation-Key Architecture.

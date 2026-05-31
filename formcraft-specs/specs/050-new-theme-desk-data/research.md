# Research: New Theme Desk Live Data Integration

**Date**: 2026-05-31 | **Feature**: 050-new-theme-desk-data

## R1: Service Injection Strategy for Standalone Components

**Decision**: Inject existing `providedIn: 'root'` services directly via constructor injection in standalone components.

**Rationale**: All desk services (`DeskService`, `DraftService`, `HistoryService`, `FormFillerService`, `CustomerService`, `ConditionEngineService`, `AutoFillService`, `FillerTafqeetService`, `ValidationService`, `SubmissionService`) are already `@Injectable({ providedIn: 'root' })`. Angular standalone components can inject root-provided services without any additional module configuration.

**Alternatives considered**:
- Creating wrapper services specific to the new theme — rejected because it adds unnecessary abstraction with no benefit (YAGNI).
- Re-exporting services through a barrel file — rejected because direct imports are simpler and more explicit.

## R2: Dashboard Data Source

**Decision**: Use `DeskService.getDashboard()` as the primary data source for the dashboard. This single API call returns `DashboardData` containing templates, recent templates, pinned templates, drafts, and notifications.

**Rationale**: The classic desk dashboard already uses this endpoint. It returns all dashboard data in one call, minimizing HTTP requests. KPI counts can be derived from the response properties: `drafts.length` for pending drafts, `templates.total` for active templates. For today's submission count, use `HistoryService.getSubmissions()` with a date filter for today.

**Alternatives considered**:
- Separate API calls for each dashboard section — rejected because `getDashboard()` already aggregates the data.
- Creating a new backend KPI endpoint — rejected per spec (no new backend work).

## R3: Pinned Templates vs. Frequent Templates

**Decision**: Use `DeskService.getDashboard()` which already returns a `pinned: PinnedTemplate[]` array. The backend already supports pin/unpin via `DeskService.pinTemplate()` and `DeskService.unpinTemplate()`. Display up to 6 pinned templates.

**Rationale**: Contrary to the spec's initial assumption that no pinning API exists, the `DeskService` already has `pinTemplate()` and `unpinTemplate()` methods, and the `DashboardData` interface includes a `pinned` array. The new theme should use real pinned templates rather than frequency-based derivation.

**Alternatives considered**:
- Frequency-based derivation from submission history — rejected now that pin/unpin API discovered in existing code.

## R4: Form Filler Architecture

**Decision**: Rebuild the form filler component to dynamically render fields from `FormFillerService.getTemplate()` response, using Angular Reactive Forms with `ConditionEngineService` for visibility/required logic, `ValidationService` for field validation, `AutoFillService` for customer data auto-fill, and `FillerTafqeetService` for number-to-words.

**Rationale**: The classic desk form filler (`fill.component.ts`) demonstrates the proven pattern. The new theme form filler currently has hardcoded sections and fields — these must be replaced with dynamic rendering from the `FillTemplate` response which contains `pages[].elements[]` with all field metadata (type, label, validation, sort_order, etc.).

**Alternatives considered**:
- Embedding the classic form filler component directly — rejected because the new theme has a different visual layout/design that must be preserved.

## R5: Auto-Save on Navigation

**Decision**: Implement auto-save using Angular Router `canDeactivate` guard. When the operator navigates away from the form filler with unsaved changes, auto-save the current field values as a draft via `DraftService.saveDraft()` or `DraftService.updateDraft()`.

**Rationale**: Prevents data loss in banking/operational context. The `DraftService` already supports create and update operations. A `canDeactivate` guard is the standard Angular pattern for intercepting navigation.

**Alternatives considered**:
- Periodic auto-save on a timer — rejected as more complex and not needed per clarification (fetch-on-load, no polling pattern).
- Browser `beforeunload` event only — rejected because it doesn't cover in-app navigation.

## R6: Mock Data Cleanup

**Decision**: Delete `formcraft-frontend/src/app/features/ui-redesign/shared/mock-data.ts` entirely. Remove all inline mock arrays from dashboard, form-filler, and customers components.

**Rationale**: Per clarification, no fallback mock data should remain. The mock-data file exports (`CUSTOMERS`, `Template`, etc.) are only imported by UI redesign prototype components. All references must be removed as part of wiring real data.

**Alternatives considered**:
- Keeping mock data behind a feature flag — rejected per clarification.
- Moving mock data to test fixtures — not needed since tests will use service mocks/stubs.

## R7: Customer Model Mapping

**Decision**: Map the existing `Customer` model from `desk/customers/customer.models.ts` to the new theme's customer display format. The existing `CustomerService` returns all needed fields (name, ID, phone, email, status, etc.).

**Rationale**: The `CustomerService` is already `providedIn: 'root'` and has `list()`, `search()`, `getById()`, and `getAutoPopulateData()` methods that cover all customer page requirements.

**Alternatives considered**: None — direct reuse is the only sensible approach.

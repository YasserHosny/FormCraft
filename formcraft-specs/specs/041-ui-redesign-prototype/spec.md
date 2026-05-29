# Feature Specification: Dual Theme Experience and UI Redesign Rollout

**Feature Branch**: `041-ui-redesign-prototype`
**Created**: 2026-05-26
**Last Updated**: 2026-05-28 (rev 2)
**Status**: Draft for business review
**Input**: User feedback that FormCraft must support two selectable themes, not render the old and new themes at the same time.

## Clarifications

### Session 2026-05-27

- Dual theme means FormCraft offers two mutually exclusive experiences: the current Classic theme and the New theme.
- Users must be able to switch between Classic and New from inside the application.
- Only one theme shell may be visible at a time. The New theme must not be nested inside the Classic shell, and the Classic shell must not be nested inside the New theme.
- Production New theme screens must use real application data from the database through existing product APIs. Static mock data is acceptable only for isolated design prototypes, tests, or explicit demo seed scenarios.
- The Classic theme remains reachable until a later deprecation decision is made.

### Session 2026-05-28

- Every production-reachable New theme screen must have a matching Classic destination, a New destination, and a documented fallback for users who cannot access the equivalent destination.
- Theme switching must work from both shells: Classic-to-New and New-to-Classic. The switch must preserve user identity, organization, role, language, and the closest supported workflow context.
- All enabled controls visible in either theme must have an explicit behavior. A visible control may navigate, open a menu or dialog, filter data, perform a business action, download/export, submit data, or show a clear unavailable state. It must not silently do nothing.
- Production New theme navigation, metrics, badges, cards, lists, tables, filters, charts, owners, statuses, and counts must be backed by real database data or by an existing product API response. Hardcoded mock arrays and static counts are allowed only behind prototype/demo gates.
- The first production New theme increment covers the shell and the routes listed in the readiness matrix in this specification. Any additional New route must be hidden, guarded, or added to the matrix before normal users can reach it.

### Session 2026-05-28 (rev 2 — gap closure)

- Theme preference MUST be stored in `localStorage` under key `fc_theme_preference` with value `classic` or `new`. This is the primary persistence mechanism. Server-side sync to the user profile is out of scope for this increment.
- On login or root redirect (`/` or `/**`), the application MUST check `localStorage` for a saved theme preference and redirect to the corresponding theme's role-default landing page instead of always redirecting to `/templates`.
- Theme switching from both shells MUST use a shared route-equivalence mapper function that reads the current URL, extracts route parameters (`:pageId`, `:templateId`, query params for filters), and produces the equivalent route in the target theme per the Route Equivalence Matrix. Hard-coded static links are not acceptable for the theme-switch control.
- The New theme toolbar MUST integrate `LanguageService` and provide a working language toggle that calls `toggleLanguage()` and updates `dir` on the layout wrapper between `rtl` and `ltr`. The Classic shell already has this; the New shell must match.
- The New theme toolbar profile menu item MUST navigate to `/auth/profile` (the same destination as Classic).
- The New theme toolbar notification badge MUST display a real count from `MyFeedbackService` (or the equivalent notification API), not a hardcoded default. The count must update via real-time subscription when available.
- The New theme sidebar MUST NOT import from `mock-data.ts` for production navigation. Badge counts (e.g., draft count, customer count, inbox count) must come from API responses or be omitted until a production source is available. Sidebar items with no production route MUST show disabled styling with a tooltip like "قريباً" (Coming soon).
- The New theme toolbar mode tabs MUST be filtered by the current user's role, matching the Classic shell behavior. An operator must not see the Admin tab; a designer must not see the Desk tab unless their role includes it.
- The New theme toolbar MUST display the organization logo from `OrgAdminService.getOrgSettings()` when available, matching the Classic shell's org branding behavior.
- The New theme toolbar global search input MUST either integrate the existing `GlobalSearchBarComponent` or show a clearly disabled/placeholder state with a tooltip explaining it is not yet available.
- The New theme help menu MUST include at least one actionable item beyond theme switching (e.g., link to documentation or a "keyboard shortcuts" dialog). If no help content exists yet, the help button must be hidden or show a tooltip indicating help is coming soon.
- The Classic shell's feedback widget (`<fc-feedback-widget>`) is out of scope for the New theme in this increment. The widget is not shown on `/ui` routes and this is acceptable.

## User Scenarios & Testing

### User Story 1 - Switch Between Themes (Priority: P1)

As an authenticated FormCraft user, I want to switch between Classic and New themes so that I can choose the experience that fits my work while the redesign is being rolled out.

**Why this priority**: This is the defining business requirement for a dual-theme rollout. Without it, the redesign either replaces the old theme too early or creates a confusing mixed interface.

**Independent Test**: Sign in, switch from Classic to New from each supported Classic module, refresh the page, switch back to Classic from each supported New module, and confirm only the selected theme is shown each time.

**Acceptance Scenarios**:

1. **Given** an authenticated user is viewing the Classic theme, **When** the user chooses the New theme, **Then** the application shows the New theme shell only.
2. **Given** an authenticated user is viewing the New theme, **When** the user chooses the Classic theme, **Then** the application shows the Classic theme shell only.
3. **Given** a user selected a theme, **When** the user refreshes or returns later, **Then** the user's selected theme is restored.
4. **Given** a theme switch target has no equivalent screen, **When** the user switches themes, **Then** the application opens the closest safe landing page for that theme.
5. **Given** a user switches themes from a supported module, **When** an equivalent destination exists in the other theme, **Then** the application opens that equivalent destination rather than a generic home page.
6. **Given** a user switches themes from a record-specific page, **When** the equivalent theme can open the same record, **Then** the route preserves the record context; otherwise it opens the closest safe list page for that module.

---

### User Story 2 - Preserve Access Control Across Themes (Priority: P1)

As a platform owner, I want the New theme to follow the same authentication, role, and permission rules as the Classic theme so that theme switching does not bypass security or expose unfinished areas.

**Why this priority**: A visual redesign must not create a second access path around existing business controls.

**Independent Test**: Attempt to open New theme URLs while signed out and with users who lack the required role; confirm the same access outcomes as Classic.

**Acceptance Scenarios**:

1. **Given** a visitor is not signed in, **When** they open a New theme route directly, **Then** they are sent to sign in before seeing protected content.
2. **Given** a signed-in user lacks access to a module, **When** they open the matching New theme route, **Then** access is denied or redirected consistently with Classic.
3. **Given** a signed-in user has access to a module, **When** they switch themes, **Then** their allowed navigation remains consistent.
4. **Given** a signed-in user lacks access to an equivalent route in the target theme, **When** they switch themes, **Then** the application redirects to the role-appropriate safe landing page and does not expose protected content.

---

### User Story 3 - Use Real Product Data in New Theme Screens (Priority: P1)

As a FormCraft user, I want production New theme screens to show real FormCraft data so that the redesigned experience can be used for actual work rather than as a visual-only prototype.

**Why this priority**: Mocked cards, counts, charts, badges, customers, submissions, or owners would misrepresent business state and create false confidence in the rollout.

**Independent Test**: Create or seed records in the database for each production New theme screen, open the matching New screen, and confirm lists, cards, counts, filters, charts, badges, owners, and empty states reflect database data for the active organization and user permissions.

**Acceptance Scenarios**:

1. **Given** templates exist in the database, **When** the user opens the New Studio template list, **Then** the list displays those templates with their real status, version, owner, department, page/field metadata, submission counts where available, and action availability.
2. **Given** customers, submissions, drafts, reports, notifications, or analytics records exist for a production New screen, **When** the user opens that screen, **Then** visible records, KPIs, badges, charts, and table rows reflect those records for the active organization.
3. **Given** no records match the current filters, **When** the user searches or filters, **Then** the page shows an empty state instead of mock records.
4. **Given** the data request fails, **When** the user opens the page, **Then** the page shows a recoverable error state with a retry path where retry is appropriate.
5. **Given** demo data is needed for local validation, **When** seed data is used, **Then** it is explicitly marked as development/demo data, is repeatable, and does not replace or mutate production data.

---

### User Story 4 - Interact With New Theme Controls (Priority: P2)

As a user trying the New theme, I want visible buttons, filters, tabs, search, and navigation controls to work so that the screen behaves like an application instead of a static mockup.

**Why this priority**: Non-interactive controls create false confidence and block validation of the redesign workflow.

**Independent Test**: Open every production-reachable New theme screen and exercise toolbar controls, sidebar links, search, filters, tabs, toggles, menus, pagination, primary actions, secondary actions, icon buttons, card/table row actions, dialogs, export/download actions, and theme switching.

**Acceptance Scenarios**:

1. **Given** the user changes search text, status, department, date range, branch, layout, sort, page, or tab controls, **When** matching data is available, **Then** the visible results, counts, or charts update accordingly.
2. **Given** an action is available in Classic and supported in the New theme, **When** the user activates it, **Then** it opens the same business workflow or performs the same operation.
3. **Given** an action is intentionally out of scope for the first New theme increment, **When** it is visible, **Then** it is disabled, hidden, or routed to a clear safe state rather than silently doing nothing.
4. **Given** a control opens a menu or dialog, **When** the user activates, dismisses, or confirms it, **Then** focus, state, and resulting navigation or business action behave consistently with the Classic workflow.
5. **Given** a control starts a mutation, export, print, import, submit, save, schedule, or delete operation, **When** the operation succeeds or fails, **Then** the user sees success, failure, loading, and retry/close states appropriate to the operation.

---

### User Story 5 - Roll Out Prototype Screens Safely (Priority: P3)

As a product owner, I want prototype-only screens to be clearly separated from production-ready New theme screens so that incomplete areas are not mistaken for released functionality.

**Why this priority**: The original prototype included multiple screens, but the production rollout should only expose screens that meet real data, access, interaction, and visual quality requirements.

**Independent Test**: Review New theme navigation and confirm only production-ready screens are reachable from normal navigation; prototype-only screens are hidden, guarded, or clearly flagged for internal review.

**Acceptance Scenarios**:

1. **Given** a New theme screen still depends on mock data, **When** normal users navigate the app, **Then** that screen is not presented as production functionality.
2. **Given** a New theme screen is promoted to production, **When** it is reachable from navigation, **Then** it meets the same data and access requirements as the rest of FormCraft.
3. **Given** a route, menu item, or sidebar item points to a prototype-only screen, **When** a normal user views production navigation, **Then** that route is hidden, guarded for internal validation, or visibly marked as unavailable before activation.

---

### User Story 6 - Keep Theme Functionality Aligned (Priority: P1)

As a product owner, I want functionality that exists in both themes to be reflected consistently so that users can move between themes without losing access to their core workflows.

**Why this priority**: A dual-theme rollout succeeds only if switching themes is a visual and interaction choice, not an accidental permission or workflow downgrade.

**Independent Test**: For each production route in the route equivalence matrix, open the Classic destination and New destination with users from each allowed role, then confirm the same business records, allowed actions, restrictions, and fallback behavior are available.

**Acceptance Scenarios**:

1. **Given** a workflow exists in both themes, **When** the user opens either theme, **Then** the same role-allowed business action is available under theme-appropriate UI.
2. **Given** a workflow exists only in Classic during this increment, **When** the user is in New theme, **Then** New navigation points to the Classic workflow, shows it as unavailable, or routes to the safe Classic equivalent without nesting theme shells.
3. **Given** a workflow exists only in New during this increment, **When** the user is in Classic theme, **Then** Classic navigation can route to the New workflow or leave it hidden according to the route equivalence matrix.
4. **Given** the user switches themes after applying filters or selecting a record, **When** the target theme supports the same context, **Then** the context is preserved; otherwise the target theme explains or safely resets to the nearest supported list or dashboard.

## Requirements

### Functional Requirements

- **FR-001**: The application MUST support two named themes: Classic and New.
- **FR-002**: The application MUST render exactly one active theme shell for an authenticated page.
- **FR-003**: The application MUST provide a user-facing control to switch from Classic to New and from New to Classic.
- **FR-004**: The application MUST persist the user's selected theme so refreshes and later sessions restore the selection.
- **FR-005**: The theme switch MUST route users to the equivalent screen when one exists, or to a safe landing page when no equivalent exists.
- **FR-006**: The New theme MUST enforce the same authentication, role, and permission rules as the matching Classic functionality.
- **FR-007**: The New theme MUST keep the Classic theme reachable until the business explicitly approves deprecation.
- **FR-008**: Production New theme screens MUST use database-backed application data through product APIs.
- **FR-009**: Production New theme screens MUST NOT use static mock data for business records, counts, statuses, ownership, or actions.
- **FR-010**: Development or demo seed data MAY be provided, but it MUST be explicit, repeatable, and separated from production data.
- **FR-011**: The New Studio template list MUST display real template records, status counts, versions, owners, and available metadata.
- **FR-012**: The New Studio template list MUST support search, status filtering, department filtering where data exists, and grid/list layout switching.
- **FR-013**: Every user-visible enabled control in the New theme MUST perform its intended action, navigate to the correct existing workflow, open the expected menu/dialog, update data presentation, or perform a documented business operation.
- **FR-014**: New theme screens MUST provide loading, empty, and error states for data-dependent views.
- **FR-015**: New theme layout MUST avoid visual overlap in supported desktop widths, including toolbar/profile/search/navigation areas.
- **FR-016**: New theme screens MUST support Arabic right-to-left usage as a first-class layout direction, while preserving access to English labels where the product already supports language switching.
- **FR-017**: Prototype-only screens MUST be hidden from normal production navigation, guarded for internal validation, or completed before release.
- **FR-018**: Every production-reachable New theme route MUST be listed in the Screen Readiness Matrix with its Classic equivalent, allowed roles, data sources, required controls, and fallback behavior.
- **FR-019**: Every production-reachable Classic route that has a New equivalent MUST be listed in the Route Equivalence Matrix so users can switch Classic-to-New and New-to-Classic predictably.
- **FR-020**: Theme switching MUST preserve record context for templates, designer pages, form filling, customers, analytics filters, and other supported route parameters when the target theme supports that context.
- **FR-021**: When target-route context cannot be preserved, the application MUST route to the nearest safe destination for the user's role and module.
- **FR-022**: Theme switching MUST NOT nest one theme shell inside the other theme shell.
- **FR-023**: New theme toolbar controls MUST support mode navigation, global search behavior or a clearly unavailable search state, Classic theme switch, help menu actions, notification action behavior, profile navigation, language switching, and logout.
- **FR-024**: New theme sidebar controls MUST navigate only to production-ready destinations, route to Classic equivalents when approved by the matrix, or present unavailable/prototype-only items as disabled or hidden.
- **FR-025**: New Studio template list controls MUST cover export, import, create, search, status filtering, department filtering, grid/list switching, status tabs, template card opening, and floating create action.
- **FR-026**: New Studio designer controls MUST cover back/navigation, page navigation, zoom controls, component search, field selection, property tabs, property edits where supported, AI suggestions, preview, version history, save draft, submit for review, rule creation, apply, and dismiss actions.
- **FR-027**: New Desk controls MUST cover identity scanning, new form fill, pinned form selection, pin management, recent activity view/print/more actions, draft continuation, customer picker open/search/select/confirm/cancel, save draft, print PDF, submit, shortcuts, customer export, duplicate merge, customer creation, customer search/filter/sort, customer view/fill/more actions, and pagination.
- **FR-028**: New Admin analytics controls MUST cover period, department, and branch filters; date-range buttons; chart/table drilldowns or safe unavailable states; export PDF; report scheduling; more menus; and view-all actions.
- **FR-029**: Production New theme data MUST include real values for navigation badges, user/profile information, organization branding, templates, pages, fields, submissions, customers, drafts, notifications, reports, analytics KPIs, charts, owners, statuses, departments, branches, and counts whenever those values are visible.
- **FR-030**: Static mock datasets, hardcoded business counts, and hardcoded production user names MUST NOT be used by any production-reachable New theme screen except as explicit loading skeletons, empty-state examples, isolated tests, or gated demo scenarios.
- **FR-031**: Any visible unavailable control MUST communicate its unavailable state through disabled styling, tooltip/help text, safe route, or guarded internal-only flag.
- **FR-032**: Theme preference MUST be persisted per authenticated user and must restore after refresh, sign-out/sign-in, and later sessions without changing organization, role, or language.
- **FR-033**: Both themes MUST expose a clear route back to the other theme from authenticated navigation unless the user's role has no allowed destination in the target theme, in which case the user MUST see a safe explanation or be routed to their allowed landing page.
- **FR-034**: Theme preference MUST be stored in `localStorage` under key `fc_theme_preference` with value `classic` or `new`.
- **FR-035**: On login, root redirect, or wildcard redirect, the application MUST check the stored theme preference and redirect to the saved theme's role-default landing page.
- **FR-036**: Theme switching MUST use a shared route-equivalence mapper that extracts route parameters from the current URL and maps them to the target theme's equivalent route per the Route Equivalence Matrix.
- **FR-037**: The New theme toolbar MUST integrate `LanguageService` to provide a working language toggle between Arabic (RTL) and English (LTR), updating the layout direction dynamically.
- **FR-038**: The New theme toolbar MUST filter mode tabs by the current user's role, hiding tabs the user cannot access.
- **FR-039**: The New theme toolbar MUST display the organization logo from `OrgAdminService` when available.
- **FR-040**: The New theme toolbar notification badge MUST display a real unread count from the notification API, not a hardcoded default.
- **FR-041**: The New theme toolbar profile menu item MUST navigate to the profile page (`/auth/profile`).
- **FR-042**: The New theme toolbar global search MUST either integrate the existing `GlobalSearchBarComponent` or display a clearly disabled state with a tooltip.
- **FR-043**: The New theme sidebar MUST NOT import static mock data for production navigation. Badge counts MUST come from API responses or be omitted.
- **FR-044**: Sidebar items with no production route MUST display disabled styling and a tooltip indicating unavailability (e.g., "قريباً").

### Non-Functional Requirements

- **NFR-001**: Switching themes MUST complete without a full sign-out/sign-in cycle.
- **NFR-002**: The selected theme MUST load on refresh without briefly showing both shells.
- **NFR-003**: Theme switching must not change user identity, organization, role, permissions, or current language.
- **NFR-004**: New theme pages MUST remain responsive and readable at 1280px, 1366px, 1440px, and 1920px desktop widths in both Arabic RTL and English LTR where labels are available.
- **NFR-005**: Switching between equivalent routes MUST either render the target shell within two seconds under normal validated test conditions or show an in-shell loading state until target-route data is ready.
- **NFR-006**: Real-data screens MUST derive visible counts from the same filtered dataset or backend response used to render the records.

## Key Entities

- **Theme Preference**: The user's selected visual experience, either Classic or New, persisted for future visits.
- **Theme Shell**: The top-level navigation, toolbar, sidebar, and page frame for one theme.
- **Theme Switch**: A user action that changes the active theme and navigates to the closest matching page.
- **New Theme Screen**: A screen implemented in the redesigned experience and subject to production-readiness requirements before normal users can rely on it.
- **Demo Seed Data**: Optional development-only records used to validate the New theme with realistic data.
- **Template Catalog View**: The New Studio template browsing experience backed by real template data.
- **Screen Readiness Matrix**: The list of New theme routes that may be production-reachable, with data, access, controls, and fallback expectations.
- **Route Equivalence Matrix**: The bidirectional mapping between Classic and New destinations used by theme switching.
- **Control Inventory**: The list of visible controls for each production New screen and the expected outcome for each control.
- **Production Data Source**: A real product API, database-backed query, or existing service response scoped to the authenticated user's organization and permissions.

## Screen Readiness Matrix

| New theme area | New destination | Classic equivalent | Allowed roles | Production data required | Required control coverage | Release state |
|----------------|-----------------|--------------------|---------------|--------------------------|---------------------------|---------------|
| Shell | New toolbar and sidebar on all `/ui` authenticated routes | Classic app shell on authenticated Classic routes | Any signed-in role with target-route access | Current user, role, organization branding, notifications where shown, language, allowed navigation items, badge counts | Mode tabs, global search or unavailable state, theme switch, help menu, notifications, profile, language, logout, sidebar navigation | Production only after all controls and data are real or unavailable |
| Studio templates | `/ui/studio/templates` | `/templates` | Admin, Designer | Templates, statuses, versions, owners, departments, pages, fields, submission counts where available, filters, empty/error states | Export, import PDF, create, search, status filter, department filter, grid/list toggle, status tabs, card open, floating create | Production-ready target for first increment |
| Studio designer | `/ui/studio/designer/:pageId` | `/designer/:pageId` | Admin, Designer | Template, page, elements, review state, validation rules, available components, version metadata | Back, page navigation, zoom, component search, field selection, property tabs, property edits, AI suggestions, preview, versions, save draft, submit review, rules, apply/dismiss | Prototype unless all listed data and controls are completed |
| Desk dashboard | `/ui/desk` | `/desk` | Admin, Branch Manager, Operator | User branch, daily submissions, drafts, pinned forms, recent activity, customer references, status counts | Scan identity, new fill, pinned form open, manage pins, view all, activity view/print/more, draft continuation | Prototype unless all listed data and controls are completed |
| Desk form filler | `/ui/desk/fill/:templateId` | `/desk/fill/:templateId` or the Classic form fill route | Admin, Branch Manager, Operator | Template, pages, elements, validation, selected customer, draft/submission state, PDF availability | Back, customer picker, clear customer, save draft, print PDF, submit, shortcuts, field entry, customer search/select/confirm/cancel/create | Prototype unless all listed data and controls are completed |
| Desk customers | `/ui/desk/customers` | Classic customer list when available, otherwise `/desk` safe landing | Admin, Branch Manager, Operator | Customers, identifiers, contact data, branches, duplicate flags, form counts, last activity, pagination totals | Export CSV, merge duplicates, add customer, search, filter, sort, view, fill form, more menu, pagination | Prototype unless all listed data and controls are completed |
| Admin analytics | `/ui/admin/analytics` | `/admin/analytics` | Admin | KPIs, charts, departments, branches, date ranges, operators, reports, exports | Period/department/branch filters, range buttons, chart drilldown/more menus, export PDF, schedule report, view all | Prototype unless all listed data and controls are completed |

## Route Equivalence Matrix

| User context | Classic destination | New destination | Switch behavior | Safe fallback |
|--------------|--------------------|-----------------|-----------------|---------------|
| Studio template list | `/templates` | `/ui/studio/templates` | Preserve theme selection and open the template list in the target shell | Role default landing page |
| Studio designer page | `/designer/:pageId` | `/ui/studio/designer/:pageId` | Preserve `pageId` when the target theme supports designer production readiness | `/templates` or `/ui/studio/templates` |
| Desk dashboard | `/desk` | `/ui/desk` | Preserve Desk mode and open the Desk dashboard in the target shell | Role default landing page |
| Desk form fill | Classic form fill route for `:templateId` | `/ui/desk/fill/:templateId` | Preserve `templateId` when the target theme supports form fill production readiness | `/desk` or `/ui/desk` |
| Desk customers | Classic customer list route when available | `/ui/desk/customers` | Open the equivalent customer list when available; otherwise open the Desk landing page | `/desk` or `/ui/desk` |
| Admin analytics | `/admin/analytics` | `/ui/admin/analytics` | Preserve analytics filters that both themes support | `/admin` or `/ui/admin/analytics` when allowed |
| Admin general | `/admin` | `/ui/admin/analytics` until a New admin overview is production-ready | Open the closest production New admin destination | Role default landing page |
| Unsupported or prototype-only route | Current Classic route or current New route | Nearest production-ready target from this matrix | Do not nest shells; do not show a broken route | Role default landing page |

## Control Inventory Requirements

- **Shell controls**: Mode tabs, theme switch, global search, help menu, notifications, user/profile menu, language switch, logout, sidebar links, badges, and organization branding must each have a defined action, real data source, or unavailable state.
- **Studio controls**: Template create/import/export, search, filters, tabs, layout toggle, template open, designer navigation, component search, property editing, AI suggestions, preview, version history, draft save, review submit, rule creation, apply, and dismiss must be implemented or marked unavailable.
- **Desk controls**: Identity scan, new form fill, pinned forms, pin management, activity actions, draft actions, customer picker, field entry, draft save, PDF print, submit, shortcuts, customer export, duplicate merge, customer creation, search/filter/sort, row actions, and pagination must be implemented or marked unavailable.
- **Admin controls**: Analytics filters, date ranges, chart/table drilldowns, export PDF, schedule report, more menus, and view-all actions must be implemented or marked unavailable.
- **Unavailable controls**: A disabled, hidden, guarded, or safe-routed control is acceptable only when the user can tell it is not currently available and no data mutation or navigation silently fails.

## Success Criteria

- **SC-001**: In authenticated navigation, no tested page renders both Classic and New toolbars or sidebars at the same time.
- **SC-002**: A user can switch from Classic to New and back to Classic without signing out.
- **SC-003**: Refreshing after a theme switch restores the selected theme.
- **SC-004**: Direct access to New theme protected URLs while signed out is blocked by sign-in.
- **SC-005**: The New Studio template list displays database records and status counts that match the backend response for the active organization.
- **SC-006**: Search, filters, tabs, layout toggle, and all visible enabled actions on the New Studio template list respond to user input.
- **SC-007**: Toolbar, profile, search, and navigation areas do not overlap at 1280px, 1366px, 1440px, and 1920px desktop widths in Arabic RTL and English LTR.
- **SC-008**: Every production-reachable New route has a documented Classic equivalent, New destination, role rule, data source, and fallback in the matrices above.
- **SC-009**: Every enabled button, link, tab, filter, menu item, icon action, and input on production New screens either changes state, navigates, opens a menu/dialog, performs the documented operation, or shows a clear unavailable state.
- **SC-010**: No production-reachable New screen displays hardcoded business records, counts, user names, owners, customers, submissions, drafts, analytics, notifications, or badges when real product data exists.
- **SC-011**: Switching from Classic to New and from New to Classic preserves supported record IDs and filters for every route listed in the Route Equivalence Matrix.
- **SC-012**: After selecting the New theme and refreshing, the user lands on a New theme route without ever seeing the Classic shell flash.
- **SC-013**: After selecting the Classic theme and refreshing, the user lands on a Classic route.
- **SC-014**: The New theme toolbar language toggle switches between Arabic RTL and English LTR, and the layout direction updates without page reload.
- **SC-015**: The New theme toolbar shows only the mode tabs the current user's role permits (e.g., operator sees Desk only).
- **SC-016**: The New theme toolbar displays the organization logo when org settings include one.
- **SC-017**: The New theme notification badge shows a real count from the API, updates in real-time, and never shows a hardcoded default.
- **SC-018**: Profile menu in the New toolbar navigates to `/auth/profile`.
- **SC-019**: Sidebar items without a production route are visually disabled and show a tooltip.
- **SC-020**: No production-reachable New theme component imports from `mock-data.ts`.

## Out of Scope

- Removing or deprecating the Classic theme.
- Replacing every Classic workflow with a New theme equivalent in this increment.
- Using mock data as the production behavior for released New theme screens.
- Changing the underlying business permissions model as part of the visual redesign.
- Building new business workflows that do not already exist in Classic or in approved New theme scope.
- Treating prototype-only New screens as production-ready before they satisfy the Screen Readiness Matrix.

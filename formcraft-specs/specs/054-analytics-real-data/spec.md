# Feature Specification: New-Theme Admin Console Analytics — Real Data Integration

**Feature Branch**: `054-analytics-real-data`
**Created**: 2026-06-01
**Status**: Draft

## Clarifications

### Session 2026-06-01

- Q: Should the new dashboard endpoints cache their results or query live on every request? → A: Short TTL cache (5 minutes) per org + filter combo, matching the existing compliance endpoint pattern.
- Q: How is "unique customer" defined for the KPI count? → A: Distinct `customer_id` field values on the `submissions` table within the selected period and filters.
- Q: Can non-admin roles access the `/ui/admin/analytics` page? → A: Admin-only. The route is guarded to the admin role; branch managers and operators use the existing operator analytics views.
- Q: Should the yearly period aggregate to weekly (52 points) or monthly (12 points) buckets? → A: Monthly buckets (12 data points) for readability, matching common analytics tooling conventions.

---

## Summary

The Admin Console "Analytics & Reports" page (`/ui/admin/analytics`) in the new theme currently displays entirely hardcoded mock data. This feature replaces every hardcoded value with live data from the backend API, adding the missing backend endpoints the dashboard requires, while preserving the new theme's layout and visual design without modification.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Live KPI Cards (Priority: P1)

An admin opens the Analytics & Reports page and sees real, up-to-date KPI values: total forms filled (with % change vs. the previous period), the ratio of active to total published templates, the organisation-wide average processing time, and the count of unique customers served — all scoped to their organisation.

**Why this priority**: KPI cards are the first thing admins read. Showing fabricated numbers erodes trust in the entire dashboard and in business decisions made from it.

**Independent Test**: Navigate to `/ui/admin/analytics` with real data in the DB; submit one more form and reload — the "Total forms filled" counter must increment.

**Acceptance Scenarios**:

1. **Given** an admin is logged in and submissions exist, **When** the Analytics page loads, **Then** "Total forms filled" shows the real count of submitted forms for the default period (30 days) scoped to that organisation.
2. **Given** the previous period had fewer submissions, **When** the page loads, **Then** the delta badge shows a positive percentage (e.g., "+18%"); a downward-trend variant appears when the count has dropped.
3. **Given** some templates are active and others are drafts, **When** the page loads, **Then** "Published templates" shows "active / total" where both numbers match the database.
4. **Given** submissions have recorded processing durations, **When** the page loads, **Then** "Avg processing time" displays in M:SS format computed from real data.
5. **Given** submissions are linked to customer profiles, **When** the page loads, **Then** "Unique customers" reflects the count of distinct `customer_id` values on submissions in the period, plus new-this-week count.

---

### User Story 2 — Submissions-Over-Time Line Chart (Priority: P1)

An admin views the line chart showing daily submission volume and can switch between 7-day, 30-day, 90-day, and yearly views. The chart highlights the peak day dynamically from loaded data.

**Why this priority**: The trend chart is the central visual on the page. Static bars that never change mislead managers reading activity trends.

**Independent Test**: Switch from 30-day to 7-day; the chart refreshes to show exactly 7 data points with the correct peak value and date label — different from the mock "١٢٤ — ٢٥ مايو".

**Acceptance Scenarios**:

1. **Given** submissions exist over the past 30 days, **When** the page loads (default 30-day period), **Then** the chart renders one bar per day (30 points) with heights proportional to actual daily submission counts.
2. **Given** a user clicks "٧ أيام" (7 days), **When** the chart refreshes, **Then** it shows 7 data points for the last 7 days with an updated peak label.
3. **Given** a user clicks "سنوي" (yearly), **When** the chart refreshes, **Then** it shows 12 monthly data points (one per calendar month) with the peak month highlighted.
4. **Given** a day (or month for yearly view) with the highest submissions, **When** the chart is rendered, **Then** the overlay displays that period's count and formatted date/month dynamically.
5. **Given** no submissions exist in the selected period, **When** the chart loads, **Then** bars render at zero height and the peak label shows "–".

---

### User Story 3 — Department Donut Chart (Priority: P2)

The donut chart shows the breakdown of submissions by department as real percentages, so managers can see which departments generate the most form activity.

**Why this priority**: Department distribution drives staffing and routing decisions. Fake percentages lead to wrong resource allocation.

**Independent Test**: Create submissions in two departments; confirm the donut segments reflect the actual split (e.g., 60% / 40%).

**Acceptance Scenarios**:

1. **Given** submissions are spread across departments, **When** the page loads, **Then** each donut segment's percentage and legend value match the database breakdown.
2. **Given** a department filter is applied, **When** the chart refreshes, **Then** the donut recalculates to show distribution within the filtered scope.
3. **Given** only one department has submissions, **When** the chart loads, **Then** the donut shows a single full-circle segment at 100%.

---

### User Story 4 — Top Templates Bar Chart (Priority: P2)

The "Most Used Templates" bar chart lists the top 7 templates by submission count for the active period, with bars scaled proportionally to the top-ranked template.

**Why this priority**: Template usage ranking drives decisions about which forms to improve, retire, or replicate. Mock rankings have no operational value.

**Independent Test**: Verify the first bar's template name and count match a direct DB query for the most-submitted template in the period.

**Acceptance Scenarios**:

1. **Given** templates have submissions in the period, **When** the page loads, **Then** the bar list is ordered by submission count descending, showing at most 7 entries.
2. **Given** the top template has 1,837 submissions and the second has 1,284, **When** bars render, **Then** the second bar's width equals (1284 / 1837) × 100% of the first.
3. **Given** fewer than 7 templates have submissions, **When** the chart loads, **Then** only templates with submissions are listed (no phantom entries).

---

### User Story 5 — Operator Performance Table (Priority: P2)

The "Employee Performance" table shows the top 5 real operators ranked by forms filled this week, with their actual branch, form count, average processing time, and accuracy rate.

**Why this priority**: This table is used for performance reviews and coaching. Fake operator data is harmful.

**Independent Test**: Confirm the top operator's name matches the highest-performing operator from the `/api/analytics/operators` endpoint for the current week.

**Acceptance Scenarios**:

1. **Given** operators have submitted forms this week, **When** the table renders, **Then** rows show real operator names, branches, form counts, times, and accuracy from the API.
2. **Given** an operator's error rate is 0.6%, **When** the accuracy column renders, **Then** it displays 99.4% (100 − error_rate).
3. **Given** fewer than 5 operators have activity, **When** the table loads, **Then** only active operators are shown (no padded rows with zeroes).

---

### User Story 6 — Period and Department/Branch Filters (Priority: P3)

The period toggle (7d / 30d / 90d / yearly) and the department and branch filter pills in the page header trigger a full reload of all dashboard widgets with filtered data.

**Why this priority**: Filters are visible in the UI but currently non-functional. They must work for the dashboard to be operationally useful.

**Independent Test**: Select a specific department filter; all four KPIs, the line chart, donut, bar chart, and operator table all update to that department's data.

**Acceptance Scenarios**:

1. **Given** the page is loaded, **When** a user clicks "٩٠ يوماً" (90 days), **Then** all widgets reload scoped to the last 90 days.
2. **Given** a department is selected from the filter pill, **When** the filter applies, **Then** all widgets show data for that department only.
3. **Given** a branch is selected, **When** the filter applies, **Then** the operator table shows only operators from that branch.
4. **Given** a filter combination returns no data, **When** widgets render, **Then** each widget shows an appropriate empty state rather than an error.

---

### User Story 7 — Loading and Error States (Priority: P3)

While data is fetched, the page shows skeleton placeholders in each widget. If a request fails, an inline error message appears in that widget without breaking the rest of the page.

**Why this priority**: Without loading states the page flashes stale mock data; without error handling a single failed endpoint crashes the whole dashboard.

**Independent Test**: Throttle to "Slow 3G" — skeleton placeholders appear during load. Simulate a 500 from the summary endpoint — only the KPI area shows an error while charts still load.

**Acceptance Scenarios**:

1. **Given** a slow network, **When** the page is loading, **Then** skeleton placeholder elements are visible in every KPI card and chart area.
2. **Given** the summary endpoint returns a 500, **When** the page loads, **Then** the KPI section shows an inline error with a retry option; other widgets load normally.
3. **Given** the page has loaded and a filter is changed, **When** data refetches, **Then** the previous values remain visible until the new response arrives (no flicker to skeleton on subsequent fetches).

---

### Edge Cases

- What happens when an organisation has zero submissions in the selected period? → All KPIs show 0 or "–", charts show empty states, delta badges are omitted.
- What if `avg_fill_time_ms` is null for all submissions? → The processing time KPI shows "–" instead of "0:00".
- What if a department name is very long? → The donut legend and bar chart truncate with ellipsis; full name shows on hover.
- What if the yearly period is selected? → Yearly view aggregates submissions to monthly buckets (12 data points), not daily or weekly, for chart readability.
- What if a non-admin user somehow reaches `/ui/admin/analytics`? → The route guard redirects them away; the page is strictly admin-only.

---

## Requirements *(mandatory)*

### Functional Requirements

**Backend — New Dashboard Endpoints**

- **FR-001**: The system MUST expose `GET /api/analytics/dashboard/summary` returning total forms filled (current and previous period), active/total published template counts, average processing time in milliseconds, unique customer count (distinct `customer_id` values on submissions), and new-this-week customer delta — all scoped to the authenticated user's organisation. Results MUST be cached with a 5-minute TTL keyed on org ID + all filter parameters.
- **FR-002**: `GET /api/analytics/dashboard/summary` MUST accept query parameters: `period` (values: `7d`, `30d`, `90d`, `yearly`; default `30d`), optional `department_id`, and optional `branch_id`.
- **FR-003**: The system MUST expose `GET /api/analytics/dashboard/submissions-over-time` returning an array of `{date, count}` objects; for `7d`/`30d`/`90d` periods the granularity is daily (one point per day); for `yearly` the granularity is monthly (12 points). Results MUST be cached with a 5-minute TTL keyed on org ID + all filter parameters.
- **FR-004**: The system MUST expose `GET /api/analytics/dashboard/department-distribution` returning an array of `{department_id, department_name, count, percentage}` items summing to 100%, scoped to the period and branch filter. Results MUST be cached with a 5-minute TTL.
- **FR-005**: The system MUST expose `GET /api/analytics/dashboard/top-templates` returning up to `limit` (default 7, max 20) templates ordered by submission count descending for the period, including template name, code, and count. Results MUST be cached with a 5-minute TTL.
- **FR-006**: All four new endpoints MUST require an authenticated admin session and MUST scope all queries to `current_user.org_id`; unauthenticated requests MUST receive 401; non-admin authenticated requests MUST receive 403.
- **FR-007**: Backend query logic MUST read from the existing `submissions`, `templates`, `profiles`, `departments`, and `branches` tables without schema changes.

**Frontend — New-Theme Analytics Component**

- **FR-008**: The `AnalyticsService` MUST be extended with four new methods — `getDashboardSummary`, `getSubmissionsOverTime`, `getDepartmentDistribution`, and `getTopTemplates` — corresponding to the new endpoints.
- **FR-009**: New TypeScript interfaces MUST be added to the analytics models file for each new endpoint's request parameters and response shapes.
- **FR-010**: The `AnalyticsComponent` (new theme) MUST replace all hardcoded arrays and literals with data loaded from the API on component initialisation.
- **FR-011**: All four dashboard sections (KPI cards, line chart, donut chart, operator table) MUST display skeleton placeholder elements while their data is loading.
- **FR-012**: If any individual endpoint fails, the corresponding widget MUST show an inline error message with a retry button; other widgets MUST continue to display their data.
- **FR-013**: Clicking any period toggle button MUST trigger a reload of all API calls with the updated period; the active button MUST receive the `active` CSS class.
- **FR-014**: The department filter pill MUST open a selection UI listing real departments from the organisation; selecting one MUST filter all widgets.
- **FR-015**: The branch filter pill MUST open a selection UI listing real branches; selecting one MUST filter all widgets.
- **FR-016**: The line chart MUST render bar elements whose heights are proportional to real daily submission counts; the peak overlay MUST display the actual peak count and its date.
- **FR-017**: The donut chart MUST compute segments from real department distribution percentages; segment colours MUST cycle through the existing palette.
- **FR-018**: The top-templates bar chart MUST compute each bar's width as `(template_count / max_count) × 100%` from real API data.
- **FR-019**: Average processing time received in milliseconds MUST be displayed as `M:SS` (e.g., 222,000 ms → "3:42").
- **FR-020**: All numeric values displayed in Arabic context MUST use RTL-safe number formatting consistent with the existing `formatValue` method.
- **FR-021**: The HTML structure and CSS classes of the new-theme analytics component MUST NOT be altered beyond adding Angular binding attributes (`*ngIf`, `[style]`, `(click)`, etc.) and skeleton placeholder elements.
- **FR-022**: All new user-visible strings (loading labels, error messages, empty state messages, filter labels) MUST have translation keys added to both `en.json` and `ar.json`.

### Key Entities

- **DashboardSummary**: Aggregated KPI snapshot — total forms, published template counts (active/total), avg processing time (ms), unique customers, period deltas.
- **TimeSeriesPoint**: A single day's (or week's) submission count — date + count.
- **DepartmentShare**: A department's slice of total submissions — department identifier, name, count, percentage.
- **TopTemplate**: A template ranked by usage — template identifier, name, code, submission count.
- **DashboardFilter**: The active filter state held in the component — selected period, optional department ID, optional branch ID.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After a new form submission is recorded, the "Total forms filled" KPI reflects it on the next page load within 5 minutes (the cache TTL window).
- **SC-002**: Switching between any two period toggles completes a full widget refresh and the user sees updated data within 3 seconds on a standard connection.
- **SC-003**: All four KPI values, the line chart peak, the donut percentages, and the top-template bar rankings match values derivable from a direct database query against the same time window — zero mock literals remain.
- **SC-004**: No hardcoded numeric literals or mock arrays remain in `analytics.component.ts` after implementation.
- **SC-005**: When any single endpoint is unavailable, the rest of the dashboard remains functional and the affected widget shows an actionable error — no full-page crash or blank screen.
- **SC-006**: The visual layout, card dimensions, typography, colour palette, and RTL alignment of the new-theme analytics page are identical before and after the data integration.
- **SC-007**: All four new backend endpoints respond within 2 seconds for an organisation with up to 100,000 submissions.
- **SC-008**: The department and branch filter pills, when used together, correctly narrow all widgets to the intersection of both filters simultaneously.
- **SC-009**: A non-admin authenticated user attempting to access `/ui/admin/analytics` is redirected by the route guard without reaching the page or triggering any analytics API call.

---

## Assumptions

- The `submissions` table has a `submitted_at` timestamp and a `status` column; `status = 'submitted'` defines "filled" forms.
- The `submissions` table references `template_id`, `operator_id`, `department_id`, and `branch_id` either directly or derivable via joins.
- Templates have a status or boolean field distinguishing "active/published" from "draft".
- Processing time is derivable from `started_at` and `submitted_at` timestamps per submission.
- Customer identity (unique customers) is tracked via a `customer_id` field on the `submissions` table; "unique customers" = `COUNT(DISTINCT customer_id)` within the filter scope.
- The existing 6-colour palette in the donut chart is sufficient for typical department counts; organisations with more than 6 departments cycle colours.
- The `profiles` table links operators to branches via a `branch_id` foreign key.
- The yearly period aggregates submissions to monthly buckets (12 data points, one per calendar month); daily granularity is used for 7d/30d/90d periods.

---

## Out of Scope

- Changes to the classic theme analytics pages or their existing endpoints.
- Real-time / WebSocket push updates — data refreshes on page load and filter change only.
- Exporting the new-theme dashboard as PDF (the "تصدير PDF" and "جدولة تقرير" buttons remain wired to existing routes unchanged).
- Adding new chart types or visual widgets not already present in the new theme HTML.
- Pagination of the operator table beyond the top 5.

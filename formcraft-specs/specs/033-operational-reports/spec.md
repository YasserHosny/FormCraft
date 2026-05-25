# Feature Specification: Operational Report Engine

**Feature Branch**: `033-operational-reports`  
**Created**: 2026-05-25  
**Status**: Draft  
**Vision Reference**: AC-08

## Clarifications

### Session 2026-05-25

- Q: What is the relationship between F033 (Operational Reports) and F032 (Data Export & Integration)? → A: Complementary — F032 provides raw data exports (flat rows, structured JSON), while F033 provides formatted reports with aggregation, totals, period comparisons, and charts. F033 reports may use F032's export infrastructure for file generation but add a reporting presentation layer.
- Q: How does the system identify which form fields contain monetary amounts for financial aggregation? → A: Designer-tagged fields — template designers tag fields as "amount" type during design. Only tagged fields are summed in financial reports.
- Q: Can the custom report builder query across multiple templates in a single report? → A: Yes, cross-template. Admin selects multiple templates; shared fields (amount, date, customer) are auto-aligned by field type tag.
- Q: How long should generated report archives be retained? → A: Fixed 12-month retention for all organizations, then auto-purged.
- Q: Which roles can access which report types? → A: Tiered access — org admins access all reports; branch managers access transaction register and daily reconciliation (branch-scoped via RLS); operators access only their own submission history (no aggregate reports).

## User Scenarios & Testing

### User Story 1 - Transaction Register (Priority: P1)

As an org admin or branch manager, I need a transaction register showing all form submissions in a date range with filters by template, operator, branch, department, status, and customer, with export to Excel/CSV/PDF, so I can track daily operations and respond to audit inquiries.

**Why this priority**: Most fundamental operational report — every enterprise customer needs a transaction register for daily operations and compliance.

**Independent Test**: Navigate to `/admin/reports/transactions`, apply date range filter, see paginated results, export to Excel.

**Acceptance Scenarios**:

1. **Given** admin navigates to `/admin/reports/transactions`, **When** selecting a date range, **Then** a sortable table shows: reference number, template name, operator, customer (if linked), date, key field values (first 3 configurable), status.
2. **Given** results are displayed, **When** admin clicks "Export Excel", **Then** a .xlsx file downloads with all filtered results including all field values.
3. **Given** a branch manager accesses the report, **When** RLS is applied, **Then** only submissions from their branch are visible.

---

### User Story 2 - Daily Reconciliation Report (Priority: P2)

As a branch manager, I need a per-operator, per-branch summary for a single day showing total submissions, total amounts for financial templates, and breakdown by template type, so I can perform end-of-day reconciliation.

**Why this priority**: Critical for banking use case — teller reconciliation is a daily mandatory process.

**Independent Test**: Navigate to daily reconciliation, select date and branch, see operator-level summary with totals.

**Acceptance Scenarios**:

1. **Given** branch manager opens daily reconciliation for today, **When** the report loads, **Then** a summary shows per-operator rows with: operator name, total submissions, total amount (for financial templates), breakdown by template type.
2. **Given** the admin configures auto-generation at 5:00 PM daily, **When** the scheduled time arrives, **Then** the report is generated and emailed to the branch manager.
3. **Given** an operator had zero submissions for the day, **When** the report includes all branch operators, **Then** that operator shows with zero counts (not omitted).

---

### User Story 3 - Period Summary Report (Priority: P3)

As an org admin, I need aggregate totals for configurable date ranges (week/month/quarter/year) grouped by department, branch, template, or operator, with period-over-period comparison, so I can prepare management and board reports.

**Why this priority**: Strategic reporting for management — supports quarterly business reviews and board reporting.

**Independent Test**: Generate monthly summary grouped by department, see this month vs. last month with trend arrows.

**Acceptance Scenarios**:

1. **Given** admin selects "Monthly" period and "Department" grouping, **When** report generates, **Then** each department row shows: submission count, total amount, average amount, with comparison arrows vs. previous month.
2. **Given** admin selects "Quarterly" and "Template" grouping, **When** exporting as PDF, **Then** a formatted PDF with charts and tables is generated suitable for board presentation.

---

### User Story 4 - Custom Report Builder (Priority: P4)

As an org admin, I need to build custom reports by selecting data dimensions, applying filters, choosing aggregation methods, and scheduling recurring delivery, so I can create organization-specific reports beyond the pre-built templates.

**Why this priority**: Differentiator — reduces dependency on FormCraft team for custom reporting needs.

**Independent Test**: Build a custom report selecting template fields + submission metadata, preview results, save and schedule.

**Acceptance Scenarios**:

1. **Given** admin opens custom report builder, **When** they select dimensions (template fields, submission metadata, customer data), **Then** a live preview shows matching data.
2. **Given** admin configures aggregation (sum of amount, grouped by branch), **When** they choose "bar chart" output, **Then** the chart renders in the preview.
3. **Given** admin saves the report with a name, **When** they configure a weekly schedule with email recipients, **Then** the report auto-generates and emails every Monday.

---

### User Story 5 - Specialized Financial Reports (Priority: P5)

As an org admin, I need pre-built reports for beneficiary/payee analysis, void & reprint register, and signatory usage, so I can support fraud monitoring, financial authorization tracking, and operational audit.

**Why this priority**: Banking-specific value — differentiates FormCraft in the financial services vertical.

**Independent Test**: Generate beneficiary report for a date range, see all transactions grouped by beneficiary with totals.

**Acceptance Scenarios**:

1. **Given** admin opens "Beneficiary Report", **When** they search for a specific beneficiary, **Then** all transactions across all templates for that beneficiary are listed with totals.
2. **Given** admin opens "Void & Reprint Register", **When** a submission was voided and reprinted 4 times, **Then** it appears flagged with a warning indicator.
3. **Given** admin opens "Signatory Usage Report", **When** a signatory is approaching their authority limit, **Then** an alert shows the remaining capacity.

---

### Edge Cases

- What happens when a report covers millions of submissions? Pagination and async generation required.
- How does the system handle reports when field_data structure varies across template versions?
- What happens when a scheduled report fails to generate? Retry + alert to admin.
- How does the custom report builder handle fields that exist in some templates but not others?

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide a transaction register with date range, template, operator, branch, department, status, and customer filters.
- **FR-002**: System MUST provide daily reconciliation reports with per-operator, per-branch summaries.
- **FR-003**: System MUST support auto-generation of daily reconciliation at configurable times with email delivery.
- **FR-004**: System MUST provide period summary reports (week/month/quarter/year) with period-over-period comparison.
- **FR-005**: System MUST provide a custom report builder with dimension selection, filter configuration, aggregation methods, and chart types. The builder MUST support cross-template queries, auto-aligning shared fields by their designer-assigned type tag.
- **FR-006**: System MUST support saving custom reports as named templates for reuse.
- **FR-007**: System MUST support scheduling recurring reports (daily/weekly/monthly) with email delivery.
- **FR-008**: System MUST provide pre-built beneficiary/payee reports, void & reprint registers, and signatory usage reports.
- **FR-009**: All reports MUST support export to Excel, CSV, and PDF formats.
- **FR-010**: Reports MUST respect RLS and tiered role access — org admins access all reports; branch managers access transaction register and daily reconciliation (branch-scoped); operators access only their own submission history with no aggregate reports.
- **FR-011**: Reports involving large datasets MUST generate asynchronously with progress indication.
- **FR-012**: Financial aggregation in reports MUST use only fields tagged as "amount" type by the template designer; untagged fields MUST NOT be included in financial totals.

### Key Entities

- **Report Template**: Named, saved report configuration with dimensions, filters, aggregation, chart type, and schedule.
- **Report Schedule**: Frequency, recipients, format, last generated timestamp, next scheduled timestamp.
- **Report Archive**: Generated report snapshots with timestamp, format, and download link (retained for 12 months).

## Success Criteria

### Measurable Outcomes

- **SC-001**: Transaction register for 10,000 submissions loads within 5 seconds.
- **SC-002**: Daily reconciliation report generates within 10 seconds for a branch with 50 operators.
- **SC-003**: Scheduled reports are delivered within 15 minutes of their configured time.
- **SC-004**: Custom reports with up to 100,000 rows export to Excel within 60 seconds.
- **SC-005**: 100% of report access respects RLS boundaries — no cross-org or cross-branch data leakage.

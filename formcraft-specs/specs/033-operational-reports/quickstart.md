# Quickstart: Operational Report Engine

## Prerequisites

- FormCraft backend running (FastAPI)
- FormCraft frontend running (Angular)
- Supabase project with existing tables: submissions, templates, profiles, departments, branches, elements
- At least one template with submissions and designer-tagged "amount" fields

## Integration Scenarios

### Scenario 1: Transaction Register (P1)

1. Admin navigates to `/admin/reports/transactions`
2. Sets date range filter (last 7 days)
3. Optionally filters by template, branch, operator
4. Table displays paginated results with reference number, template, operator, date, key fields, status
5. Clicks "Export Excel" → downloads .xlsx with all filtered rows
6. Branch manager sees only their branch data (RLS enforced)

**Verify**: Exported rows match filter count. Arabic text renders correctly in Excel.

### Scenario 2: Daily Reconciliation (P2)

1. Branch manager navigates to `/admin/reports/reconciliation`
2. Selects today's date (defaults to today)
3. Sees per-operator breakdown: submissions count, total amount (from tagged fields), by template
4. Operators with zero submissions appear with zero values
5. Exports to PDF for end-of-day sign-off

**Verify**: Total amounts sum only from fields with `field_type_tag = 'amount'`. All branch operators listed.

### Scenario 3: Scheduled Report (P2)

1. Admin opens reconciliation report → clicks "Schedule"
2. Configures: daily at 17:00, recipients: manager@bank.com, format: xlsx
3. At 17:00, system generates report and emails it
4. Admin checks schedule history → sees success with delivery timestamp

**Verify**: Email arrives within 15 min of schedule time. Attachment matches expected data.

### Scenario 4: Period Summary (P3)

1. Admin navigates to `/admin/reports/period-summary`
2. Selects "Monthly" period, "Department" grouping
3. Sees current month vs. previous month with percentage change arrows
4. Exports to PDF for board presentation

**Verify**: Comparison percentages are mathematically correct. PDF renders charts and RTL text.

### Scenario 5: Custom Report Builder (P4)

1. Admin opens `/admin/reports/builder`
2. Selects 2 templates (Transfer Order + Account Opening)
3. Adds dimensions: date, branch, amount (auto-aligned across templates by type tag)
4. Adds aggregation: SUM of amount, grouped by branch
5. Sees live preview with bar chart
6. Saves as "Monthly Branch Performance"
7. Schedules weekly delivery

**Verify**: Cross-template amounts sum correctly. Chart renders in preview. Saved report persists.

### Scenario 6: Beneficiary Report (P5)

1. Admin opens `/admin/reports/financial/beneficiary`
2. Searches for beneficiary name "Al-Rashid Trading"
3. Sees all submissions across all templates referencing that beneficiary
4. Total amount displayed

**Verify**: Only submissions with matching beneficiary field_type_tag content shown.

## Key Test Cases

| Test | Input | Expected |
|------|-------|----------|
| RLS enforcement | Branch manager queries all branches | Only own branch data returned |
| Operator restriction | Operator accesses /reports/ | 403 Forbidden (except own history) |
| Empty report | Date range with no submissions | Empty table + "No records match" message |
| Large export | 100K+ records | Async job created, polling until complete |
| Export limit | 150K records | 400 error with "narrow filters" message |
| Arabic export | Submissions with Arabic field values | Correct RTL rendering in Excel/PDF |
| Amount aggregation | Templates without tagged amount fields | $0 / no financial columns shown |
| Schedule failure | Invalid email recipient | Schedule saves but delivery_status = failed, error logged |

## Database Migration Checklist

1. Add `field_type_tag` column to `elements` table (nullable enum)
2. Create `report_templates` table
3. Create `report_schedules` table
4. Create `report_archives` table
5. Add RLS policies to all new tables
6. Seed pre-built report templates (system = true) for each org
7. Create index on `submissions(organization_id, created_at)` if not exists
8. Create cleanup function for expired archives (> 12 months)

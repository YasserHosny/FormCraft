# Quickstart: Analytics & Reporting Dashboard

**Feature**: 027-analytics-reporting
**Date**: 2026-05-24

---

## Prerequisites

- FormCraft backend running (`formcraft-backend/`)
- FormCraft frontend running (`formcraft-frontend/`)
- Supabase instance with existing migrations applied (001–028)
- At least one organization with departments, branches, operators, and submissions

---

## Test Scenarios

### Scenario 1: Dashboard Overview (P1 — MVP)

**Setup**: Org with 3 branches, 5 operators, ~100 submissions across different dates/templates.

1. Log in as Org Admin
2. Navigate to `/admin/analytics`
3. Verify: KPI cards show total submissions (today / this week / this month)
4. Verify: Trend line chart shows current month vs. previous month
5. Verify: Branch breakdown table lists all 3 branches with counts
6. Change date range to "This Quarter" → verify all metrics update
7. Select custom date range → verify data filters correctly

**Expected**: All metrics computed live, page loads < 3 seconds.

### Scenario 2: Role-Based Scoping

1. Log in as Branch Manager → navigate to analytics
2. Verify: Only sees own department's branches and operators
3. Verify: Total matches department-only submissions (not org-wide)
4. Log in as Operator → navigate to Form Desk
5. Verify: "My Stats" widget shows only their own submissions
6. Verify: Cannot access `/admin/analytics` (403 or redirect)

**Expected**: Complete data isolation between roles.

### Scenario 3: Template Usage

1. Log in as Org Admin → go to template analytics tab
2. Verify: Templates ranked by fill count, bar chart visible
3. Click a template with multiple versions → verify version adoption timeline
4. Apply date filter → verify rankings update

### Scenario 4: Operator Productivity

1. Log in as Branch Manager → go to operator productivity tab
2. Verify: Table lists operators in their branch with submission counts
3. Verify: Daily breakdown visible for selected period
4. Log in as Org Admin → select "All Branches" → verify cross-branch view

### Scenario 5: Branch Comparison

1. Log in as Org Admin → go to branch comparison
2. Verify: All branches listed with total, active operators, top template, trend
3. Select 2 branches → verify side-by-side chart comparison

### Scenario 6: Transaction Register

1. Log in as Org Admin → go to transaction register
2. Verify: Paginated table with reference #, template, operator, branch, date, status
3. Filter by template → verify filtered results
4. Filter by operator → verify filtered results
5. Search by reference number → verify result found
6. Click "Export as CSV" → verify file downloads with correct data + Arabic text

### Scenario 7: Export

1. View any analytics page → click "Export as CSV"
2. Open CSV in Excel → verify Arabic text displays correctly (UTF-8 BOM)
3. Click "Export as PDF" → verify PDF contains chart + summary table
4. Apply filters → export → verify export matches filtered view (not full data)

### Scenario 8: Empty States

1. Create a new org with no submissions
2. Navigate to analytics → verify empty state message displayed
3. Verify: No errors, helpful guidance shown

### Scenario 9: Bilingual Support

1. Switch language to Arabic → navigate to analytics
2. Verify: All labels, axes, headers render in Arabic with RTL layout
3. Export CSV → verify Arabic column headers
4. Export PDF → verify Arabic title and labels

### Scenario 10: Operator Stats Widget

1. Log in as Operator → navigate to Form Desk dashboard
2. Verify: "My Stats" card shows today/this week/this month counts
3. Verify: Mini trend line shows last 7 days
4. Submit a new form → refresh dashboard → verify count increments

---

## API Smoke Tests

```bash
# Overview
curl -H "Authorization: Bearer $TOKEN" \
  "$API/analytics/overview?preset=this_month"

# Branch breakdown
curl -H "Authorization: Bearer $TOKEN" \
  "$API/analytics/by-branch?preset=this_month"

# Template usage
curl -H "Authorization: Bearer $TOKEN" \
  "$API/analytics/templates?preset=this_month&limit=10"

# Operator productivity
curl -H "Authorization: Bearer $TOKEN" \
  "$API/analytics/operators?preset=this_month"

# Transaction register
curl -H "Authorization: Bearer $TOKEN" \
  "$API/analytics/transactions?preset=last_7_days&page=1&limit=25"

# CSV export
curl -H "Authorization: Bearer $TOKEN" \
  "$API/analytics/export?view=transactions&preset=this_month" -o report.csv

# Operator widget
curl -H "Authorization: Bearer $TOKEN" \
  "$API/desk/my-stats"
```

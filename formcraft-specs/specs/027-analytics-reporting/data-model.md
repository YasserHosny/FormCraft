# Data Model: Analytics & Reporting Dashboard

**Feature**: 027-analytics-reporting
**Date**: 2026-05-24

---

## Overview

This feature does NOT create new database tables. All analytics are computed live via aggregation queries against existing tables. This document maps which existing entities serve which analytics views.

---

## Existing Entities Used

### submissions (primary data source)

| Field | Type | Used For |
|-------|------|----------|
| id | UUID PK | Row count |
| template_id | UUID FK → templates | Template usage grouping |
| template_version | INT | Version adoption tracking |
| operator_id | UUID FK → auth.users | Operator productivity |
| org_id | UUID FK → organizations | Multi-tenant scoping |
| branch_id | UUID FK → branches (nullable) | Branch breakdown |
| field_values | JSONB | Transaction register display |
| reference_number | TEXT | Transaction register display |
| status | TEXT | Status filtering (printed/submitted) |
| created_at | TIMESTAMPTZ | Time-series grouping, date range filtering |

**Key indexes** (already exist):
- `idx_submissions_operator(operator_id, created_at DESC)`
- `idx_submissions_template(template_id)`
- `idx_submissions_org(org_id)`

**Recommended new indexes** (for analytics performance):
- `idx_submissions_org_created(org_id, created_at)` — composite for date-range scoped org queries
- `idx_submissions_branch_created(branch_id, created_at)` — for branch breakdown queries

### templates

| Field | Type | Used For |
|-------|------|----------|
| id | UUID PK | Join target |
| name | TEXT | Display in rankings/register |
| version | INT | Version adoption curves |
| status | TEXT | Active vs. archived/deleted indicator |
| org_id | UUID FK | Scoping |
| department_id | UUID FK (nullable) | Department scoping |
| created_at | TIMESTAMPTZ | Template creation timeline |

### profiles

| Field | Type | Used For |
|-------|------|----------|
| id | UUID PK | Join target |
| full_name | TEXT | Operator name display |
| email | TEXT | Unique operator identification |
| role | TEXT | Role-based scoping |
| org_id | UUID FK | Multi-tenant scoping |
| department_id | UUID FK (nullable) | Department scoping |
| branch_id | UUID FK (nullable) | Branch scoping |

### departments

| Field | Type | Used For |
|-------|------|----------|
| id | UUID PK | Grouping dimension |
| name | TEXT | Display label |
| org_id | UUID FK | Scoping |

### branches

| Field | Type | Used For |
|-------|------|----------|
| id | UUID PK | Grouping dimension |
| name | TEXT | Display label |
| department_id | UUID FK | Department-branch hierarchy |
| org_id | UUID FK | Scoping |

---

## Query Patterns

### 1. Submission Volume Overview
```sql
SELECT date_trunc('day', created_at) AS day, COUNT(*) AS total
FROM submissions
WHERE org_id = :org_id AND created_at BETWEEN :from AND :to
GROUP BY day ORDER BY day;
```

### 2. Branch Breakdown
```sql
SELECT b.name AS branch_name, COUNT(s.id) AS total
FROM submissions s
JOIN branches b ON s.branch_id = b.id
WHERE s.org_id = :org_id AND s.created_at BETWEEN :from AND :to
GROUP BY b.name ORDER BY total DESC;
```

### 3. Template Usage Rankings
```sql
SELECT t.name, t.version, COUNT(s.id) AS fill_count
FROM submissions s
JOIN templates t ON s.template_id = t.id
WHERE s.org_id = :org_id AND s.created_at BETWEEN :from AND :to
GROUP BY t.name, t.version ORDER BY fill_count DESC;
```

### 3b. Template Version Adoption Timeline
```sql
SELECT s.template_version AS version,
       date_trunc('day', s.created_at) AS day,
       COUNT(s.id) AS count,
       MIN(s.created_at) AS first_used,
       MAX(s.created_at) AS last_used
FROM submissions s
WHERE s.template_id = :template_id AND s.org_id = :org_id
  AND s.created_at BETWEEN :from AND :to
GROUP BY s.template_version, day
ORDER BY version, day;
```

### 4. Operator Productivity
```sql
SELECT p.full_name, p.email, COUNT(s.id) AS total,
       date_trunc('day', s.created_at) AS day
FROM submissions s
JOIN profiles p ON s.operator_id = p.id
WHERE s.org_id = :org_id AND s.created_at BETWEEN :from AND :to
GROUP BY p.full_name, p.email, day ORDER BY total DESC;
```

### 5. Transaction Register
```sql
SELECT s.reference_number, t.name AS template_name, p.full_name AS operator,
       b.name AS branch, s.status, s.created_at, s.field_values
FROM submissions s
JOIN templates t ON s.template_id = t.id
JOIN profiles p ON s.operator_id = p.id
LEFT JOIN branches b ON s.branch_id = b.id
WHERE s.org_id = :org_id AND s.created_at BETWEEN :from AND :to
ORDER BY s.created_at DESC
LIMIT :limit OFFSET :offset;
```

---

## Pydantic Response Models (backend)

### SubmissionVolumeResponse
- period_label: str
- total: int
- previous_total: int
- change_pct: float
- daily_breakdown: list[{date: str, count: int}]

### BranchBreakdownItem
- branch_name: str
- total: int
- pct_of_org: float

### TemplateUsageItem
- template_name: str
- template_id: UUID
- version: int
- fill_count: int
- is_deleted: bool

### OperatorProductivityItem
- operator_name: str
- operator_email: str
- total: int
- daily_counts: list[{date: str, count: int}]

### TransactionRegisterItem
- reference_number: str
- template_name: str
- operator_name: str
- branch_name: str | None
- status: str
- created_at: datetime
- field_summary: dict (selected key fields from field_values)

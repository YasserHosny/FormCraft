# Data Model: Template Approval Workflow

**Feature**: 028-approval-workflow
**Date**: 2026-05-24

---

## Overview

This feature primarily extends existing tables rather than creating new ones. The `template_reviews` table already exists — it gains an `element_comments` column. Organization settings gain approval workflow configuration fields. One new table (`department_default_reviewers`) stores optional default reviewer assignments.

---

## Existing Tables Modified

### template_reviews (extended)

| Field | Type | Status | Used For |
|-------|------|--------|----------|
| id | UUID PK | EXISTS | Row identity |
| template_id | UUID FK → templates | EXISTS | Which template was reviewed |
| reviewer_id | UUID FK → profiles | EXISTS | Who reviewed |
| action | TEXT | EXISTS | Decision: approved, rejected, withdrawn |
| comment | TEXT | EXISTS | Overall review comment |
| element_comments | JSONB | **NEW** | Array of `{element_key, comment}` for element-level feedback |
| org_id | UUID FK → organizations | EXISTS | Multi-tenant scoping |
| created_at | TIMESTAMPTZ | EXISTS | When review happened |

**New `element_comments` structure**:
```json
[
  {"element_key": "national_id", "comment": "Needs Arabic label"},
  {"element_key": "amount_field", "comment": "Add currency validator"}
]
```

### organizations.settings (JSONB — extended)

| Key | Type | Status | Used For |
|-----|------|--------|----------|
| approval_workflow_enabled | boolean | EXISTS (schema) | Toggle approval on/off |
| review_overdue_threshold_days | integer | **NEW** | Days before a pending review is flagged overdue (default: 3) |

### templates (no schema changes)

All needed fields already exist: `status`, `created_by`, `org_id`, `department_id`, `created_at`, `updated_at`.

The `submitted_at` timestamp can be derived from the audit log entry for `TEMPLATE_SUBMITTED_FOR_REVIEW`, or from the last `updated_at` when status changed to `submitted_for_review`.

---

## New Tables

### department_default_reviewers

| Field | Type | Description |
|-------|------|-------------|
| id | UUID PK | Row identity |
| department_id | UUID FK → departments | Which department |
| reviewer_id | UUID FK → profiles | Suggested default reviewer |
| org_id | UUID FK → organizations | Multi-tenant scoping |
| created_at | TIMESTAMPTZ | When assigned |

**Notes**:
- Soft suggestion only — any branch_manager or admin can review regardless of this assignment
- One default reviewer per department (UNIQUE on department_id)
- RLS: scoped by org_id

---

## State Machine (Updated)

```
                           ┌──────────────────────────────────┐
                           │  approval_workflow_enabled=false  │
                           │  draft ──────► published          │
                           │  (direct shortcut)                │
                           └──────────────────────────────────┘

                           ┌──────────────────────────────────┐
                           │  approval_workflow_enabled=true   │
                           │                                   │
  draft ──► submitted_for_review ──► approved ──► published   │
    ▲               │      │              │                    │
    │               │      │              │                    │
    │         ◄─────┘      │        (admin only)               │
    │       (withdraw -    │                                   │
    │        designer)     │                                   │
    │               │      │                                   │
    │               ▼      │                                   │
    └────── rejected       │                                   │
                           └──────────────────────────────────┘

  published ──► archived ──► published (re-publish)
  published ──► deprecated ──► archived
```

### Transition Map (Updated)

| From | To | Allowed Roles | Condition |
|------|----|---------------|-----------|
| draft | submitted_for_review | designer, admin | approval enabled |
| draft | published | designer, admin | approval **disabled** (shortcut) |
| submitted_for_review | approved | admin, branch_manager | actor ≠ template.created_by |
| submitted_for_review | rejected | admin, branch_manager | actor ≠ template.created_by; comment required |
| submitted_for_review | draft | designer, admin | withdrawal (designer can withdraw own) |
| approved | published | admin | — |
| rejected | submitted_for_review | designer, admin | designer edits then resubmits (skips explicit draft transition) |
| published | archived | admin | — |
| published | deprecated | admin | — |
| archived | published | admin | re-publish |
| deprecated | archived | admin | — |

---

## Query Patterns

### 1. Review Queue (Pending Templates)
```sql
SELECT t.id, t.name, t.category, t.status, t.updated_at AS submitted_at,
       p.display_name AS designer_name, d.name_en AS department_name,
       EXTRACT(DAY FROM NOW() - t.updated_at) AS days_waiting
FROM templates t
JOIN profiles p ON t.created_by = p.id
LEFT JOIN departments d ON t.department_id = d.id
WHERE t.org_id = :org_id
  AND t.status IN ('submitted_for_review', 'approved', 'rejected')
ORDER BY t.updated_at ASC;
```

### 2. Governance Metrics
```sql
-- Average review turnaround (days)
SELECT AVG(EXTRACT(EPOCH FROM (r.created_at - t.updated_at)) / 86400) AS avg_days
FROM template_reviews r
JOIN templates t ON r.template_id = t.id
WHERE t.org_id = :org_id AND r.created_at > :since;

-- Rejection rate
SELECT
  COUNT(*) FILTER (WHERE action = 'rejected') AS rejected,
  COUNT(*) AS total,
  ROUND(100.0 * COUNT(*) FILTER (WHERE action = 'rejected') / NULLIF(COUNT(*), 0), 1) AS rejection_pct
FROM template_reviews
WHERE org_id = :org_id AND created_at > :since;
```

### 3. Self-Review Check
```sql
SELECT created_by FROM templates WHERE id = :template_id;
-- Compare with actor_id; block if equal
```

---

## Migration

**Migration 030**: `030_approval_workflow.sql`
- ADD `element_comments JSONB DEFAULT NULL` to `template_reviews`
- CREATE `department_default_reviewers` table with RLS policy
- ADD composite index: `idx_templates_org_status(org_id, status)` for review queue performance

# API Contract: Template Approval Workflow

**Base path**: `/api`
**Auth**: Required (Bearer token)

---

## Existing Endpoints (behavior extended)

### POST /api/templates/{template_id}/transition

Already exists. Behavior extended:

**Body**:
```json
{
  "status": "submitted_for_review",
  "comment": null,
  "element_comments": null
}
```

**New fields**:
- `element_comments` (optional): Array of `{element_key, comment}` — only applicable when `status` is `approved` or `rejected`

**New behaviors**:
- **Self-review prevention**: Returns 403 if actor is the template's `created_by` and transition is `submitted_for_review → approved/rejected`
- **Approval-disabled shortcut**: Allows `draft → published` when org's `approval_workflow_enabled = false`
- **Withdrawal**: Allows `submitted_for_review → draft` by designer (template's creator) or admin
- **Withdrawal action logged**: Creates audit event `TEMPLATE_WITHDRAWN`

**New error responses**:

| Status | When |
|--------|------|
| 403 | Self-review attempt (actor is template creator) |
| 422 | Direct publish attempted when approval workflow is enabled |
| 422 | Withdrawal attempted after reviewer has already acted |

---

### GET /api/templates/{template_id}/reviews

Already exists. Response extended with `element_comments`:

**Response 200**:
```json
{
  "reviews": [
    {
      "id": "uuid",
      "template_id": "uuid",
      "reviewer_id": "uuid",
      "reviewer_name": "Ahmed Ali",
      "action": "rejected",
      "comment": "Please fix the address section",
      "element_comments": [
        {"element_key": "national_id", "comment": "Needs Arabic label"},
        {"element_key": "amount_field", "comment": "Add currency validator"}
      ],
      "created_at": "2026-05-24T10:30:00Z"
    }
  ]
}
```

---

## New Endpoints

### GET /api/admin/review-queue

Review queue for Reviewers and Admins.

**Role gate**: admin, branch_manager

**Query params**:
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| status | string | no | submitted_for_review | Filter: submitted_for_review, approved, rejected, all |
| department_id | UUID | no | — | Filter by department |
| designer_id | UUID | no | — | Filter by template creator |
| sort_by | string | no | submitted_at | Sort: submitted_at, days_waiting, name |
| sort_dir | string | no | asc | Sort direction: asc, desc |

**Response 200**:
```json
{
  "items": [
    {
      "template_id": "uuid",
      "template_name": "Cheque Request Form",
      "category": "banking",
      "status": "submitted_for_review",
      "version": 2,
      "designer_id": "uuid",
      "designer_name": "Fatima Hassan",
      "department_name": "Retail Banking",
      "submitted_at": "2026-05-21T09:00:00Z",
      "days_waiting": 3,
      "is_overdue": true
    }
  ],
  "total": 12,
  "overdue_count": 2
}
```

**Scoping**: branch_manager sees only templates from their department. admin sees all org templates.

---

### GET /api/admin/review-queue/metrics

Governance dashboard metrics.

**Role gate**: admin

**Query params**:
| Param | Type | Required | Default |
|-------|------|----------|---------|
| since | string (YYYY-MM-DD) | no | 30 days ago |

**Response 200**:
```json
{
  "pending_count": 12,
  "approved_awaiting_publish": 3,
  "avg_turnaround_days": 1.8,
  "rejection_rate_pct": 22.5,
  "overdue_count": 2,
  "total_reviews": 45,
  "overdue_threshold_days": 3
}
```

---

### GET /api/admin/review-queue/{template_id}/timeline

Complete review timeline for a single template.

**Role gate**: admin, branch_manager, designer (own templates only)

**Response 200**:
```json
{
  "template_id": "uuid",
  "template_name": "Cheque Request Form",
  "timeline": [
    {
      "event": "submitted_for_review",
      "actor_id": "uuid",
      "actor_name": "Fatima Hassan",
      "actor_role": "designer",
      "timestamp": "2026-05-20T14:00:00Z",
      "comment": null,
      "element_comments": null
    },
    {
      "event": "rejected",
      "actor_id": "uuid",
      "actor_name": "Ahmed Ali",
      "actor_role": "branch_manager",
      "timestamp": "2026-05-21T10:30:00Z",
      "comment": "Fix address section layout",
      "element_comments": [
        {"element_key": "address_field", "comment": "Too narrow for Arabic text"}
      ]
    },
    {
      "event": "submitted_for_review",
      "actor_id": "uuid",
      "actor_name": "Fatima Hassan",
      "actor_role": "designer",
      "timestamp": "2026-05-22T09:00:00Z",
      "comment": "Fixed address field width"
    },
    {
      "event": "approved",
      "actor_id": "uuid",
      "actor_name": "Ahmed Ali",
      "actor_role": "branch_manager",
      "timestamp": "2026-05-22T15:00:00Z",
      "comment": "Looks good"
    },
    {
      "event": "published",
      "actor_id": "uuid",
      "actor_name": "Admin User",
      "actor_role": "admin",
      "timestamp": "2026-05-23T08:00:00Z"
    }
  ]
}
```

---

### POST /api/admin/review-queue/{template_id}/export-timeline

Export review timeline as a document.

**Role gate**: admin, branch_manager

**Response 200**: `application/pdf`, `Content-Disposition: attachment; filename="review-timeline-{template_name}-{date}.pdf"`

---

### GET /api/admin/departments/{department_id}/default-reviewer

Get default reviewer for a department.

**Role gate**: admin

**Response 200**:
```json
{
  "department_id": "uuid",
  "reviewer_id": "uuid",
  "reviewer_name": "Ahmed Ali"
}
```

**Response 404**: No default reviewer assigned.

---

### PUT /api/admin/departments/{department_id}/default-reviewer

Set or update default reviewer for a department.

**Role gate**: admin

**Body**:
```json
{
  "reviewer_id": "uuid"
}
```

**Response 200**: Same as GET response.

---

### DELETE /api/admin/departments/{department_id}/default-reviewer

Remove default reviewer assignment.

**Role gate**: admin

**Response 204**: No content.

---

## Error Responses (shared)

| Status | When |
|--------|------|
| 401 | No valid auth token |
| 403 | Role insufficient or self-review attempt |
| 404 | Template or department not found |
| 422 | Invalid transition, missing required comment, or approval workflow constraint violation |

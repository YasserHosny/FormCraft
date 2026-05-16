# API Contract: Template Versioning & Cloning

## Modified Endpoint: `POST /api/templates/:templateId/version`

Creates a new version (draft) from a published template. Now sets lineage tracking.

### Response (201 Created)

```json
{
  "id": "new-template-uuid",
  "name": "KYC Form",
  "version": 4,
  "status": "draft",
  "lineage_id": "lineage-uuid",
  "parent_version_id": "source-template-uuid",
  "created_at": "2026-05-16T10:30:00Z"
}
```

### Error Responses

| Status | Condition | Body |
|--------|-----------|------|
| 400 | Source template not published | `{ "detail": "Only published templates can be versioned" }` |
| 404 | Template not found or not in user's org | `{ "detail": "Template not found" }` |

---

## New Endpoint: `POST /api/templates/:templateId/transition`

Transitions a template to a new lifecycle status.

### Request Body

```json
{
  "status": "submitted_for_review",
  "comment": "Ready for review — added NID validation"
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| status | string | yes | Target status. Must be a valid transition from current status. |
| comment | string | conditional | Required when transitioning to 'rejected'. Optional otherwise. |

### Allowed Transitions & Required Roles

| From | To | Allowed Roles |
|------|-----|---------------|
| draft | submitted_for_review | designer, admin |
| submitted_for_review | approved | admin, branch_manager |
| submitted_for_review | rejected | admin, branch_manager |
| approved | published | admin |
| rejected | draft | designer, admin |
| published | archived | admin |
| published | deprecated | admin |
| archived | published | admin |
| deprecated | archived | admin |

### Response (200 OK)

```json
{
  "id": "template-uuid",
  "status": "submitted_for_review",
  "version": 3,
  "lineage_id": "lineage-uuid",
  "updated_at": "2026-05-16T11:00:00Z"
}
```

### Error Responses

| Status | Condition | Body |
|--------|-----------|------|
| 422 | Invalid transition | `{ "detail": "Cannot transition from 'draft' to 'published'" }` |
| 422 | Missing rejection comment | `{ "detail": "Comment required when rejecting" }` |
| 403 | Insufficient role | `{ "detail": "Only admin can publish templates" }` |
| 404 | Template not found | `{ "detail": "Template not found" }` |

### Side Effects

- Audit log entry: `{ action: "TEMPLATE_{STATUS}", resource_type: "template", resource_id: templateId, metadata: { from_status, to_status, comment } }`
- If transition is `approved` or `rejected`: creates a `template_reviews` row

---

## New Endpoint: `POST /api/templates/:templateId/clone`

Clones a template into a new independent template.

### Request Body

```json
{
  "name": "KYC Form - Corporate"
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | string | no | Name for the clone. Defaults to "{original_name} (Copy)" |

### Response (201 Created)

```json
{
  "id": "new-template-uuid",
  "name": "KYC Form - Corporate",
  "version": 1,
  "status": "draft",
  "lineage_id": "new-template-uuid",
  "parent_version_id": null,
  "created_at": "2026-05-16T10:30:00Z"
}
```

### Side Effects

- Audit log entry: `{ action: "TEMPLATE_CLONED", resource_type: "template", resource_id: newTemplateId, metadata: { source_template_id, source_version } }`

---

## New Endpoint: `GET /api/templates/:templateId/history`

Returns all versions in the template's lineage.

### Response (200 OK)

```json
{
  "lineage_id": "lineage-uuid",
  "versions": [
    {
      "id": "template-v3-uuid",
      "version": 3,
      "status": "draft",
      "created_by": "user-uuid",
      "created_by_name": "أحمد محمد",
      "created_at": "2026-05-16T10:30:00Z",
      "published_at": null,
      "element_count": 15,
      "page_count": 2
    },
    {
      "id": "template-v2-uuid",
      "version": 2,
      "status": "published",
      "created_by": "user-uuid",
      "created_by_name": "أحمد محمد",
      "created_at": "2026-05-10T09:00:00Z",
      "published_at": "2026-05-12T14:00:00Z",
      "element_count": 14,
      "page_count": 2
    }
  ]
}
```

---

## New Endpoint: `GET /api/templates/:templateId/diff`

Computes and returns the diff between two versions.

### Request Query Parameters

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| compare_to | UUID | yes | The template ID of the other version to compare against |

### Response (200 OK)

```json
{
  "base_version": { "id": "uuid", "version": 2 },
  "compare_version": { "id": "uuid", "version": 3 },
  "summary": {
    "elements_added": 2,
    "elements_removed": 0,
    "elements_modified": 3,
    "pages_added": 0,
    "pages_removed": 0
  },
  "changes": {
    "added": [
      {
        "key": "secondary_phone",
        "type": "text",
        "label_ar": "هاتف ثانوي",
        "label_en": "Secondary Phone",
        "page_sort_order": 1
      }
    ],
    "removed": [],
    "modified": [
      {
        "key": "customer_name",
        "changes": [
          { "property": "x_mm", "from": 20, "to": 25 },
          { "property": "width_mm", "from": 80, "to": 75 }
        ]
      }
    ],
    "pages": {
      "added": [],
      "removed": [],
      "modified": []
    }
  }
}
```

### Error Responses

| Status | Condition | Body |
|--------|-----------|------|
| 400 | Templates not in same lineage | `{ "detail": "Can only compare versions within the same lineage" }` |
| 404 | Template not found | `{ "detail": "Template not found" }` |

---

## New Endpoint: `GET /api/templates/:templateId/reviews`

Returns the review history for a template.

### Response (200 OK)

```json
{
  "reviews": [
    {
      "id": "review-uuid",
      "reviewer_id": "user-uuid",
      "reviewer_name": "محمد علي",
      "action": "rejected",
      "comment": "Missing NID validation on field 3",
      "created_at": "2026-05-15T09:00:00Z"
    },
    {
      "id": "review-uuid-2",
      "reviewer_id": "user-uuid",
      "reviewer_name": "محمد علي",
      "action": "approved",
      "comment": null,
      "created_at": "2026-05-16T11:00:00Z"
    }
  ]
}
```

---

## Modified Endpoint: `GET /api/desk/dashboard`

Template grid now only shows latest published version per lineage.

**Change**: The backend query for available templates changes from:
```sql
WHERE status = 'published' AND org_id = ?
```
to:
```sql
SELECT DISTINCT ON (lineage_id) *
FROM templates
WHERE status = 'published' AND org_id = ?
ORDER BY lineage_id, version DESC
```

Deprecated templates are still shown but with `is_deprecated: true` in the response for UI warning rendering.

---

## Modified Endpoint: PUT/PATCH template edit endpoints

All edit endpoints (`PUT /api/templates/:id`, element CRUD, page CRUD) now check:
- If template status is `published`, `archived`, or `deprecated`: return 403
- If template status is `submitted_for_review` or `approved`: return 403 (read-only during review)
- Only `draft` and `rejected` statuses allow edits

### Error Response (403)

```json
{
  "detail": "Template is not editable in current status",
  "status": "published",
  "hint": "Create a new version to make changes"
}
```

---

## Authentication & Authorization

All endpoints require:
- Valid JWT token (AuthGuard)
- Transitions and reviews: role-based access per transition table above
- Clone: any role with studio access (designer, admin)
- History/diff: any authenticated user in the same org
- Template edits blocked for non-draft statuses (enforced at API level, not just UI)

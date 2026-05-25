# API Contract: Operational Reports

Base path: `/api/reports`

All endpoints require JWT authentication and respect RLS + tiered role access.

---

## Transaction Register

### GET /api/reports/transactions

Query submission data with filters. Paginated.

**Access**: org_admin, branch_manager (branch-scoped)

**Query Parameters**:
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| template_id | uuid | No | Filter by template |
| date_from | date (ISO) | Yes | Start of date range |
| date_to | date (ISO) | Yes | End of date range |
| branch_id | uuid | No | Filter by branch |
| department_id | uuid | No | Filter by department |
| operator_id | uuid | No | Filter by operator |
| status | string | No | Filter by submission status |
| customer_query | string | No | Search customer name/ID |
| page | int | No | Default 1 |
| page_size | int | No | Default 50, max 200 |
| sort_by | string | No | Column to sort (default: created_at) |
| sort_dir | string | No | asc/desc (default: desc) |

**Response 200**:
```json
{
  "data": [
    {
      "id": "uuid",
      "reference_number": "string",
      "template_name": "string",
      "template_name_ar": "string",
      "operator_name": "string",
      "customer_name": "string | null",
      "created_at": "2026-05-25T10:30:00Z",
      "status": "submitted",
      "key_fields": [
        {"key": "amount", "label": "Amount", "value": "1500.00"},
        {"key": "account", "label": "Account", "value": "SA1234"}
      ]
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total_count": 10234,
    "total_pages": 205
  }
}
```

---

### POST /api/reports/transactions/export

Generate export file for transaction register.

**Access**: org_admin, branch_manager (branch-scoped)

**Request Body**:
```json
{
  "filters": {
    "template_id": "uuid | null",
    "date_from": "2026-05-01",
    "date_to": "2026-05-25",
    "branch_id": "uuid | null",
    "department_id": "uuid | null",
    "operator_id": "uuid | null",
    "status": "string | null"
  },
  "format": "xlsx | csv | pdf"
}
```

**Response 200** (sync, < 10K records):
```json
{
  "download_url": "string",
  "file_name": "transactions_2026-05-25.xlsx",
  "record_count": 5432,
  "archive_id": "uuid"
}
```

**Response 202** (async, >= 10K records):
```json
{
  "job_id": "uuid",
  "status": "generating",
  "estimated_seconds": 45
}
```

**Response 400** (exceeds limit):
```json
{
  "error": "export_limit_exceeded",
  "message": "Selected filters match 150,000 records. Maximum is 100,000. Please narrow your filters.",
  "record_count": 150000,
  "max_allowed": 100000
}
```

---

## Daily Reconciliation

### GET /api/reports/reconciliation

**Access**: org_admin, branch_manager (own branch only)

**Query Parameters**:
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| date | date (ISO) | Yes | Report date |
| branch_id | uuid | No | Required for admin; auto-set for branch_manager |

**Response 200**:
```json
{
  "date": "2026-05-25",
  "branch": {"id": "uuid", "name": "string", "name_ar": "string"},
  "summary": {
    "total_submissions": 245,
    "total_amount": 1250000.50,
    "template_breakdown": [
      {"template_id": "uuid", "name": "Transfer Order", "count": 120, "amount": 850000.00},
      {"template_id": "uuid", "name": "Account Opening", "count": 125, "amount": 400000.50}
    ]
  },
  "operators": [
    {
      "operator_id": "uuid",
      "name": "string",
      "total_submissions": 35,
      "total_amount": 175000.00,
      "by_template": [
        {"template_id": "uuid", "name": "Transfer Order", "count": 20, "amount": 150000.00},
        {"template_id": "uuid", "name": "Account Opening", "count": 15, "amount": 25000.00}
      ]
    }
  ]
}
```

---

## Period Summary

### GET /api/reports/period-summary

**Access**: org_admin only

**Query Parameters**:
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| period | string | Yes | week, month, quarter, year |
| group_by | string | Yes | department, branch, template, operator |
| date_from | date | No | Start date (defaults to current period) |
| compare | boolean | No | Include previous period comparison (default: true) |

**Response 200**:
```json
{
  "period": "month",
  "current": {"from": "2026-05-01", "to": "2026-05-31"},
  "previous": {"from": "2026-04-01", "to": "2026-04-30"},
  "groups": [
    {
      "id": "uuid",
      "name": "Retail Banking",
      "name_ar": "الخدمات المصرفية للأفراد",
      "current": {"count": 5200, "amount": 25000000.00, "avg_amount": 4807.69},
      "previous": {"count": 4800, "amount": 22000000.00, "avg_amount": 4583.33},
      "change": {"count_pct": 8.33, "amount_pct": 13.64}
    }
  ]
}
```

---

## Custom Report Builder

### POST /api/reports/custom/preview

Preview custom report results (limited to 100 rows).

**Access**: org_admin only

**Request Body**:
```json
{
  "template_ids": ["uuid1", "uuid2"],
  "dimensions": [
    {"source": "submission", "field": "created_at"},
    {"source": "field_data", "field_key": "amount", "type_tag": "amount"}
  ],
  "filters": [
    {"field": "branch_id", "operator": "eq", "value": "uuid"}
  ],
  "aggregations": [
    {"function": "sum", "field": "amount", "alias": "total_amount"}
  ],
  "group_by": ["branch_id"],
  "date_from": "2026-05-01",
  "date_to": "2026-05-31"
}
```

**Response 200**:
```json
{
  "columns": [
    {"key": "branch_name", "label": "Branch", "type": "text"},
    {"key": "total_amount", "label": "Total Amount", "type": "number"}
  ],
  "rows": [...],
  "total_matching": 15234,
  "preview_limited": true
}
```

### POST /api/reports/custom/save

Save custom report as named template.

**Request Body**:
```json
{
  "name": "Monthly Branch Performance",
  "name_ar": "أداء الفروع الشهري",
  "description": "string",
  "config": { ... }
}
```

**Response 201**: Created report_template object.

---

## Financial Reports

### GET /api/reports/financial/beneficiary

**Access**: org_admin only

**Query Parameters**: date_from, date_to, beneficiary_query, template_id

### GET /api/reports/financial/void-reprint

**Access**: org_admin only

**Query Parameters**: date_from, date_to, branch_id, min_reprint_count

### GET /api/reports/financial/signatory-usage

**Access**: org_admin only

**Query Parameters**: date_from, date_to, signatory_id

---

## Export Job Status

### GET /api/reports/jobs/{job_id}

Poll async export generation status.

**Response 200**:
```json
{
  "job_id": "uuid",
  "status": "generating | completed | failed",
  "progress_pct": 75,
  "download_url": "string | null",
  "error": "string | null"
}
```

---

## Report History

### GET /api/reports/archives

List generated report archives for the org.

**Access**: org_admin only

**Query Parameters**: page, page_size, report_type, date_from, date_to

**Response 200**:
```json
{
  "data": [
    {
      "id": "uuid",
      "report_type": "transaction_register",
      "file_name": "transactions_2026-05-25.xlsx",
      "export_format": "xlsx",
      "record_count": 5432,
      "file_size_bytes": 245000,
      "generation_method": "manual",
      "generated_by": "string",
      "created_at": "2026-05-25T14:30:00Z",
      "download_url": "string"
    }
  ],
  "pagination": { ... }
}
```

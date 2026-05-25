# API Contract: Report Scheduling

Base path: `/api/reports/schedules`

All endpoints require JWT authentication. Access: org_admin only.

---

## CRUD Operations

### GET /api/reports/schedules

List all report schedules for the org.

**Query Parameters**: page, page_size, is_active (boolean), report_type

**Response 200**:
```json
{
  "data": [
    {
      "id": "uuid",
      "report_template": {
        "id": "uuid",
        "name": "Daily Reconciliation - Main Branch",
        "report_type": "daily_reconciliation"
      },
      "frequency": "daily",
      "schedule_time": "17:00",
      "day_of_week": null,
      "day_of_month": null,
      "recipients": ["manager@bank.com", "ops@bank.com"],
      "export_format": "xlsx",
      "no_data_behavior": "send_empty",
      "is_active": true,
      "last_run_at": "2026-05-24T17:00:00Z",
      "next_run_at": "2026-05-25T17:00:00Z",
      "last_status": "success",
      "last_error": null,
      "created_by": "string",
      "created_at": "2026-05-01T10:00:00Z"
    }
  ],
  "pagination": { ... }
}
```

---

### POST /api/reports/schedules

Create a new report schedule.

**Request Body**:
```json
{
  "report_template_id": "uuid",
  "frequency": "daily | weekly | monthly",
  "schedule_time": "17:00",
  "day_of_week": 0,
  "day_of_month": null,
  "recipients": ["manager@bank.com"],
  "export_format": "xlsx | csv | pdf",
  "no_data_behavior": "send_empty | skip_delivery"
}
```

**Validation**:
- `recipients`: 1-10 valid email addresses
- `day_of_week`: Required if frequency = weekly (0=Monday, 6=Sunday)
- `day_of_month`: Required if frequency = monthly (1-28)
- `schedule_time`: Valid HH:MM format

**Response 201**: Created schedule object with computed `next_run_at`.

---

### PATCH /api/reports/schedules/{id}

Update schedule. Partial update.

**Request Body**: Any subset of POST fields.

**Response 200**: Updated schedule object.

---

### DELETE /api/reports/schedules/{id}

Soft-delete (sets is_active = false) or hard-delete.

**Response 204**: No content.

---

## Schedule Operations

### POST /api/reports/schedules/{id}/run-now

Trigger immediate execution of a schedule (for testing).

**Response 202**:
```json
{
  "job_id": "uuid",
  "message": "Report generation started"
}
```

---

### GET /api/reports/schedules/{id}/history

Get execution history for a schedule.

**Query Parameters**: page, page_size, status_filter

**Response 200**:
```json
{
  "data": [
    {
      "archive_id": "uuid",
      "status": "success | failed",
      "record_count": 245,
      "file_name": "reconciliation_2026-05-24.xlsx",
      "delivery_status": "delivered",
      "delivery_recipients": ["manager@bank.com"],
      "delivery_error": null,
      "created_at": "2026-05-24T17:02:00Z"
    }
  ],
  "pagination": { ... }
}
```

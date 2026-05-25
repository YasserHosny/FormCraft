# Data Model: Operational Report Engine

## Entity Relationship Diagram

```
organizations (existing)
    │
    ├── 1:N ── report_templates
    │              │
    │              └── 1:N ── report_schedules
    │                            │
    │                            └── 1:N ── report_archives
    │
    └── 1:N ── submissions (existing, queried by reports)
```

## New Tables

### report_templates

Saved report configurations (both pre-built and custom).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, default gen_random_uuid() | |
| organization_id | uuid | FK → organizations.id, NOT NULL | Owning org |
| name | text | NOT NULL | Display name (bilingual via i18n key) |
| name_ar | text | | Arabic name |
| report_type | enum | NOT NULL | `transaction_register`, `daily_reconciliation`, `period_summary`, `custom`, `beneficiary`, `void_reprint`, `signatory_usage` |
| description | text | | Optional description |
| config | jsonb | NOT NULL, default '{}' | Report-specific configuration (see Config Schemas below) |
| is_system | boolean | NOT NULL, default false | true = pre-built report, false = custom |
| created_by | uuid | FK → profiles.id, NOT NULL | Creator |
| created_at | timestamptz | NOT NULL, default now() | |
| updated_at | timestamptz | NOT NULL, default now() | |

**Indexes**:
- `idx_report_templates_org` on (organization_id)
- `idx_report_templates_type` on (organization_id, report_type)

**RLS Policy**: `organization_id = auth.org_id()`

---

### report_schedules

Recurring report delivery schedules.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, default gen_random_uuid() | |
| report_template_id | uuid | FK → report_templates.id, NOT NULL, ON DELETE CASCADE | |
| organization_id | uuid | FK → organizations.id, NOT NULL | Denormalized for RLS |
| frequency | enum | NOT NULL | `daily`, `weekly`, `monthly` |
| schedule_time | time | NOT NULL | Time of day to generate (org timezone) |
| day_of_week | smallint | | 0-6 for weekly schedules (0=Monday) |
| day_of_month | smallint | | 1-28 for monthly schedules |
| recipients | jsonb | NOT NULL | Array of email addresses |
| export_format | enum | NOT NULL, default 'xlsx' | `xlsx`, `csv`, `pdf` |
| no_data_behavior | enum | NOT NULL, default 'send_empty' | `send_empty`, `skip_delivery` |
| is_active | boolean | NOT NULL, default true | |
| last_run_at | timestamptz | | |
| next_run_at | timestamptz | | Computed on save/after run |
| last_status | enum | default 'pending' | `pending`, `success`, `failed` |
| last_error | text | | Error message from last failed run |
| created_by | uuid | FK → profiles.id, NOT NULL | |
| created_at | timestamptz | NOT NULL, default now() | |
| updated_at | timestamptz | NOT NULL, default now() | |

**Indexes**:
- `idx_report_schedules_next_run` on (next_run_at) WHERE is_active = true
- `idx_report_schedules_org` on (organization_id)

**RLS Policy**: `organization_id = auth.org_id()`

---

### report_archives

Generated report file snapshots.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, default gen_random_uuid() | |
| organization_id | uuid | FK → organizations.id, NOT NULL | |
| report_template_id | uuid | FK → report_templates.id, ON DELETE SET NULL | |
| schedule_id | uuid | FK → report_schedules.id, ON DELETE SET NULL | NULL for one-time exports |
| report_type | enum | NOT NULL | Same enum as report_templates |
| file_name | text | NOT NULL | Generated filename |
| file_path | text | NOT NULL | Supabase Storage path |
| file_size_bytes | bigint | NOT NULL | |
| export_format | enum | NOT NULL | `xlsx`, `csv`, `pdf` |
| filters_applied | jsonb | NOT NULL | Snapshot of filters used |
| record_count | integer | NOT NULL | Number of rows in report |
| generated_by | uuid | FK → profiles.id | NULL for scheduled reports |
| generation_method | enum | NOT NULL | `manual`, `scheduled` |
| delivery_status | enum | default 'generated' | `generated`, `delivered`, `delivery_failed` |
| delivery_recipients | jsonb | | Email recipients for scheduled delivery |
| delivery_error | text | | |
| expires_at | timestamptz | NOT NULL | created_at + 12 months |
| created_at | timestamptz | NOT NULL, default now() | |

**Indexes**:
- `idx_report_archives_org_date` on (organization_id, created_at DESC)
- `idx_report_archives_expires` on (expires_at) — for cleanup job

**RLS Policy**: `organization_id = auth.org_id()`

---

## Modified Existing Tables

### elements (existing — add column)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| field_type_tag | enum | default NULL | `amount`, `date`, `customer_name`, `customer_id`, `reference_number`, `beneficiary`, `signatory` — used by report engine to identify summable/groupable fields |

**Note**: This is a designer-assigned tag, independent of the element's `control_type`. Designers assign it via the element properties panel.

---

## Config Schemas (JSONB)

### Transaction Register Config
```json
{
  "display_columns": ["reference_number", "template_name", "operator", "customer", "date", "status"],
  "key_field_display": ["field_key_1", "field_key_2", "field_key_3"],
  "default_sort": "created_at_desc"
}
```

### Daily Reconciliation Config
```json
{
  "auto_generate_time": "17:00",
  "include_zero_operators": true,
  "amount_field_tags": ["amount"]
}
```

### Period Summary Config
```json
{
  "periods": ["week", "month", "quarter", "year"],
  "groupings": ["department", "branch", "template", "operator"],
  "show_comparison": true,
  "chart_type": "bar"
}
```

### Custom Report Config
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
    {"function": "sum", "field": "amount", "alias": "total_amount"},
    {"function": "count", "field": "*", "alias": "submission_count"}
  ],
  "group_by": ["branch_id"],
  "chart_type": "bar",
  "chart_config": {}
}
```

## State Transitions

### Report Schedule States
```
pending → success (after successful generation + delivery)
pending → failed (after generation or delivery error)
failed → success (on next successful run)
```

### Report Archive Lifecycle
```
generated → delivered (email sent successfully)
generated → delivery_failed (email send failed)
[Any state] → [deleted] (after expires_at reached, purged by cleanup job)
```

## Validation Rules

- `report_schedules.recipients`: Must contain 1-10 valid email addresses
- `report_schedules.schedule_time`: Valid time in 24h format
- `report_schedules.day_of_week`: Required when frequency = 'weekly', must be 0-6
- `report_schedules.day_of_month`: Required when frequency = 'monthly', must be 1-28
- `report_archives.expires_at`: Always set to `created_at + interval '12 months'`
- `elements.field_type_tag`: Optional; only set by designer; does not affect form filling behavior

# Data Model: Customer Profiles & Auto-Populate

**Feature**: 030-customer-profiles
**Date**: 2026-05-25

---

## New Tables

### `customers`

Primary customer profile table. One row per known customer/entity per organization.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | Unique customer ID |
| org_id | UUID | FK → organizations(id), NOT NULL | Organization scope |
| name_ar | TEXT | NOT NULL | Customer name in Arabic |
| name_en | TEXT | | Customer name in English |
| identifier_type | TEXT | NOT NULL, CHECK (identifier_type IN ('national_id', 'iqama', 'commercial_register', 'passport', 'other')) | Type of government identifier |
| identifier | TEXT | NOT NULL | Government identifier value |
| contact_phone | TEXT | | Phone number |
| contact_email | TEXT | | Email address |
| address | TEXT | | Mailing/physical address |
| custom_fields | JSONB | DEFAULT '{}' | Org-specific custom field values (validated against org settings schema) |
| is_active | BOOLEAN | NOT NULL, DEFAULT true | false = deactivated (hidden from operator search) |
| search_vector | tsvector | GENERATED ALWAYS AS (to_tsvector('simple', coalesce(name_ar,'') \|\| ' ' \|\| coalesce(name_en,'') \|\| ' ' \|\| coalesce(identifier,'') \|\| ' ' \|\| coalesce(contact_phone,'') \|\| ' ' \|\| coalesce(contact_email,''))) STORED | Full-text search vector |
| created_by | UUID | FK → auth.users(id) | User who created the record |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Last update timestamp |

**Constraints**:
- `UNIQUE (org_id, identifier_type, identifier)` — prevents duplicate customers within an org
- GIN index on `search_vector` for full-text search performance
- Index on `(org_id, is_active)` for filtered list queries
- Index on `(org_id, updated_at DESC)` for sorting by recent activity

**RLS Policies**:
- SELECT: `auth.uid() IN (SELECT id FROM profiles WHERE org_id = customers.org_id)`
- INSERT: Same as SELECT + role IN ('operator', 'admin', 'org_admin')
- UPDATE: Same as INSERT
- DELETE: role IN ('admin', 'org_admin') only

---

### `customer_field_mappings`

Per-template designer overrides for auto-populate field mapping. Tier 2 of the two-tier mapping system.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | Mapping ID |
| template_id | UUID | FK → templates(id) ON DELETE CASCADE, NOT NULL | Template this mapping belongs to |
| element_key | TEXT | NOT NULL | The template element's field key (e.g., 'applicant_name') |
| customer_field | TEXT | NOT NULL, CHECK (customer_field IN ('name_ar', 'name_en', 'identifier', 'identifier_type', 'contact_phone', 'contact_email', 'address')) | Customer profile field to map from |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Creation timestamp |

**Constraints**:
- `UNIQUE (template_id, element_key)` — each element maps to at most one customer field per template
- Index on `template_id` for lookup by template

**RLS Policies**:
- SELECT: User has access to the template's org
- INSERT/UPDATE/DELETE: role IN ('designer', 'admin', 'org_admin')

---

## Table Extensions

### `form_submissions` — Add `customer_id`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| customer_id | UUID | FK → customers(id) ON DELETE SET NULL, NULLABLE | Link to customer profile used during form filling |

**Index**: `(customer_id)` for customer submission history lookups

**Notes**:
- Nullable — existing submissions have no customer link
- ON DELETE SET NULL — deleting a customer doesn't cascade-delete submissions
- No backfill of existing data

---

### Org Settings — Add `customer_custom_fields`

Stored in the organization's `settings` JSONB column under the key `customer_custom_fields`.

**Schema shape**:
```json
{
  "customer_custom_fields": [
    {
      "key": "account_number",
      "label_ar": "رقم الحساب",
      "label_en": "Account Number",
      "type": "text",
      "required": false
    },
    {
      "key": "credit_rating",
      "label_ar": "التصنيف الائتماني",
      "label_en": "Credit Rating",
      "type": "dropdown",
      "required": false,
      "options": ["A", "B", "C", "D"]
    }
  ]
}
```

**Supported types**: `text`, `number`, `date`, `dropdown`

**Validation**: On customer create/update, validate `custom_fields` JSONB against the org's `customer_custom_fields` schema:
- All required fields must be present
- Values must match declared type
- Dropdown values must be in the options list
- Unknown keys (not in schema) are rejected

---

### Org Settings — Add `auto_create_customer_profiles`

Stored in the organization's `settings` JSONB column.

```json
{
  "auto_create_customer_profiles": true
}
```

Default: `false` (auto-create prompt disabled)

---

## Entity Relationships

```
organizations 1──* customers (org_id)
customers 1──* form_submissions (customer_id, nullable)
templates 1──* customer_field_mappings (template_id)
auth.users 1──* customers (created_by)
```

---

## Migration: `032_customer_profiles.sql`

**Order**: After 031 (notification center)

**Steps**:
1. Create `IdentifierType` check constraint values
2. Create `customers` table with all columns and constraints
3. Create GIN index on `search_vector`
4. Create supporting indexes
5. Enable RLS on `customers`
6. Create RLS policies for `customers`
7. Create `customer_field_mappings` table
8. Enable RLS on `customer_field_mappings`
9. Create RLS policies for `customer_field_mappings`
10. Add `customer_id` column to `form_submissions`
11. Create index on `form_submissions(customer_id)`
12. Create `updated_at` trigger for `customers` (reuse existing trigger function if available)

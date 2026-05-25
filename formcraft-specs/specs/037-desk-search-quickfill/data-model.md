# Data Model: Desk Search & Quick Fill

## New Tables

### `quickfill_mappings`

Stores per-organization configurable field-to-customer-attribute mappings.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | uuid | PK, default gen_random_uuid() | Surrogate key |
| org_id | uuid | NOT NULL, FK → organizations.id | Organization scope |
| field_key | text | NOT NULL | Template element key (e.g., "national_id") |
| customer_attribute | text | NOT NULL | Customer profile attribute (e.g., "identifier") |
| created_at | timestamptz | default now() | Record creation |
| updated_at | timestamptz | default now() | Last update |

**Constraints**:
- UNIQUE (org_id, field_key)
- RLS: SELECT/INSERT/UPDATE/DELETE restricted to org members

**Default seed data** (per org on creation):
- `('full_name', 'name')`
- `('name', 'name')`
- `('national_id', 'identifier')`
- `('id_number', 'identifier')`
- `('phone', 'contact_phone')`
- `('mobile', 'contact_phone')`
- `('address', 'address')`

---

## New Views

### `mv_global_search`

Materialized view for unified search across templates, submissions, and customers.

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Original record ID |
| entity_type | text | 'template', 'submission', or 'customer' |
| org_id | uuid | Organization for RLS filtering |
| branch_id | uuid | Branch for submission/customer filtering |
| department_id | uuid | Department for submission filtering |
| title | text | Display title (template name, ref number, or customer name) |
| subtitle | text | Secondary info (description, customer identifier, etc.) |
| search_vector | tsvector | Full-text search vector |
| name_trigram | text | Name for trigram similarity search |
| metadata | jsonb | Extra type-specific data (e.g., template status, submission date, customer recent count) |
| updated_at | timestamptz | Last update time for refresh tracking |

**Indexes**:
- GIN index on `search_vector`
- GIN index on `name_trigram` using `gin_trgm_ops`
- B-tree index on `(org_id, entity_type)`
- B-tree index on `updated_at`

**Refresh**: Every 5 minutes or on-demand via `REFRESH MATERIALIZED VIEW CONCURRENTLY mv_global_search`.

---

## Modified Tables

### `form_submissions`

| Addition | Type | Description |
|----------|------|-------------|
| customer_id | uuid | FK → customers.id, nullable. Links submission to customer profile when created via Quick Fill. |

### `customers`

No schema changes. Existing fields used:
- `name_ar`, `name_en` → mapped to name fields
- `identifier` → mapped to ID fields
- `contact_phone` → mapped to phone fields
- `address` → mapped to address fields

---

## Entity Relationships

```
organizations ||--o{ quickfill_mappings : configures
organizations ||--o{ templates : owns
organizations ||--o{ customers : owns
organizations ||--o{ form_submissions : owns
branches ||--o{ form_submissions : contains
departments ||--o{ form_submissions : contains
customers ||--o{ form_submissions : linked_to
```

## Search Query Pattern

```sql
-- Global search (grouped by type)
SELECT entity_type, id, title, subtitle, metadata
FROM mv_global_search
WHERE org_id = :org_id
  AND search_vector @@ plainto_tsquery('english', :query)
ORDER BY entity_type, ts_rank(search_vector, plainto_tsquery('english', :query)) DESC
LIMIT :limit_per_type;

-- Fuzzy customer search (Quick Fill dialog)
SELECT id, name_ar, name_en, identifier, contact_phone, metadata
FROM customers
WHERE org_id = :org_id
  AND (
    identifier ILIKE :query
    OR contact_phone ILIKE :query
    OR similarity(name_trigram, :query) > 0.3
  )
ORDER BY similarity(name_trigram, :query) DESC
LIMIT :limit;

-- Exact reference number
SELECT * FROM form_submissions
WHERE reference_number = :ref AND org_id = :org_id;
```

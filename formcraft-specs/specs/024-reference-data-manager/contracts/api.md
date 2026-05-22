# API Contracts: Reference Data Manager

**Date**: 2026-05-17

## Endpoints

### Reference Lists

#### `POST /api/reference-lists`

Create a new reference list.

**Auth**: Admin, Branch Manager  
**Request**:
```json
{
  "name_ar": "البنوك المصرية",
  "name_en": "Egyptian Banks",
  "description": "Master list of banks operating in Egypt",
  "schema": [
    { "key": "code", "label_ar": "الكود", "label_en": "Code", "type": "text", "required": true, "is_unique_key": true, "is_hidden": false },
    { "key": "name_ar", "label_ar": "الاسم", "label_en": "Arabic Name", "type": "text", "required": true, "is_unique_key": false, "is_hidden": false },
    { "key": "swift", "label_ar": "سويفت", "label_en": "SWIFT", "type": "text", "required": false, "is_unique_key": false, "is_hidden": false }
  ]
}
```

**Response 201**:
```json
{
  "id": "uuid",
  "name_ar": "البنوك المصرية",
  "name_en": "Egyptian Banks",
  "description": "Master list of banks operating in Egypt",
  "schema": [...],
  "is_archived": false,
  "entry_count": 0,
  "created_at": "2026-05-17T10:00:00Z"
}
```

**Errors**: 422 (validation), 403 (insufficient role)

---

#### `GET /api/reference-lists`

List all reference lists for the org.

**Auth**: Any authenticated user  
**Query Params**:
- `include_archived` (boolean, default false)
- `page` (int, default 1)
- `page_size` (int, default 50)

**Response 200**:
```json
{
  "items": [
    {
      "id": "uuid",
      "name_ar": "البنوك المصرية",
      "name_en": "Egyptian Banks",
      "description": "...",
      "column_count": 3,
      "entry_count": 42,
      "is_archived": false,
      "created_at": "2026-05-17T10:00:00Z"
    }
  ],
  "total": 12,
  "page": 1,
  "page_size": 50
}
```

---

#### `GET /api/reference-lists/:id`

Get a single list with full schema.

**Auth**: Any authenticated user  
**Response 200**:
```json
{
  "id": "uuid",
  "name_ar": "البنوك المصرية",
  "name_en": "Egyptian Banks",
  "description": "...",
  "schema": [...],
  "is_archived": false,
  "entry_count": 42,
  "created_by": "uuid",
  "created_at": "2026-05-17T10:00:00Z",
  "updated_at": "2026-05-17T10:00:00Z"
}
```

---

#### `PATCH /api/reference-lists/:id`

Update list metadata or schema.

**Auth**: Admin, Branch Manager  
**Request** (partial update):
```json
{
  "name_en": "Banks in Egypt",
  "schema": [
    { "key": "code", "label_ar": "الكود", "label_en": "Code", "type": "text", "required": true, "is_unique_key": true, "is_hidden": false },
    { "key": "name_ar", "label_ar": "الاسم", "label_en": "Arabic Name", "type": "text", "required": true, "is_unique_key": false, "is_hidden": false },
    { "key": "swift", "label_ar": "سويفت", "label_en": "SWIFT", "type": "text", "required": false, "is_unique_key": false, "is_hidden": false },
    { "key": "branch_count", "label_ar": "عدد الفروع", "label_en": "Branch Count", "type": "number", "required": false, "is_unique_key": false }
  ]
}
```

**Constraint**: Removing a required column that has existing entry values is rejected (422). Adding new optional columns is always safe.

**Response 200**: Updated list object  
**Errors**: 422 (schema conflict), 403, 404

---

#### `POST /api/reference-lists/:id/archive`

Archive a list.

**Auth**: Admin  
**Response 200**: `{ "id": "uuid", "is_archived": true }`  
**Errors**: 403, 404

---

#### `POST /api/reference-lists/:id/unarchive`

Unarchive a list.

**Auth**: Admin  
**Response 200**: `{ "id": "uuid", "is_archived": false }`

---

#### `DELETE /api/reference-lists/:id`

Delete a list (only if not bound to any elements).

**Auth**: Admin  
**Response 204**: No content  
**Errors**: 409 "List is bound to N form elements", 403, 404

---

### Reference Entries

#### `GET /api/reference-lists/:id/entries`

Get entries for a list.

**Auth**: Any authenticated user  
**Query Params**:
- `active_only` (boolean, default true) — Form Desk uses true, admin grid uses false
- `q` (string) — full-text search across all text columns
- `page` (int, default 1)
- `page_size` (int, default 100)

**Response 200**:
```json
{
  "items": [
    {
      "id": "uuid",
      "values": { "code": "NBE", "name_ar": "البنك الأهلي", "swift": "NBEGEGCX" },
      "is_active": true,
      "created_at": "2026-05-17T10:00:00Z",
      "updated_at": "2026-05-17T10:00:00Z"
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 100
}
```

---

#### `POST /api/reference-lists/:id/entries`

Create a new entry.

**Auth**: Admin, Branch Manager  
**Request**:
```json
{
  "values": { "code": "CIB", "name_ar": "البنك التجاري الدولي", "swift": "CIBEEGCX" }
}
```

**Response 201**: Entry object  
**Errors**: 422 (schema validation), 409 (unique key conflict), 403

---

#### `PATCH /api/reference-lists/:id/entries/:entry_id`

Update an entry's values.

**Auth**: Admin, Branch Manager  
**Request** (partial values update):
```json
{
  "values": { "swift": "CIBEEGCX001" }
}
```

**Response 200**: Updated entry object  
**Errors**: 422, 409, 403, 404

---

#### `POST /api/reference-lists/:id/entries/:entry_id/deactivate`

Deactivate an entry.

**Auth**: Admin, Branch Manager  
**Response 200**: `{ "id": "uuid", "is_active": false }`

---

#### `POST /api/reference-lists/:id/entries/:entry_id/activate`

Reactivate an entry.

**Auth**: Admin, Branch Manager  
**Response 200**: `{ "id": "uuid", "is_active": true }`

---

### CSV Import

#### `POST /api/reference-lists/:id/import/preview`

Upload CSV and get validation preview.

**Auth**: Admin, Branch Manager  
**Content-Type**: multipart/form-data  
**Form Fields**:
- `file`: CSV file (max 10MB)
- `mode`: "insert" | "update" (default "insert")
- `column_mapping`: JSON string of CSV header → schema key overrides (optional)

**Response 200**:
```json
{
  "total_rows": 50,
  "valid_count": 48,
  "invalid_count": 2,
  "column_mapping": {
    "Bank Code": "code",
    "Arabic Name": "name_ar",
    "SWIFT": "swift"
  },
  "errors": [
    { "row": 12, "column": "code", "message": "Required field is empty" },
    { "row": 34, "column": "swift", "message": "Duplicate value 'NBEGEGCX' (exists in active entries)" }
  ],
  "preview_token": "temp-token-uuid"
}
```

---

#### `POST /api/reference-lists/:id/import/confirm`

Confirm import of valid rows.

**Auth**: Admin, Branch Manager  
**Request**:
```json
{
  "preview_token": "temp-token-uuid",
  "import_valid_only": true
}
```

**Response 200**:
```json
{
  "imported_count": 48,
  "skipped_count": 2,
  "mode": "insert"
}
```

**Errors**: 410 "Preview token expired" (15-min TTL), 403

---

### Form Desk Integration

#### `GET /api/reference-lists/:id/entries/dropdown`

Optimized endpoint for Form Desk dropdown population. Returns only display and value columns for active entries.

**Auth**: Any authenticated (operator+)  
**Query Params**:
- `display_column` (required)
- `value_column` (required)
- `q` (string, optional — for server-side search when >500 entries)

**Response 200**:
```json
{
  "items": [
    { "display": "البنك الأهلي المصري", "value": "NBE", "entry_id": "uuid" },
    { "display": "البنك التجاري الدولي", "value": "CIB", "entry_id": "uuid" }
  ],
  "total": 42,
  "full_entry_available": true
}
```

**Cache**: 5-min TTL, keyed by (org_id, list_id, display_column, value_column)

---

#### `GET /api/reference-lists/:id/entries/:entry_id`

Get full entry (for auto-fill after selection).

**Auth**: Any authenticated (operator+)  
**Response 200**:
```json
{
  "id": "uuid",
  "values": { "code": "NBE", "name_ar": "البنك الأهلي", "name_en": "National Bank of Egypt", "swift": "NBEGEGCX" },
  "is_active": true
}
```

## Error Response Format

All errors follow the standard FormCraft error format:
```json
{
  "detail": "Human-readable error message",
  "errors": [
    { "field": "schema[0].key", "message": "Column key is required" }
  ]
}
```

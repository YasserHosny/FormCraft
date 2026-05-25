# API Contract: Customer Profiles

**Feature**: 030-customer-profiles
**Date**: 2026-05-25
**Base Path**: `/api/customers`

---

## Authentication

All endpoints require a valid JWT token via `Authorization: Bearer <token>`. User must belong to the same org as the customer data being accessed.

---

## Endpoints

### 1. List Customers

**GET** `/api/customers`

List customers for the authenticated user's organization with pagination and optional search.

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page | int | No | 1 | Page number |
| page_size | int | No | 25 | Items per page (max 100) |
| search | string | No | | Full-text search query (name, identifier, phone, email) |
| is_active | bool | No | true | Filter by active status (admins can set false to see deactivated) |
| sort_by | string | No | name_ar | Sort field: name_ar, name_en, created_at, updated_at |
| sort_order | string | No | asc | Sort direction: asc, desc |

**Response 200**:
```json
{
  "items": [
    {
      "id": "uuid",
      "name_ar": "أحمد حسن",
      "name_en": "Ahmed Hassan",
      "identifier_type": "national_id",
      "identifier": "29001011234567",
      "contact_phone": "+966501234567",
      "contact_email": "ahmed@example.com",
      "is_active": true,
      "created_at": "2026-05-25T10:00:00Z",
      "updated_at": "2026-05-25T10:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 25
}
```

**Audit**: Logs `CUSTOMER_SEARCH` with search query in metadata.

---

### 2. Get Customer Detail

**GET** `/api/customers/{customer_id}`

Retrieve a single customer profile with full details including custom fields.

**Response 200**:
```json
{
  "id": "uuid",
  "org_id": "uuid",
  "name_ar": "أحمد حسن",
  "name_en": "Ahmed Hassan",
  "identifier_type": "national_id",
  "identifier": "29001011234567",
  "contact_phone": "+966501234567",
  "contact_email": "ahmed@example.com",
  "address": "Riyadh, Saudi Arabia",
  "custom_fields": {
    "account_number": "SA1234567890",
    "credit_rating": "A"
  },
  "is_active": true,
  "created_by": "uuid",
  "created_at": "2026-05-25T10:00:00Z",
  "updated_at": "2026-05-25T10:00:00Z"
}
```

**Response 404**: Customer not found or not in user's org.

**Audit**: Logs `CUSTOMER_ACCESSED` with customer_id.

---

### 3. Create Customer

**POST** `/api/customers`

Create a new customer profile.

**Request Body**:
```json
{
  "name_ar": "أحمد حسن",
  "name_en": "Ahmed Hassan",
  "identifier_type": "national_id",
  "identifier": "29001011234567",
  "contact_phone": "+966501234567",
  "contact_email": "ahmed@example.com",
  "address": "Riyadh, Saudi Arabia",
  "custom_fields": {
    "account_number": "SA1234567890"
  }
}
```

**Required fields**: `name_ar`, `identifier_type`, `identifier`

**Response 201**: Created customer object (same shape as GET detail).

**Response 409**: Duplicate — customer with same (identifier_type, identifier) already exists in org. Returns existing customer in response body.

**Audit**: Logs `CUSTOMER_CREATED` with customer_id.

**Roles**: operator, admin, org_admin

---

### 4. Update Customer

**PATCH** `/api/customers/{customer_id}`

Update an existing customer profile. Partial update — only include fields to change.

**Request Body**:
```json
{
  "name_en": "Ahmad Hassan",
  "contact_phone": "+966509876543",
  "custom_fields": {
    "credit_rating": "B"
  }
}
```

**Response 200**: Updated customer object.

**Response 404**: Customer not found.

**Response 409**: If identifier_type/identifier changed and conflicts with existing customer.

**Audit**: Logs `CUSTOMER_UPDATED` with changed fields in metadata.

**Roles**: operator, admin, org_admin

---

### 5. Delete Customer

**DELETE** `/api/customers/{customer_id}`

Delete a customer profile. Linked form submissions retain their data but lose customer_id reference (SET NULL).

**Response 200**:
```json
{
  "deleted": true,
  "submissions_unlinked": 12
}
```

**Response 404**: Customer not found.

**Audit**: Logs `CUSTOMER_DELETED` with submission count in metadata.

**Roles**: admin, org_admin

---

### 6. Deactivate / Reactivate Customer

**PATCH** `/api/customers/{customer_id}/status`

Toggle customer active status.

**Request Body**:
```json
{
  "is_active": false
}
```

**Response 200**: Updated customer object.

**Audit**: Logs `CUSTOMER_DEACTIVATED` or `CUSTOMER_REACTIVATED`.

**Roles**: admin, org_admin

---

### 7. Merge Customers

**POST** `/api/customers/merge`

Merge two customer profiles into one. Atomic operation.

**Request Body**:
```json
{
  "surviving_id": "uuid-of-profile-to-keep",
  "duplicate_id": "uuid-of-profile-to-remove",
  "field_selections": {
    "name_ar": "surviving",
    "name_en": "duplicate",
    "contact_phone": "surviving",
    "contact_email": "duplicate",
    "address": "surviving",
    "custom_fields": "surviving"
  }
}
```

`field_selections` values: `"surviving"` or `"duplicate"` — indicates which profile's value to keep for each field.

**Response 200**:
```json
{
  "merged_customer": { "...full customer object..." },
  "submissions_relinked": 8
}
```

**Response 404**: Either customer not found.

**Response 400**: Cannot merge — both IDs are the same, or one is already deactivated.

**Audit**: Logs `CUSTOMER_MERGED` with both source IDs, surviving ID, field selections, and submission count in metadata.

**Roles**: admin, org_admin

---

### 8. Get Customer Submission History

**GET** `/api/customers/{customer_id}/submissions`

List all form submissions linked to this customer, grouped by template.

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page | int | No | 1 | Page number |
| page_size | int | No | 25 | Items per page |
| template_id | uuid | No | | Filter by template |
| date_from | date | No | | Filter submissions from this date |
| date_to | date | No | | Filter submissions up to this date |

**Response 200**:
```json
{
  "items": [
    {
      "id": "submission-uuid",
      "template_id": "template-uuid",
      "template_name": "Employment Certificate",
      "status": "completed",
      "created_at": "2026-05-20T14:30:00Z",
      "created_by_name": "Operator Name"
    }
  ],
  "total": 45,
  "page": 1,
  "page_size": 25
}
```

**Audit**: Logs `CUSTOMER_HISTORY_ACCESSED`.

---

### 9. Get Auto-Populate Data

**GET** `/api/customers/{customer_id}/auto-populate?template_id={template_id}`

Returns the field mapping for auto-populating a specific template from this customer's data.

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| template_id | uuid | Yes | Template being filled |

**Response 200**:
```json
{
  "customer_id": "uuid",
  "customer_name": "أحمد حسن",
  "mappings": [
    {
      "element_key": "national_id",
      "value": "29001011234567",
      "source": "default"
    },
    {
      "element_key": "customer_name_ar",
      "value": "أحمد حسن",
      "source": "default"
    },
    {
      "element_key": "applicant_phone",
      "value": "+966501234567",
      "source": "override"
    }
  ]
}
```

`source`: `"default"` (Tier 1 convention match) or `"override"` (Tier 2 template-specific mapping).

**Audit**: Logs `CUSTOMER_AUTO_POPULATED` with template_id and field count.

---

### 10. Get/Set Template Field Mappings (Designer)

**GET** `/api/templates/{template_id}/customer-field-mappings`

Returns default + override mappings for a template.

**Response 200**:
```json
{
  "default_mappings": [
    {
      "element_key": "national_id",
      "customer_field": "identifier",
      "source": "default"
    }
  ],
  "override_mappings": [
    {
      "id": "mapping-uuid",
      "element_key": "applicant_phone",
      "customer_field": "contact_phone",
      "source": "override"
    }
  ]
}
```

**PUT** `/api/templates/{template_id}/customer-field-mappings`

Replace all override mappings for a template.

**Request Body**:
```json
{
  "mappings": [
    {
      "element_key": "applicant_phone",
      "customer_field": "contact_phone"
    },
    {
      "element_key": "company_name",
      "customer_field": "name_en"
    }
  ]
}
```

**Response 200**: Updated mappings (same shape as GET response).

**Roles**: designer, admin, org_admin

---

### 11. Get Recently Used Customers

**GET** `/api/customers/recent`

Returns the last 5 customers used by the authenticated user (based on audit log entries for auto-populate actions).

**Response 200**:
```json
{
  "items": [
    {
      "id": "uuid",
      "name_ar": "أحمد حسن",
      "name_en": "Ahmed Hassan",
      "identifier": "29001011234567",
      "last_used_at": "2026-05-25T09:00:00Z"
    }
  ]
}
```

---

## Submission Extension

### Create Submission (Extended)

**POST** `/api/submissions` (existing endpoint — extended)

**Added field in request body**:
```json
{
  "template_id": "uuid",
  "template_version": 1,
  "field_values": {},
  "status": "completed",
  "customer_id": "uuid-optional"
}
```

`customer_id` is optional. When provided, the submission is linked to the customer profile.

---

## Error Responses

All endpoints use standard error format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

| Status | Meaning |
|--------|---------|
| 400 | Invalid request body or parameters |
| 401 | Missing or invalid JWT token |
| 403 | Insufficient role permissions |
| 404 | Resource not found or not in user's org |
| 409 | Conflict (duplicate identifier) |
| 500 | Internal server error |

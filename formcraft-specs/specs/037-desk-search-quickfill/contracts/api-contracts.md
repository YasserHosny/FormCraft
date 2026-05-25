# API Contracts: Desk Search & Quick Fill

## Endpoints

### Global Search

#### `GET /api/v1/search`

Searches across templates, submissions, and customers.

**Query Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| q | string | Yes | Search query string |
| types | string | No | Comma-separated list of types to include: `template,submission,customer`. Default: all. |
| limit | integer | No | Max results per type. Default: 5. Max: 20. |

**Response** (200 OK):
```json
{
  "query": "string",
  "results": [
    {
      "type": "template",
      "id": "uuid",
      "title": "string",
      "subtitle": "string",
      "metadata": {}
    },
    {
      "type": "submission",
      "id": "uuid",
      "title": "FC-2026-05-0042",
      "subtitle": "Customer Name",
      "metadata": {
        "template_name": "string",
        "created_at": "2026-05-26T10:00:00Z"
      }
    },
    {
      "type": "customer",
      "id": "uuid",
      "title": "Customer Name",
      "subtitle": "ID: 1234567890",
      "metadata": {
        "recent_submissions_count": 3
      }
    }
  ]
}
```

**Error Responses**:
- `400 Bad Request` — query missing or too short (< 2 chars)
- `429 Too Many Requests` — rate limit exceeded (50 req/min per operator)

---

### Reference Number Search

#### `GET /api/v1/search/reference`

Exact-match search for submission by reference number.

**Query Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| ref | string | Yes | Reference number (e.g., "FC-2026-05-0042") |

**Response** (200 OK):
```json
{
  "found": true,
  "submission": {
    "id": "uuid",
    "reference_number": "FC-2026-05-0042",
    "template_name": "string",
    "customer_name": "string",
    "created_at": "2026-05-26T10:00:00Z",
    "status": "completed"
  }
}
```

**Response** (200 OK, not found):
```json
{
  "found": false,
  "submission": null
}
```

---

### Quick Fill Customer Search

#### `GET /api/v1/quickfill/customers`

Searches customers for Quick Fill dialog with fuzzy matching.

**Query Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| q | string | Yes | Search query (name, identifier, or phone) |
| limit | integer | No | Max results. Default: 10. Max: 50. |

**Response** (200 OK):
```json
{
  "query": "string",
  "customers": [
    {
      "id": "uuid",
      "name_ar": "string",
      "name_en": "string",
      "identifier": "string",
      "contact_phone": "string",
      "recent_submissions_count": 3,
      "match_score": 0.95
    }
  ]
}
```

---

### Quick Fill Field Mapping

#### `POST /api/v1/quickfill/map`

Maps customer data to template fields for auto-population.

**Request Body**:
```json
{
  "customer_id": "uuid",
  "template_id": "uuid"
}
```

**Response** (200 OK):
```json
{
  "customer_id": "uuid",
  "template_id": "uuid",
  "mapped_fields": [
    {
      "field_key": "full_name",
      "field_label": "Full Name",
      "value": "Ahmed Ali",
      "source_attribute": "name",
      "confidence": "high"
    }
  ],
  "unmapped_customer_attributes": ["email"],
  "mapping_count": 4
}
```

**Error Responses**:
- `404 Not Found` — customer or template not found
- `403 Forbidden` — customer/template not in operator's scope

---

## WebSocket / Real-Time (Future)

Not required for MVP. Search is request-response with client-side debounce.

## Rate Limits

- `search`: 50 requests per minute per operator
- `quickfill/customers`: 30 requests per minute per operator
- `quickfill/map`: 30 requests per minute per operator

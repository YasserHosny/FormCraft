# API Contracts: Form Import & OCR Detection

**Date**: 2026-05-23
**Base Path**: `/api/forms`

## POST /forms/import/{template_id}

Upload a form image and detect fillable fields using OCR.

**Auth**: Required (role: admin or designer)
**Content-Type**: multipart/form-data

**Parameters**:
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| template_id | path | UUID | yes | Target template ID |
| file | body | File | yes | JPEG or PNG image (max 10 MB) |
| page_index | query | int | no | Zero-indexed page number (default: 0) |

**Response 200**:
```json
{
  "id": "uuid",
  "template_id": "uuid",
  "page_index": 0,
  "detected_fields": [
    {
      "text": "25-09-2012",
      "bbox": {"x": 10.5, "y": 20.3, "width": 30.2, "height": 8.1},
      "confidence": 0.95,
      "suggested_type": "date",
      "status": "pending"
    }
  ],
  "page_dimensions": {"width": 210.0, "height": 148.5},
  "created_at": "2026-05-23T10:30:00Z"
}
```

**Errors**:
| Code | Condition |
|------|-----------|
| 400 | Unsupported file type (not JPEG/PNG) |
| 400 | No page dimensions detected |
| 413 | File exceeds 10 MB |
| 500 | OCR service configuration error (credentials missing) |
| 500 | OCR processing failure |

---

## GET /forms/{template_id}/detections

Get all OCR detections for a template, ordered by most recent first.

**Auth**: Required
**Response 200**: Array of FormDetectionResponse (same schema as import response)

---

## POST /forms/{template_id}/detections/{detection_id}/accept

Accept selected detections and create FormCraft elements.

**Auth**: Required (role: admin or designer)
**Content-Type**: application/json

**Request Body**:
```json
{
  "detection_ids": [0, 2, 5],
  "type_overrides": {
    "2": "date",
    "5": "currency"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| detection_ids | int[] | yes | Indices into the detected_fields array |
| type_overrides | object | no | Map of index → overridden element type |

**Response 200**:
```json
{
  "message": "Accepted detections",
  "created_elements": 3
}
```

**Errors**:
| Code | Condition |
|------|-----------|
| 400 | Invalid detection index |
| 404 | Detection or page not found |

---

## DELETE /forms/detections/{detection_id}

Delete a detection record entirely.

**Auth**: Required (role: admin or designer)
**Response 200**:
```json
{
  "message": "Detection deleted successfully"
}
```

**Errors**:
| Code | Condition |
|------|-----------|
| 404 | Detection not found |

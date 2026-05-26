# API Contracts: Batch OCR Onboarding

**Date**: 2026-05-26
**Base Path**: `/api/ocr-onboarding`

## POST /batches

Create an onboarding batch and validate uploaded files.

**Auth**: Admin or Designer
**Content-Type**: multipart/form-data

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | yes | Batch name |
| confidence_threshold | number | no | Bulk-accept threshold, default 0.85 |
| files | File[] | yes | PDF/JPEG/PNG files, max 200 |

**Response 201**

```json
{
  "id": "uuid",
  "name": "Legacy HR Forms",
  "status": "queued",
  "confidence_threshold": 0.85,
  "total_items": 2,
  "processed_items": 0,
  "accepted_items": 0,
  "failed_items": 0,
  "duplicate_items": 0,
  "created_at": "2026-05-26T10:00:00Z",
  "updated_at": "2026-05-26T10:00:00Z"
}
```

## GET /batches

List onboarding batches for the current organization.

**Query**: `status`, `limit`, `offset`

**Response 200**

```json
{
  "items": [{ "id": "uuid", "name": "Legacy HR Forms", "status": "needs_review", "total_items": 200 }],
  "total": 1
}
```

## GET /batches/{batch_id}

Return batch details and items.

**Response 200**

```json
{
  "id": "uuid",
  "name": "Legacy HR Forms",
  "status": "needs_review",
  "items": [
    {
      "id": "uuid",
      "file_name": "scan-001.png",
      "status": "needs_review",
      "confidence": 0.93,
      "likely_type": "employment_application",
      "category": "HR",
      "language": "ar",
      "retry_count": 0,
      "last_error": null,
      "converted_template_id": null
    }
  ]
}
```

## POST /batches/{batch_id}/items/{item_id}/retry

Retry one failed or delayed item without re-uploading the batch.

**Response 200**: Updated item.

## POST /batches/{batch_id}/items/{item_id}/decision

Record item-level review decision.

**Request**

```json
{
  "action": "accept",
  "payload": {
    "detection_overrides": []
  }
}
```

**Response 200**: Updated item.

## POST /batches/{batch_id}/bulk-accept

Accept eligible high-confidence items. The server rejects items below the batch threshold.

**Request**

```json
{
  "item_ids": ["uuid"]
}
```

**Response 200**

```json
{
  "accepted_count": 1,
  "skipped": []
}
```

## POST /batches/{batch_id}/duplicates/{candidate_id}/resolve

Resolve a duplicate candidate.

**Request**

```json
{
  "decision": "keep_one"
}
```

**Response 200**: Updated duplicate candidate.

# Quickstart: Batch OCR Onboarding

## Prerequisites

1. Backend and frontend are running locally.
2. Migration `042_batch_ocr_onboarding.sql` is applied.
3. Existing OCR provider settings from the single-form OCR feature are configured.
4. User has admin or designer/reviewer permissions in an organization.

## API Smoke Test

```bash
curl -X POST http://localhost:8000/api/ocr-onboarding/batches \
  -H "Authorization: Bearer $JWT" \
  -F "name=Legacy HR Forms" \
  -F "confidence_threshold=0.85" \
  -F "files=@scan-001.png" \
  -F "files=@scan-002.png"

curl http://localhost:8000/api/ocr-onboarding/batches/{batch_id} \
  -H "Authorization: Bearer $JWT"

curl -X POST http://localhost:8000/api/ocr-onboarding/batches/{batch_id}/bulk-accept \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{"item_ids":["..."]}'
```

## UI Smoke Test

1. Open Admin → OCR Onboarding.
2. Create a batch with scanned PDF/image files.
3. Confirm the dashboard shows queued, processing, needs-review, failed, and duplicate counts.
4. Bulk-accept eligible high-confidence items.
5. Open a low-confidence item, edit/reject/defer detections, then accept.
6. Retry one failed item and verify the batch history keeps the first failure and retry decision.
7. Switch Arabic/English and verify labels, confidence messages, and RTL/LTR layout.

# Data Model: Batch OCR Onboarding

**Date**: 2026-05-26
**Feature**: 045-batch-ocr-onboarding

## Entities

### OCRImportBatch

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Batch identifier |
| org_id | UUID | FK, NOT NULL | Owning organization |
| name | TEXT | NOT NULL | User-visible batch name |
| status | TEXT | CHECK queued/processing/needs_review/completed/failed/cancelled | Aggregate batch state |
| confidence_threshold | NUMERIC | 0.0-1.0, default 0.85 | Minimum confidence for bulk-accept eligibility |
| total_items | INT | default 0, max 200 | Uploaded item count |
| processed_items | INT | default 0 | Items with final OCR result or review state |
| accepted_items | INT | default 0 | Items converted to drafts |
| failed_items | INT | default 0 | Items currently failed |
| duplicate_items | INT | default 0 | Items marked duplicate |
| created_by | UUID | FK profiles | Creator |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL | Audit timestamps |

### OCRImportItem

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Item identifier |
| batch_id | UUID | FK OCRImportBatch, cascade | Parent batch |
| org_id | UUID | FK, NOT NULL | Owning organization |
| file_name | TEXT | NOT NULL | Original upload name |
| storage_path | TEXT | nullable | Uploaded scan location |
| mime_type | TEXT | NOT NULL | PDF/image media type |
| file_size_bytes | BIGINT | NOT NULL | Size used for validation |
| checksum | TEXT | nullable | Duplicate detection fingerprint |
| status | TEXT | CHECK queued/processing/needs_review/accepted/rejected/failed/duplicate/converted | Item lifecycle state |
| likely_type | TEXT | nullable | Detected form type |
| category | TEXT | nullable | Detected category |
| language | TEXT | nullable | Detected language hint |
| page_count | INT | default 1 | Detected page count |
| confidence | NUMERIC | 0.0-1.0 | Aggregate detection confidence |
| detection_set | JSONB | default '{}' | Fields/pages returned by OCR |
| existing_detection_id | UUID | nullable | Optional link to `form_detections` when reused |
| retry_count | INT | default 0 | Item-level retry count |
| last_error | TEXT | nullable | Last failure reason |
| converted_template_id | UUID | FK templates, nullable | Draft template created after acceptance |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL | Audit timestamps |

### OCRReviewDecision

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Decision identifier |
| batch_id | UUID | FK | Batch |
| item_id | UUID | FK | Item |
| decided_by | UUID | FK profiles | Reviewer |
| action | TEXT | CHECK accept/reject/edit/defer/merge/retry/bulk_accept | Review action |
| payload | JSONB | default '{}' | Edited detections, merge target, or retry details |
| created_at | TIMESTAMPTZ | NOT NULL | Decision timestamp |

### OCRDuplicateCandidate

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Candidate identifier |
| batch_id | UUID | FK | Batch |
| item_id | UUID | FK | Candidate item |
| duplicate_item_id | UUID | nullable | Matching item in same batch |
| existing_template_id | UUID | nullable | Matching existing template |
| similarity_score | NUMERIC | 0.0-1.0 | Similarity score |
| evidence | JSONB | default '{}' | Matching signals and thumbnails |
| decision | TEXT | CHECK pending/keep_one/keep_both/merge/exclude | Reviewer resolution |
| created_at / updated_at | TIMESTAMPTZ | NOT NULL | Audit timestamps |

## Relationships

```text
ocr_import_batches (1) ── (N) ocr_import_items
ocr_import_batches (1) ── (N) ocr_review_decisions
ocr_import_items   (1) ── (N) ocr_review_decisions
ocr_import_items   (1) ── (N) ocr_duplicate_candidates
ocr_import_items   (0..1) ── (1) templates converted draft
ocr_import_items   (0..1) ── (1) form_detections reused detection record
```

## State Transitions

```text
queued -> processing -> needs_review -> accepted -> converted
queued -> failed -> queued
needs_review -> rejected
needs_review -> duplicate -> needs_review | rejected | accepted
processing -> failed
```

## Validation Rules

- A batch cannot contain more than 200 items.
- Bulk accept only applies to items in `needs_review` with `confidence >= confidence_threshold`.
- Conversion requires a recorded reviewer decision.
- Retry is allowed only for `failed`, `queued`, or quota-delayed items and increments `retry_count`.
- Converted items must store the created draft template id.

# Research: Batch OCR Onboarding

**Date**: 2026-05-26
**Feature**: 045-batch-ocr-onboarding

## R1: OCR Processing Reuse

**Decision**: Reuse the existing single-form OCR services for each batch item.
**Rationale**: The project already has OCR extraction, field classification, coordinate conversion, and detection persistence. Reuse limits provider drift and respects the clarification that F045 is an onboarding layer, not a new OCR engine.
**Alternatives Considered**: A separate batch OCR provider adapter was rejected because it would duplicate provider configuration, tests, and confidence behavior.

## R2: Conversion Gate

**Decision**: High-confidence items are eligible for bulk acceptance, but no item converts to a draft template until a reviewer explicitly accepts it.
**Rationale**: This satisfies the constitution's human-review requirement for probabilistic suggestions while preserving the time savings of confidence-ranked triage.
**Alternatives Considered**: Fully automatic conversion was rejected because false positives would create templates without accountability.

## R3: Batch Scale

**Decision**: Guarantee 200 forms per onboarding batch for the first implementation.
**Rationale**: The spec success criteria name 200 forms, and the UI/API can enforce a bounded first release without inventing a general-purpose processing platform.
**Alternatives Considered**: Unlimited uploads were rejected as operationally unsafe; a lower limit would not meet SC-001.

## R4: Retry and Failure Model

**Decision**: Store each file as an item with status, retry count, last error, and timestamps; retry only selected failed/timed-out/quota-delayed items.
**Rationale**: Item-level recovery avoids re-uploading a whole legacy library and keeps audit history intact.
**Alternatives Considered**: Batch-level restart was rejected because one bad file would waste already-successful OCR work.

## R5: Duplicate Resolution

**Decision**: Store duplicate candidates separately with similarity score/evidence and reviewer decision.
**Rationale**: Duplicate relationships may point to another uploaded item or an existing template. A separate table keeps item state normalized and auditable.
**Alternatives Considered**: Embedding duplicate evidence in item JSON was rejected because reviewers need to query unresolved duplicate groups efficiently.

# Feature Specification: Batch OCR Onboarding

**Feature Branch**: `045-batch-ocr-onboarding`  
**Created**: 2026-05-26  
**Status**: Draft  
**Input**: User description: "Batch OCR onboarding for form libraries: admins upload large sets of scanned forms, monitor background OCR classification, review confidence-ranked detections, bulk approve high-confidence templates, resolve duplicate or low-confidence forms, and convert a legacy form library into draft templates."

## Clarifications

### Session 2026-05-26

- Q: Should high-confidence detections convert automatically or require reviewer confirmation? → A: Reviewer bulk acceptance required.
- Q: Should F045 introduce a separate OCR provider workflow or reuse the existing single-form OCR capability? → A: Reuse existing OCR pipeline.
- Q: What batch scale should the first implementation guarantee? → A: 200 forms per batch.
- Q: How should partially failed provider work be recovered? → A: Resumable item-level retries.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload a Legacy Form Library (Priority: P1)

An admin or implementation consultant uploads a large set of scanned forms and starts an OCR onboarding batch.

**Why this priority**: Enterprise onboarding value depends on digitizing many existing forms quickly, not one form at a time.

**Independent Test**: Can be tested by uploading a mixed batch of scanned PDFs and images and confirming each file receives a processing state.

**Acceptance Scenarios**:

1. **Given** an admin uploads a supported set of scanned forms, **When** they start the batch, **Then** the system validates files, creates batch items, and shows processing progress.
2. **Given** one file is unsupported or corrupt, **When** the batch starts, **Then** the valid files continue and the invalid item is marked for user action.

---

### User Story 2 - Review and Bulk Accept Results (Priority: P2)

A reviewer works through confidence-ranked OCR results, bulk accepting high-confidence forms and manually reviewing uncertain forms.

**Why this priority**: Batch OCR only saves time if users can triage results quickly and focus attention where confidence is low.

**Independent Test**: Can be tested by processing sample forms with varied confidence levels and confirming bulk actions create draft templates only for accepted items.

**Acceptance Scenarios**:

1. **Given** a batch has high-confidence items, **When** the reviewer bulk accepts them, **Then** draft templates are created with detected pages, fields, categories, and review metadata.
2. **Given** a low-confidence item has ambiguous fields, **When** the reviewer opens it, **Then** they can accept, reject, edit, or defer individual detections.
3. **Given** high-confidence detections are available, **When** the reviewer has not selected bulk accept, **Then** no draft templates are created from those detections.

---

### User Story 3 - Resolve Duplicates and Failed Items (Priority: P3)

An admin handles duplicate forms, OCR failures, and retries without losing the batch history.

**Why this priority**: Real form libraries contain repeated scans, rotated pages, bad files, and provider timeouts.

**Independent Test**: Can be tested by including duplicate and failing samples and confirming the system groups, retries, or excludes them with clear reasons.

**Acceptance Scenarios**:

1. **Given** two uploads appear to be duplicates, **When** the reviewer opens duplicate review, **Then** the system shows similarity evidence and lets the reviewer keep one, keep both, or merge decisions.
2. **Given** OCR provider quota is exceeded mid-batch, **When** capacity returns, **Then** queued or failed items can retry without re-uploading the whole batch.

### Edge Cases

- Mixed DPI, rotated, skewed, or multi-page scans appear in one batch.
- A password-protected PDF or damaged image is uploaded.
- OCR completes for some pages but fails for others.
- A high-confidence bulk accepted form is later found to be wrong.
- Storage cleanup must not remove files still needed for review evidence.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow authorized users to create OCR import batches containing multiple PDF or image files.
- **FR-002**: System MUST validate each file independently and keep the batch running when individual files fail validation.
- **FR-003**: System MUST show batch and item states including queued, processing, needs review, accepted, rejected, failed, duplicate, and converted.
- **FR-004**: System MUST classify detected forms by likely type, category, language, page count, and confidence.
- **FR-005**: System MUST support bulk acceptance for items above configurable confidence thresholds.
- **FR-006**: System MUST provide item-level review for low-confidence detections, duplicate candidates, and failed pages.
- **FR-007**: System MUST convert accepted items into draft templates with source scan, detection, and reviewer metadata.
- **FR-008**: System MUST preserve import history, decisions, retries, failures, and created template links.
- **FR-009**: System MUST record batch upload, OCR, review, acceptance, rejection, retry, and conversion events in the audit trail.
- **FR-010**: System MUST provide Arabic and English review labels, confidence messages, and error summaries.
- **FR-011**: System MUST require explicit reviewer acceptance before any detected form becomes a draft template, including high-confidence items.
- **FR-012**: System MUST reuse the existing form OCR detection capability for per-item OCR extraction and classification rather than introducing an independent OCR workflow.
- **FR-013**: System MUST support onboarding batches of up to 200 forms in the first implementation.
- **FR-014**: System MUST allow item-level retry for failed, timed-out, or quota-delayed OCR items without re-uploading the whole batch.

### Key Entities

- **OCR Import Batch**: Group of uploaded forms, owner, status, progress, thresholds, and summary counts.
- **OCR Import Item**: Individual file or form candidate with validation, processing, confidence, retry count, failure reason, and review state.
- **Detection Set**: OCR-detected fields, labels, bounding boxes, page references, language hints, and confidence.
- **Review Decision**: User action accepting, rejecting, editing, deferring, merging, or retrying an item or detection.
- **Duplicate Candidate**: Similarity relationship between uploaded items or existing templates.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can upload and start a 200-form batch without manually creating individual import jobs.
- **SC-002**: At least 80% of high-confidence sample forms can be converted to draft templates through bulk accept.
- **SC-003**: A single failed file does not stop processing for the rest of the batch.
- **SC-004**: Reviewers can identify all low-confidence, duplicate, and failed items from one dashboard.
- **SC-005**: Every accepted draft template links back to its source scan, detection set, and review decision.

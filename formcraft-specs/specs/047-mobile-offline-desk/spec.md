# Feature Specification: Mobile and Offline Form Desk

**Feature Branch**: `047-mobile-offline-desk`
**Created**: 2026-05-26
**Status**: Clarified
**Input**: Mobile and offline Form Desk for branch operators.

## Clarifications

### Session 2026-05-26

- Q: Which client-side offline store should hold encrypted drafts and queued submissions? -> A: IndexedDB with WebCrypto envelope encryption.
- Q: What is the default offline policy for downloaded work? -> A: 7-day max offline age, 250 MB per device, wipe on revocation.
- Q: How should sync conflicts be resolved by default? -> A: Block automatic submission and require operator or manager action.
- Q: Which mobile viewports are supported for acceptance testing? -> A: 360px phone and 768px tablet in Arabic RTL and English LTR.
- Q: How should duplicate queued submissions be handled after network retries? -> A: Idempotency keys per queued submission.

## User Scenarios & Testing

### User Story 1 - Use Form Desk on Mobile Devices (Priority: P1)

A branch operator uses Form Desk on a tablet or phone to find, fill, validate, preview, and submit forms with touch-friendly Arabic and English controls.

**Independent Test**: Complete a published template on 360px phone and 768px tablet viewports in Arabic and English without horizontal scrolling or blocked controls.

### User Story 2 - Continue Work During Connectivity Loss (Priority: P2)

An operator saves encrypted offline drafts and queues completed submissions while branch connectivity is unavailable.

**Independent Test**: Go offline, fill a downloaded template, save a draft, reload, and confirm the draft remains available until sync, expiry, deletion, or wipe.

### User Story 3 - Resolve Sync Conflicts and Device Risk (Priority: P3)

A branch manager or operator reviews sync conflicts, stale data warnings, and device revocation events.

**Independent Test**: Modify a template while a device is offline and confirm reconnect shows a clear conflict resolution path.

## Requirements

- **FR-001**: System MUST provide mobile and tablet layouts for Form Desk search, template selection, filling, validation, preview, draft, and submission workflows.
- **FR-002**: System MUST preserve Arabic RTL usability and English LTR usability across supported mobile viewports.
- **FR-003**: Users MUST be able to mark permitted templates, reference data, and customer context for offline availability within organization policy.
- **FR-004**: System MUST store offline drafts and queued submissions in IndexedDB using WebCrypto envelope encryption; plaintext payloads MUST NOT be persisted.
- **FR-005**: System MUST pin offline drafts and queued submissions to the template version used when work began.
- **FR-006**: System MUST sync queued work when connectivity returns and show pending, syncing, submitted, failed, and conflict states.
- **FR-007**: System MUST detect conflicts involving template version, customer profile, reference data, user permission, duplicate submission, and account status.
- **FR-008**: System MUST allow authorized users to revoke devices and define maximum offline age, storage limits, and wipe behavior.
- **FR-009**: System MUST record offline draft creation, queued submission, sync result, conflict resolution, and device revocation events.
- **FR-010**: Sync requests MUST use per-submission idempotency keys so retries after timeouts do not create duplicate submissions.
- **FR-011**: Conflict states MUST block automatic submission until an operator or manager selects an allowed resolution.

## Key Entities

- **Offline Device**: Registered browser or device authorized for offline Form Desk use.
- **Offline Package**: Templates, reference data, customer fields, and policies available offline.
- **Sync Operation**: Queued draft, submission, attachment, or status update waiting to synchronize.
- **Sync Conflict**: Detected mismatch requiring user or admin resolution.
- **Device Policy**: Organization rules for offline age, storage, revocation, and data wipe.
- **Idempotency Key**: Stable unique key generated when a queued submission is created and reused for every retry.

## Success Criteria

- **SC-001**: Operators can complete the top 5 Form Desk workflows on 360px phone and 768px tablet viewports in Arabic RTL and English LTR without horizontal scrolling.
- **SC-002**: Offline drafts survive refresh and reconnect in supported browsers until submitted, deleted, expired, or wiped.
- **SC-003**: 95% of queued submissions without conflicts sync automatically within 2 minutes of restored connectivity.
- **SC-004**: Conflicts identify the blocking cause and next action without raw technical errors.
- **SC-005**: Revoked devices can no longer access offline FormCraft data after policy enforcement.

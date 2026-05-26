# Feature Specification: Digital Signatures

**Feature Branch**: `046-digital-signatures`  
**Created**: 2026-05-26  
**Status**: Draft  
**Input**: User description: "Digital signatures for filled forms and approvals: organizations enable internal and external signer workflows, collect signatures on submissions or template approvals, verify signer identity, preserve signed PDF evidence, and expose signature status in history and audit views."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Request Signatures on a Submission (Priority: P1)

An operator or external user completes a form that requires one or more digital signatures before final acceptance.

**Why this priority**: Digital completion requires legally traceable signer intent, not only a drawn signature image.

**Independent Test**: Can be tested by submitting a form with required signers and confirming each signer receives, completes, or declines a signature request.

**Acceptance Scenarios**:

1. **Given** a filled form requires a customer signature, **When** the operator submits it for signature, **Then** the signer receives a secure request and the submission enters awaiting signature status.
2. **Given** the signer completes identity verification and signs, **When** all required signatures are complete, **Then** the submission is sealed and visible as signed in history.

---

### User Story 2 - Manage Multi-Signer Approval (Priority: P2)

An admin configures ordered or parallel signers for internal approvals, external customers, or authorized signatories.

**Why this priority**: Enterprise forms often require branch staff, managers, customers, and compliance reviewers to sign in a defined order.

**Independent Test**: Can be tested by creating a two-signer workflow and confirming the second signer is invited only when the first completes if ordered signing is configured.

**Acceptance Scenarios**:

1. **Given** ordered signing is enabled, **When** the first signer completes, **Then** the next signer is invited and the timeline updates.
2. **Given** a signer declines, **When** the decline is submitted, **Then** the request stops or routes according to configured policy and records the reason.

---

### User Story 3 - Verify Signed Evidence (Priority: P3)

A compliance user opens a signed document later and verifies signer identity, document integrity, and event history.

**Why this priority**: Signed documents must remain trustworthy during disputes, audits, and reprints.

**Independent Test**: Can be tested by opening a signed submission and confirming the evidence package shows signer events, timestamps, document hash, and verification status.

**Acceptance Scenarios**:

1. **Given** a signed PDF exists, **When** an auditor verifies it, **Then** the system confirms whether the document is unchanged since signing.
2. **Given** a provider callback is received twice, **When** the system processes it, **Then** the signature timeline remains consistent and no duplicate finalization occurs.

### Edge Cases

- A signer signs the wrong template version or a regenerated PDF.
- A signer loses access to their email, phone, or verification method.
- A provider is unavailable after a request is sent.
- A signature expires, is canceled, or is declined.
- Two provider callbacks arrive out of order.
- A signer attempts to sign after the request has expired or been canceled.
- An operator tries to modify a submission that has pending or completed signatures.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow organizations to enable digital signature workflows for selected templates, submissions, approval steps, and signer roles.
- **FR-002**: System MUST distinguish digital signatures from drawn signature elements and require signer identity verification for digital signatures.
  - *Internal signers*: Re-authenticate with their FormCraft password before signing.
  - *External signers*: Verify identity via a one-time email OTP code before signing.
- **FR-003**: System MUST support internal users and external recipients as signers.
- **FR-004**: System MUST support ordered and parallel multi-signer workflows.
  - Maximum 10 signers per signature request.
  - Ordered workflows unlock the next signer only after the previous signer completes.
- **FR-005**: System MUST track signature request states including draft, sent, viewed, verified, signed, declined, expired, canceled, failed, and sealed.
- **FR-006**: System MUST preserve a signed evidence package containing signer identity, timestamps, events, signed document reference, and integrity status.
  - Evidence stored as a JSONB record with SHA-256 document hash, event timeline, and a reference to the signed PDF in Supabase Storage.
- **FR-007**: System MUST prevent signed documents from being silently regenerated or modified without invalidating or superseding the signature evidence.
- **FR-008**: Users MUST be able to resend, cancel, expire, or correct pending signature requests according to permission.
  - Default expiration for signature requests is 7 days from creation.
- **FR-009**: System MUST record all signature lifecycle events in submission history and audit views.
- **FR-010**: System MUST provide Arabic and English signer-facing and admin-facing signature messages.

### Non-Functional Requirements

- **NFR-001**: Signature request creation MUST complete within 5 seconds under normal load.
- **NFR-002**: Evidence data MUST be encrypted at rest using AES-256.
- **NFR-003**: Audit records for signature events MUST be retained for 7 years.
- **NFR-004**: Signature callback and webhook processing MUST be idempotent to prevent duplicate finalization.

### Key Entities

- **Signature Workflow**: Template or approval rule defining signer roles, order, expiration, and completion policy.
- **Signature Request**: Instance requesting one or more signatures for a submission, PDF, or approval.
- **Signature Recipient**: Internal or external signer with identity, delivery, verification, and completion state.
- **Signature Event**: Auditable timeline entry for request, view, verification, sign, decline, resend, cancel, or failure.
- **Signed Evidence Package**: Sealed proof bundle containing the signed document, integrity details, and event summary.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A signer can complete a straightforward digital signature request in under 3 minutes.
- **SC-002**: 100% of finalized signed documents have a verifiable evidence package.
- **SC-003**: Signature status is visible from submission history, approval views, and audit views within 30 seconds.
- **SC-004**: Duplicate or out-of-order signature events do not create duplicate signed documents.
- **SC-005**: Auditors can verify document integrity and signer timeline without contacting engineering support.

## Clarifications

### Session 2026-05-26

- Q: How should signer identity verification be performed for internal and external signers? → A: Internal signers re-authenticate with their FormCraft password; external signers verify via a one-time email OTP code before signing.
- Q: Should digital signatures use an external provider API or an in-house signing mechanism? → A: In-house mechanism using PDF SHA-256 hash, timestamp, and signer metadata stored in PostgreSQL; signed PDF stored in Supabase Storage. No external provider dependency.
- Q: What are the default signature request expiration and maximum signer limits? → A: Default expiration is 7 days from request creation; maximum 10 signers per signature request.
- Q: How should the signed evidence package be structured and stored? → A: Evidence stored as a JSONB record in PostgreSQL containing document SHA-256 hash, signer event timeline, and a reference to the signed PDF file in Supabase Storage.
- Q: What non-functional requirements (performance, encryption, audit retention) apply to digital signatures? → A: Request creation under 5 seconds; evidence encrypted at rest with AES-256; signature audit records retained for 7 years; idempotent webhook processing to prevent duplicates.


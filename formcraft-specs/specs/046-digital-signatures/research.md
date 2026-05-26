# Research: Digital Signatures

## In-House vs External Provider

**Decision**: Implement an in-house digital signing mechanism using SHA-256 document hashing, timestamping, signer metadata, and signed PDF overlay. No external DocuSign/Adobe Sign integration.

**Rationale**: The specification requires legally traceable signer intent and evidence preservation, but the project has no existing third-party signature provider contracts. An in-house solution keeps the service testable, avoids provider downtime risks, and leverages existing WeasyPrint/PDF and Supabase Storage infrastructure.

**Alternatives considered**: External provider integration was rejected because no provider is specified and it would introduce dependency on third-party uptime, pricing, and API versioning. Pure drawn-signature-only approach was rejected because the spec explicitly requires identity verification and evidence packages distinct from canvas signature elements.

## Identity Verification Mechanism

**Decision**: Internal signers re-authenticate with their existing FormCraft password before signing. External signers verify via a one-time email OTP code sent to their registered email address.

**Rationale**: This reuses existing authentication infrastructure (Supabase Auth for internal users, existing email notification service for external OTP) without introducing new identity systems.

**Alternatives considered**: SMS OTP was rejected to avoid introducing a new SMS provider dependency. Government ID verification was rejected as outside MVP scope. Magic link was considered but OTP provides a clearer "I am present and consenting" moment.

## Evidence Storage Format

**Decision**: Store evidence as a structured JSONB record in PostgreSQL containing document SHA-256 hash, event timeline, signer identity snapshots, and a reference to the signed PDF file in Supabase Storage.

**Rationale**: JSONB provides queryable evidence fields for audit views. Supabase Storage handles file durability and access control. The combination satisfies the requirement for verifiable integrity without external blockchain or notary services.

**Alternatives considered**: Flat file evidence packages were rejected for poor queryability. External evidence notary services were rejected for cost and complexity.

## PDF Sealing Approach

**Decision**: When a signature is completed, generate a new sealed PDF using WeasyPrint that appends a signature certificate page containing signer names, timestamps, and document hash. The original filled form PDF is preserved and referenced, and the sealed PDF becomes the primary evidence artifact.

**Rationale**: This creates a human-readable and printable evidence record while keeping the original form intact for reference. WeasyPrint is already the project's PDF renderer.

**Alternatives considered**: Embedding digital certificates into the PDF stream was rejected as overly complex for MVP and would require PDF manipulation libraries not in the project. Only preserving metadata without a visual certificate was rejected because auditors need a human-readable document.

## Token Security Model

**Decision**: Public signer-facing endpoints use opaque, random, time-bound tokens (not JWTs) delivered via invitation links. Tokens are stored hashed in the database and validated on each request.

**Rationale**: Opaque tokens prevent signers from extracting or modifying token payload data. They can be independently revoked without affecting the signer's FormCraft account (external signers have no account).

**Alternatives considered**: JWTs for signers were rejected because external signers have no FormCraft account and JWT would either require fake user records or expose internal claims structure.

## Expiration and Cleanup Strategy

**Decision**: Signature requests expire after 7 days by default (configurable per workflow). Expired requests transition to `expired` state and remain in the database for audit. Admins can configure custom expiration (1–30 days). No automatic deletion of expired requests.

**Rationale**: Legal traceability requires retaining signature request records even after expiration. Automatic deletion would break audit chains.

**Alternatives considered**: Automatic deletion after expiration was rejected for compliance reasons. Fixed 24-hour expiration was rejected because enterprise workflows often need longer review cycles.

## Ordered vs Parallel Workflow Engine

**Decision**: Store signer `order_index` on each recipient. For ordered workflows, the engine advances a `current_signer_index` on the request. The next signer is invited only when `current_signer_index` matches their `order_index` and all previous signers are in `signed` state. Parallel workflows set all signers to `order_index = 0` and invite all simultaneously.

**Rationale**: This is a simple, deterministic rule that maps directly to database fields without needing a complex workflow graph engine.

**Alternatives considered**: A full DAG workflow engine was rejected as over-engineering for the specified scope (max 10 signers, simple sequential or parallel).

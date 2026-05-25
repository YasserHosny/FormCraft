# Research: External Form Portal

## Decision: Public Portal Route Boundary

Use dedicated public FastAPI routes under `/api/public/forms/...`: initial enabled-form discovery is anonymous and rate-limited, while OTP, submit, and PDF actions require opaque portal-session or scoped download tokens. Keep all admin configuration under `/api/admin/portal/...` with existing JWT admin guards.

**Rationale**: Public users do not have FormCraft accounts, so the route layer must not rely on Supabase user JWTs. Opaque portal-session tokens keep post-discovery endpoints authenticated within the portal domain, align with the constitution's API-authentication posture, and make abuse controls explicit.

**Alternatives considered**:
- Reuse `/api/submissions`: rejected because those routes assume authenticated operators and would blur public/publication rules.
- Create temporary Supabase users for public submitters: rejected because the spec explicitly avoids account creation.

## Decision: QR Codes

Generate QR codes on demand from the canonical public URL returned by admin portal configuration; do not persist QR binaries in F034.

**Rationale**: QR content is fully derived from the public URL, so storing it would add unnecessary storage/cache invalidation. On-demand SVG/PNG generation is enough for admin preview and download.

**Alternatives considered**:
- Persist generated QR assets: rejected because public URL changes would require invalidation.
- Require admins to use external QR tooling: rejected because the user story promises public URL or QR access.

## Decision: Template Version Pinning

Create a portal session when a public form is loaded and store the template ID/version used for that session. All validation and submission for the session use that pinned version.

**Rationale**: The clarification requires users to continue with the version loaded at session start. Persisting the pin makes validation, audit, optional PDF, and troubleshooting deterministic.

**Alternatives considered**:
- Always fetch latest template at submit: rejected because it can change fields mid-fill.
- Block submit after template update: rejected by clarification.

## Decision: Validation and Tafqeet Reuse

Reuse existing Form Desk validation, condition engine, and tafqeet services behind a portal orchestration service rather than creating public-only validation logic.

**Rationale**: FR-003 requires parity with internal Form Desk. Reuse reduces divergence and keeps deterministic country validators as the source of truth.

**Alternatives considered**:
- Duplicate validation rules in public frontend only: rejected because backend must remain authoritative.
- Accept public payload first and validate asynchronously: rejected because users need immediate deterministic errors.

## Decision: OTP Storage and Provider Failure

Persist OTP challenges with hashed codes, selected contact mode, hashed contact, attempt count, expiry, lockout timestamp, and provider status. OTP-gated forms fail closed when the provider is unavailable.

**Rationale**: The spec requires SMS/email OTP, 3-attempt lockout, provider outage blocking, and no account creation. Hashing codes/contacts limits exposure if logs or tables are inspected.

**Alternatives considered**:
- Store plaintext OTP codes: rejected for security.
- Continue without OTP during outage: rejected by clarification.
- Force both SMS and email: rejected by clarification.

## Decision: CAPTCHA Adapter

Implement a small CAPTCHA verification adapter supporting hCaptcha or reCAPTCHA through configuration, returning deterministic pass/fail/provider-error results to the portal service.

**Rationale**: The spec allows either hCaptcha or reCAPTCHA. A narrow adapter avoids provider details leaking into route handlers and supports contract tests with mocked verification.

**Alternatives considered**:
- Hardcode one provider: rejected because the spec names two possible providers.
- Build custom CAPTCHA: rejected as out of scope and weaker than established providers.

## Decision: Rate-Limit Keying

Use a composite rate-limit policy: IP hash + browser/session key before OTP verification, then verified contact hash after OTP verification. Store bounded events/counters in PostgreSQL for auditability and deterministic tests.

**Rationale**: The clarification balances shared NAT false positives and abuse control. Postgres storage fits the current stack and avoids introducing Redis for F034.

**Alternatives considered**:
- IP-only rate limits: rejected because shared corporate/public networks can create false positives.
- Admin-configurable keying: rejected as unnecessary complexity for initial scope.
- Redis-only counters: deferred because it adds infrastructure not present in the project.

## Decision: Public Submission Metadata and Audit

Store submitted field values in the existing submission path, and store public-specific metadata in a normalized one-to-one `public_submission_metadata` table. Audit logs receive metadata plus a bounded/redacted field summary, never the full raw payload. Email confirmation status/failure metadata is recorded without rolling back the submission.

**Rationale**: This preserves current submission reporting while satisfying source filtering, verified contact/IP tracking, pinned version, and the clarification about audit-safe summaries.

**Alternatives considered**:
- Add many nullable public columns directly to `submissions`: rejected because it mixes portal-only concerns into the core table.
- Store full payload in audit logs: rejected by clarification and privacy posture.
- Roll back submission when email confirmation fails: rejected because users need stable reference numbers even if delivery infrastructure is temporarily unavailable.

## Decision: Burst Traffic Handling

Handle social/link bursts with cacheable public form configuration responses, server-side rate limits, CAPTCHA for enabled forms, and lightweight portal sessions. Do not add a queue for normal submissions in F034.

**Rationale**: SC-003 requires 100 concurrent submissions, not unbounded campaign-scale ingestion. Rate limiting and CAPTCHA are specified, while queuing submissions would complicate confirmation/reference guarantees.

**Alternatives considered**:
- Queue all public submissions asynchronously: rejected because confirmation/reference number must be immediate.
- Add CDN edge logic in spec: deferred to deployment tuning; backend must still enforce limits.

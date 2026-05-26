# Data Model: Digital Signatures

## Signature Workflow

Represents a template or approval-level configuration defining who must sign, in what order, and under what policy.

- `id`: UUID primary key
- `org_id`: UUID references `organizations.id`
- `template_id`: UUID references `templates.id`, nullable (null means approval workflow)
- `approval_step_id`: UUID references `template_reviews.id`, nullable (null means submission workflow)
- `created_by`: UUID references `profiles.id`
- `name`: text (e.g., "Customer Approval Workflow")
- `is_ordered`: boolean default false
- `expiration_days`: integer default 7, min 1, max 30
- `decline_policy`: enum-like text `stop`, `continue_next`, `route_to_admin`
- `require_all_signers`: boolean default true
- `is_active`: boolean default true
- `created_at`, `updated_at`: timestamps

Validation:

- Exactly one of `template_id` or `approval_step_id` must be non-null.
- Only one active workflow per `template_id` per org.
- Only one active workflow per `approval_step_id` per org.

## Signature Request

Represents an instance requesting signatures for a submission or approval.

- `id`: UUID primary key
- `workflow_id`: UUID references `signature_workflows.id`
- `org_id`: UUID references `organizations.id`
- `submission_id`: UUID references `form_submissions.id`, nullable
- `approval_id`: UUID references `template_reviews.id`, nullable
- `created_by`: UUID references `profiles.id`
- `status`: enum-like text `draft`, `sent`, `in_progress`, `signed`, `declined`, `expired`, `canceled`, `sealed`, `failed`
- `current_signer_index`: integer default 0 (meaningful when workflow is_ordered)
- `expires_at`: timestamp
- `completed_at`: timestamp nullable
- `sealed_pdf_path`: text nullable (Supabase Storage path to sealed PDF)
- `document_hash`: text nullable (SHA-256 of original document)
- `created_at`, `updated_at`: timestamps

Validation:

- Exactly one of `submission_id` or `approval_id` must be non-null.
- `expires_at` must be after `created_at`.
- Status transitions must follow the state machine.

State transitions:

- `draft` -> `sent` (when first invitations are sent)
- `sent` -> `in_progress` (when first signer views or verifies)
- `in_progress` -> `signed` (when all required signers complete)
- `in_progress` -> `declined` (when a signer declines and policy = stop)
- `sent` | `in_progress` -> `expired` (when `expires_at` reached)
- `draft` | `sent` | `in_progress` -> `canceled` (by operator/admin)
- `signed` -> `sealed` (when evidence package is finalized)
- Any -> `failed` (on unrecoverable error)

## Signature Recipient

Represents a signer invited to a signature request.

- `id`: UUID primary key
- `request_id`: UUID references `signature_requests.id`
- `signer_type`: enum-like text `internal`, `external`
- `profile_id`: UUID references `profiles.id`, nullable (required when `signer_type = internal`)
- `email`: text, nullable (required when `signer_type = external`)
- `name`: text
- `phone`: text nullable
- `order_index`: integer default 0
- `status`: enum-like text `pending`, `invited`, `viewed`, `verified`, `signed`, `declined`, `expired`, `canceled`
- `decline_reason`: text nullable
- `signed_at`: timestamp nullable
- `signature_token`: text nullable (hashed opaque token for public signer access)
- `token_expires_at`: timestamp nullable
- `otp_code_hash`: text nullable (for external signer OTP verification)
- `otp_expires_at`: timestamp nullable
- `created_at`, `updated_at`: timestamps

Validation:

- `profile_id` required when `signer_type = internal`; `email` required when `signer_type = external`.
- `signature_token` and `token_expires_at` required after invitation is sent.
- Max 10 recipients per request.
- `order_index` must be unique within a request when workflow is ordered.

State transitions:

- `pending` -> `invited` (when invitation sent)
- `invited` -> `viewed` (when signer opens link)
- `viewed` -> `verified` (after successful identity verification)
- `verified` -> `signed` (after signer completes signature)
- `viewed` | `verified` -> `declined` (signer declines)
- Any non-terminal -> `expired` (when request expires)
- Any non-terminal -> `canceled` (when request is canceled)

## Signature Event

Auditable timeline entry for every significant action in a signature lifecycle.

- `id`: UUID primary key
- `request_id`: UUID references `signature_requests.id`
- `recipient_id`: UUID references `signature_recipients.id`, nullable
- `actor_type`: enum-like text `system`, `operator`, `admin`, `signer`
- `actor_id`: UUID references `profiles.id`, nullable
- `event_type`: enum-like text `created`, `invited`, `viewed`, `verified`, `signed`, `declined`, `resend`, `canceled`, `expired`, `sealed`, `failed`, `hash_verified`
- `event_data`: jsonb default '{}' (contextual payload: IP, user agent, reason, etc.)
- `created_at`: timestamp

Validation:

- `recipient_id` required for signer-specific events (`viewed`, `verified`, `signed`, `declined`).
- `actor_id` nullable for system-generated events.

## Signed Evidence Package

Sealed proof bundle stored after all required signatures are collected.

- `id`: UUID primary key
- `request_id`: UUID references `signature_requests.id`, unique
- `document_hash`: text not null (SHA-256)
- `hash_algorithm`: text default 'sha256'
- `original_pdf_path`: text nullable
- `sealed_pdf_path`: text not null
- `signer_snapshot`: jsonb not null (array of signer identities and completion times)
- `event_summary`: jsonb not null (condensed event timeline)
- `integrity_status`: enum-like text `valid`, `invalid`, `unknown`
- `verified_at`: timestamp nullable
- `created_at`, `updated_at`: timestamps

Validation:

- One evidence package per signature request.
- `integrity_status` is `valid` at creation and updated during verification.

## Relationships

- A `Signature Workflow` has many `Signature Requests`.
- A `Signature Request` has many `Signature Recipients` and many `Signature Events`.
- A `Signature Request` has one `Signed Evidence Package`.
- `Signature Events` link to both a request and optionally a recipient.

## RLS Policies

- `signature_workflows`: SELECT/UPDATE/DELETE restricted to members of the owning `org_id` with Admin or Designer role.
- `signature_requests`: SELECT/UPDATE restricted to members of the owning `org_id` with appropriate roles; internal signers can see requests where they are a recipient.
- `signature_recipients`: External signers can access only their own record via `signature_token` hash match.
- `signature_events`: Readable by org members and by signers for their own requests.
- `signed_evidence_packages`: Readable by org members with Admin, Designer, or Operator role; auditors with Viewer role can read.

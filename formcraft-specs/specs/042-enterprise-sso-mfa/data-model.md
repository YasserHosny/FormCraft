# Data Model: Enterprise SSO and MFA

## Entities

### identity_provider

Stores an organization's SAML or OIDC configuration.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | uuid | PK | |
| org_id | uuid | FK → organizations.id, NOT NULL | |
| name | text | NOT NULL | Human-readable label (e.g., "Corporate Azure AD") |
| provider_type | enum('saml', 'oidc') | NOT NULL | |
| domains | text[] | NOT NULL | Verified email domains routed to this provider |
| metadata_url | text | nullable | OIDC discovery or SAML metadata URL |
| metadata_xml | text | nullable | SAML metadata XML (encrypted at rest) |
| client_id | text | nullable | OIDC client identifier |
| client_secret | text | nullable | OIDC client secret (encrypted at rest) |
| signing_cert | text | nullable | SAML/OIDC signing certificate (encrypted) |
| is_active | boolean | DEFAULT false | |
| last_validated_at | timestamptz | nullable | |
| created_at | timestamptz | DEFAULT now() | |
| updated_at | timestamptz | DEFAULT now() | |
| created_by | uuid | FK → profiles.id | |

**Validation Rules**:
- Exactly one of `metadata_xml` or `metadata_url` must be present for SAML.
- `client_id` and `client_secret` required for OIDC.
- `domains` must be unique across all active providers in the system (case-insensitive).

### auth_policy

Organization-level authentication and session rules.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | uuid | PK | |
| org_id | uuid | FK → organizations.id, NOT NULL, UNIQUE | One policy per org |
| require_mfa_for | jsonb | NOT NULL DEFAULT '{}' | JSON object mapping criteria (roles, departments, branches, platform_admin flag) to bool |
| session_timeout_minutes | int | DEFAULT 480 (8h) | Absolute session lifetime |
| idle_timeout_minutes | int | DEFAULT 30 | Idle timeout |
| max_concurrent_sessions | int | DEFAULT 3 | |
| trusted_ip_ranges | inet[] | nullable | Allowed CIDRs; NULL means allow all |
| fallback_policy | enum('deny', 'strip_access', 'allow_minimal') | DEFAULT 'strip_access' | Behavior when identity groups no longer match |
| created_at | timestamptz | DEFAULT now() | |
| updated_at | timestamptz | DEFAULT now() | |
| created_by | uuid | FK → profiles.id | |

### identity_mapping

JIT provisioning rules linking IdP claims to FormCraft access.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | uuid | PK | |
| org_id | uuid | FK → organizations.id, NOT NULL | |
| provider_id | uuid | FK → identity_provider.id, NOT NULL | |
| claim_type | text | NOT NULL | e.g., "groups", "department", "role" |
| claim_value | text | NOT NULL | Exact or wildcard match |
| assigned_role | text | nullable | FormCraft role slug |
| assigned_department_id | uuid | FK → departments.id, nullable | |
| assigned_branch_id | uuid | FK → branches.id, nullable | |
| default_language | text | DEFAULT 'ar' | |
| priority | int | DEFAULT 0 | Evaluation order; lower = first |
| is_active | boolean | DEFAULT true | |
| created_at | timestamptz | DEFAULT now() | |
| updated_at | timestamptz | DEFAULT now() | |
| created_by | uuid | FK → profiles.id | |

### mfa_enrollment

User MFA method state.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | uuid | PK | |
| user_id | uuid | FK → profiles.id, NOT NULL | |
| method_type | enum('totp', 'sms', 'email') | NOT NULL | WebAuthn deferred |
| secret | text | NOT NULL | Encrypted TOTP secret or OTP seed |
| phone_number | text | nullable | For SMS method |
| is_verified | boolean | DEFAULT false | Must be verified before active |
| is_active | boolean | DEFAULT false | |
| recovery_codes | text[] | nullable | Encrypted one-time recovery codes |
| last_challenged_at | timestamptz | nullable | |
| created_at | timestamptz | DEFAULT now() | |
| updated_at | timestamptz | DEFAULT now() | |

**Validation Rules**:
- Max 2 active enrollments per user.
- At least one method must be verified before `is_active` can be true.

### session_event

Auditable sign-in/session records.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | uuid | PK | |
| user_id | uuid | FK → profiles.id, NOT NULL | |
| event_type | enum('signin', 'signout', 'mfa_enroll', 'mfa_challenge', 'mfa_verify', 'mfa_reset', 'session_revoke', 'timeout', 'policy_change', 'idp_change') | NOT NULL | |
| provider_id | uuid | FK → identity_provider.id, nullable | For SSO events |
| ip_address | inet | nullable | |
| user_agent | text | nullable | |
| result | enum('success', 'failure', 'blocked') | NOT NULL | |
| reason | text | nullable | Human-readable failure or policy reason |
| created_at | timestamptz | DEFAULT now() | |

## Relationships

```text
organizations ||--o{ identity_provider : has
organizations ||--|| auth_policy : owns
organizations ||--o{ identity_mapping : defines
identity_provider ||--o{ identity_mapping : sources
profiles ||--o{ mfa_enrollment : enrolls
profiles ||--o{ session_event : generates
```

## State Transitions

### identity_provider
`draft` → `validated` → `active`
- On creation: `is_active=false`
- After successful metadata validation: `last_validated_at` set; admin can activate.
- On metadata health failure: system marks `is_active=false` and notifies admins.

### mfa_enrollment
`pending` → `verified` → `active`
- Enrollment starts as `is_verified=false`, `is_active=false`.
- After user verifies challenge: `is_verified=true`; admin or user can activate.
- On recovery code use: specific code is consumed; if all codes consumed, require re-enrollment.

## Migrations

1. `CREATE TYPE provider_type AS ENUM ('saml', 'oidc');`
2. `CREATE TYPE fallback_policy AS ENUM ('deny', 'strip_access', 'allow_minimal');`
3. `CREATE TYPE mfa_method_type AS ENUM ('totp', 'sms', 'email');`
4. `CREATE TYPE session_event_type AS ENUM (...);`
5. `CREATE TYPE session_result AS ENUM ('success', 'failure', 'blocked');`
6. Create tables with FKs, indexes on `org_id`, `user_id`, `domains`, `claim_value`, and `event_type`.
7. Add RLS policies:
   - `identity_provider`: org members can read; org admins can write.
   - `auth_policy`: org admins can read/write.
   - `identity_mapping`: org admins can read/write.
   - `mfa_enrollment`: users can read/write own rows; org admins can read own org.
   - `session_event`: org admins can read own org; users can read own rows.

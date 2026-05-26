# SSO / MFA / Auth Policy API Contract

## Base Path
`/api/v1/sso`, `/api/v1/mfa`, `/api/v1/auth-policy`

## Authentication
All endpoints require a valid Supabase JWT Bearer token, except SAML ACS and OIDC callback which are POST/GET from the identity provider.

---

## Identity Provider Endpoints

### POST /api/v1/sso/providers
Create an identity provider configuration.

**Request (Pydantic)**:
```json
{
  "name": "Corporate Azure AD",
  "provider_type": "saml",
  "domains": ["example.com"],
  "metadata_url": "https://login.microsoftonline.com/.../federationmetadata.xml",
  "metadata_xml": null,
  "client_id": null,
  "client_secret": null
}
```

**Response 201**:
```json
{
  "id": "uuid",
  "org_id": "uuid",
  "name": "Corporate Azure AD",
  "provider_type": "saml",
  "domains": ["example.com"],
  "is_active": false,
  "last_validated_at": null,
  "created_at": "2026-05-26T00:00:00Z"
}
```

**Errors**:
- 409: Domain already assigned to an active provider.
- 422: Metadata validation failed.

### GET /api/v1/sso/providers
List providers for the current organization.

**Response 200**:
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Corporate Azure AD",
      "provider_type": "saml",
      "domains": ["example.com"],
      "is_active": true,
      "last_validated_at": "2026-05-26T00:00:00Z"
    }
  ]
}
```

### GET /api/v1/sso/providers/{id}
Get provider details (secrets redacted).

### PATCH /api/v1/sso/providers/{id}
Update provider. Re-validates metadata before allowing activation.

### DELETE /api/v1/sso/providers/{id}
Soft-delete provider; preserves audit history.

---

## SAML/OIDC Sign-In Flows

### GET /api/v1/sso/saml/login?provider_id={id}
Initiate SAML login. Returns redirect URL to IdP.

### POST /api/v1/sso/saml/acs
SAML Assertion Consumer Service. Validates SAMLResponse, provisions user via JIT mapping, issues JWT.

**Request**: `application/x-www-form-urlencoded`
- `SAMLResponse`: Base64-encoded SAML assertion
- `RelayState`: Optional deep-link state

**Response**:
- 302 redirect to frontend with `?token={jwt}` on success.
- 302 redirect to frontend with `?error={code}` on failure.

### GET /api/v1/sso/oidc/login?provider_id={id}
Initiate OIDC login. Returns redirect to authorization endpoint.

### GET /api/v1/sso/oidc/callback
OIDC callback. Validates code + state, exchanges token, provisions user, issues JWT.

**Query Parameters**:
- `code`: Authorization code
- `state`: CSRF state token

**Response**:
- 302 redirect to frontend with `?token={jwt}` on success.
- 302 redirect to frontend with `?error={code}` on failure.

---

## MFA Endpoints

### POST /api/v1/mfa/enroll
Begin MFA enrollment.

**Request**:
```json
{
  "method_type": "totp",
  "phone_number": null
}
```

**Response 201**:
```json
{
  "enrollment_id": "uuid",
  "method_type": "totp",
  "qr_code_uri": "otpauth://totp/...",
  "secret": null
}
```
Note: `secret` is only returned during creation for TOTP; it is not returned on subsequent reads.

### POST /api/v1/mfa/enroll/{id}/verify
Verify enrollment challenge.

**Request**:
```json
{
  "code": "123456"
}
```

**Response 200**:
```json
{
  "is_verified": true,
  "recovery_codes": ["xxxx-xxxx-xxxx", "yyyy-yyyy-yyyy"]
}
```

### POST /api/v1/mfa/challenge
Initiate MFA challenge for the current session.

**Response 200**:
```json
{
  "challenge_id": "uuid",
  "method_type": "totp",
  "expires_at": "2026-05-26T00:05:00Z"
}
```

### POST /api/v1/mfa/challenge/{id}/verify
Verify challenge code.

**Request**:
```json
{
  "code": "123456"
}
```

**Response 200**:
```json
{
  "token": "jwt-with-mfa-verified-claim"
}
```

### POST /api/v1/mfa/recovery
Use a recovery code.

**Request**:
```json
{
  "recovery_code": "xxxx-xxxx-xxxx"
}
```

**Response 200**:
```json
{
  "token": "jwt-with-mfa-verified-claim",
  "remaining_codes": 4
}
```

---

## Auth Policy Endpoints

### GET /api/v1/auth-policy
Get the organization's auth policy.

### PUT /api/v1/auth-policy
Create or update the organization's auth policy.

**Request**:
```json
{
  "require_mfa_for": {
    "roles": ["admin", "reviewer"],
    "platform_admin": true,
    "departments": [],
    "branches": [],
    "all_users": false
  },
  "session_timeout_minutes": 480,
  "idle_timeout_minutes": 30,
  "max_concurrent_sessions": 3,
  "trusted_ip_ranges": ["10.0.0.0/8"],
  "fallback_policy": "strip_access"
}
```

**Response 200**:
```json
{
  "id": "uuid",
  "org_id": "uuid",
  "require_mfa_for": { ... },
  "session_timeout_minutes": 480,
  "idle_timeout_minutes": 30,
  "max_concurrent_sessions": 3,
  "trusted_ip_ranges": ["10.0.0.0/8"],
  "fallback_policy": "strip_access",
  "updated_at": "2026-05-26T00:00:00Z"
}
```

---

## Zod ↔ Pydantic Schema Sync

- Frontend Zod schemas in `formcraft-frontend/src/app/core/contracts/sso.ts`, `mfa.ts`, `auth-policy.ts` must mirror backend Pydantic models.
- Contract tests in `formcraft-backend/tests/contract/` verify response shapes.

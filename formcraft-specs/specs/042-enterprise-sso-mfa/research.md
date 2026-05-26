# Research: Enterprise SSO and MFA

## Decisions

### SAML Library
- **Decision**: `python-saml` (OneLogin) for SAML 2.0 SP flows.
- **Rationale**: Mature, widely adopted, supports metadata parsing, assertion validation, and Arabic-friendly attribute handling. Compatible with Python 3.12.
- **Alternatives considered**: `pysaml2` (more complex API, heavier dependency tree); external SAML proxy (adds infrastructure complexity, violates simplicity principle).

### OIDC Library
- **Decision**: `authlib` for OIDC RP flows.
- **Rationale**: Lightweight, supports discovery, ID token validation, and easy FastAPI integration.
- **Alternatives considered**: `oic` (less maintained); external proxy (same complexity concern as SAML).

### TOTP Library
- **Decision**: `pyotp` for RFC 6238 TOTP generation and verification.
- **Rationale**: Standard, simple, well-tested.
- **Alternatives considered**: Custom implementation (rejected — unnecessary risk); WebAuthn (deferred per clarification).

### Encryption
- **Decision**: AES-256-GCM via `cryptography` library for IdP secrets.
- **Rationale**: Industry standard, Python-native, authenticated encryption prevents tampering.
- **Alternatives considered**: `pynacl` (libsodium) — excellent but introduces an extra native dependency; AES-256-CBC (rejected — lacks authentication).

### Session Store
- **Decision**: Extend existing PostgreSQL session tracking; no Redis added.
- **Rationale**: Feature scope targets <100 concurrent sessions per org; PostgreSQL is sufficient. Keeps stack simple and preserves existing backup/DR patterns.
- **Alternatives considered**: Redis (rejected — adds infrastructure for marginal gain at this scale).

### JIT Provisioning
- **Decision**: Claim-to-role mapping evaluated at login time against PostgreSQL mapping table.
- **Rationale**: Simple, deterministic, auditable.
- **Alternatives considered**: SCIM provisioning (rejected — overkill for current scale; can be added later).

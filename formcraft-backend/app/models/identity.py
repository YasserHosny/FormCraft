"""Identity, SSO, and MFA models."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class ProviderType(str, Enum):
    SAML = "saml"
    OIDC = "oidc"


class FallbackPolicy(str, Enum):
    DENY = "deny"
    STRIP_ACCESS = "strip_access"
    ALLOW_MINIMAL = "allow_minimal"


class MfaMethodType(str, Enum):
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"


class SessionEventType(str, Enum):
    SIGNIN = "signin"
    SIGNOUT = "signout"
    MFA_ENROLL = "mfa_enroll"
    MFA_CHALLENGE = "mfa_challenge"
    MFA_VERIFY = "mfa_verify"
    MFA_RESET = "mfa_reset"
    SESSION_REVOKE = "session_revoke"
    TIMEOUT = "timeout"
    POLICY_CHANGE = "policy_change"
    IDP_CHANGE = "idp_change"


class SessionResult(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    BLOCKED = "blocked"


class IdentityProvider(BaseModel):
    id: UUID
    org_id: UUID
    name: str
    provider_type: ProviderType
    domains: list[str] = Field(default_factory=list)
    metadata_url: str | None = None
    metadata_xml: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    signing_cert: str | None = None
    is_active: bool = False
    last_validated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None = None


class AuthPolicy(BaseModel):
    id: UUID
    org_id: UUID
    require_mfa_for: dict = Field(default_factory=dict)
    session_timeout_minutes: int = 480
    idle_timeout_minutes: int = 30
    max_concurrent_sessions: int = 3
    trusted_ip_ranges: list[str] | None = None
    fallback_policy: FallbackPolicy = FallbackPolicy.STRIP_ACCESS
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None = None


class IdentityMapping(BaseModel):
    id: UUID
    org_id: UUID
    provider_id: UUID
    claim_type: str
    claim_value: str
    assigned_role: str | None = None
    assigned_department_id: UUID | None = None
    assigned_branch_id: UUID | None = None
    default_language: str = "ar"
    priority: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None = None


class MfaEnrollment(BaseModel):
    id: UUID
    user_id: UUID
    method_type: MfaMethodType
    secret: str
    phone_number: str | None = None
    is_verified: bool = False
    is_active: bool = False
    recovery_codes: list[str] | None = None
    last_challenged_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class SessionEvent(BaseModel):
    id: UUID
    user_id: UUID
    event_type: SessionEventType
    provider_id: UUID | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    result: SessionResult
    reason: str | None = None
    created_at: datetime

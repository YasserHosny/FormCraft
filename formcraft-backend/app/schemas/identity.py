"""Schemas for SSO, MFA, and auth policy endpoints."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.identity import FallbackPolicy, MfaMethodType, ProviderType


# ------------------------------------------------------------------
# Identity Provider
# ------------------------------------------------------------------


class IdentityProviderCreate(BaseModel):
    name: str
    provider_type: ProviderType
    domains: list[str] = Field(default_factory=list)
    metadata_url: str | None = None
    metadata_xml: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    signing_cert: str | None = None


class IdentityProviderUpdate(BaseModel):
    name: str | None = None
    domains: list[str] | None = None
    metadata_url: str | None = None
    metadata_xml: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    signing_cert: str | None = None
    is_active: bool | None = None


class IdentityProviderResponse(BaseModel):
    id: UUID
    org_id: UUID
    name: str
    provider_type: ProviderType
    domains: list[str]
    is_active: bool
    last_validated_at: datetime | None = None
    created_at: datetime


# ------------------------------------------------------------------
# Auth Policy
# ------------------------------------------------------------------


class AuthPolicyCreateUpdate(BaseModel):
    require_mfa_for: dict = Field(default_factory=dict)
    session_timeout_minutes: int = 480
    idle_timeout_minutes: int = 30
    max_concurrent_sessions: int = 3
    trusted_ip_ranges: list[str] | None = None
    fallback_policy: FallbackPolicy = FallbackPolicy.STRIP_ACCESS


class AuthPolicyResponse(BaseModel):
    id: UUID
    org_id: UUID
    require_mfa_for: dict
    session_timeout_minutes: int
    idle_timeout_minutes: int
    max_concurrent_sessions: int
    trusted_ip_ranges: list[str] | None = None
    fallback_policy: FallbackPolicy
    updated_at: datetime


# ------------------------------------------------------------------
# Identity Mapping
# ------------------------------------------------------------------


class IdentityMappingCreate(BaseModel):
    provider_id: UUID
    claim_type: str
    claim_value: str
    assigned_role: str | None = None
    assigned_department_id: UUID | None = None
    assigned_branch_id: UUID | None = None
    default_language: str = "ar"
    priority: int = 0


class IdentityMappingUpdate(BaseModel):
    claim_type: str | None = None
    claim_value: str | None = None
    assigned_role: str | None = None
    assigned_department_id: UUID | None = None
    assigned_branch_id: UUID | None = None
    default_language: str | None = None
    priority: int | None = None
    is_active: bool | None = None


class IdentityMappingResponse(BaseModel):
    id: UUID
    org_id: UUID
    provider_id: UUID
    claim_type: str
    claim_value: str
    assigned_role: str | None = None
    assigned_department_id: UUID | None = None
    assigned_branch_id: UUID | None = None
    default_language: str
    priority: int
    is_active: bool


# ------------------------------------------------------------------
# MFA
# ------------------------------------------------------------------


class MfaEnrollRequest(BaseModel):
    method_type: MfaMethodType
    phone_number: str | None = None


class MfaEnrollResponse(BaseModel):
    enrollment_id: UUID
    method_type: MfaMethodType
    qr_code_uri: str | None = None


class MfaVerifyRequest(BaseModel):
    code: str


class MfaVerifyResponse(BaseModel):
    is_verified: bool
    recovery_codes: list[str] | None = None


class MfaChallengeResponse(BaseModel):
    challenge_id: UUID
    method_type: MfaMethodType
    expires_at: datetime


class MfaChallengeVerifyResponse(BaseModel):
    token: str


class MfaRecoveryRequest(BaseModel):
    recovery_code: str


class MfaRecoveryResponse(BaseModel):
    token: str
    remaining_codes: int


# ------------------------------------------------------------------
# Session
# ------------------------------------------------------------------


class SessionEventCreate(BaseModel):
    user_id: UUID
    event_type: str
    provider_id: UUID | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    result: str
    reason: str | None = None

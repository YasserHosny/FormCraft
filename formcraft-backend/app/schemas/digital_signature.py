from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


DeclinePolicy = Literal["stop", "continue_next", "route_to_admin"]
RequestStatus = Literal["draft", "sent", "in_progress", "signed", "declined", "expired", "canceled", "sealed", "failed"]
RecipientStatus = Literal["pending", "invited", "viewed", "verified", "signed", "declined", "expired", "canceled"]
SignerType = Literal["internal", "external"]
ActorType = Literal["system", "operator", "admin", "signer"]
EventType = Literal["created", "invited", "viewed", "verified", "signed", "declined", "resend", "canceled", "expired", "sealed", "failed", "hash_verified"]
IntegrityStatus = Literal["valid", "invalid", "unknown"]


# ============================================================
# Workflow Schemas
# ============================================================

class SignatureWorkflowBase(BaseModel):
    name: str
    is_ordered: bool = False
    expiration_days: int = Field(default=7, ge=1, le=30)
    decline_policy: DeclinePolicy = "stop"
    require_all_signers: bool = True
    is_active: bool = True


class SignatureWorkflowCreate(SignatureWorkflowBase):
    template_id: UUID | None = None
    approval_step_id: UUID | None = None

    @model_validator(mode="after")
    def validate_target(self):
        if self.template_id is None and self.approval_step_id is None:
            raise ValueError("Either template_id or approval_step_id is required")
        if self.template_id is not None and self.approval_step_id is not None:
            raise ValueError("Only one of template_id or approval_step_id should be provided")
        return self


class SignatureWorkflowUpdate(BaseModel):
    name: str | None = None
    expiration_days: int | None = Field(default=None, ge=1, le=30)
    decline_policy: DeclinePolicy | None = None
    is_active: bool | None = None


class SignatureWorkflowResponse(SignatureWorkflowBase):
    id: UUID
    org_id: UUID
    template_id: UUID | None = None
    approval_step_id: UUID | None = None
    created_by: UUID
    created_at: str | None = None
    updated_at: str | None = None


class SignatureWorkflowListResponse(BaseModel):
    items: list[SignatureWorkflowResponse]
    total: int
    page: int
    page_size: int


# ============================================================
# Recipient Schemas
# ============================================================

class SignerInput(BaseModel):
    signer_type: SignerType
    profile_id: UUID | None = None
    email: str | None = None
    name: str
    phone: str | None = None
    order_index: int = 0

    @model_validator(mode="after")
    def validate_signer(self):
        if self.signer_type == "internal" and self.profile_id is None:
            raise ValueError("profile_id is required for internal signers")
        if self.signer_type == "external" and not self.email:
            raise ValueError("email is required for external signers")
        return self


class SignatureRecipientResponse(BaseModel):
    id: UUID
    request_id: UUID
    signer_type: SignerType
    profile_id: UUID | None = None
    email: str | None = None
    name: str
    phone: str | None = None
    order_index: int
    status: RecipientStatus
    decline_reason: str | None = None
    signed_at: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


# ============================================================
# Request Schemas
# ============================================================

class SignatureRequestCreate(BaseModel):
    workflow_id: UUID
    submission_id: UUID | None = None
    approval_id: UUID | None = None
    signers: list[SignerInput] = Field(default_factory=list, max_length=10)

    @model_validator(mode="after")
    def validate_target(self):
        if self.submission_id is None and self.approval_id is None:
            raise ValueError("Either submission_id or approval_id is required")
        if self.submission_id is not None and self.approval_id is not None:
            raise ValueError("Only one of submission_id or approval_id should be provided")
        return self


class SignatureRequestResponse(BaseModel):
    id: UUID
    workflow_id: UUID
    org_id: UUID
    submission_id: UUID | None = None
    approval_id: UUID | None = None
    created_by: UUID
    status: RequestStatus
    current_signer_index: int
    expires_at: str
    completed_at: str | None = None
    sealed_pdf_path: str | None = None
    document_hash: str | None = None
    recipients: list[SignatureRecipientResponse] = Field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None


class SignatureRequestListResponse(BaseModel):
    items: list[SignatureRequestResponse]
    total: int
    page: int
    page_size: int


class SignatureRequestCancel(BaseModel):
    reason: str | None = None


class SignatureSignPayload(BaseModel):
    consent: bool
    ip_address: str | None = None
    user_agent: str | None = None


class SignatureDeclinePayload(BaseModel):
    reason: str | None = None


# ============================================================
# Event Schemas
# ============================================================

class SignatureEventResponse(BaseModel):
    id: UUID
    request_id: UUID
    recipient_id: UUID | None = None
    actor_type: ActorType
    actor_id: UUID | None = None
    event_type: EventType
    event_data: dict = Field(default_factory=dict)
    created_at: str | None = None


# ============================================================
# Evidence Schemas
# ============================================================

class SignedEvidenceResponse(BaseModel):
    id: UUID
    request_id: UUID
    document_hash: str
    hash_algorithm: str
    original_pdf_path: str | None = None
    sealed_pdf_path: str
    signer_snapshot: list[dict] = Field(default_factory=list)
    event_summary: list[dict] = Field(default_factory=list)
    integrity_status: IntegrityStatus
    verified_at: str | None = None
    created_at: str | None = None


class EvidenceVerifyResponse(BaseModel):
    integrity_status: IntegrityStatus
    verified_at: str
    message: str


# ============================================================
# Public Signer Portal Schemas
# ============================================================

class SignerPortalMetadata(BaseModel):
    request_id: UUID
    template_name: str
    organization_name: str
    signer_name: str
    status: RecipientStatus
    requires_otp: bool
    document_url: str | None = None
    expires_at: str


class OtpVerifyRequest(BaseModel):
    otp: str = Field(..., min_length=4, max_length=10)


class SignerAuthenticateRequest(BaseModel):
    password: str


class OtpSendResponse(BaseModel):
    message: str = "OTP sent"


class OtpVerifyResponse(BaseModel):
    verified: bool = True


class SignerAuthenticateResponse(BaseModel):
    authenticated: bool = True


class SignCompleteResponse(BaseModel):
    signed: bool = True
    request_status: RequestStatus

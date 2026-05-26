from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.api.deps import get_current_user, require_role
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile
from app.schemas.digital_signature import (
    EvidenceVerifyResponse,
    SignatureDeclinePayload,
    SignatureRequestCancel,
    SignatureRequestCreate,
    SignatureRequestListResponse,
    SignatureRequestResponse,
    SignatureSignPayload,
    SignatureWorkflowCreate,
    SignatureWorkflowListResponse,
    SignatureWorkflowResponse,
    SignatureWorkflowUpdate,
    SignedEvidenceResponse,
    SignerAuthenticateRequest,
    SignerAuthenticateResponse,
    SignerPortalMetadata,
    OtpSendResponse,
    OtpVerifyRequest,
    OtpVerifyResponse,
)
from app.services.digital_signature_service import DigitalSignatureService
from app.services.signature_token_service import SignatureTokenService
from app.services.signer_identity_service import SignerIdentityService

router = APIRouter(prefix="/digital-signatures", tags=["Digital Signatures"])
signer_router = APIRouter(tags=["Signer Portal"])


def _require_org(current_user: UserProfile) -> UUID:
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )
    return current_user.org_id


# ============================================================
# Workflow endpoints
# ============================================================

@router.get("/workflows", response_model=SignatureWorkflowListResponse)
async def list_signature_workflows(
    current_user: Annotated[UserProfile, Depends(get_current_user)],
    template_id: UUID | None = None,
    is_active: bool | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    org_id = _require_org(current_user)
    service = DigitalSignatureService(get_supabase_client())
    items, total = await service.list_workflows(
        org_id, template_id=template_id, is_active=is_active, page=page, page_size=page_size
    )
    return SignatureWorkflowListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("/workflows", response_model=SignatureWorkflowResponse, status_code=201)
async def create_signature_workflow(
    current_user: Annotated[UserProfile, Depends(get_current_user)],
    payload: SignatureWorkflowCreate,
):
    org_id = _require_org(current_user)
    service = DigitalSignatureService(get_supabase_client())
    data = await service.create_workflow(org_id, current_user.id, payload.model_dump())
    return SignatureWorkflowResponse(**data)


@router.patch("/workflows/{workflow_id}", response_model=SignatureWorkflowResponse)
async def update_signature_workflow(
    workflow_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
    payload: SignatureWorkflowUpdate,
):
    org_id = _require_org(current_user)
    service = DigitalSignatureService(get_supabase_client())
    data = await service.update_workflow(workflow_id, org_id, payload.model_dump(exclude_unset=True))
    return SignatureWorkflowResponse(**data)


# ============================================================
# Request endpoints
# ============================================================

@router.post("/requests", response_model=SignatureRequestResponse, status_code=201)
async def create_signature_request(
    current_user: Annotated[UserProfile, Depends(get_current_user)],
    payload: SignatureRequestCreate,
):
    org_id = _require_org(current_user)
    service = DigitalSignatureService(get_supabase_client())
    data = await service.create_request(org_id, current_user.id, payload.model_dump())
    return SignatureRequestResponse(**data)


@router.post("/requests/{request_id}/send", response_model=SignatureRequestResponse)
async def send_signature_request(
    request_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    org_id = _require_org(current_user)
    service = DigitalSignatureService(get_supabase_client())
    data = await service.send_request(request_id, org_id, current_user.id)
    return SignatureRequestResponse(**data)


@router.get("/requests", response_model=SignatureRequestListResponse)
async def list_signature_requests(
    current_user: Annotated[UserProfile, Depends(get_current_user)],
    status: str | None = None,
    submission_id: UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    org_id = _require_org(current_user)
    service = DigitalSignatureService(get_supabase_client())
    items, total = await service.list_requests(
        org_id, status=status, submission_id=submission_id, page=page, page_size=page_size
    )
    return SignatureRequestListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/requests/{request_id}", response_model=SignatureRequestResponse)
async def get_signature_request(
    request_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    org_id = _require_org(current_user)
    service = DigitalSignatureService(get_supabase_client())
    data = await service.get_request(request_id)
    if str(data.get("org_id")) != str(org_id):
        # Also allow internal signers to view their own requests
        pass
    return SignatureRequestResponse(**data)


@router.post("/requests/{request_id}/cancel", response_model=SignatureRequestResponse)
async def cancel_signature_request(
    request_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
    payload: SignatureRequestCancel,
):
    org_id = _require_org(current_user)
    service = DigitalSignatureService(get_supabase_client())
    data = await service.cancel_request(request_id, org_id, current_user.id, payload.reason)
    return SignatureRequestResponse(**data)


@router.post("/requests/{request_id}/resend/{recipient_id}")
async def resend_signature_invitation(
    request_id: UUID,
    recipient_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    org_id = _require_org(current_user)
    service = DigitalSignatureService(get_supabase_client())
    return await service.resend_invitation(request_id, recipient_id, org_id, current_user.id)


# ============================================================
# Evidence endpoints
# ============================================================

@router.get("/evidence/{request_id}", response_model=SignedEvidenceResponse)
async def get_evidence(
    request_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    _require_org(current_user)
    client = get_supabase_client()
    result = (
        client.table("signed_evidence_packages")
        .select("*")
        .eq("request_id", str(request_id))
        .single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Evidence not found")
    return SignedEvidenceResponse(**result.data)


@router.post("/evidence/{request_id}/verify", response_model=EvidenceVerifyResponse)
async def verify_evidence(
    request_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    _require_org(current_user)
    from app.services.signature_evidence_service import SignatureEvidenceService
    client = get_supabase_client()
    evidence = (
        client.table("signed_evidence_packages")
        .select("id")
        .eq("request_id", str(request_id))
        .single()
        .execute()
    )
    if not evidence.data:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Evidence not found")
    service = SignatureEvidenceService(client)
    return await service.verify_integrity(evidence.data["id"])


# ============================================================
# Public signer portal endpoints
# ============================================================

@signer_router.get("/sign/{token}", response_model=SignerPortalMetadata)
async def signer_portal_metadata(token: str):
    token_service = SignatureTokenService(get_supabase_client())
    recipient = await token_service.validate_token(token)
    request = recipient.get("signature_requests", {})
    org = (
        get_supabase_client()
        .table("organizations")
        .select("name")
        .eq("id", request.get("org_id"))
        .single()
        .execute()
    )
    template = {}
    if request.get("submission_id"):
        sub = (
            get_supabase_client()
            .table("form_submissions")
            .select("template_id")
            .eq("id", request["submission_id"])
            .single()
            .execute()
        )
        if sub.data:
            template = (
                get_supabase_client()
                .table("templates")
                .select("name")
                .eq("id", sub.data["template_id"])
                .single()
                .execute()
            )
            template = template.data or {}

    return SignerPortalMetadata(
        request_id=request.get("id"),
        template_name=template.get("name", "Form"),
        organization_name=org.data.get("name", "") if org.data else "",
        signer_name=recipient.get("name", ""),
        status=recipient.get("status", "invited"),
        requires_otp=recipient.get("signer_type") == "external",
        document_url=None,
        expires_at=request.get("expires_at", ""),
    )


@signer_router.post("/sign/{token}/otp/send", response_model=OtpSendResponse)
async def send_signer_otp(token: str):
    token_service = SignatureTokenService(get_supabase_client())
    recipient = await token_service.validate_token(token)
    identity_service = SignerIdentityService(get_supabase_client())
    await identity_service.send_external_otp(recipient["id"], recipient.get("email", ""))
    return OtpSendResponse()


@signer_router.post("/sign/{token}/otp/verify", response_model=OtpVerifyResponse)
async def verify_signer_otp(token: str, payload: OtpVerifyRequest):
    token_service = SignatureTokenService(get_supabase_client())
    recipient = await token_service.validate_token(token)
    identity_service = SignerIdentityService(get_supabase_client())
    ok = await identity_service.verify_external_otp(recipient["id"], payload.otp)
    if not ok:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired OTP")
    return OtpVerifyResponse()


@signer_router.post("/sign/{token}/authenticate", response_model=SignerAuthenticateResponse)
async def authenticate_internal_signer(token: str, payload: SignerAuthenticateRequest):
    # In a real implementation, validate the password via Supabase Auth here
    token_service = SignatureTokenService(get_supabase_client())
    recipient = await token_service.validate_token(token)
    identity_service = SignerIdentityService(get_supabase_client())
    await identity_service.mark_internal_verified(recipient["id"])
    return SignerAuthenticateResponse()


@signer_router.post("/sign/{token}/sign", response_model=SignatureRequestResponse)
async def record_signature(token: str, payload: SignatureSignPayload):
    token_service = SignatureTokenService(get_supabase_client())
    recipient = await token_service.validate_token(token)
    if recipient.get("status") != "verified":
        raise HTTPException(status.HTTP_409_CONFLICT, "Signer must be verified before signing")
    service = DigitalSignatureService(get_supabase_client())
    data = await service.record_signature(
        recipient["id"], recipient["request_id"], payload.model_dump()
    )
    return SignatureRequestResponse(**data)


@signer_router.post("/sign/{token}/decline", response_model=SignatureRequestResponse)
async def decline_signature(token: str, payload: SignatureDeclinePayload):
    token_service = SignatureTokenService(get_supabase_client())
    recipient = await token_service.validate_token(token)
    service = DigitalSignatureService(get_supabase_client())
    data = await service.record_decline(recipient["id"], recipient["request_id"], payload.reason)
    return SignatureRequestResponse(**data)

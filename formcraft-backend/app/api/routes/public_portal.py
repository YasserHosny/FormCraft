"""Public portal routes for anonymous form discovery and portal-session actions."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status

from app.core.supabase import get_supabase_client
from app.schemas.portal import (
    OtpSendRequest,
    OtpSendResponse,
    OtpVerifyRequest,
    OtpVerifyResponse,
    PublicFormSession,
    PublicSubmissionRequest,
    PublicSubmissionResponse,
)
from app.services.captcha_service import CaptchaService
from app.services.portal_otp_service import PortalOtpService
from app.services.portal_rate_limit_service import PortalRateLimitService
from app.services.portal_service import PortalService

router = APIRouter(tags=["Public Portal"])


def _get_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.get("/public/forms/{org_slug}/{public_slug}", response_model=PublicFormSession)
async def load_public_form(
    org_slug: str,
    public_slug: str,
    request: Request,
):
    """Load a public form and create a pinned portal session."""
    client = get_supabase_client()
    service = PortalService(client)

    config = await service.get_portal_config_by_slug(org_slug, public_slug)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public form not found or disabled",
        )

    # Rate limit: load events are limited by pre-OTP key
    rate_service = PortalRateLimitService(client)
    ip_address = _get_ip(request)
    ip_hash = service.hash_ip(ip_address)
    # Use a simple browser key from headers if provided; otherwise IP only
    browser_key = request.headers.get("x-browser-key")
    pre_otp_key = rate_service.derive_pre_otp_key(
        ip_hash, service.hash_browser_key(browser_key) if browser_key else None
    )

    # We need org_id and portal_configuration_id for rate limiting
    # Resolve config row
    config_row_resp = (
        client.table("portal_configurations")
        .select("id, org_id")
        .eq("template_id", str(config.template_id))
        .limit(1)
        .execute()
    )
    config_rows = config_row_resp.data or []
    if not config_rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found",
        )
    org_id = UUID(config_rows[0]["org_id"])
    portal_configuration_id = UUID(config_rows[0]["id"])

    allowed = await rate_service.check_and_record(
        org_id=org_id,
        portal_configuration_id=portal_configuration_id,
        portal_session_id=None,
        key_type="pre_otp",
        key_hash=pre_otp_key,
        event_type="load",
        max_requests=config.rate_limit_max,
        window_minutes=config.rate_limit_window_minutes,
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )

    # Fetch template details for session creation
    template_resp = (
        client.table("templates")
        .select("id, name, version, status, country, language_default, pages(id, elements(*))")
        .eq("id", str(config.template_id))
        .limit(1)
        .execute()
    )
    templates = template_resp.data or []
    if not templates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    template = templates[0]
    if template.get("status") != "published":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not published",
        )

    token, session_id = await service.create_portal_session(
        config=config,
        template=template,
        ip_address=ip_address,
        browser_fingerprint=browser_key,
    )

    result = service._session_to_public_form(
        {
            "portal_configurations": {
                **config.model_dump(),
                "templates": template,
            },
            "template_version": template.get("version", 1),
        }
    )
    result.session_token = token
    return result


@router.post("/public/forms/{session_token}/otp/send", response_model=OtpSendResponse)
async def send_otp(
    session_token: str,
    body: OtpSendRequest,
):
    """Send OTP for an OTP-gated public form session."""
    client = get_supabase_client()
    service = PortalService(client)
    otp_service = PortalOtpService(client)

    session = await service.get_session_by_token(session_token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
        )

    config = session.get("portal_configurations", {})
    allowed_modes = config.get("allowed_otp_modes", [])

    result = await otp_service.send_otp(
        session_id=UUID(session["id"]),
        contact_mode=body.contact_mode,
        contact_value=body.contact_value,
        allowed_modes=allowed_modes,
    )
    return OtpSendResponse(**result)


@router.post("/public/forms/{session_token}/otp/verify", response_model=OtpVerifyResponse)
async def verify_otp(
    session_token: str,
    body: OtpVerifyRequest,
):
    """Verify OTP and unlock the public form session."""
    client = get_supabase_client()
    service = PortalService(client)
    otp_service = PortalOtpService(client)

    session = await service.get_session_by_token(session_token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
        )

    result = await otp_service.verify_otp(
        session_id=UUID(session["id"]),
        code=body.code,
    )
    return OtpVerifyResponse(**result)


@router.post("/public/forms/{session_token}/submit", response_model=PublicSubmissionResponse)
async def submit_public_form(
    session_token: str,
    body: PublicSubmissionRequest,
    request: Request,
):
    """Submit a public form session."""
    client = get_supabase_client()
    service = PortalService(client)
    rate_service = PortalRateLimitService(client)

    session = await service.get_session_by_token(session_token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
        )

    config = session.get("portal_configurations", {})
    org_id = UUID(session["org_id"])
    portal_configuration_id = UUID(session["portal_configuration_id"])
    portal_session_id = UUID(session["id"])

    # OTP gate enforcement
    if config.get("verification_required", False) and session["status"] != "otp_verified":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="OTP verification required",
        )

    # CAPTCHA verification
    if config.get("captcha_enabled", False):
        captcha_service = CaptchaService(
            provider=config.get("captcha_provider"),
            secret_key=None,  # loaded from environment in production
        )
        ok, msg = await captcha_service.verify(body.captcha_token)
        if not ok:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=msg or "CAPTCHA verification failed",
            )

    # Rate limiting
    ip_address = _get_ip(request)
    ip_hash = service.hash_ip(ip_address)
    browser_key = request.headers.get("x-browser-key")

    if session.get("verified_contact_hash"):
        rate_key = rate_service.derive_verified_key(session["verified_contact_hash"])
        key_type = "verified_contact"
    else:
        rate_key = rate_service.derive_pre_otp_key(
            ip_hash, service.hash_browser_key(browser_key) if browser_key else None
        )
        key_type = "pre_otp"

    allowed = await rate_service.check_and_record(
        org_id=org_id,
        portal_configuration_id=portal_configuration_id,
        portal_session_id=portal_session_id,
        key_type=key_type,
        key_hash=rate_key,
        event_type="submit",
        max_requests=config.get("rate_limit_max", 10),
        window_minutes=config.get("rate_limit_window_minutes", 60),
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )

    result = await service.submit_public_form(
        session=session,
        request=body,
        ip_address=ip_address,
    )

    # Mark CAPTCHA as verified in metadata if it was checked
    if config.get("captcha_enabled", False):
        client.table("public_submission_metadata").update(
            {"captcha_verified": True}
        ).eq("portal_session_id", str(portal_session_id)).execute()

    return result


@router.get("/public/submissions/{reference_number}/pdf")
async def download_public_pdf(
    reference_number: str,
    token: str,
):
    """Download optional public submission PDF."""
    client = get_supabase_client()
    service = PortalService(client)
    token_hash = service.hash_token(token)

    # Lookup metadata by reference number and token hash
    meta_resp = (
        client.table("public_submission_metadata")
        .select("*, portal_configurations!inner(allow_pdf_download)")
        .eq("pdf_download_token_hash", token_hash)
        .limit(1)
        .execute()
    )
    rows = meta_resp.data or []
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired download token",
        )

    meta = rows[0]
    portal_config = meta.get("portal_configurations", {})
    if not portal_config.get("allow_pdf_download", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="PDF download disabled",
        )

    # Check token expiry
    expires = meta.get("pdf_download_expires_at")
    if expires and expires < datetime.now(timezone.utc).isoformat():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Download token expired",
        )

    # Reuse existing PDF renderer for pinned template version

    submission_id = meta["submission_id"]
    submission_resp = (
        client.table("submissions")
        .select("*, templates!inner(id, name, version)")
        .eq("id", str(submission_id))
        .limit(1)
        .execute()
    )
    sub_rows = submission_resp.data or []
    if not sub_rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )

    # TODO: Implement PDF streaming using existing renderer with pinned version
    # For now return placeholder response to satisfy route contract
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="PDF streaming to be wired to existing renderer",
    )

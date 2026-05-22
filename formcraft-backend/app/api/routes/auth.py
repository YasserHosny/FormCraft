"""Authentication routes (T030-T033) — enhanced for multi-tenancy."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.deps import get_current_user, require_role
from app.core.audit import AuditLogger
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile
from pydantic import BaseModel

from app.schemas.auth import LoginRequest, LoginResponse, RefreshRequest, RegisterRequest
from app.services.organization_service import OrganizationService
from app.services.user_service import UserService


class SelectOrgRequest(BaseModel):
    org_id: str

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


# ------------------------------------------------------------------
# LOGIN
# ------------------------------------------------------------------


@router.post("/login")
async def login(body: LoginRequest, request: Request):
    """Authenticate user via Supabase Auth and return JWT tokens.

    If the user belongs to multiple organisations, the response includes
    ``requires_org_select: true`` and an ``orgs`` list so the frontend
    can prompt for organisation selection before proceeding.
    """
    client_ip = request.client.host if request.client else None
    logger.info("login_attempt", extra={"email": body.email, "ip_address": client_ip})
    client = get_supabase_client()
    audit = AuditLogger(client)

    try:
        response = client.auth.sign_in_with_password(
            {"email": body.email, "password": body.password}
        )
    except Exception:
        logger.warning(
            "login_failed",
            extra={"email": body.email, "ip_address": client_ip},
        )
        await audit.log_event(
            user_id="00000000-0000-0000-0000-000000000000",
            action="auth_login_failed",
            resource_type="auth",
            metadata={"email": body.email},
            ip_address=client_ip,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user_id = str(response.user.id)

    # Check if user profile is active
    profile_result = (
        client.table("profiles")
        .select("id,is_active,org_id,role,display_name")
        .eq("id", user_id)
        .execute()
    )
    profiles = profile_result.data or []

    if not profiles:
        await audit.log_event(
            user_id=user_id,
            action="auth_login_no_profile",
            resource_type="auth",
            ip_address=client_ip,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User profile not found",
        )

    # Filter to active profiles only
    active_profiles = [p for p in profiles if p.get("is_active", True)]
    if not active_profiles:
        await audit.log_event(
            user_id=user_id,
            action="auth_login_deactivated",
            resource_type="auth",
            ip_address=client_ip,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    # Update last login timestamp (fire-and-forget)
    service = UserService(client)
    await service.update_last_login(response.user.id)

    logger.info(
        "login_succeeded",
        extra={"user_id": user_id, "ip_address": client_ip},
    )
    await audit.log_event(
        user_id=user_id,
        action="auth_login",
        resource_type="auth",
        ip_address=client_ip,
    )

    # Check for multi-org membership
    org_ids = list({p["org_id"] for p in active_profiles if p.get("org_id")})
    if len(org_ids) > 1:
        # User belongs to multiple orgs — frontend must call /login/select-org
        org_service = OrganizationService(client)
        orgs = []
        for oid in org_ids:
            try:
                org = await org_service.get_org(oid)
                orgs.append(
                    {
                        "org_id": org["id"],
                        "name_en": org.get("name_en"),
                        "name_ar": org.get("name_ar"),
                        "logo_url": org.get("logo_url"),
                    }
                )
            except Exception:
                continue

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer",
            "expires_in": response.session.expires_in,
            "requires_org_select": True,
            "orgs": orgs,
        }

    return LoginResponse(
        access_token=response.session.access_token,
        refresh_token=response.session.refresh_token,
        expires_in=response.session.expires_in,
    )


# ------------------------------------------------------------------
# SELECT ORG (for multi-org users)
# ------------------------------------------------------------------


@router.post("/login/select-org")
async def select_org(
    body: SelectOrgRequest,
    request: Request,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    """Select an organisation after login when the user belongs to multiple orgs.

    Returns the user's profile scoped to the chosen organisation.
    """
    client = get_supabase_client()
    org_id = body.org_id

    # Verify the user has a profile in the requested org
    result = (
        client.table("profiles")
        .select("*")
        .eq("id", str(current_user.id))
        .eq("org_id", org_id)
        .eq("is_active", True)
        .execute()
    )
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to this organization",
        )

    profile = result.data[0]
    audit = AuditLogger(client)
    await audit.log_event(
        user_id=str(current_user.id),
        action="auth_org_selected",
        resource_type="auth",
        metadata={"org_id": org_id},
        ip_address=request.client.host if request.client else None,
    )
    return {
        "user_id": profile["id"],
        "org_id": profile["org_id"],
        "role": profile["role"],
        "display_name": profile.get("display_name"),
        "department_id": profile.get("department_id"),
        "branch_id": profile.get("branch_id"),
    }


# ------------------------------------------------------------------
# BRANDING (public — by custom domain)
# ------------------------------------------------------------------


@router.get("/branding/{domain}")
async def get_branding(domain: str):
    """Get organisation branding by custom domain (public, no auth).

    Used by the login page to display the correct logo and colours.
    """
    try:
        client = get_supabase_client()
        service = OrganizationService(client)
        branding = await service.get_branding_by_domain(domain)
    except Exception:
        # organizations table may not exist yet (migration pending)
        branding = None
    if not branding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No organisation found for this domain",
        )
    return branding


# ------------------------------------------------------------------
# REGISTER (existing)
# ------------------------------------------------------------------


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    request: Request,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN))
    ],
):
    """Register a new user (Admin only)."""
    client = get_supabase_client()
    service = UserService(client)
    profile = await service.create_user(
        email=body.email,
        password=body.password,
        role=Role(body.role),
        display_name=body.display_name,
        org_id=current_user.org_id,
    )

    audit = AuditLogger(client)
    await audit.log_event(
        user_id=str(current_user.id),
        action="auth_register",
        resource_type="user",
        resource_id=str(profile.id),
        metadata={"email": body.email, "role": body.role},
        ip_address=request.client.host if request.client else None,
    )
    return {"id": str(profile.id), "role": profile.role.value}


# ------------------------------------------------------------------
# REFRESH
# ------------------------------------------------------------------


@router.post("/refresh", response_model=LoginResponse)
async def refresh(body: RefreshRequest):
    """Refresh an expired access token."""
    client = get_supabase_client()
    try:
        response = client.auth.refresh_session(body.refresh_token)
        return LoginResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            expires_in=response.session.expires_in,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )


# ------------------------------------------------------------------
# LOGOUT
# ------------------------------------------------------------------


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    """Logout the current user (invalidate session server-side)."""
    client = get_supabase_client()
    audit = AuditLogger(client)
    await audit.log_event(
        user_id=str(current_user.id),
        action="auth_logout",
        resource_type="auth",
        ip_address=request.client.host if request.client else None,
    )
    try:
        client.auth.sign_out()
    except Exception:
        pass  # Best-effort logout

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.deps import get_current_user, require_role
from app.core.audit import AuditLogger
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile
from app.schemas.auth import LoginRequest, LoginResponse, RefreshRequest, RegisterRequest
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, request: Request):
    """Authenticate user via Supabase Auth and return JWT tokens."""
    client_ip = request.client.host if request.client else None
    logger.info("login_attempt", extra={"email": body.email, "ip_address": client_ip})
    client = get_supabase_client()
    try:
        response = client.auth.sign_in_with_password(
            {"email": body.email, "password": body.password}
        )
    except Exception:
        logger.warning(
            "login_failed",
            extra={"email": body.email, "ip_address": client_ip},
        )
        audit = AuditLogger(client)
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

    logger.info(
        "login_succeeded",
        extra={"user_id": response.user.id, "ip_address": client_ip},
    )
    audit = AuditLogger(client)
    await audit.log_event(
        user_id=response.user.id,
        action="auth_login",
        resource_type="auth",
        ip_address=client_ip,
    )
    return LoginResponse(
        access_token=response.session.access_token,
        refresh_token=response.session.refresh_token,
        expires_in=response.session.expires_in,
    )


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

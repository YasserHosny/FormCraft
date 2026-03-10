from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from app.api.deps import get_current_user, require_role
from app.core.audit import AuditLogger
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile
from app.schemas.user import UpdateProfileRequest, UpdateRoleRequest, UserProfileResponse
from app.services.user_service import UserService


def _get_user_email(client, user_id: UUID) -> str:
    """Fetch user email from Supabase Auth admin API."""
    try:
        user = client.auth.admin.get_user_by_id(str(user_id))
        return user.user.email or ""
    except Exception:
        return ""

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    """Get the current user's profile."""
    client = get_supabase_client()
    email = _get_user_email(client, current_user.id)
    return UserProfileResponse(
        id=current_user.id,
        email=email,
        role=current_user.role,
        language=current_user.language,
        display_name=current_user.display_name,
        is_active=current_user.is_active,
    )


@router.put("/me", response_model=UserProfileResponse)
async def update_my_profile(
    body: UpdateProfileRequest,
    request: Request,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    """Update the current user's language or display name."""
    client = get_supabase_client()
    service = UserService(client)
    updated = await service.update_profile(
        user_id=current_user.id,
        language=body.language,
        display_name=body.display_name,
    )

    audit = AuditLogger(client)
    await audit.log_event(
        user_id=str(current_user.id),
        action="user_profile_updated",
        resource_type="user",
        resource_id=str(current_user.id),
        metadata=body.model_dump(exclude_none=True),
        ip_address=request.client.host if request.client else None,
    )

    email = _get_user_email(client, updated.id)
    return UserProfileResponse(
        id=updated.id,
        email=email,
        role=updated.role,
        language=updated.language,
        display_name=updated.display_name,
        is_active=updated.is_active,
    )


@router.get("")
async def list_users(
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN))
    ],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """List all users (Admin only)."""
    client = get_supabase_client()
    service = UserService(client)
    profiles, total = await service.list_users(page=page, limit=limit)
    results = []
    for p in profiles:
        email = _get_user_email(client, p.id)
        results.append(
            UserProfileResponse(
                id=p.id,
                email=email,
                role=p.role,
                language=p.language,
                display_name=p.display_name,
                is_active=p.is_active,
            )
        )
    return {"data": results, "total": total, "page": page, "limit": limit}


@router.put("/{user_id}/role")
async def update_user_role(
    user_id: UUID,
    body: UpdateRoleRequest,
    request: Request,
    current_user: Annotated[
        UserProfile, Depends(require_role(Role.ADMIN))
    ],
):
    """Update a user's role (Admin only)."""
    client = get_supabase_client()
    service = UserService(client)
    updated = await service.update_role(user_id, body.role)

    audit = AuditLogger(client)
    await audit.log_event(
        user_id=str(current_user.id),
        action="user_role_updated",
        resource_type="user",
        resource_id=str(user_id),
        metadata={"new_role": body.role.value},
        ip_address=request.client.host if request.client else None,
    )
    return {"id": str(updated.id), "role": updated.role.value}

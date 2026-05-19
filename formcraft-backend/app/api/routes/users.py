from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel

from app.api.deps import get_current_user, require_role
from app.core.audit import AuditLogger
from app.core.supabase import get_supabase_client
from app.middleware.org_context import OrgContext, get_org_context, require_org_admin
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


class UpdateAssignmentRequest(BaseModel):
    department_id: UUID | None = None
    branch_id: UUID | None = None
    role: str | None = None


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
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    department_id: UUID | None = Query(None),
    branch_id: UUID | None = Query(None),
    role: str | None = Query(None),
    is_active: bool | None = Query(None),
    search: str | None = Query(None),
):
    """List users within the caller's organisation.

    Supports filtering by department, branch, role, active status, and name search.
    """
    client = get_supabase_client()
    service = UserService(client)
    profiles, total = await service.list_users(
        page=page,
        limit=limit,
        org_id=ctx.org_id,
        department_id=department_id,
        branch_id=branch_id,
        role=role,
        is_active=is_active,
        search=search,
    )
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
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    """Update a user's role (org admin only)."""
    client = get_supabase_client()
    service = UserService(client)
    updated = await service.update_role(user_id, body.role)

    audit = AuditLogger(client)
    await audit.log_event(
        user_id=str(ctx.user_id),
        action="user_role_updated",
        resource_type="user",
        resource_id=str(user_id),
        metadata={"new_role": body.role.value},
        ip_address=request.client.host if request.client else None,
    )
    return {"id": str(updated.id), "role": updated.role.value}


@router.patch("/{user_id}/assignment")
async def update_user_assignment(
    user_id: UUID,
    body: UpdateAssignmentRequest,
    request: Request,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    """Update a user's department/branch/role assignment (org admin only)."""
    client = get_supabase_client()
    service = UserService(client)
    updated = await service.update_user_assignment(
        user_id=user_id,
        org_id=ctx.org_id,
        department_id=body.department_id,
        branch_id=body.branch_id,
        role=body.role,
    )

    audit = AuditLogger(client)
    await audit.log_event(
        user_id=str(ctx.user_id),
        action="user_assignment_updated",
        resource_type="user",
        resource_id=str(user_id),
        metadata=body.model_dump(exclude_none=True, mode="json"),
        ip_address=request.client.host if request.client else None,
    )
    return {
        "id": str(updated.id),
        "role": updated.role.value,
        "department_id": str(updated.department_id) if updated.department_id else None,
        "branch_id": str(updated.branch_id) if updated.branch_id else None,
    }


@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: UUID,
    request: Request,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    """Deactivate a user within the caller's organisation (org admin only)."""
    if user_id == ctx.user_id:
        from fastapi import HTTPException, status as http_status

        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate yourself",
        )
    client = get_supabase_client()
    service = UserService(client)
    updated = await service.deactivate_user(user_id, org_id=ctx.org_id)

    audit = AuditLogger(client)
    await audit.log_event(
        user_id=str(ctx.user_id),
        action="user_deactivated",
        resource_type="user",
        resource_id=str(user_id),
        ip_address=request.client.host if request.client else None,
    )
    return {"id": str(updated.id), "is_active": updated.is_active}


@router.post("/{user_id}/activate")
async def activate_user(
    user_id: UUID,
    request: Request,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    """Re-activate a deactivated user (org admin only)."""
    client = get_supabase_client()
    service = UserService(client)
    updated = await service.activate_user(user_id, org_id=ctx.org_id)

    audit = AuditLogger(client)
    await audit.log_event(
        user_id=str(ctx.user_id),
        action="user_activated",
        resource_type="user",
        resource_id=str(user_id),
        ip_address=request.client.host if request.client else None,
    )
    return {"id": str(updated.id), "is_active": updated.is_active}

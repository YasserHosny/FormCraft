"""Org-context dependency — provides org_id scoping for all multi-tenant queries.

Usage in routes:
    from app.middleware.org_context import get_org_context, OrgContext, require_platform_admin, require_org_admin

    @router.get("/something")
    async def handler(ctx: OrgContext = Depends(get_org_context)):
        # ctx.org_id is guaranteed non-None for tenant-scoped endpoints
        ...
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, HTTPException, status

from app.api.deps import get_current_user
from app.models.user import UserProfile


@dataclass(frozen=True, slots=True)
class OrgContext:
    """Immutable per-request organisation context extracted from the authenticated user."""

    org_id: UUID | None
    user_id: UUID
    is_platform_admin: bool
    department_id: UUID | None
    branch_id: UUID | None
    role: str


async def get_org_context(
    current_user: UserProfile = Depends(get_current_user),
) -> OrgContext:
    """Build an OrgContext from the current authenticated user.

    Platform admins may have org_id=None when they operate at the global level.
    Regular users must always have an org_id set on their profile.
    """
    if not current_user.is_platform_admin and current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not assigned to any organization",
        )

    return OrgContext(
        org_id=current_user.org_id,
        user_id=current_user.id,
        is_platform_admin=current_user.is_platform_admin,
        department_id=current_user.department_id,
        branch_id=current_user.branch_id,
        role=current_user.role.value,
    )


def require_platform_admin():
    """Dependency that ensures the caller is a platform admin."""

    async def _check(ctx: OrgContext = Depends(get_org_context)) -> OrgContext:
        if not ctx.is_platform_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Platform admin required",
            )
        return ctx

    return _check


def require_org_admin():
    """Dependency that ensures the caller is either an org admin or a platform admin."""

    async def _check(ctx: OrgContext = Depends(get_org_context)) -> OrgContext:
        if ctx.role != "admin" and not ctx.is_platform_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Org admin required",
            )
        return ctx

    return _check


def require_org_role(*allowed_roles: str):
    """Dependency factory — caller must hold one of *allowed_roles* or be platform admin."""

    async def _check(ctx: OrgContext = Depends(get_org_context)) -> OrgContext:
        if ctx.is_platform_admin:
            return ctx
        if ctx.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of: {', '.join(allowed_roles)}",
            )
        return ctx

    return _check

"""API routes for Feature 048: Custom Locale Validators.

Endpoints:
  /admin/validators              — Admin CRUD (admin role only)
  /admin/validators/:id/templates — Template usage audit (admin role only)
  /validators/org                 — Designer-facing payload (any authenticated user)

See: formcraft-specs/specs/048-custom-locale-validators/spec.md
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.api.deps import require_role
from app.core.middleware.rate_limit import limiter
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile
from app.schemas.custom_validator import (
    CustomValidatorCreate,
    CustomValidatorDesignerView,
    CustomValidatorListResponse,
    CustomValidatorResponse,
    CustomValidatorUpdate,
    ValidatorTemplateUsage,
    ValidatorTemplateUsageResponse,
)
from app.services.custom_validator_service import CustomValidatorService


admin_router = APIRouter(prefix="/admin/validators", tags=["Custom Validators (Admin)"])
designer_router = APIRouter(prefix="/validators", tags=["Custom Validators (Designer)"])


def _require_org(user: UserProfile) -> UUID:
    if not user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )
    return user.org_id


# ------------------------------------------------------------------
# Admin CRUD
# ------------------------------------------------------------------

@admin_router.post("", status_code=201, response_model=CustomValidatorResponse)
@limiter.limit("30/minute")
async def create_validator(
    request: Request,
    body: CustomValidatorCreate,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    org_id = _require_org(current_user)
    service = CustomValidatorService(get_supabase_client())
    created = await service.create(body, org_id=org_id, created_by=current_user.id)
    return CustomValidatorResponse(**created)


@admin_router.get("", response_model=CustomValidatorListResponse)
async def list_validators(
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
):
    org_id = _require_org(current_user)
    service = CustomValidatorService(get_supabase_client())
    items, total = await service.list_for_admin(
        org_id=org_id, page=page, page_size=page_size, search=search
    )
    return CustomValidatorListResponse(
        items=[CustomValidatorResponse(**row) for row in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@admin_router.get("/{validator_id}", response_model=CustomValidatorResponse)
async def get_validator(
    validator_id: UUID,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    org_id = _require_org(current_user)
    service = CustomValidatorService(get_supabase_client())
    row = await service.get(validator_id, org_id=org_id)
    return CustomValidatorResponse(**row)


@admin_router.put("/{validator_id}", response_model=CustomValidatorResponse)
@limiter.limit("30/minute")
async def update_validator(
    request: Request,
    validator_id: UUID,
    body: CustomValidatorUpdate,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    org_id = _require_org(current_user)
    service = CustomValidatorService(get_supabase_client())
    updated = await service.update(
        validator_id, body, org_id=org_id, updated_by=current_user.id
    )
    return CustomValidatorResponse(**updated)


@admin_router.delete("/{validator_id}", status_code=204)
async def delete_validator(
    validator_id: UUID,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    org_id = _require_org(current_user)
    service = CustomValidatorService(get_supabase_client())
    await service.soft_delete(validator_id, org_id=org_id, deleted_by=current_user.id)


@admin_router.get("/{validator_id}/templates", response_model=ValidatorTemplateUsageResponse)
async def list_validator_template_usage(
    validator_id: UUID,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    org_id = _require_org(current_user)
    service = CustomValidatorService(get_supabase_client())
    items, total = await service.list_template_usage(
        validator_id, org_id=org_id, page=page, page_size=page_size
    )
    return ValidatorTemplateUsageResponse(
        items=[ValidatorTemplateUsage(**row) for row in items],
        total=total,
        page=page,
        page_size=page_size,
    )


# ------------------------------------------------------------------
# Designer-facing query
# ------------------------------------------------------------------

@designer_router.get("/org", response_model=list[CustomValidatorDesignerView])
async def list_validators_for_designer(
    current_user: Annotated[
        UserProfile,
        Depends(require_role(Role.ADMIN, Role.DESIGNER, Role.OPERATOR, Role.VIEWER, Role.BRANCH_MANAGER)),
    ],
):
    """Return all active custom validators for the current user's org.

    Used by the Design Studio canvas dropdown and the Form Desk validator engine.
    Cached per-org for 60s; cache is invalidated on any admin CRUD operation.
    """
    org_id = _require_org(current_user)
    service = CustomValidatorService(get_supabase_client())
    items = await service.list_for_designer(org_id)
    return [CustomValidatorDesignerView(**row) for row in items]

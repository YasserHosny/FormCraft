from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from app.api.deps import get_current_user, require_role
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile
from app.schemas.template_permissions import (
    TemplateAccessDecisionResponse,
    TemplateAccessPolicyRequest,
    TemplateAccessPolicyResponse,
    TemplateCapability,
)
from app.services.template_permission_service import TemplatePermissionService

router = APIRouter(prefix="/template-permissions", tags=["Template Permissions"])
admin_router = APIRouter(
    prefix="/template-permissions", tags=["Admin Template Permissions"]
)


@router.get(
    "/templates/{template_id}/decision",
    response_model=TemplateAccessDecisionResponse,
)
async def get_template_access_decision(
    template_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
    capability: TemplateCapability = Query(...),
):
    service = TemplatePermissionService(get_supabase_client())
    return await service.evaluate_access(template_id, capability, current_user)


@admin_router.put(
    "/templates/{template_id}/policy",
    response_model=TemplateAccessPolicyResponse,
)
async def replace_template_access_policy(
    request: Request,
    template_id: UUID,
    body: TemplateAccessPolicyRequest,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    service = TemplatePermissionService(get_supabase_client())
    return await service.replace_policy(
        template_id=template_id,
        org_id=current_user.org_id,
        request=body,
        actor_id=current_user.id,
    )


@admin_router.get(
    "/templates/{template_id}/diagnostics",
    response_model=TemplateAccessDecisionResponse,
)
async def diagnose_template_access(
    template_id: UUID,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
    user_id: UUID = Query(...),
    capability: TemplateCapability = Query(...),
):
    service = TemplatePermissionService(get_supabase_client())
    return await service.diagnose_access(
        template_id=template_id,
        capability=capability,
        user_id=user_id,
        org_id=current_user.org_id,
    )

"""Admin portal routes for portal configuration and analytics."""

from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import require_role
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile
from app.schemas.portal import (
    PortalAnalyticsResponse,
    PortalConfiguration,
    PortalConfigurationUpdate,
    PortalTemplateListResponse,
)
from app.services.portal_service import PortalService

router = APIRouter(prefix="/portal", tags=["Admin Portal"])


@router.get("/templates", response_model=PortalTemplateListResponse)
async def list_portal_templates(
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    """List templates and public portal configuration."""
    client = get_supabase_client()
    service = PortalService(client)
    org_id = current_user.org_id
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with an organization",
        )
    return await service.list_portal_templates(org_id)


@router.get("/templates/{template_id}", response_model=PortalConfiguration)
async def get_portal_template(
    template_id: UUID,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    """Get portal configuration for one template."""
    client = get_supabase_client()
    service = PortalService(client)
    org_id = current_user.org_id
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with an organization",
        )
    config = await service.get_portal_config_by_template(org_id, template_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portal configuration not found",
        )
    return config


@router.patch("/templates/{template_id}", response_model=PortalConfiguration)
async def update_portal_template(
    template_id: UUID,
    body: PortalConfigurationUpdate,
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
):
    """Update portal configuration for a template."""
    client = get_supabase_client()
    service = PortalService(client)
    org_id = current_user.org_id
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with an organization",
        )
    return await service.update_portal_configuration(
        org_id=org_id,
        template_id=template_id,
        update=body,
        user_id=current_user.id,
    )


@router.get("/analytics", response_model=PortalAnalyticsResponse)
async def get_portal_analytics(
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
    template_id: UUID | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
):
    """Get portal submission, OTP, and rate-limit analytics."""
    client = get_supabase_client()
    service = PortalService(client)
    org_id = current_user.org_id
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with an organization",
        )
    return await service.get_portal_analytics(
        org_id=org_id,
        template_id=template_id,
        date_from=date_from,
        date_to=date_to,
    )

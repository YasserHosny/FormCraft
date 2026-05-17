"""Template feedback API routes."""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, require_role
from app.core.supabase import get_supabase_client
from app.models.enums import Role
from app.models.user import UserProfile
from app.schemas.template_feedback import (
    TemplateFeedbackAdminOverviewResponse,
    TemplateFeedbackListResponse,
    TemplateFeedbackSubmitRequest,
    TemplateFeedbackUpdateRequest,
)
from app.services.template_feedback_service import TemplateFeedbackService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/templates", tags=["Template Feedback"])

admin_router = APIRouter(prefix="/admin", tags=["Admin — Template Feedback"])


@router.post("/{template_id}/feedback", status_code=201)
async def submit_feedback(
    template_id: UUID,
    body: TemplateFeedbackSubmitRequest,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    """Submit feedback on a template (operator, designer, admin)."""
    client = get_supabase_client()
    service = TemplateFeedbackService(client)
    return service.submit_feedback(
        template_id=template_id,
        user_id=current_user.id,
        category=body.category,
        comment=body.comment,
        page_number=body.page_number,
        element_key=body.element_key,
        screenshot_path=body.screenshot_path,
    )


@router.get("/{template_id}/feedback")
async def list_feedback(
    template_id: UUID,
    status: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    current_user: Annotated[UserProfile, Depends(get_current_user)] = None,
):
    """List all feedback items for a template."""
    client = get_supabase_client()
    service = TemplateFeedbackService(client)
    return service.list_feedback(
        template_id=template_id,
        status_filter=status,
        page=page,
        limit=limit,
    )


@router.patch("/{template_id}/feedback/{feedback_id}")
async def update_feedback_status(
    template_id: UUID,
    feedback_id: UUID,
    body: TemplateFeedbackUpdateRequest,
    current_user: Annotated[UserProfile, Depends(require_role(Role.DESIGNER, Role.ADMIN))],
):
    """Update feedback status (designer/admin only)."""
    client = get_supabase_client()
    service = TemplateFeedbackService(client)
    return service.update_feedback_status(
        feedback_id=feedback_id,
        new_status=body.status,
        user_id=current_user.id,
    )


@admin_router.get("/template-feedback")
async def admin_template_feedback_overview(
    current_user: Annotated[UserProfile, Depends(require_role(Role.ADMIN))],
    org_id: UUID | None = None,
):
    """Admin overview of template feedback aggregated by template."""
    client = get_supabase_client()
    service = TemplateFeedbackService(client)
    items = service.get_admin_overview(org_id=org_id)
    return {"items": items}
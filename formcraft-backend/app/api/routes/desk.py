from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.api.deps import get_current_user
from app.core.audit import AuditLogger
from app.core.supabase import get_supabase_client
from app.models.user import UserProfile
from app.schemas.desk import DashboardResponse, PinRequest
from app.services.desk_service import DeskService
from app.services.template_service import TemplateService

router = APIRouter(prefix="/desk", tags=["Desk"])


@router.get("/fill/{template_id}")
async def get_template_for_fill(
    template_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    """Get a published template structure for form filling.

    Only returns published templates to prevent operators from seeing draft templates.
    """
    client = get_supabase_client()
    service = TemplateService(client)
    template = await service.get_template(template_id)

    if template.get("status") == "archived":
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This template is no longer available",
        )

    if template.get("status") not in ("published", "deprecated"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found or not published",
        )

    result = {**template, "is_deprecated": template.get("status") == "deprecated"}
    return result


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    current_user: Annotated[UserProfile, Depends(get_current_user)],
    search: str | None = Query(None, description="Search templates by name"),
    category: str | None = Query(None, description="Filter by category"),
    country: str | None = Query(None, description="Filter by country code"),
    language: str | None = Query(None, description="Filter by language"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """Get operator dashboard with templates, recent, pinned, and notifications."""
    client = get_supabase_client()
    service = DeskService(client)
    return await service.get_dashboard(
        operator_id=current_user.id,
        org_id=None,
        search=search,
        category=category,
        country=country,
        language=language,
        page=page,
        limit=limit,
    )


@router.post("/pins", status_code=status.HTTP_201_CREATED)
async def pin_template(
    body: PinRequest,
    request: Request,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    """Pin a template to favorites."""
    client = get_supabase_client()
    service = DeskService(client)

    pin = await service.pin_template(
        operator_id=current_user.id,
        template_id=body.template_id,
        org_id=current_user.id,
    )

    audit = AuditLogger(client)
    await audit.log_event(
        user_id=str(current_user.id),
        action="template.pin",
        resource_type="operator_pin",
        resource_id=str(pin.id),
        metadata={"template_id": str(body.template_id)},
        ip_address=request.client.host if request.client else None,
    )

    return {
        "id": str(pin.id),
        "template_id": str(pin.template_id),
        "created_at": pin.created_at.isoformat(),
    }


@router.delete("/pins/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unpin_template(
    template_id: UUID,
    request: Request,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    """Unpin a template from favorites."""
    client = get_supabase_client()
    service = DeskService(client)
    await service.unpin_template(
        operator_id=current_user.id,
        template_id=template_id,
    )

    audit = AuditLogger(client)
    await audit.log_event(
        user_id=str(current_user.id),
        action="template.unpin",
        resource_type="operator_pin",
        resource_id=str(template_id),
        metadata={"template_id": str(template_id)},
        ip_address=request.client.host if request.client else None,
    )


@router.post("/notifications/{notification_id}/dismiss", status_code=status.HTTP_204_NO_CONTENT)
async def dismiss_notification(
    notification_id: str,
    request: Request,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    """Dismiss a version notification. notificationId format: {template_id}:{version}"""
    parts = notification_id.split(":")
    if len(parts) != 2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    try:
        template_id = UUID(parts[0])
        version = int(parts[1])
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    client = get_supabase_client()
    service = DeskService(client)
    await service.dismiss_notification(
        operator_id=current_user.id,
        template_id=template_id,
        version=version,
        org_id=current_user.id,
    )

    audit = AuditLogger(client)
    await audit.log_event(
        user_id=str(current_user.id),
        action="notification.dismiss",
        resource_type="notification_dismissal",
        resource_id=notification_id,
        metadata={"template_id": str(template_id), "version": version},
        ip_address=request.client.host if request.client else None,
    )
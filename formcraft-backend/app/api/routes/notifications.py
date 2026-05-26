from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user
from app.core.supabase import get_supabase_client
from app.models.user import UserProfile
from app.schemas.notification import (
    MarkAllReadResponse,
    MarkReadResponse,
    NotificationsListResponse,
    NotificationResponse,
    PreferenceUpdateRequest,
    PreferencesListResponse,
    UnreadCountResponse,
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=NotificationsListResponse)
async def list_notifications(
    current_user: Annotated[UserProfile, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: str | None = Query(None),
    read_status: str | None = Query(None, pattern="^(read|unread|all)$"),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = NotificationService(client)
    items, total = await service.get_notifications(
        user_id=current_user.id,
        org_id=current_user.org_id,
        page=page,
        page_size=page_size,
        type_filter=type,
        read_status=read_status,
        date_from=date_from,
        date_to=date_to,
    )
    return NotificationsListResponse(
        notifications=[NotificationResponse(**item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = NotificationService(client)
    count = await service.get_unread_count(current_user.id, current_user.org_id)
    return UnreadCountResponse(unread_count=count)


@router.patch("/{notification_id}/read", response_model=MarkReadResponse)
async def mark_as_read(
    notification_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = NotificationService(client)
    result = await service.mark_as_read(notification_id, current_user.id)
    return MarkReadResponse(id=notification_id, read_at=result["read_at"])


@router.post("/read-all", response_model=MarkAllReadResponse)
async def mark_all_as_read(
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = NotificationService(client)
    count = await service.mark_all_as_read(current_user.id, current_user.org_id)
    return MarkAllReadResponse(marked_count=count)


@router.get("/preferences", response_model=PreferencesListResponse)
async def get_preferences(
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = NotificationService(client)
    prefs = await service.get_preferences(current_user.id, current_user.org_id)
    return PreferencesListResponse(preferences=prefs)


@router.patch("/preferences")
async def update_preference(
    body: PreferenceUpdateRequest,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User must belong to an organization",
        )

    client = get_supabase_client()
    service = NotificationService(client)
    result = await service.update_preference(
        current_user.id,
        current_user.org_id,
        body.notification_type,
        body.in_app_enabled,
        body.email_enabled,
    )
    return result

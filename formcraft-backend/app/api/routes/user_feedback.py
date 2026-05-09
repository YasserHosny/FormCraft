"""User-facing top-level endpoints for Feature 014: my-feedback and notifications."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.core.supabase import get_supabase_client
from app.models.user import UserProfile
from app.schemas.reply import (
    MyFeedbackResponse,
    NotificationsResponse,
)
from app.services.feedback.reply_service import ReplyService

router = APIRouter(tags=["User Feedback"])


@router.get("/my-feedback", response_model=MyFeedbackResponse)
async def get_my_feedback(
    current_user: Annotated[UserProfile, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List the authenticated user's own feedback submissions with reply status."""
    client = get_supabase_client()
    service = ReplyService(client)
    return await service.get_my_feedback(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
    )


@router.get("/notifications", response_model=NotificationsResponse)
async def get_notifications(
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    """Fetch all notifications for the current user; mark undelivered ones as delivered."""
    client = get_supabase_client()
    service = ReplyService(client)
    return await service.get_notifications(user_id=current_user.id)


@router.patch(
    "/notifications/{notification_id}/read",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def mark_notification_read(
    notification_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    """Mark a notification as read (sets read_at timestamp)."""
    client = get_supabase_client()
    service = ReplyService(client)
    await service.mark_notification_read(
        notification_id=notification_id,
        user_id=current_user.id,
    )

"""Feedback submission and file upload endpoints."""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from app.api.deps import get_current_user
from app.models.user import UserProfile
from app.schemas.feedback import (
    FeedbackDeleteUploadRequest,
    FeedbackSubmitRequest,
    FeedbackSubmitResponse,
    FeedbackUploadResponse,
)
from app.schemas.reply import (
    MyFeedbackResponse,
    NotificationsResponse,
    ReplyCreateRequest,
    ReplyResponse,
    ThreadResponse,
)
from app.core.supabase import get_supabase_client
from app.services.feedback.reply_service import ReplyService
from app.services.feedback.service import (
    FeedbackService,
    ALLOWED_AUDIO_MIMES,
    AUDIO_MAX_SIZE,
)


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/feedback", tags=["Feedback"])

# Second router — no prefix — for /my-feedback and /notifications top-level endpoints.
# Kept in this module so test patches on app.api.routes.feedback.get_supabase_client apply.
user_router = APIRouter(tags=["My Feedback"])


@router.post(
    "/upload/image",
    response_model=FeedbackUploadResponse,
    status_code=status.HTTP_200_OK,
)
async def upload_image(
    file: UploadFile = File(...),
    current_user: UserProfile = Depends(get_current_user),
):
    """Upload an image attachment (JPEG, PNG, WEBP, max 5 MB)."""
    client = get_supabase_client()
    service = FeedbackService(client)
    storage_path = await service.upload_image(
        user_id=current_user.id,
        file=file,
    )
    return FeedbackUploadResponse(storage_path=storage_path)


@router.post(
    "/upload/audio",
    response_model=FeedbackUploadResponse,
    status_code=status.HTTP_200_OK,
)
async def upload_audio(
    file: UploadFile = File(...),
    current_user: UserProfile = Depends(get_current_user),
):
    """Upload an audio attachment (MP3, M4A, WAV, WebM, max 10 MB)."""
    client = get_supabase_client()
    service = FeedbackService(client)
    content = await file.read()
    storage_path = await service.upload_file(
        user_id=current_user.id,
        file_content=content,
        filename=file.filename or "audio.webm",
        content_type=file.content_type or "application/octet-stream",
        allowed_mimes=ALLOWED_AUDIO_MIMES,
        max_size=AUDIO_MAX_SIZE,
    )
    return FeedbackUploadResponse(storage_path=storage_path)


@router.post(
    "/upload/video",
    response_model=FeedbackUploadResponse,
    status_code=status.HTTP_200_OK,
)
async def upload_video(
    file: UploadFile = File(...),
    current_user: UserProfile = Depends(get_current_user),
):
    """Upload a video attachment (MP4, WebM, max 100 MB)."""
    client = get_supabase_client()
    service = FeedbackService(client)
    storage_path = await service.upload_video(
        user_id=current_user.id,
        file=file,
    )
    return FeedbackUploadResponse(storage_path=storage_path)


@router.delete("/upload", status_code=status.HTTP_204_NO_CONTENT)
async def delete_upload_legacy(
    request: FeedbackDeleteUploadRequest,
    current_user: UserProfile = Depends(get_current_user),
):
    """Delete an orphaned upload (backward-compatible endpoint)."""
    client = get_supabase_client()
    service = FeedbackService(client)
    await service.delete_upload(
        user_id=current_user.id, storage_path=request.storage_path
    )


@router.delete("/upload/{media_type}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_upload(
    media_type: str,
    request: FeedbackDeleteUploadRequest,
    current_user: UserProfile = Depends(get_current_user),
):
    """Delete an orphaned upload (when submission fails after upload)."""
    client = get_supabase_client()
    service = FeedbackService(client)
    await service.delete_upload(
        user_id=current_user.id, storage_path=request.storage_path
    )


@router.post(
    "", response_model=FeedbackSubmitResponse, status_code=status.HTTP_201_CREATED
)
async def submit_feedback(
    payload: FeedbackSubmitRequest,
    current_user: UserProfile = Depends(get_current_user),
):
    """Submit a feedback entry. Enforces 30-second cooldown per user."""
    client = get_supabase_client()
    service = FeedbackService(client)
    result = await service.submit_feedback(user_id=current_user.id, payload=payload)
    return FeedbackSubmitResponse(**result)


# ── Feature 014: User-facing reply endpoints ────────────────────────────────


@router.get("/{feedback_id}/replies", response_model=ThreadResponse)
async def get_user_replies(
    feedback_id: UUID,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
    limit: int = Query(20, ge=1, le=100),
    before_id: UUID | None = None,
):
    """Get the reply thread for a feedback the current user owns."""
    client = get_supabase_client()
    service = ReplyService(client)
    return await service.get_replies(
        feedback_id=feedback_id,
        user_id=current_user.id,
        is_admin=False,
        limit=limit,
        before_id=before_id,
    )


@router.post(
    "/{feedback_id}/replies",
    response_model=ReplyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def post_user_reply(
    feedback_id: UUID,
    request: ReplyCreateRequest,
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    """Post a follow-up reply on the user's own feedback submission."""
    client = get_supabase_client()
    service = ReplyService(client)
    return await service.post_reply(
        feedback_id=feedback_id,
        author_id=current_user.id,
        author_role="user",
        payload=request,
    )


# ── Feature 014: Top-level user routes (/my-feedback, /notifications) ────────
# These are on user_router (no prefix) so they resolve at /api/my-feedback
# and /api/notifications — not under /api/feedback/*.


@user_router.get("/my-feedback", response_model=MyFeedbackResponse)
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


@user_router.get("/notifications", response_model=NotificationsResponse)
async def get_notifications(
    current_user: Annotated[UserProfile, Depends(get_current_user)],
):
    """Fetch all notifications for the current user; mark undelivered ones as delivered."""
    client = get_supabase_client()
    service = ReplyService(client)
    return await service.get_notifications(user_id=current_user.id)


@user_router.patch(
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

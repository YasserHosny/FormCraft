"""Feedback submission and file upload endpoints."""

import logging

from fastapi import APIRouter, Depends, File, UploadFile, status
from app.api.deps import get_current_user
from app.models.user import UserProfile
from app.schemas.feedback import (
    FeedbackDeleteUploadRequest,
    FeedbackSubmitRequest,
    FeedbackSubmitResponse,
    FeedbackUploadResponse,
)
from app.core.supabase import get_supabase_client
from app.services.feedback.service import (
    FeedbackService,
    ALLOWED_AUDIO_MIMES,
    AUDIO_MAX_SIZE,
)


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/feedback", tags=["Feedback"])


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

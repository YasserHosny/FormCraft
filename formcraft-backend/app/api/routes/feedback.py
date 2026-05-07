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
    ALLOWED_IMAGE_MIMES,
    ALLOWED_AUDIO_MIMES,
    IMAGE_MAX_SIZE,
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
    content = await file.read()
    url = await service.upload_file(
        user_id=current_user.id,
        file_content=content,
        filename=file.filename or "image.jpg",
        content_type=file.content_type or "application/octet-stream",
        allowed_mimes=ALLOWED_IMAGE_MIMES,
        max_size=IMAGE_MAX_SIZE,
    )
    return FeedbackUploadResponse(url=url)


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
    url = await service.upload_file(
        user_id=current_user.id,
        file_content=content,
        filename=file.filename or "audio.webm",
        content_type=file.content_type or "application/octet-stream",
        allowed_mimes=ALLOWED_AUDIO_MIMES,
        max_size=AUDIO_MAX_SIZE,
    )
    return FeedbackUploadResponse(url=url)


@router.delete("/upload", status_code=status.HTTP_204_NO_CONTENT)
async def delete_upload(
    request: FeedbackDeleteUploadRequest,
    current_user: UserProfile = Depends(get_current_user),
):
    """Delete an orphaned upload (when submission fails after upload)."""
    client = get_supabase_client()
    service = FeedbackService(client)
    await service.delete_file(user_id=current_user.id, storage_path=request.url)


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

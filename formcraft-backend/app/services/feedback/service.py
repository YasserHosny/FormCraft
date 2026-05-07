"""Feedback submission business logic."""

import logging
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from supabase import Client


logger = logging.getLogger(__name__)

COOLDOWN_SECONDS = 30
IMAGE_MAX_SIZE = 5 * 1024 * 1024  # 5 MB
AUDIO_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_IMAGE_MIMES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_AUDIO_MIMES = {
    "audio/mpeg",
    "audio/mp4",
    "audio/wav",
    "audio/webm",
    "audio/x-m4a",
}
FEEDBACK_BUCKET = "feedback"


class FeedbackService:
    """Service for feedback submission, file upload, and admin review."""

    def __init__(self, client: Client):
        self.client = client

    async def upload_file(
        self,
        user_id: UUID,
        file_content: bytes,
        filename: str,
        content_type: str,
        allowed_mimes: set[str],
        max_size: int,
    ) -> str:
        """Upload a file to Supabase Storage and return the storage path."""
        if content_type not in allowed_mimes:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Unsupported file type: {content_type}",
            )
        if len(file_content) > max_size:
            raise HTTPException(
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                f"File exceeds {max_size // (1024 * 1024)} MB limit",
            )

        storage_path = f"feedback/{user_id}/{uuid4()}.{filename.rsplit('.', 1)[-1]}"
        self.client.storage.from_(FEEDBACK_BUCKET).upload(
            path=storage_path,
            file=file_content,
            file_options={"content-type": content_type},
        )
        return storage_path

    async def delete_file(self, user_id: UUID, storage_path: str) -> None:
        """Delete an orphaned file from Supabase Storage."""
        expected_prefix = f"feedback/{user_id}/"
        if not storage_path.startswith(expected_prefix):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Cannot delete files belonging to another user",
            )
        try:
            self.client.storage.from_(FEEDBACK_BUCKET).remove([storage_path])
        except Exception:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "File not found in storage")

    async def submit_feedback(self, user_id: UUID, payload) -> dict:
        """Submit a feedback entry. Enforces 30-second cooldown."""
        result = (
            self.client.table("feedback_submissions")
            .select("submitted_at")
            .eq("user_id", str(user_id))
            .order("submitted_at", desc=True)
            .limit(1)
            .execute()
        )
        if result.data:
            last_submission = datetime.fromisoformat(
                result.data[0]["submitted_at"].replace("Z", "+00:00")
            )
            elapsed = (datetime.now(timezone.utc) - last_submission).total_seconds()
            if elapsed < COOLDOWN_SECONDS:
                remaining = int(COOLDOWN_SECONDS - elapsed)
                raise HTTPException(
                    status.HTTP_429_TOO_MANY_REQUESTS,
                    f"Please wait {remaining} seconds before submitting again",
                )

        row = {
            "user_id": str(user_id),
            "page_url": str(payload.page_url),
            "text_content": payload.text_content,
            "image_url": payload.image_url,
            "audio_url": payload.audio_url,
        }
        insert_result = self.client.table("feedback_submissions").insert(row).execute()
        if not insert_result.data:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Failed to submit feedback",
            )

        entry = insert_result.data[0]
        return {
            "id": entry["id"],
            "submitted_at": entry["submitted_at"],
            "status": entry["status"],
        }

    async def list_feedback(
        self,
        page: int = 1,
        limit: int = 50,
        status: str | None = None,
        user_id: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> tuple[list[dict], int]:
        """List feedback entries (admin). Returns items and total count."""
        offset = (page - 1) * limit
        query = self.client.table("feedback_submissions").select(
            "*, profiles!feedback_submissions_user_id_fkey(display_name,email)",
            count="exact",
        )

        if status:
            query = query.eq("status", status)
        if user_id:
            query = query.eq("user_id", user_id)
        if date_from:
            query = query.gte("submitted_at", date_from)
        if date_to:
            query = query.lte("submitted_at", date_to)

        result = (
            query.range(offset, offset + limit - 1)
            .order("submitted_at", desc=True)
            .execute()
        )

        items = []
        for row in result.data or []:
            profile = row.pop("profiles", None) or {}
            display_name = (
                profile.get("display_name") or profile.get("email") or "Unknown"
            )
            row["submitter_display_name"] = display_name

            if row.get("image_url"):
                try:
                    row["image_signed_url"] = self.client.storage.from_(
                        FEEDBACK_BUCKET
                    ).create_signed_url(row["image_url"], 3600)
                except Exception:
                    row["image_signed_url"] = None
            else:
                row["image_signed_url"] = None

            if row.get("audio_url"):
                try:
                    row["audio_signed_url"] = self.client.storage.from_(
                        FEEDBACK_BUCKET
                    ).create_signed_url(row["audio_url"], 3600)
                except Exception:
                    row["audio_signed_url"] = None
            else:
                row["audio_signed_url"] = None

            items.append(row)

        return items, result.count or 0

    async def update_status(self, feedback_id: UUID, new_status: str) -> dict:
        """Update the review status of a feedback entry (admin only)."""
        result = (
            self.client.table("feedback_submissions")
            .update({"status": new_status})
            .eq("id", str(feedback_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Feedback entry not found")
        entry = result.data[0]
        return {"id": entry["id"], "status": entry["status"]}

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
        search: str | None = None,
        label_ids: list[str] | None = None,
    ) -> tuple[list[dict], int]:
        """List feedback entries (admin). Returns items and total count."""
        offset = (page - 1) * limit
        query = self.client.table("feedback_submissions").select(
            "*, profiles!feedback_submissions_user_id_fkey(display_name,email), feedback_submission_labels(feedback_labels(id,name,colour,created_at))",
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
        if search:
            query = query.ilike("text_content", f"%{search}%")
        if label_ids:
            sub_result = (
                self.client.table("feedback_submission_labels")
                .select("submission_id")
                .in_("label_id", label_ids)
                .execute()
            )
            submission_ids = list(
                {row["submission_id"] for row in sub_result.data or []}
            )
            if submission_ids:
                query = query.in_("id", submission_ids)
            else:
                return [], 0

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

            labels_data = row.pop("feedback_submission_labels", []) or []
            row["labels"] = [
                lbl["feedback_labels"]
                for lbl in labels_data
                if lbl.get("feedback_labels")
            ]

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

    async def list_submitters(self) -> list[dict]:
        """List distinct submitters (admin). Returns id and display_name."""
        result = (
            self.client.table("feedback_submissions")
            .select(
                "user_id, profiles!feedback_submissions_user_id_fkey(display_name,email)"
            )
            .execute()
        )
        seen = set()
        submitters = []
        for row in result.data or []:
            uid = row["user_id"]
            if uid in seen:
                continue
            seen.add(uid)
            profile = row.get("profiles") or {}
            display_name = (
                profile.get("display_name") or profile.get("email") or "Unknown"
            )
            submitters.append({"id": uid, "display_name": display_name})
        return submitters

    async def list_labels(self) -> list[dict]:
        """List all labels (admin)."""
        result = (
            self.client.table("feedback_labels")
            .select("*")
            .order("created_at")
            .execute()
        )
        return result.data or []

    async def create_label(self, admin_id: UUID, payload) -> dict:
        """Create a new label (admin). Raises 409 on name conflict."""
        row = {
            "name": payload.name,
            "colour": payload.colour.value if payload.colour else None,
            "created_by": str(admin_id),
        }
        try:
            result = self.client.table("feedback_labels").insert(row).execute()
        except Exception as exc:
            error_msg = str(exc).lower()
            if (
                "unique" in error_msg
                or "duplicate" in error_msg
                or "23505" in error_msg
            ):
                raise HTTPException(
                    status.HTTP_409_CONFLICT,
                    f"Label with name '{payload.name}' already exists",
                )
            raise
        if not result.data:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create label"
            )
        return result.data[0]

    async def update_label(self, label_id: UUID, payload) -> dict:
        """Update a label (admin). Raises 404 if not found, 409 on name conflict."""
        updates = {}
        if payload.name is not None:
            updates["name"] = payload.name
        if payload.colour is not None:
            updates["colour"] = payload.colour.value
        if not updates:
            result = (
                self.client.table("feedback_labels")
                .select("*")
                .eq("id", str(label_id))
                .single()
                .execute()
            )
            if not result.data:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "Label not found")
            return result.data
        try:
            result = (
                self.client.table("feedback_labels")
                .update(updates)
                .eq("id", str(label_id))
                .execute()
            )
        except Exception as exc:
            error_msg = str(exc).lower()
            if (
                "unique" in error_msg
                or "duplicate" in error_msg
                or "23505" in error_msg
            ):
                raise HTTPException(
                    status.HTTP_409_CONFLICT,
                    "Label with this name already exists",
                )
            raise
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Label not found")
        return result.data[0]

    async def delete_label(self, label_id: UUID) -> None:
        """Delete a label (admin). CASCADE handles associations."""
        result = (
            self.client.table("feedback_labels")
            .delete()
            .eq("id", str(label_id))
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Label not found")

    async def assign_labels(
        self, feedback_id: UUID, label_ids: list[str], admin_id: UUID
    ) -> list[dict]:
        """Assign labels to a feedback submission. Max 5 labels."""
        if len(label_ids) > 5:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Maximum of 5 labels allowed per submission",
            )

        valid_labels = (
            self.client.table("feedback_labels")
            .select("id")
            .in_("id", label_ids)
            .execute()
        )
        found_ids = {row["id"] for row in valid_labels.data}
        missing = set(label_ids) - found_ids
        if missing:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Label(s) not found: {', '.join(missing)}",
            )

        feedback_check = (
            self.client.table("feedback_submissions")
            .select("id")
            .eq("id", str(feedback_id))
            .execute()
        )
        if not feedback_check.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Feedback entry not found")

        self.client.table("feedback_submission_labels").delete().eq(
            "feedback_id", str(feedback_id)
        ).execute()

        rows = [
            {
                "feedback_id": str(feedback_id),
                "label_id": lid,
                "assigned_by": str(admin_id),
            }
            for lid in label_ids
        ]
        self.client.table("feedback_submission_labels").insert(rows).execute()

        assigned = (
            self.client.table("feedback_submission_labels")
            .select("feedback_labels(id,name,colour,created_at)")
            .eq("feedback_id", str(feedback_id))
            .execute()
        )
        return [
            row["feedback_labels"]
            for row in assigned.data
            if row.get("feedback_labels")
        ]

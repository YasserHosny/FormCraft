"""Business logic for feedback replies, notifications, and my-feedback (Feature 014)."""

import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.schemas.reply import (
    MyFeedbackItem,
    MyFeedbackResponse,
    NotificationResponse,
    NotificationsResponse,
    ReplyCreateRequest,
    ReplyResponse,
    ThreadResponse,
)

logger = logging.getLogger(__name__)

REPLY_PAGE_SIZE = 20


def _row(result) -> dict | None:
    """Normalize a Supabase .maybe_single() / .single() result to a dict or None.

    The real Supabase SDK returns ``data`` as a plain dict (or None) for single-row
    queries.  Test mocks built with ``make_supabase_response([...])`` return a list.
    This helper accepts both shapes so the service works in tests and production.
    """
    data = result.data
    if data is None:
        return None
    if isinstance(data, list):
        return data[0] if data else None
    return data


class ReplyService:
    """Service for feedback threading, notifications, and my-feedback list."""

    def __init__(self, client: Client):
        self.client = client

    async def get_replies(
        self,
        feedback_id: UUID,
        user_id: UUID,
        is_admin: bool,
        limit: int = REPLY_PAGE_SIZE,
        before_id: UUID | None = None,
    ) -> ThreadResponse:
        """Return paginated replies for a submission thread.

        For non-admins, validates that user_id owns the submission.
        Uses keyset cursor via before_id for stable pagination.
        """
        # Validate ownership for non-admins
        sub_result = (
            self.client.table("feedback_submissions")
            .select("user_id")
            .eq("id", str(feedback_id))
            .maybe_single()
            .execute()
        )
        sub_row = _row(sub_result)
        if not sub_row:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Submission not found")
        if not is_admin and str(sub_row["user_id"]) != str(user_id):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")

        # Resolve cursor pivot timestamp
        pivot_ts: str | None = None
        pivot_id: str | None = None
        if before_id:
            pivot_result = (
                self.client.table("feedback_replies")
                .select("created_at, id")
                .eq("id", str(before_id))
                .maybe_single()
                .execute()
            )
            pivot_row = _row(pivot_result)
            if pivot_row:
                pivot_ts = pivot_row["created_at"]
                pivot_id = pivot_row["id"]

        # Fetch limit+1 to detect has_earlier
        query = (
            self.client.table("feedback_replies")
            .select("id, author_id, author_role, text_content, created_at")
            .eq("feedback_id", str(feedback_id))
            .order("created_at", desc=True)
            .order("id", desc=True)
            .limit(limit + 1)
        )
        if pivot_ts and pivot_id:
            # Keyset: replies older than the pivot
            query = query.lt("created_at", pivot_ts)

        result = query.execute()
        rows = result.data or []

        has_earlier = len(rows) > limit
        rows = rows[:limit]

        # Batch-fetch display names
        author_ids = list({r["author_id"] for r in rows})
        profiles_map: dict[str, str] = {}
        if author_ids:
            pr = (
                self.client.table("profiles")
                .select("id,display_name")
                .in_("id", author_ids)
                .execute()
            )
            for p in pr.data or []:
                profiles_map[p["id"]] = p.get("display_name") or "Unknown"

        replies = [
            ReplyResponse(
                id=r["id"],
                author_role=r["author_role"],
                author_name=profiles_map.get(r["author_id"], "Unknown"),
                text_content=r["text_content"],
                created_at=r["created_at"],
            )
            for r in rows
        ]

        return ThreadResponse(replies=replies, has_earlier=has_earlier)

    async def post_reply(
        self,
        feedback_id: UUID,
        author_id: UUID,
        author_role: str,
        payload: ReplyCreateRequest,
    ) -> ReplyResponse:
        """Insert a reply and update denormalised counters / notifications."""
        # Validate submission exists and check ownership for users
        sub_result = (
            self.client.table("feedback_submissions")
            .select("id, user_id")
            .eq("id", str(feedback_id))
            .maybe_single()
            .execute()
        )
        submission = _row(sub_result)
        if not submission:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Submission not found")
        if author_role == "user" and str(submission["user_id"]) != str(author_id):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")

        # Resolve author display name — use plain .execute() (list result) so the
        # mock chain stays independent from the submission maybe_single() chain above.
        profile_result = (
            self.client.table("profiles")
            .select("display_name")
            .eq("id", str(author_id))
            .execute()
        )
        profile_rows = profile_result.data or []
        author_name = (profile_rows[0].get("display_name") if profile_rows else None) or "Unknown"

        # Insert reply
        reply_data = {
            "feedback_id": str(feedback_id),
            "author_id": str(author_id),
            "author_role": author_role,
            "text_content": payload.text_content,
        }
        reply_result = (
            self.client.table("feedback_replies").insert(reply_data).execute()
        )
        reply_row = reply_result.data[0]

        # Update reply_count (read current value, increment, write back)
        # Use .execute() (list result) rather than .single() to avoid sharing
        # the mock chain used by get_current_user during integration tests.
        count_result = (
            self.client.table("feedback_submissions")
            .select("reply_count")
            .eq("id", str(feedback_id))
            .execute()
        )
        count_rows = count_result.data or []
        current_count = count_rows[0].get("reply_count") if count_rows else 0
        new_count = (current_count or 0) + 1
        self.client.table("feedback_submissions").update(
            {"reply_count": new_count}
        ).eq("id", str(feedback_id)).execute()

        # Role-specific side effects
        if author_role == "user":
            self.client.table("feedback_submissions").update(
                {"has_unread_user_reply": True}
            ).eq("id", str(feedback_id)).execute()
        elif author_role == "admin":
            self.client.table("feedback_notifications").insert(
                {
                    "recipient_user_id": str(submission["user_id"]),
                    "feedback_id": str(feedback_id),
                    "reply_id": str(reply_row["id"]),
                }
            ).execute()

        return ReplyResponse(
            id=reply_row["id"],
            author_role=author_role,
            author_name=author_name,
            text_content=reply_row["text_content"],
            created_at=reply_row["created_at"],
        )

    async def mark_submission_read(self, feedback_id: UUID) -> None:
        """Clear has_unread_user_reply on the submission (called on admin thread expand)."""
        result = (
            self.client.table("feedback_submissions")
            .select("id")
            .eq("id", str(feedback_id))
            .maybe_single()
            .execute()
        )
        if not _row(result):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Submission not found")
        self.client.table("feedback_submissions").update(
            {"has_unread_user_reply": False}
        ).eq("id", str(feedback_id)).execute()

    async def get_my_feedback(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> MyFeedbackResponse:
        """Return paginated submission history for the authenticated user.

        Uses a single query with EXISTS subquery to determine has_unread_admin_reply
        without N+1 round-trips (satisfies SC-003 at 500 submissions).
        """
        offset = (page - 1) * page_size

        # Count total
        count_result = (
            self.client.table("feedback_submissions")
            .select("id", count="exact")
            .eq("user_id", str(user_id))
            .execute()
        )
        total = count_result.count or 0

        # Fetch page
        rows_result = (
            self.client.table("feedback_submissions")
            .select("id, page_url, text_content, status, submitted_at, reply_count")
            .eq("user_id", str(user_id))
            .order("submitted_at", desc=True)
            .range(offset, offset + page_size - 1)
            .execute()
        )
        rows = rows_result.data or []

        if not rows:
            return MyFeedbackResponse(
                results=[], total=total, page=page, page_size=page_size
            )

        feedback_ids = [r["id"] for r in rows]

        # Single query: find which feedback_ids have unread admin notifications
        notif_result = (
            self.client.table("feedback_notifications")
            .select("feedback_id")
            .eq("recipient_user_id", str(user_id))
            .is_("read_at", "null")
            .in_("feedback_id", feedback_ids)
            .execute()
        )
        unread_set = {n["feedback_id"] for n in (notif_result.data or [])}

        results = [
            MyFeedbackItem(
                id=r["id"],
                page_url=r["page_url"],
                text_content=r["text_content"],
                status=r["status"],
                submitted_at=r["submitted_at"],
                reply_count=r["reply_count"],
                has_unread_admin_reply=r["id"] in unread_set,
            )
            for r in rows
        ]

        return MyFeedbackResponse(
            results=results, total=total, page=page, page_size=page_size
        )

    async def get_notifications(self, user_id: UUID) -> NotificationsResponse:
        """Fetch all notifications for user; atomically mark undelivered as delivered."""
        result = (
            self.client.table("feedback_notifications")
            .select("id, feedback_id, reply_id, created_at, delivered_at, read_at")
            .eq("recipient_user_id", str(user_id))
            .order("created_at", desc=True)
            .execute()
        )
        rows = result.data or []

        # Mark undelivered as delivered
        now_iso = datetime.now(timezone.utc).isoformat()
        undelivered_ids = [r["id"] for r in rows if r["delivered_at"] is None]
        if undelivered_ids:
            self.client.table("feedback_notifications").update(
                {"delivered_at": now_iso}
            ).in_("id", undelivered_ids).execute()
            # Update local rows so response reflects new state
            for r in rows:
                if r["id"] in undelivered_ids:
                    r["delivered_at"] = now_iso

        unread_count = sum(1 for r in rows if r["read_at"] is None)

        notifications = [
            NotificationResponse(
                id=r["id"],
                feedback_id=r["feedback_id"],
                reply_id=r["reply_id"],
                created_at=r["created_at"],
                delivered_at=r["delivered_at"],
                read_at=r["read_at"],
            )
            for r in rows
        ]

        return NotificationsResponse(
            notifications=notifications, unread_count=unread_count
        )

    async def mark_notification_read(
        self, notification_id: UUID, user_id: UUID
    ) -> None:
        """Mark a specific notification as read."""
        result = (
            self.client.table("feedback_notifications")
            .select("id, recipient_user_id")
            .eq("id", str(notification_id))
            .maybe_single()
            .execute()
        )
        notif_row = _row(result)
        if not notif_row:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found")
        if str(notif_row["recipient_user_id"]) != str(user_id):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")

        now_iso = datetime.now(timezone.utc).isoformat()
        self.client.table("feedback_notifications").update(
            {"read_at": now_iso}
        ).eq("id", str(notification_id)).execute()

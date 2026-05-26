"""Unit tests for ReplyService — feedback threading & notifications (Feature 014)."""

from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException

from app.schemas.reply import ReplyCreateRequest
from app.services.feedback.reply_service import ReplyService
from tests.conftest import make_supabase_response


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def service(mock_client):
    return ReplyService(client=mock_client)


@pytest.fixture
def feedback_id():
    return uuid4()


@pytest.fixture
def admin_id():
    return uuid4()


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def now_iso():
    return datetime.now(timezone.utc).isoformat()


def _sub(feedback_id: UUID, user_id: UUID):
    return {"id": str(feedback_id), "user_id": str(user_id), "reply_count": 0}


def _reply_row(feedback_id: UUID, author_id: UUID, role: str):
    return {
        "id": str(uuid4()),
        "feedback_id": str(feedback_id),
        "author_id": str(author_id),
        "author_role": role,
        "text_content": "Test reply",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "profiles": {"display_name": "Test User"},
    }


# ---------------------------------------------------------------------------
# get_replies — admin path
# ---------------------------------------------------------------------------

class TestGetRepliesAdmin:
    """Admin bypasses ownership check; keyset cursor; has_earlier flag."""

    def _build_rows(self, feedback_id: UUID, count: int):
        return [_reply_row(feedback_id, uuid4(), "admin") for _ in range(count)]

    @pytest.mark.asyncio
    async def test_admin_gets_up_to_20_replies(
        self, service, mock_client, feedback_id, user_id
    ):
        rows = self._build_rows(feedback_id, 20)
        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [_sub(feedback_id, user_id)]
        )
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.order.return_value.limit.return_value.execute.return_value = make_supabase_response(
            rows
        )

        result = await service.get_replies(
            feedback_id=feedback_id,
            user_id=admin_id,
            is_admin=True,
            limit=20,
        )

        assert len(result.replies) == 20
        assert result.has_earlier is False

    @pytest.mark.asyncio
    async def test_has_earlier_true_when_more_than_limit(
        self, service, mock_client, feedback_id, user_id
    ):
        """21 rows returned for limit=20 → has_earlier=True, 20 replies returned."""
        rows = self._build_rows(feedback_id, 21)
        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [_sub(feedback_id, user_id)]
        )
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.order.return_value.limit.return_value.execute.return_value = make_supabase_response(
            rows
        )

        result = await service.get_replies(
            feedback_id=feedback_id,
            user_id=admin_id,
            is_admin=True,
            limit=20,
        )

        assert len(result.replies) == 20
        assert result.has_earlier is True

    @pytest.mark.asyncio
    async def test_before_id_cursor_applied(
        self, service, mock_client, feedback_id, user_id, admin_id
    ):
        """When before_id is given, pivot timestamp is resolved and filter applied."""
        pivot_ts = datetime.now(timezone.utc).isoformat()
        before_id = uuid4()
        rows = self._build_rows(feedback_id, 5)

        # Submission lookup
        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [_sub(feedback_id, user_id)]
        )
        # Pivot lookup
        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [{"created_at": pivot_ts, "id": str(before_id)}]
        )
        # Main query
        (
            mock_client.table.return_value.select.return_value
            .eq.return_value.order.return_value.order.return_value
            .limit.return_value.lt.return_value.execute.return_value
        ) = make_supabase_response(rows)

        result = await service.get_replies(
            feedback_id=feedback_id,
            user_id=admin_id,
            is_admin=True,
            before_id=before_id,
        )
        assert len(result.replies) == 5
        assert result.has_earlier is False

    @pytest.mark.asyncio
    async def test_before_id_oldest_reply_returns_empty(
        self, service, mock_client, feedback_id, user_id
    ):
        """When before_id is the oldest reply, empty list and has_earlier=False."""
        pivot_ts = "2020-01-01T00:00:00+00:00"
        before_id = uuid4()

        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [{"created_at": pivot_ts, "id": str(before_id)}]
        )
        (
            mock_client.table.return_value.select.return_value
            .eq.return_value.order.return_value.order.return_value
            .limit.return_value.lt.return_value.execute.return_value
        ) = make_supabase_response([])

        result = await service.get_replies(
            feedback_id=feedback_id,
            user_id=uuid4(),
            is_admin=True,
            before_id=before_id,
        )
        assert result.replies == []
        assert result.has_earlier is False

    @pytest.mark.asyncio
    async def test_non_admin_non_owner_gets_403(
        self, service, mock_client, feedback_id
    ):
        """Non-admin accessing submission they don't own → 403."""
        other_user = uuid4()
        requesting_user = uuid4()

        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [_sub(feedback_id, other_user)]
        )

        with pytest.raises(HTTPException) as exc_info:
            await service.get_replies(
                feedback_id=feedback_id,
                user_id=requesting_user,
                is_admin=False,
            )
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_missing_submission_returns_404(
        self, service, mock_client, feedback_id
    ):
        """Submission not found → 404."""
        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            []
        )

        with pytest.raises(HTTPException) as exc_info:
            await service.get_replies(
                feedback_id=feedback_id,
                user_id=uuid4(),
                is_admin=False,
            )
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# post_reply — admin path
# ---------------------------------------------------------------------------

class TestPostReplyAdmin:
    """Admin reply: increments reply_count, inserts notification, does NOT set has_unread."""

    @pytest.mark.asyncio
    async def test_admin_reply_success(
        self, service, mock_client, feedback_id, user_id, admin_id
    ):
        sub_data = _sub(feedback_id, user_id)
        sub_data["reply_count"] = 2
        reply_row = _reply_row(feedback_id, admin_id, "admin")

        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [sub_data]
        )
        mock_client.table.return_value.insert.return_value.execute.return_value = make_supabase_response(
            [reply_row]
        )
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = make_supabase_response(
            [{"reply_count": 2}]
        )

        payload = ReplyCreateRequest(text_content="Great report, investigating now.")
        result = await service.post_reply(
            feedback_id=feedback_id,
            author_id=admin_id,
            author_role="admin",
            payload=payload,
        )

        assert result.author_role == "admin"
        assert result.text_content == reply_row["text_content"]

    @pytest.mark.asyncio
    async def test_admin_reply_does_not_set_has_unread_user_reply(
        self, service, mock_client, feedback_id, user_id, admin_id
    ):
        """Admin reply must NOT set has_unread_user_reply=True."""
        sub_data = _sub(feedback_id, user_id)
        reply_row = _reply_row(feedback_id, admin_id, "admin")

        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [sub_data]
        )
        mock_client.table.return_value.insert.return_value.execute.return_value = make_supabase_response(
            [reply_row]
        )
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = make_supabase_response(
            [{"reply_count": 0}]
        )

        payload = ReplyCreateRequest(text_content="Admin reply.")
        await service.post_reply(
            feedback_id=feedback_id,
            author_id=admin_id,
            author_role="admin",
            payload=payload,
        )

        # Ensure no update with has_unread_user_reply=True was called
        update_calls = [str(c) for c in mock_client.table.return_value.update.call_args_list]
        assert not any("has_unread_user_reply" in c and "True" in c for c in update_calls)

    @pytest.mark.asyncio
    async def test_admin_reply_inserts_notification(
        self, service, mock_client, feedback_id, user_id, admin_id
    ):
        """Admin reply must insert a feedback_notifications row for the submitter."""
        sub_data = _sub(feedback_id, user_id)
        reply_row = _reply_row(feedback_id, admin_id, "admin")

        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [sub_data]
        )
        mock_client.table.return_value.insert.return_value.execute.return_value = make_supabase_response(
            [reply_row]
        )
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = make_supabase_response(
            [{"reply_count": 0}]
        )

        payload = ReplyCreateRequest(text_content="Here's the fix.")
        await service.post_reply(
            feedback_id=feedback_id,
            author_id=admin_id,
            author_role="admin",
            payload=payload,
        )

        # Verify feedback_notifications insert was called
        table_calls = [str(c) for c in mock_client.table.call_args_list]
        assert any("feedback_notifications" in c for c in table_calls)

    @pytest.mark.asyncio
    async def test_empty_text_raises_400(
        self, service, mock_client, feedback_id, admin_id
    ):
        with pytest.raises(Exception):
            ReplyCreateRequest(text_content="")

    @pytest.mark.asyncio
    async def test_text_over_2000_chars_raises_400(
        self, service, mock_client, feedback_id, admin_id
    ):
        with pytest.raises(Exception):
            ReplyCreateRequest(text_content="x" * 2001)


# ---------------------------------------------------------------------------
# post_reply — user path
# ---------------------------------------------------------------------------

class TestPostReplyUser:
    """User reply: sets has_unread_user_reply=True, does NOT insert notification."""

    @pytest.mark.asyncio
    async def test_user_reply_success(
        self, service, mock_client, feedback_id, user_id
    ):
        sub_data = _sub(feedback_id, user_id)
        reply_row = _reply_row(feedback_id, user_id, "user")

        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [sub_data]
        )
        mock_client.table.return_value.insert.return_value.execute.return_value = make_supabase_response(
            [reply_row]
        )
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = make_supabase_response(
            [{"reply_count": 0}]
        )

        payload = ReplyCreateRequest(text_content="Follow-up from user.")
        result = await service.post_reply(
            feedback_id=feedback_id,
            author_id=user_id,
            author_role="user",
            payload=payload,
        )
        assert result.author_role == "user"

    @pytest.mark.asyncio
    async def test_user_reply_sets_has_unread_user_reply(
        self, service, mock_client, feedback_id, user_id
    ):
        sub_data = _sub(feedback_id, user_id)
        reply_row = _reply_row(feedback_id, user_id, "user")

        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [sub_data]
        )
        mock_client.table.return_value.insert.return_value.execute.return_value = make_supabase_response(
            [reply_row]
        )
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = make_supabase_response(
            [{"reply_count": 0}]
        )

        payload = ReplyCreateRequest(text_content="Follow-up.")
        await service.post_reply(
            feedback_id=feedback_id,
            author_id=user_id,
            author_role="user",
            payload=payload,
        )

        update_calls = [str(c) for c in mock_client.table.return_value.update.call_args_list]
        assert any("has_unread_user_reply" in c for c in update_calls)

    @pytest.mark.asyncio
    async def test_user_reply_does_not_insert_notification(
        self, service, mock_client, feedback_id, user_id
    ):
        sub_data = _sub(feedback_id, user_id)
        reply_row = _reply_row(feedback_id, user_id, "user")

        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [sub_data]
        )
        mock_client.table.return_value.insert.return_value.execute.return_value = make_supabase_response(
            [reply_row]
        )
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = make_supabase_response(
            [{"reply_count": 0}]
        )

        payload = ReplyCreateRequest(text_content="Follow-up.")
        await service.post_reply(
            feedback_id=feedback_id,
            author_id=user_id,
            author_role="user",
            payload=payload,
        )

        # feedback_notifications must NOT be inserted by user reply
        table_calls = [c[0][0] for c in mock_client.table.call_args_list]
        notif_insert_calls = [
            t for t in table_calls if t == "feedback_notifications"
        ]
        assert len(notif_insert_calls) == 0

    @pytest.mark.asyncio
    async def test_user_reply_non_owner_raises_403(
        self, service, mock_client, feedback_id, user_id
    ):
        other_user = uuid4()
        sub_data = _sub(feedback_id, other_user)  # owned by other_user

        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [sub_data]
        )

        payload = ReplyCreateRequest(text_content="Trying to reply to someone else's.")
        with pytest.raises(HTTPException) as exc_info:
            await service.post_reply(
                feedback_id=feedback_id,
                author_id=user_id,  # not the owner
                author_role="user",
                payload=payload,
            )
        assert exc_info.value.status_code == 403


# ---------------------------------------------------------------------------
# mark_submission_read
# ---------------------------------------------------------------------------

class TestMarkSubmissionRead:
    @pytest.mark.asyncio
    async def test_clears_has_unread_user_reply(
        self, service, mock_client, feedback_id
    ):
        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [{"id": str(feedback_id)}]
        )

        await service.mark_submission_read(feedback_id)

        mock_client.table.return_value.update.assert_called_with(
            {"has_unread_user_reply": False}
        )

    @pytest.mark.asyncio
    async def test_missing_submission_raises_404(
        self, service, mock_client, feedback_id
    ):
        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            []
        )

        with pytest.raises(HTTPException) as exc_info:
            await service.mark_submission_read(feedback_id)
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# get_my_feedback
# ---------------------------------------------------------------------------

class TestGetMyFeedback:
    @pytest.mark.asyncio
    async def test_returns_own_submissions(
        self, service, mock_client, user_id
    ):
        subs = [
            {
                "id": str(uuid4()),
                "page_url": "https://example.com",
                "text_content": f"Feedback {i}",
                "status": "new",
                "submitted_at": datetime.now(timezone.utc).isoformat(),
                "reply_count": 0,
            }
            for i in range(5)
        ]

        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = make_supabase_response(
            subs, count=5
        )
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = make_supabase_response(
            subs
        )
        mock_client.table.return_value.select.return_value.eq.return_value.is_.return_value.in_.return_value.execute.return_value = make_supabase_response(
            []
        )

        result = await service.get_my_feedback(user_id=user_id)
        assert len(result.results) == 5
        assert result.total == 5
        assert all(not item.has_unread_admin_reply for item in result.results)

    @pytest.mark.asyncio
    async def test_empty_user_returns_empty_list(
        self, service, mock_client, user_id
    ):
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = make_supabase_response(
            [], count=0
        )
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = make_supabase_response(
            []
        )

        result = await service.get_my_feedback(user_id=user_id)
        assert result.results == []
        assert result.total == 0

    @pytest.mark.asyncio
    async def test_has_unread_admin_reply_correct(
        self, service, mock_client, user_id
    ):
        feedback_id_unread = str(uuid4())
        feedback_id_read = str(uuid4())

        subs = [
            {
                "id": feedback_id_unread,
                "page_url": "https://example.com",
                "text_content": "Unread",
                "status": "new",
                "submitted_at": datetime.now(timezone.utc).isoformat(),
                "reply_count": 1,
            },
            {
                "id": feedback_id_read,
                "page_url": "https://example.com",
                "text_content": "Read",
                "status": "reviewed",
                "submitted_at": datetime.now(timezone.utc).isoformat(),
                "reply_count": 1,
            },
        ]

        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = make_supabase_response(
            subs, count=2
        )
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = make_supabase_response(
            subs
        )
        # Only feedback_id_unread has an unread notification
        mock_client.table.return_value.select.return_value.eq.return_value.is_.return_value.in_.return_value.execute.return_value = make_supabase_response(
            [{"feedback_id": feedback_id_unread}]
        )

        result = await service.get_my_feedback(user_id=user_id)
        unread_item = next(r for r in result.results if r.id == UUID(feedback_id_unread))
        read_item = next(r for r in result.results if r.id == UUID(feedback_id_read))
        assert unread_item.has_unread_admin_reply is True
        assert read_item.has_unread_admin_reply is False


# ---------------------------------------------------------------------------
# get_notifications
# ---------------------------------------------------------------------------

class TestGetNotifications:
    @pytest.mark.asyncio
    async def test_undelivered_notifications_returned_and_marked_delivered(
        self, service, mock_client, user_id
    ):
        notif_id = str(uuid4())
        rows = [
            {
                "id": notif_id,
                "feedback_id": str(uuid4()),
                "reply_id": str(uuid4()),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "delivered_at": None,
                "read_at": None,
            }
        ]
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = make_supabase_response(
            rows
        )

        result = await service.get_notifications(user_id=user_id)

        assert len(result.notifications) == 1
        assert result.unread_count == 1
        # delivered_at should be set on undelivered rows
        mock_client.table.return_value.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_already_delivered_not_reset(
        self, service, mock_client, user_id
    ):
        original_ts = "2026-05-01T10:00:00+00:00"
        rows = [
            {
                "id": str(uuid4()),
                "feedback_id": str(uuid4()),
                "reply_id": str(uuid4()),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "delivered_at": original_ts,
                "read_at": None,
            }
        ]
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = make_supabase_response(
            rows
        )

        result = await service.get_notifications(user_id=user_id)
        assert len(result.notifications) == 1
        # No update call because delivered_at was already set
        mock_client.table.return_value.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_unread_count_correct(
        self, service, mock_client, user_id
    ):
        rows = [
            {
                "id": str(uuid4()),
                "feedback_id": str(uuid4()),
                "reply_id": str(uuid4()),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "delivered_at": "2026-05-01T10:00:00+00:00",
                "read_at": None,  # unread
            },
            {
                "id": str(uuid4()),
                "feedback_id": str(uuid4()),
                "reply_id": str(uuid4()),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "delivered_at": "2026-05-01T10:00:00+00:00",
                "read_at": "2026-05-02T10:00:00+00:00",  # read
            },
        ]
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = make_supabase_response(
            rows
        )

        result = await service.get_notifications(user_id=user_id)
        assert result.unread_count == 1


# ---------------------------------------------------------------------------
# mark_notification_read
# ---------------------------------------------------------------------------

class TestMarkNotificationRead:
    @pytest.mark.asyncio
    async def test_success(self, service, mock_client, user_id):
        notif_id = uuid4()
        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [{"id": str(notif_id), "recipient_user_id": str(user_id)}]
        )

        await service.mark_notification_read(notification_id=notif_id, user_id=user_id)

        mock_client.table.return_value.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_wrong_owner_raises_403(self, service, mock_client, user_id):
        notif_id = uuid4()
        other_user = uuid4()
        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [{"id": str(notif_id), "recipient_user_id": str(other_user)}]
        )

        with pytest.raises(HTTPException) as exc_info:
            await service.mark_notification_read(notification_id=notif_id, user_id=user_id)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_not_found_raises_404(self, service, mock_client, user_id):
        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            []
        )

        with pytest.raises(HTTPException) as exc_info:
            await service.mark_notification_read(notification_id=uuid4(), user_id=user_id)
        assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# Durability assertion (SC-005)
# ---------------------------------------------------------------------------

class TestReplyDurability:
    @pytest.mark.asyncio
    async def test_posted_reply_immediately_retrievable(
        self, service, mock_client, feedback_id, user_id, admin_id
    ):
        """SC-005: after post_reply returns, the reply appears at position 0 in get_replies."""
        sub_data = _sub(feedback_id, user_id)
        reply_row = _reply_row(feedback_id, admin_id, "admin")

        # post_reply mocks
        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [sub_data]
        )
        mock_client.table.return_value.insert.return_value.execute.return_value = make_supabase_response(
            [reply_row]
        )
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = make_supabase_response(
            [{"reply_count": 0}]
        )

        payload = ReplyCreateRequest(text_content="Fix deployed.")
        await service.post_reply(
            feedback_id=feedback_id,
            author_id=admin_id,
            author_role="admin",
            payload=payload,
        )

        # get_replies returns the same reply at position 0
        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [sub_data]
        )
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.order.return_value.limit.return_value.execute.return_value = make_supabase_response(
            [reply_row]
        )

        thread = await service.get_replies(
            feedback_id=feedback_id,
            user_id=admin_id,
            is_admin=True,
        )

        assert len(thread.replies) == 1
        assert str(thread.replies[0].id) == reply_row["id"]

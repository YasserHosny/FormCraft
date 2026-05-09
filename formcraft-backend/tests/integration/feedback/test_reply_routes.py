"""Integration tests for feedback threading & notification routes (Feature 014)."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import make_supabase_response


@pytest.fixture
def client():
    return TestClient(app)


ADMIN_ID = UUID("11111111-1111-1111-1111-111111111111")
USER_ID = UUID("33333333-3333-3333-3333-333333333333")

ADMIN_FEEDBACK_ID = uuid4()
USER_FEEDBACK_ID = uuid4()


def _sub(feedback_id: UUID, user_id: UUID):
    return {
        "id": str(feedback_id),
        "user_id": str(user_id),
        "reply_count": 0,
        "has_unread_user_reply": False,
    }


def _reply_row():
    return {
        "id": str(uuid4()),
        "author_id": str(ADMIN_ID),
        "author_role": "admin",
        "text_content": "We've looked into this.",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "profiles": {"display_name": "Test Admin"},
    }


def _notif_row(feedback_id: UUID, user_id: UUID):
    return {
        "id": str(uuid4()),
        "feedback_id": str(feedback_id),
        "reply_id": str(uuid4()),
        "recipient_user_id": str(user_id),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "delivered_at": None,
        "read_at": None,
    }


def _profile_mock(mock_client, profile: dict):
    mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = make_supabase_response(
        profile
    )


# ---------------------------------------------------------------------------
# GET /api/admin/feedback/{id}/replies
# ---------------------------------------------------------------------------

class TestAdminGetReplies:
    def test_admin_gets_replies_200(
        self, client, valid_admin_token, admin_profile
    ):
        mock = MagicMock()
        _profile_mock(mock, admin_profile)

        feedback_id = uuid4()
        sub = _sub(feedback_id, USER_ID)
        rows = [_reply_row()]

        mock.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [sub]
        )
        mock.table.return_value.select.return_value.eq.return_value.order.return_value.order.return_value.limit.return_value.execute.return_value = make_supabase_response(
            rows
        )

        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock),
            patch("app.api.deps.get_supabase_client", return_value=mock),
        ):
            resp = client.get(
                f"/api/admin/feedback/{feedback_id}/replies",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "replies" in data
        assert "has_earlier" in data

    def test_non_admin_gets_403(
        self, client, valid_viewer_token, viewer_profile
    ):
        mock = MagicMock()
        _profile_mock(mock, viewer_profile)

        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock),
            patch("app.api.deps.get_supabase_client", return_value=mock),
        ):
            resp = client.get(
                f"/api/admin/feedback/{uuid4()}/replies",
                headers={"Authorization": f"Bearer {valid_viewer_token}"},
            )
        assert resp.status_code == 403

    def test_bad_id_gets_404(
        self, client, valid_admin_token, admin_profile
    ):
        mock = MagicMock()
        _profile_mock(mock, admin_profile)

        mock.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            []
        )

        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock),
            patch("app.api.deps.get_supabase_client", return_value=mock),
        ):
            resp = client.get(
                f"/api/admin/feedback/{uuid4()}/replies",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/admin/feedback/{id}/replies
# ---------------------------------------------------------------------------

class TestAdminPostReply:
    def test_admin_posts_reply_201(
        self, client, valid_admin_token, admin_profile
    ):
        mock = MagicMock()
        _profile_mock(mock, admin_profile)

        feedback_id = uuid4()
        sub = _sub(feedback_id, USER_ID)
        row = _reply_row()

        mock.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [sub]
        )
        mock.table.return_value.insert.return_value.execute.return_value = make_supabase_response(
            [row]
        )
        mock.table.return_value.select.return_value.eq.return_value.execute.return_value = make_supabase_response(
            [{"reply_count": 0}]
        )

        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock),
            patch("app.api.deps.get_supabase_client", return_value=mock),
        ):
            resp = client.post(
                f"/api/admin/feedback/{feedback_id}/replies",
                json={"text_content": "We're investigating."},
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert resp.status_code == 201
        assert resp.json()["author_role"] == "admin"

    def test_non_admin_gets_403(
        self, client, valid_viewer_token, viewer_profile
    ):
        mock = MagicMock()
        _profile_mock(mock, viewer_profile)

        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock),
            patch("app.api.deps.get_supabase_client", return_value=mock),
        ):
            resp = client.post(
                f"/api/admin/feedback/{uuid4()}/replies",
                json={"text_content": "reply"},
                headers={"Authorization": f"Bearer {valid_viewer_token}"},
            )
        assert resp.status_code == 403

    def test_bad_id_gets_404(
        self, client, valid_admin_token, admin_profile
    ):
        mock = MagicMock()
        _profile_mock(mock, admin_profile)

        mock.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            []
        )

        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock),
            patch("app.api.deps.get_supabase_client", return_value=mock),
        ):
            resp = client.post(
                f"/api/admin/feedback/{uuid4()}/replies",
                json={"text_content": "reply"},
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert resp.status_code == 404

    def test_empty_text_gets_400(
        self, client, valid_admin_token, admin_profile
    ):
        mock = MagicMock()
        _profile_mock(mock, admin_profile)

        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock),
            patch("app.api.deps.get_supabase_client", return_value=mock),
        ):
            resp = client.post(
                f"/api/admin/feedback/{uuid4()}/replies",
                json={"text_content": ""},
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert resp.status_code == 422  # Pydantic validation


# ---------------------------------------------------------------------------
# PATCH /api/admin/feedback/{id}/read
# ---------------------------------------------------------------------------

class TestAdminMarkRead:
    def test_admin_marks_read_204(
        self, client, valid_admin_token, admin_profile
    ):
        mock = MagicMock()
        _profile_mock(mock, admin_profile)

        feedback_id = uuid4()
        mock.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [{"id": str(feedback_id)}]
        )

        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock),
            patch("app.api.deps.get_supabase_client", return_value=mock),
        ):
            resp = client.patch(
                f"/api/admin/feedback/{feedback_id}/read",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert resp.status_code == 204

    def test_non_admin_gets_403(
        self, client, valid_viewer_token, viewer_profile
    ):
        mock = MagicMock()
        _profile_mock(mock, viewer_profile)

        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock),
            patch("app.api.deps.get_supabase_client", return_value=mock),
        ):
            resp = client.patch(
                f"/api/admin/feedback/{uuid4()}/read",
                headers={"Authorization": f"Bearer {valid_viewer_token}"},
            )
        assert resp.status_code == 403

    def test_bad_id_gets_404(
        self, client, valid_admin_token, admin_profile
    ):
        mock = MagicMock()
        _profile_mock(mock, admin_profile)

        mock.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            []
        )

        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock),
            patch("app.api.deps.get_supabase_client", return_value=mock),
        ):
            resp = client.patch(
                f"/api/admin/feedback/{uuid4()}/read",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/my-feedback
# ---------------------------------------------------------------------------

class TestMyFeedback:
    def test_own_submissions_200(
        self, client, valid_viewer_token, viewer_profile
    ):
        mock = MagicMock()
        _profile_mock(mock, viewer_profile)

        subs = [
            {
                "id": str(uuid4()),
                "page_url": "https://example.com",
                "text_content": "Feedback",
                "status": "new",
                "submitted_at": datetime.now(timezone.utc).isoformat(),
                "reply_count": 0,
            }
        ]
        mock.table.return_value.select.return_value.eq.return_value.execute.return_value = make_supabase_response(
            subs, count=1
        )
        mock.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = make_supabase_response(
            subs
        )
        mock.table.return_value.select.return_value.eq.return_value.is_.return_value.in_.return_value.execute.return_value = make_supabase_response(
            []
        )

        with (
            patch("app.api.routes.feedback.get_supabase_client", return_value=mock),
            patch("app.api.deps.get_supabase_client", return_value=mock),
        ):
            resp = client.get(
                "/api/my-feedback",
                headers={"Authorization": f"Bearer {valid_viewer_token}"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        assert data["total"] == 1

    def test_unauthenticated_gets_401(self, client):
        resp = client.get("/api/my-feedback")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /api/feedback/{id}/replies  (user path)
# ---------------------------------------------------------------------------

class TestUserGetReplies:
    def test_own_submission_200(
        self, client, valid_viewer_token, viewer_profile
    ):
        mock = MagicMock()
        _profile_mock(mock, viewer_profile)

        feedback_id = uuid4()
        sub = _sub(feedback_id, USER_ID)

        mock.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [sub]
        )
        mock.table.return_value.select.return_value.eq.return_value.order.return_value.order.return_value.limit.return_value.execute.return_value = make_supabase_response(
            []
        )

        with (
            patch("app.api.routes.feedback.get_supabase_client", return_value=mock),
            patch("app.api.deps.get_supabase_client", return_value=mock),
        ):
            resp = client.get(
                f"/api/feedback/{feedback_id}/replies",
                headers={"Authorization": f"Bearer {valid_viewer_token}"},
            )
        assert resp.status_code == 200

    def test_non_owner_gets_403(
        self, client, valid_admin_token, admin_profile
    ):
        mock = MagicMock()
        _profile_mock(mock, admin_profile)

        feedback_id = uuid4()
        # owned by a different user (viewer, not admin)
        sub = _sub(feedback_id, USER_ID)

        mock.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [sub]
        )

        with (
            patch("app.api.routes.feedback.get_supabase_client", return_value=mock),
            patch("app.api.deps.get_supabase_client", return_value=mock),
        ):
            resp = client.get(
                f"/api/feedback/{feedback_id}/replies",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert resp.status_code == 403

    def test_bad_id_gets_404(
        self, client, valid_viewer_token, viewer_profile
    ):
        mock = MagicMock()
        _profile_mock(mock, viewer_profile)

        mock.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            []
        )

        with (
            patch("app.api.routes.feedback.get_supabase_client", return_value=mock),
            patch("app.api.deps.get_supabase_client", return_value=mock),
        ):
            resp = client.get(
                f"/api/feedback/{uuid4()}/replies",
                headers={"Authorization": f"Bearer {valid_viewer_token}"},
            )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/feedback/{id}/replies  (user path)
# ---------------------------------------------------------------------------

class TestUserPostReply:
    def test_own_submission_201(
        self, client, valid_viewer_token, viewer_profile
    ):
        mock = MagicMock()
        _profile_mock(mock, viewer_profile)

        feedback_id = uuid4()
        sub = _sub(feedback_id, USER_ID)
        row = {
            "id": str(uuid4()),
            "author_role": "user",
            "text_content": "Follow up question.",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "profiles": {"display_name": "Test Viewer"},
        }

        mock.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [sub]
        )
        mock.table.return_value.insert.return_value.execute.return_value = make_supabase_response(
            [row]
        )
        mock.table.return_value.select.return_value.eq.return_value.execute.return_value = make_supabase_response(
            [{"reply_count": 0}]
        )

        with (
            patch("app.api.routes.feedback.get_supabase_client", return_value=mock),
            patch("app.api.deps.get_supabase_client", return_value=mock),
        ):
            resp = client.post(
                f"/api/feedback/{feedback_id}/replies",
                json={"text_content": "Follow up question."},
                headers={"Authorization": f"Bearer {valid_viewer_token}"},
            )
        assert resp.status_code == 201

    def test_empty_text_gets_422(
        self, client, valid_viewer_token, viewer_profile
    ):
        mock = MagicMock()
        _profile_mock(mock, viewer_profile)

        with (
            patch("app.api.routes.feedback.get_supabase_client", return_value=mock),
            patch("app.api.deps.get_supabase_client", return_value=mock),
        ):
            resp = client.post(
                f"/api/feedback/{uuid4()}/replies",
                json={"text_content": ""},
                headers={"Authorization": f"Bearer {valid_viewer_token}"},
            )
        assert resp.status_code == 422

    def test_unauthenticated_gets_401(self, client):
        resp = client.post(
            f"/api/feedback/{uuid4()}/replies",
            json={"text_content": "hello"},
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# GET /api/notifications
# ---------------------------------------------------------------------------

class TestGetNotifications:
    def test_own_notifications_200(
        self, client, valid_viewer_token, viewer_profile
    ):
        mock = MagicMock()
        _profile_mock(mock, viewer_profile)

        notif = _notif_row(uuid4(), USER_ID)
        mock.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = make_supabase_response(
            [notif]
        )

        with (
            patch("app.api.routes.feedback.get_supabase_client", return_value=mock),
            patch("app.api.deps.get_supabase_client", return_value=mock),
        ):
            resp = client.get(
                "/api/notifications",
                headers={"Authorization": f"Bearer {valid_viewer_token}"},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "notifications" in data
        assert "unread_count" in data

    def test_unauthenticated_gets_401(self, client):
        resp = client.get("/api/notifications")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# PATCH /api/notifications/{id}/read
# ---------------------------------------------------------------------------

class TestMarkNotificationRead:
    def test_own_notification_204(
        self, client, valid_viewer_token, viewer_profile
    ):
        mock = MagicMock()
        _profile_mock(mock, viewer_profile)

        notif_id = uuid4()
        mock.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [{"id": str(notif_id), "recipient_user_id": str(USER_ID)}]
        )

        with (
            patch("app.api.routes.feedback.get_supabase_client", return_value=mock),
            patch("app.api.deps.get_supabase_client", return_value=mock),
        ):
            resp = client.patch(
                f"/api/notifications/{notif_id}/read",
                headers={"Authorization": f"Bearer {valid_viewer_token}"},
            )
        assert resp.status_code == 204

    def test_wrong_owner_gets_403(
        self, client, valid_admin_token, admin_profile
    ):
        mock = MagicMock()
        _profile_mock(mock, admin_profile)

        notif_id = uuid4()
        # notification belongs to USER_ID, not ADMIN_ID
        mock.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = make_supabase_response(
            [{"id": str(notif_id), "recipient_user_id": str(USER_ID)}]
        )

        with (
            patch("app.api.routes.feedback.get_supabase_client", return_value=mock),
            patch("app.api.deps.get_supabase_client", return_value=mock),
        ):
            resp = client.patch(
                f"/api/notifications/{notif_id}/read",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert resp.status_code == 403

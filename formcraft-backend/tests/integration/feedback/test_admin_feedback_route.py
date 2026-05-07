"""Integration tests for admin feedback routes (GET/PATCH /api/admin/feedback)."""

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


def _setup_profile_mock(mock_client, profile):
    profile_response = make_supabase_response(profile)
    mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = profile_response


def _make_feedback_item(feedback_id=None, user_id=None):
    return {
        "id": str(feedback_id or uuid4()),
        "user_id": str(user_id or UUID("22222222-2222-2222-2222-222222222222")),
        "page_url": "https://example.com/page",
        "text_content": "Some feedback text",
        "image_url": None,
        "image_signed_url": None,
        "audio_url": None,
        "audio_signed_url": None,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "status": "new",
        "submitter_display_name": "Test Designer",
    }


class TestListFeedback:
    def test_list_feedback_200_admin(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)

        list_response = make_supabase_response([], count=0)
        # Use a flexible query mock that supports chained calls
        query_chain = MagicMock()
        query_chain.eq.return_value = query_chain
        query_chain.gte.return_value = query_chain
        query_chain.lte.return_value = query_chain
        query_chain.range.return_value = query_chain
        query_chain.order.return_value = query_chain
        query_chain.execute.return_value = list_response

        # Override only the feedback_submissions table query
        # The profiles table is already mocked by _setup_profile_mock
        original_table = mock_client.table

        def table_side_effect(name):
            if name == "profiles":
                return original_table.return_value
            # For feedback_submissions, return the flexible chain
            mock_query = MagicMock()
            mock_query.select.return_value = query_chain
            return mock_query

        mock_client.table.side_effect = table_side_effect
        mock_client.storage.from_.return_value.create_signed_url.return_value = (
            "https://signed.url"
        )

        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.get(
                "/api/admin/feedback",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert response.status_code == 200
        body = response.json()
        assert "data" in body
        assert "total" in body

    def test_list_feedback_403_non_admin(
        self, client, valid_viewer_token, viewer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, viewer_profile)

        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.get(
                "/api/admin/feedback",
                headers={"Authorization": f"Bearer {valid_viewer_token}"},
            )
        assert response.status_code == 403


class TestUpdateFeedbackStatus:
    def test_update_status_200(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)

        feedback_id = str(uuid4())
        updated_at = datetime.now(timezone.utc).isoformat()
        update_response = make_supabase_response(
            [{"id": feedback_id, "status": "reviewed", "submitted_at": updated_at}]
        )
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = update_response

        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.patch(
                f"/api/admin/feedback/{feedback_id}",
                json={"status": "reviewed"},
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "reviewed"

    def test_update_status_400_invalid_status(
        self, client, valid_admin_token, admin_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)

        feedback_id = str(uuid4())

        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.patch(
                f"/api/admin/feedback/{feedback_id}",
                json={"status": "invalid_status"},
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert response.status_code == 422

    def test_update_status_404_not_found(
        self, client, valid_admin_token, admin_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)

        feedback_id = str(uuid4())
        update_response = make_supabase_response([])
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = update_response

        with (
            patch("app.api.routes.admin.get_supabase_client", return_value=mock_client),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.patch(
                f"/api/admin/feedback/{feedback_id}",
                json={"status": "resolved"},
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert response.status_code == 404

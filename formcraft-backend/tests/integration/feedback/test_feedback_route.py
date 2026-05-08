"""Integration tests for the feedback submission route (POST /api/feedback)."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.feedback.service import (
    IMAGE_MAX_SIZE,
    AUDIO_MAX_SIZE,
)
from tests.conftest import make_supabase_response


@pytest.fixture
def client():
    return TestClient(app)


def _setup_profile_mock(mock_client, profile):
    profile_response = make_supabase_response(profile)
    mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = profile_response


class TestSubmitFeedback:
    def test_submit_feedback_201_valid(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)

        cooldown_response = make_supabase_response([], count=0)
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = cooldown_response

        new_id = str(uuid4())
        submitted_at = datetime.now(timezone.utc).isoformat()
        insert_response = make_supabase_response(
            [{"id": new_id, "submitted_at": submitted_at, "status": "new"}]
        )
        mock_client.table.return_value.insert.return_value.execute.return_value = (
            insert_response
        )

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client", return_value=mock_client
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.post(
                "/api/feedback",
                json={
                    "page_url": "https://example.com/page",
                    "text_content": "Looks good!",
                    "image_url": None,
                    "audio_url": None,
                },
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 201
        body = response.json()
        assert body["id"] == new_id
        assert body["status"] == "new"

    def test_submit_feedback_429_cooldown_active(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)

        recent = datetime.now(timezone.utc).isoformat()
        cooldown_response = make_supabase_response([{"submitted_at": recent}], count=1)
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = cooldown_response

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client", return_value=mock_client
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.post(
                "/api/feedback",
                json={
                    "page_url": "https://example.com/page",
                    "text_content": "Duplicate feedback",
                },
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 429

    def test_submit_feedback_400_empty_text(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client", return_value=mock_client
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.post(
                "/api/feedback",
                json={
                    "page_url": "https://example.com/page",
                    "text_content": "",
                },
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 422

    def test_submit_feedback_401_unauthenticated(self, client):
        response = client.post(
            "/api/feedback",
            json={
                "page_url": "https://example.com/page",
                "text_content": "Anonymous feedback",
            },
        )
        assert response.status_code == 401


class TestImageUpload:
    def test_upload_image_200_valid(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)

        mock_client.storage.from_.return_value.upload.return_value = None
        mock_client.storage.from_.return_value.get_public_url.return_value = (
            "https://storage.example.com/feedback/image.jpg"
        )

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client", return_value=mock_client
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.post(
                "/api/feedback/upload/image",
                files={"file": ("test.jpg", b"fake-image-data", "image/jpeg")},
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 200
        body = response.json()
        assert "storage_path" in body
        assert body["storage_path"].startswith(f"feedback/{designer_profile['id']}/")

    def test_upload_image_413_oversized(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)

        big_content = b"x" * (IMAGE_MAX_SIZE + 1)

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client", return_value=mock_client
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.post(
                "/api/feedback/upload/image",
                files={"file": ("big.jpg", big_content, "image/jpeg")},
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 413

    def test_upload_image_400_bad_mime(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client", return_value=mock_client
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.post(
                "/api/feedback/upload/image",
                files={"file": ("doc.pdf", b"fake-pdf-data", "application/pdf")},
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 400

    def test_upload_image_401_unauthenticated(self, client):
        response = client.post(
            "/api/feedback/upload/image",
            files={"file": ("test.jpg", b"fake-image-data", "image/jpeg")},
        )
        assert response.status_code == 401

    def test_delete_upload_204_own_file(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)

        mock_client.storage.from_.return_value.remove.return_value = None
        storage_path = f"feedback/{designer_profile['id']}/some-file.jpg"

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client", return_value=mock_client
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.request(
                "DELETE",
                "/api/feedback/upload",
                json={"storage_path": storage_path},
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 204

    def test_delete_upload_403_foreign_path(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)

        other_user_id = "33333333-3333-3333-3333-333333333333"
        storage_path = f"feedback/{other_user_id}/some-file.jpg"

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client", return_value=mock_client
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.request(
                "DELETE",
                "/api/feedback/upload",
                json={"storage_path": storage_path},
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 403


class TestAudioUpload:
    def test_upload_audio_200_valid_mp3(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)

        mock_client.storage.from_.return_value.upload.return_value = None
        mock_client.storage.from_.return_value.get_public_url.return_value = (
            "https://storage.example.com/feedback/audio.mp3"
        )

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client", return_value=mock_client
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.post(
                "/api/feedback/upload/audio",
                files={"file": ("test.mp3", b"fake-mp3-data", "audio/mpeg")},
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 200
        body = response.json()
        assert "storage_path" in body
        assert body["storage_path"].startswith(f"feedback/{designer_profile['id']}/")

    def test_upload_audio_200_valid_webm(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)

        mock_client.storage.from_.return_value.upload.return_value = None
        mock_client.storage.from_.return_value.get_public_url.return_value = (
            "https://storage.example.com/feedback/audio.webm"
        )

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client", return_value=mock_client
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.post(
                "/api/feedback/upload/audio",
                files={"file": ("test.webm", b"fake-webm-data", "audio/webm")},
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 200
        body = response.json()
        assert "storage_path" in body
        assert body["storage_path"].startswith(f"feedback/{designer_profile['id']}/")

    def test_upload_audio_413_oversized(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)

        big_content = b"x" * (AUDIO_MAX_SIZE + 1)

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client", return_value=mock_client
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.post(
                "/api/feedback/upload/audio",
                files={"file": ("big.mp3", big_content, "audio/mpeg")},
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 413

    def test_upload_audio_400_bad_mime(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client", return_value=mock_client
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.post(
                "/api/feedback/upload/audio",
                files={"file": ("test.mp4", b"fake-video-data", "video/mp4")},
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 400

    def test_upload_audio_401_unauthenticated(self, client):
        response = client.post(
            "/api/feedback/upload/audio",
            files={"file": ("test.mp3", b"fake-mp3-data", "audio/mpeg")},
        )
        assert response.status_code == 401

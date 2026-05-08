"""Integration tests for rich media upload and feedback routes."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.feedback.service import IMAGE_MAX_SIZE, VIDEO_MAX_SIZE
from tests.conftest import make_supabase_response


@pytest.fixture
def client():
    return TestClient(app)


def _setup_profile_mock(mock_client, profile):
    profile_response = make_supabase_response(profile)
    mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = profile_response


class TestUploadImageRoute:
    def test_upload_image_200(self, client, valid_designer_token, designer_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)
        mock_client.storage.from_.return_value.upload.return_value = None

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client",
                return_value=mock_client,
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

    def test_upload_image_400_bad_mime(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client",
                return_value=mock_client,
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.post(
                "/api/feedback/upload/image",
                files={"file": ("doc.pdf", b"fake-pdf-data", "application/pdf")},
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 400

    def test_upload_image_413_oversize(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)

        big_content = b"x" * (IMAGE_MAX_SIZE + 1)

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client",
                return_value=mock_client,
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.post(
                "/api/feedback/upload/image",
                files={"file": ("big.jpg", big_content, "image/jpeg")},
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 413

    def test_upload_image_401_unauthenticated(self, client):
        response = client.post(
            "/api/feedback/upload/image",
            files={"file": ("test.jpg", b"fake-image-data", "image/jpeg")},
        )
        assert response.status_code == 401


class TestDeleteUploadImageRoute:
    def test_delete_upload_image_204(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)
        mock_client.storage.from_.return_value.remove.return_value = None
        storage_path = f"feedback/{designer_profile['id']}/image.jpg"

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client",
                return_value=mock_client,
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.request(
                "DELETE",
                "/api/feedback/upload/image",
                json={"storage_path": storage_path},
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 204

    def test_delete_upload_image_403_wrong_owner(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)
        other_user_id = "33333333-3333-3333-3333-333333333333"
        storage_path = f"feedback/{other_user_id}/image.jpg"

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client",
                return_value=mock_client,
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.request(
                "DELETE",
                "/api/feedback/upload/image",
                json={"storage_path": storage_path},
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 403

    def test_delete_upload_image_404_not_found(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)
        mock_client.storage.from_.return_value.remove.side_effect = Exception(
            "Not found"
        )
        storage_path = f"feedback/{designer_profile['id']}/missing.jpg"

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client",
                return_value=mock_client,
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.request(
                "DELETE",
                "/api/feedback/upload/image",
                json={"storage_path": storage_path},
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 404


class TestUploadVideoRoute:
    def test_upload_video_200(self, client, valid_designer_token, designer_profile):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)
        mock_client.storage.from_.return_value.upload.return_value = None

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client",
                return_value=mock_client,
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.post(
                "/api/feedback/upload/video",
                files={"file": ("test.mp4", b"fake-mp4-data", "video/mp4")},
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 200
        body = response.json()
        assert "storage_path" in body

    def test_upload_video_400_bad_mime(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client",
                return_value=mock_client,
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.post(
                "/api/feedback/upload/video",
                files={"file": ("test.avi", b"fake-avi-data", "video/x-msvideo")},
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 400

    def test_upload_video_413_oversize(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)

        big_content = b"x" * (VIDEO_MAX_SIZE + 1)

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client",
                return_value=mock_client,
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.post(
                "/api/feedback/upload/video",
                files={"file": ("big.mp4", big_content, "video/mp4")},
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 413

    def test_upload_video_401_unauthenticated(self, client):
        response = client.post(
            "/api/feedback/upload/video",
            files={"file": ("test.mp4", b"fake-mp4-data", "video/mp4")},
        )
        assert response.status_code == 401


class TestDeleteUploadVideoRoute:
    def test_delete_upload_video_204(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)
        mock_client.storage.from_.return_value.remove.return_value = None
        storage_path = f"feedback/{designer_profile['id']}/video.mp4"

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client",
                return_value=mock_client,
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.request(
                "DELETE",
                "/api/feedback/upload/video",
                json={"storage_path": storage_path},
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 204

    def test_delete_upload_video_403_wrong_owner(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)
        other_user_id = "33333333-3333-3333-3333-333333333333"
        storage_path = f"feedback/{other_user_id}/video.mp4"

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client",
                return_value=mock_client,
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.request(
                "DELETE",
                "/api/feedback/upload/video",
                json={"storage_path": storage_path},
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 403


class TestSubmitFeedbackWithImagesRoute:
    def test_submit_feedback_with_images_201(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)

        cooldown_response = make_supabase_response([], count=0)
        select_chain = MagicMock()
        select_chain.eq.return_value.order.return_value.limit.return_value.execute.return_value = cooldown_response

        feedback_id = str(uuid4())
        submitted_at = datetime.now(timezone.utc).isoformat()
        image_ids = [str(uuid4()), str(uuid4())]

        original_table = mock_client.table

        def table_side_effect(name):
            if name == "profiles":
                return original_table.return_value
            tbl = MagicMock()
            if name == "feedback_submissions":
                tbl.select.return_value = select_chain
                tbl.insert.return_value.execute.return_value = make_supabase_response(
                    [
                        {
                            "id": feedback_id,
                            "submitted_at": submitted_at,
                            "status": "new",
                        }
                    ]
                )
            elif name == "feedback_images":
                tbl.insert.return_value.execute.return_value = make_supabase_response(
                    [
                        {
                            "id": image_ids[i],
                            "storage_path": f"feedback/{designer_profile['id']}/img{i + 1}.jpg",
                            "display_order": i,
                        }
                        for i in range(2)
                    ]
                )
            return tbl

        mock_client.table.side_effect = table_side_effect

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client",
                return_value=mock_client,
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.post(
                "/api/feedback",
                json={
                    "page_url": "https://example.com/page",
                    "text_content": "Test with images",
                    "image_paths": [
                        f"feedback/{designer_profile['id']}/img1.jpg",
                        f"feedback/{designer_profile['id']}/img2.jpg",
                    ],
                },
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 201
        body = response.json()
        assert len(body["images"]) == 2

    def test_submit_feedback_too_many_images_400(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client",
                return_value=mock_client,
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.post(
                "/api/feedback",
                json={
                    "page_url": "https://example.com/page",
                    "text_content": "Test with images",
                    "image_paths": [
                        f"feedback/{designer_profile['id']}/img{i}.jpg"
                        for i in range(6)
                    ],
                },
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 422

    def test_submit_feedback_audio_and_video_422(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, designer_profile)

        with (
            patch(
                "app.api.routes.feedback.get_supabase_client",
                return_value=mock_client,
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.post(
                "/api/feedback",
                json={
                    "page_url": "https://example.com/page",
                    "text_content": "Test with audio and video",
                    "audio_url": "feedback/audio.mp3",
                    "video_url": "feedback/video.mp4",
                },
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 422


class TestListFeedbackAdminRoute:
    def test_list_feedback_admin_200_with_images(
        self, client, valid_admin_token, admin_profile
    ):
        mock_client = MagicMock()
        _setup_profile_mock(mock_client, admin_profile)

        feedback_id = str(uuid4())
        user_id_str = str(uuid4())
        img_id = str(uuid4())

        list_response = make_supabase_response(
            [
                {
                    "id": feedback_id,
                    "user_id": user_id_str,
                    "page_url": "https://example.com",
                    "text_content": "Admin test",
                    "audio_url": None,
                    "video_url": "feedback/video.mp4",
                    "submitted_at": datetime.now(timezone.utc).isoformat(),
                    "status": "new",
                    "profiles": {
                        "display_name": "Test User",
                        "email": "test@example.com",
                    },
                    "feedback_submission_labels": [],
                }
            ],
            count=1,
        )

        query_chain = MagicMock()
        query_chain.eq.return_value = query_chain
        query_chain.gte.return_value = query_chain
        query_chain.lte.return_value = query_chain
        query_chain.ilike.return_value = query_chain
        query_chain.range.return_value = query_chain
        query_chain.order.return_value = query_chain
        query_chain.execute.return_value = list_response

        original_table = mock_client.table

        def table_side_effect(name):
            if name == "profiles":
                return original_table.return_value
            if name == "feedback_submissions":
                mock_query = MagicMock()
                mock_query.select.return_value = query_chain
                return mock_query
            if name == "feedback_images":
                images_chain = MagicMock()
                images_chain.eq.return_value = images_chain
                images_chain.order.return_value = images_chain
                images_chain.execute.return_value = MagicMock(
                    data=[
                        {
                            "id": img_id,
                            "storage_path": f"feedback/{user_id_str}/img1.jpg",
                            "display_order": 0,
                        }
                    ]
                )
                mock_query = MagicMock()
                mock_query.select.return_value = images_chain
                return mock_query
            return MagicMock()

        mock_client.table.side_effect = table_side_effect
        mock_client.storage.from_.return_value.create_signed_url.return_value = (
            "https://signed.example.com/url"
        )

        with (
            patch(
                "app.api.routes.admin.get_supabase_client",
                return_value=mock_client,
            ),
            patch("app.api.deps.get_supabase_client", return_value=mock_client),
        ):
            response = client.get(
                "/api/admin/feedback",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        assert response.status_code == 200
        body = response.json()
        assert len(body["data"]) == 1
        item = body["data"][0]
        assert len(item["images"]) == 1
        assert item["images"][0]["storage_url"] == "https://signed.example.com/url"
        assert item["video_url"] == "feedback/video.mp4"
        assert item["video_signed_url"] == "https://signed.example.com/url"

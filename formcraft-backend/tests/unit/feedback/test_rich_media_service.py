"""Unit tests for FeedbackService rich media methods."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException, UploadFile

from app.schemas.feedback import FeedbackSubmitRequest
from app.services.feedback.service import (
    FEEDBACK_BUCKET,
    IMAGE_MAX_SIZE,
    VIDEO_MAX_SIZE,
    FeedbackService,
)
from pydantic import HttpUrl


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def service(mock_client):
    return FeedbackService(client=mock_client)


@pytest.fixture
def user_id():
    return uuid4()


def _make_upload_file(filename: str, content_type: str, content: bytes):
    file = MagicMock(spec=UploadFile)
    file.filename = filename
    file.content_type = content_type
    file.read = AsyncMock(return_value=content)
    return file


class TestUploadImage:
    @pytest.mark.asyncio
    async def test_upload_image_success_jpeg(self, service, mock_client, user_id):
        file = _make_upload_file("test.jpg", "image/jpeg", b"fake-jpeg")
        mock_client.storage.from_(FEEDBACK_BUCKET).upload.return_value = None

        result = await service.upload_image(user_id, file)

        assert isinstance(result, str)
        assert result.startswith(f"feedback/{user_id}/")
        assert result.endswith(".jpg")

    @pytest.mark.asyncio
    async def test_upload_image_invalid_mime(self, service, user_id):
        file = _make_upload_file("test.gif", "image/gif", b"fake-gif")
        with pytest.raises(HTTPException) as exc_info:
            await service.upload_image(user_id, file)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_upload_image_oversize(self, service, user_id):
        file = _make_upload_file("big.jpg", "image/jpeg", b"x" * (IMAGE_MAX_SIZE + 1))
        with pytest.raises(HTTPException) as exc_info:
            await service.upload_image(user_id, file)
        assert exc_info.value.status_code == 413


class TestUploadVideo:
    @pytest.mark.asyncio
    async def test_upload_video_success_mp4(self, service, mock_client, user_id):
        file = _make_upload_file("test.mp4", "video/mp4", b"fake-mp4")
        mock_client.storage.from_(FEEDBACK_BUCKET).upload.return_value = None

        result = await service.upload_video(user_id, file)

        assert isinstance(result, str)
        assert result.startswith(f"feedback/{user_id}/")
        assert result.endswith(".mp4")

    @pytest.mark.asyncio
    async def test_upload_video_success_webm(self, service, mock_client, user_id):
        file = _make_upload_file("test.webm", "video/webm", b"fake-webm")
        mock_client.storage.from_(FEEDBACK_BUCKET).upload.return_value = None

        result = await service.upload_video(user_id, file)

        assert isinstance(result, str)
        assert result.startswith(f"feedback/{user_id}/")
        assert result.endswith(".webm")

    @pytest.mark.asyncio
    async def test_upload_video_oversize(self, service, user_id):
        file = _make_upload_file("big.mp4", "video/mp4", b"x" * (VIDEO_MAX_SIZE + 1))
        with pytest.raises(HTTPException) as exc_info:
            await service.upload_video(user_id, file)
        assert exc_info.value.status_code == 413

    @pytest.mark.asyncio
    async def test_upload_video_invalid_mime(self, service, user_id):
        file = _make_upload_file("test.avi", "video/x-msvideo", b"fake-avi")
        with pytest.raises(HTTPException) as exc_info:
            await service.upload_video(user_id, file)
        assert exc_info.value.status_code == 400


class TestDeleteUpload:
    @pytest.mark.asyncio
    async def test_delete_upload_success(self, service, mock_client, user_id):
        storage_path = f"feedback/{user_id}/image.jpg"
        mock_client.storage.from_(FEEDBACK_BUCKET).remove.return_value = None

        await service.delete_upload(user_id, storage_path)

        mock_client.storage.from_(FEEDBACK_BUCKET).remove.assert_called_once_with(
            [storage_path]
        )

    @pytest.mark.asyncio
    async def test_delete_upload_wrong_owner(self, service, user_id):
        other_user_id = uuid4()
        storage_path = f"feedback/{other_user_id}/image.jpg"
        with pytest.raises(HTTPException) as exc_info:
            await service.delete_upload(user_id, storage_path)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_upload_not_found(self, service, mock_client, user_id):
        storage_path = f"feedback/{user_id}/missing.jpg"
        mock_client.storage.from_(FEEDBACK_BUCKET).remove.side_effect = Exception(
            "Not found"
        )

        with pytest.raises(HTTPException) as exc_info:
            await service.delete_upload(user_id, storage_path)
        assert exc_info.value.status_code == 404


class TestSubmitFeedbackWithImages:
    @pytest.mark.asyncio
    async def test_submit_feedback_three_images(self, service, mock_client, user_id):
        feedback_id = str(uuid4())
        submitted_at = datetime.now(timezone.utc).isoformat()
        image_ids = [str(uuid4()) for _ in range(3)]

        select_chain = MagicMock()
        select_chain.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[]
        )

        def table_side_effect(name):
            tbl = MagicMock()
            if name == "feedback_submissions":
                tbl.select.return_value = select_chain
                tbl.insert.return_value.execute.return_value = MagicMock(
                    data=[
                        {
                            "id": feedback_id,
                            "submitted_at": submitted_at,
                            "status": "new",
                        }
                    ]
                )
            elif name == "feedback_images":
                tbl.insert.return_value.execute.return_value = MagicMock(
                    data=[
                        {
                            "id": image_ids[i],
                            "storage_path": f"feedback/{user_id}/img{i + 1}.jpg",
                            "display_order": i,
                        }
                        for i in range(3)
                    ]
                )
            return tbl

        mock_client.table.side_effect = table_side_effect

        payload = FeedbackSubmitRequest(
            page_url=HttpUrl("https://example.com/page"),
            text_content="Test feedback",
            image_paths=[
                f"feedback/{user_id}/img1.jpg",
                f"feedback/{user_id}/img2.jpg",
                f"feedback/{user_id}/img3.jpg",
            ],
        )

        result = await service.submit_feedback(user_id, payload)

        assert result["id"] == feedback_id
        assert len(result["images"]) == 3
        for idx, img in enumerate(result["images"]):
            assert img["storage_path"] == payload.image_paths[idx]  # type: ignore[index]
            assert img["display_order"] == idx

    @pytest.mark.asyncio
    async def test_submit_feedback_six_images(self, service, mock_client, user_id):
        payload = FeedbackSubmitRequest.model_construct(
            page_url=HttpUrl("https://example.com/page"),
            text_content="Test feedback",
            image_paths=[f"feedback/{user_id}/img{i}.jpg" for i in range(6)],
        )
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[]
        )
        with pytest.raises(HTTPException) as exc_info:
            await service.submit_feedback(user_id, payload)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_submit_feedback_audio_and_video(self, service, mock_client, user_id):
        payload = MagicMock()
        payload.page_url = "https://example.com/page"
        payload.text_content = "Test feedback"
        payload.image_paths = None
        payload.audio_url = "feedback/audio.mp3"
        payload.video_url = "feedback/video.mp4"

        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(
            data=[]
        )
        with pytest.raises(HTTPException) as exc_info:
            await service.submit_feedback(user_id, payload)
        assert exc_info.value.status_code == 422


class TestListFeedbackImages:
    @pytest.mark.asyncio
    async def test_list_feedback_admin_images_sorted_and_signed(
        self, service, mock_client
    ):
        feedback_id = str(uuid4())
        user_id_str = str(uuid4())
        img1_id = str(uuid4())
        img2_id = str(uuid4())

        main_query = MagicMock()
        main_query.eq.return_value = main_query
        main_query.gte.return_value = main_query
        main_query.lte.return_value = main_query
        main_query.ilike.return_value = main_query
        main_query.range.return_value = main_query
        main_query.order.return_value = main_query
        main_query.execute.return_value = MagicMock(
            data=[
                {
                    "id": feedback_id,
                    "user_id": user_id_str,
                    "page_url": "https://example.com",
                    "text_content": "Test",
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

        images_query = MagicMock()
        images_query.eq.return_value = images_query
        images_query.order.return_value = images_query
        images_query.execute.return_value = MagicMock(
            data=[
                {
                    "id": img1_id,
                    "storage_path": f"feedback/{user_id_str}/img1.jpg",
                    "display_order": 0,
                },
                {
                    "id": img2_id,
                    "storage_path": f"feedback/{user_id_str}/img2.jpg",
                    "display_order": 1,
                },
            ]
        )

        def table_side_effect(name):
            if name == "feedback_submissions":
                mock_tbl = MagicMock()
                mock_tbl.select.return_value = main_query
                return mock_tbl
            if name == "feedback_images":
                mock_tbl = MagicMock()
                mock_tbl.select.return_value = images_query
                return mock_tbl
            return MagicMock()

        mock_client.table.side_effect = table_side_effect
        mock_client.storage.from_(
            FEEDBACK_BUCKET
        ).create_signed_url.return_value = "https://signed.example.com/url"

        items, total = await service.list_feedback()

        assert total == 1
        item = items[0]
        assert len(item["images"]) == 2
        assert item["images"][0]["display_order"] == 0
        assert item["images"][0]["id"] == img1_id
        assert item["images"][1]["display_order"] == 1
        assert item["images"][1]["id"] == img2_id
        assert item["images"][0]["storage_url"] == "https://signed.example.com/url"
        assert item["images"][1]["storage_url"] == "https://signed.example.com/url"
        assert item["video_signed_url"] == "https://signed.example.com/url"

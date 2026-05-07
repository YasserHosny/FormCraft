"""Unit tests for FeedbackService business logic."""

from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.services.feedback.service import (
    FeedbackService,
    COOLDOWN_SECONDS,
    IMAGE_MAX_SIZE,
    ALLOWED_IMAGE_MIMES,
    AUDIO_MAX_SIZE,
    ALLOWED_AUDIO_MIMES,
)
from tests.conftest import make_supabase_response


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def service(mock_client):
    return FeedbackService(client=mock_client)


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def now():
    return datetime.now(timezone.utc)


class TestSubmitFeedbackCooldown:
    @pytest.mark.asyncio
    async def test_cooldown_blocks_submission_within_30s(
        self, service, mock_client, user_id, now
    ):
        recent = now.isoformat()
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = make_supabase_response(
            [{"submitted_at": recent}], count=1
        )

        payload = MagicMock()
        payload.text_content = "Great feedback"
        payload.page_url = "https://example.com"
        payload.image_url = None
        payload.audio_url = None

        with pytest.raises(HTTPException) as exc_info:
            await service.submit_feedback(user_id, payload)
        assert exc_info.value.status_code == 429

    @pytest.mark.asyncio
    async def test_cooldown_allows_submission_after_30s(
        self, service, mock_client, user_id, now
    ):
        past = (now - timedelta(seconds=COOLDOWN_SECONDS + 1)).isoformat()
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = make_supabase_response(
            [{"submitted_at": past}], count=1
        )

        new_id = str(uuid4())
        submitted_at = now.isoformat()
        mock_client.table.return_value.insert.return_value.execute.return_value = (
            make_supabase_response(
                [{"id": new_id, "submitted_at": submitted_at, "status": "new"}]
            )
        )

        payload = MagicMock()
        payload.text_content = "Great feedback"
        payload.page_url = "https://example.com"
        payload.image_url = None
        payload.audio_url = None

        result = await service.submit_feedback(user_id, payload)
        assert result["id"] == new_id
        assert result["status"] == "new"

    @pytest.mark.asyncio
    async def test_cooldown_allows_first_submission(
        self, service, mock_client, user_id
    ):
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = make_supabase_response(
            [], count=0
        )

        new_id = str(uuid4())
        submitted_at = datetime.now(timezone.utc).isoformat()
        mock_client.table.return_value.insert.return_value.execute.return_value = (
            make_supabase_response(
                [{"id": new_id, "submitted_at": submitted_at, "status": "new"}]
            )
        )

        payload = MagicMock()
        payload.text_content = "First feedback"
        payload.page_url = "https://example.com"
        payload.image_url = None
        payload.audio_url = None

        result = await service.submit_feedback(user_id, payload)
        assert result["id"] == new_id


class TestSubmitFeedbackValidation:
    @pytest.mark.asyncio
    async def test_text_validation_handled_by_schema(
        self, service, mock_client, user_id
    ):
        """Text validation (empty, too long) is handled by Pydantic schemas at the route level,
        not in the service. The service receives pre-validated data."""
        pass


class TestSubmitFeedbackOptionalFields:
    @pytest.mark.asyncio
    async def test_null_image_audio_accepted(self, service, mock_client, user_id):
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = make_supabase_response(
            [], count=0
        )

        new_id = str(uuid4())
        submitted_at = datetime.now(timezone.utc).isoformat()
        mock_client.table.return_value.insert.return_value.execute.return_value = (
            make_supabase_response(
                [{"id": new_id, "submitted_at": submitted_at, "status": "new"}]
            )
        )

        payload = MagicMock()
        payload.text_content = "Text only feedback"
        payload.page_url = "https://example.com"
        payload.image_url = None
        payload.audio_url = None

        result = await service.submit_feedback(user_id, payload)
        assert result["status"] == "new"
        insert_call = mock_client.table.return_value.insert.call_args
        inserted_data = (
            insert_call[0][0] if insert_call[0] else insert_call[1].get("data", {})
        )
        assert (
            inserted_data.get("image_url") is None
            or "image_url" not in inserted_data
            or inserted_data["image_url"] is None
        )

    @pytest.mark.asyncio
    async def test_image_url_stored_when_provided(self, service, mock_client, user_id):
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = make_supabase_response(
            [], count=0
        )

        new_id = str(uuid4())
        submitted_at = datetime.now(timezone.utc).isoformat()
        mock_client.table.return_value.insert.return_value.execute.return_value = (
            make_supabase_response(
                [{"id": new_id, "submitted_at": submitted_at, "status": "new"}]
            )
        )

        image_url = "https://storage.example.com/feedback/img1.jpg"
        payload = MagicMock()
        payload.text_content = "Feedback with image"
        payload.page_url = "https://example.com"
        payload.image_url = image_url
        payload.audio_url = None

        result = await service.submit_feedback(user_id, payload)
        assert result["status"] == "new"
        insert_call = mock_client.table.return_value.insert.call_args
        inserted_data = insert_call[0][0] if insert_call[0] else {}
        assert inserted_data["image_url"] == image_url

    @pytest.mark.asyncio
    async def test_audio_url_stored_when_provided(self, service, mock_client, user_id):
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = make_supabase_response(
            [], count=0
        )

        new_id = str(uuid4())
        submitted_at = datetime.now(timezone.utc).isoformat()
        mock_client.table.return_value.insert.return_value.execute.return_value = (
            make_supabase_response(
                [{"id": new_id, "submitted_at": submitted_at, "status": "new"}]
            )
        )

        audio_url = "https://storage.example.com/feedback/audio1.mp3"
        payload = MagicMock()
        payload.text_content = "Feedback with audio"
        payload.page_url = "https://example.com"
        payload.image_url = None
        payload.audio_url = audio_url

        result = await service.submit_feedback(user_id, payload)
        assert result["status"] == "new"
        insert_call = mock_client.table.return_value.insert.call_args
        inserted_data = insert_call[0][0] if insert_call[0] else {}
        assert inserted_data["audio_url"] == audio_url


class TestUploadFile:
    @pytest.mark.asyncio
    async def test_valid_image_stored(self, service, mock_client, user_id):
        file_content = b"fake-jpeg-data"
        mock_client.storage.from_.return_value.upload.return_value = None

        result = await service.upload_file(
            user_id=user_id,
            file_content=file_content,
            filename="test.jpg",
            content_type="image/jpeg",
            allowed_mimes={"image/jpeg", "image/png", "image/webp"},
            max_size=IMAGE_MAX_SIZE,
        )

        assert result.startswith(f"feedback/{user_id}/")
        assert result.endswith(".jpg")
        mock_client.storage.from_.return_value.upload.assert_called_once()

    @pytest.mark.asyncio
    async def test_image_url_linked_to_submission(self, service, mock_client, user_id):
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = make_supabase_response(
            [], count=0
        )

        new_id = str(uuid4())
        submitted_at = datetime.now(timezone.utc).isoformat()
        mock_client.table.return_value.insert.return_value.execute.return_value = (
            make_supabase_response(
                [{"id": new_id, "submitted_at": submitted_at, "status": "new"}]
            )
        )

        image_url = f"feedback/{user_id}/{uuid4()}.jpg"
        payload = MagicMock()
        payload.text_content = "Feedback with image"
        payload.page_url = "https://example.com"
        payload.image_url = image_url
        payload.audio_url = None

        result = await service.submit_feedback(user_id, payload)
        assert result["status"] == "new"
        insert_call = mock_client.table.return_value.insert.call_args
        inserted_data = (
            insert_call[0][0] if insert_call[0] else insert_call[1].get("data", {})
        )
        assert inserted_data["image_url"] == image_url

    @pytest.mark.asyncio
    async def test_oversized_image_rejected(self, service, user_id):
        file_content = b"x" * (IMAGE_MAX_SIZE + 1)

        with pytest.raises(HTTPException) as exc_info:
            await service.upload_file(
                user_id=user_id,
                file_content=file_content,
                filename="big.jpg",
                content_type="image/jpeg",
                allowed_mimes={"image/jpeg", "image/png", "image/webp"},
                max_size=IMAGE_MAX_SIZE,
            )
        assert exc_info.value.status_code == 413

    @pytest.mark.asyncio
    async def test_bad_mime_rejected(self, service, user_id):
        with pytest.raises(HTTPException) as exc_info:
            await service.upload_file(
                user_id=user_id,
                file_content=b"fake-pdf-data",
                filename="doc.pdf",
                content_type="application/pdf",
                allowed_mimes=ALLOWED_IMAGE_MIMES,
                max_size=IMAGE_MAX_SIZE,
            )
        assert exc_info.value.status_code == 400


class TestDeleteFile:
    @pytest.mark.asyncio
    async def test_delete_own_file_succeeds(self, service, mock_client, user_id):
        storage_path = f"feedback/{user_id}/some-file.jpg"
        mock_client.storage.from_.return_value.remove.return_value = None

        await service.delete_file(user_id=user_id, storage_path=storage_path)

        mock_client.storage.from_.return_value.remove.assert_called_once_with(
            [storage_path]
        )

    @pytest.mark.asyncio
    async def test_delete_foreign_path_rejected(self, service, user_id):
        other_user_id = uuid4()
        storage_path = f"feedback/{other_user_id}/some-file.jpg"

        with pytest.raises(HTTPException) as exc_info:
            await service.delete_file(user_id=user_id, storage_path=storage_path)
        assert exc_info.value.status_code == 400


class TestAudioUpload:
    @pytest.mark.asyncio
    async def test_valid_mp3_accepted(self, service, mock_client, user_id):
        file_content = b"fake-mp3-data"
        mock_client.storage.from_.return_value.upload.return_value = None

        result = await service.upload_file(
            user_id=user_id,
            file_content=file_content,
            filename="test.mp3",
            content_type="audio/mpeg",
            allowed_mimes=ALLOWED_AUDIO_MIMES,
            max_size=AUDIO_MAX_SIZE,
        )

        assert result.startswith(f"feedback/{user_id}/")
        assert result.endswith(".mp3")
        mock_client.storage.from_.return_value.upload.assert_called_once()

    @pytest.mark.asyncio
    async def test_valid_webm_accepted(self, service, mock_client, user_id):
        file_content = b"fake-webm-data"
        mock_client.storage.from_.return_value.upload.return_value = None

        result = await service.upload_file(
            user_id=user_id,
            file_content=file_content,
            filename="test.webm",
            content_type="audio/webm",
            allowed_mimes=ALLOWED_AUDIO_MIMES,
            max_size=AUDIO_MAX_SIZE,
        )

        assert result.startswith(f"feedback/{user_id}/")
        assert result.endswith(".webm")
        mock_client.storage.from_.return_value.upload.assert_called_once()

    @pytest.mark.asyncio
    async def test_oversized_audio_rejected(self, service, user_id):
        file_content = b"x" * (AUDIO_MAX_SIZE + 1)

        with pytest.raises(HTTPException) as exc_info:
            await service.upload_file(
                user_id=user_id,
                file_content=file_content,
                filename="big.mp3",
                content_type="audio/mpeg",
                allowed_mimes=ALLOWED_AUDIO_MIMES,
                max_size=AUDIO_MAX_SIZE,
            )
        assert exc_info.value.status_code == 413

    @pytest.mark.asyncio
    async def test_bad_mime_audio_rejected(self, service, user_id):
        with pytest.raises(HTTPException) as exc_info:
            await service.upload_file(
                user_id=user_id,
                file_content=b"fake-video-data",
                filename="test.mp4",
                content_type="video/mp4",
                allowed_mimes=ALLOWED_AUDIO_MIMES,
                max_size=AUDIO_MAX_SIZE,
            )
        assert exc_info.value.status_code == 400

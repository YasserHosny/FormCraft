"""Route tests for form import and OCR detection endpoints."""

import io
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from tests.conftest import make_supabase_response

TEMPLATE_ID = str(uuid4())
DETECTION_ID = str(uuid4())
PAGE_ID = str(uuid4())


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _mock_profile_query(mock_client, profile: dict):
    """Set up mock for get_current_user profile lookup."""
    mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = (
        make_supabase_response(profile)
    )


def _make_jpeg_bytes(size_bytes: int = 1000) -> bytes:
    """Create a minimal valid JPEG-like byte stream."""
    from PIL import Image

    img = Image.new("RGB", (100, 100), color="white")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    data = buf.read()
    # Pad to desired size if needed
    if len(data) < size_bytes:
        data += b"\x00" * (size_bytes - len(data))
    return data


# --- T010: POST /forms/import/{template_id} ---


@pytest.mark.asyncio
class TestImportForm:
    async def test_import_rejects_non_image(self, valid_admin_token, admin_profile):
        """Non-image content type should return 400."""
        with patch("app.api.deps.get_supabase_client") as mock_get:
            mock_client = MagicMock()
            mock_get.return_value = mock_client
            _mock_profile_query(mock_client, admin_profile)

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post(
                    f"/api/forms/import/{TEMPLATE_ID}",
                    headers=_auth_header(valid_admin_token),
                    files={"file": ("test.txt", b"not an image", "text/plain")},
                )
            assert response.status_code == 400
            assert "Unsupported file type" in response.json()["detail"]

    async def test_import_rejects_oversized_file(self, valid_admin_token, admin_profile):
        """Files over 10MB should return 413."""
        with patch("app.api.deps.get_supabase_client") as mock_get:
            mock_client = MagicMock()
            mock_get.return_value = mock_client
            _mock_profile_query(mock_client, admin_profile)

            # Create 11MB of data
            large_data = b"\xff\xd8\xff\xe0" + b"\x00" * (11 * 1024 * 1024)

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post(
                    f"/api/forms/import/{TEMPLATE_ID}",
                    headers=_auth_header(valid_admin_token),
                    files={"file": ("big.jpg", large_data, "image/jpeg")},
                )
            assert response.status_code == 413

    async def test_import_success_with_mocked_ocr(
        self, valid_admin_token, admin_profile, sample_ocr_response, sample_detected_fields_jsonb
    ):
        """Successful import with mocked Azure OCR."""
        with (
            patch("app.api.deps.get_supabase_client") as mock_get,
            patch("app.api.routes.forms.get_supabase_client") as mock_route_get,
            patch("app.api.routes.forms.AzureOCRClient") as mock_ocr_cls,
        ):
            mock_client = MagicMock()
            mock_get.return_value = mock_client
            mock_route_get.return_value = mock_client
            _mock_profile_query(mock_client, admin_profile)

            # Mock storage to return a real string URL
            mock_client.storage.from_.return_value.get_public_url.return_value = (
                "https://storage.example.com/form-backgrounds/image.jpg"
            )

            # Mock OCR client
            mock_ocr = MagicMock()
            mock_ocr.analyze_layout.return_value = sample_ocr_response
            mock_ocr_cls.return_value = mock_ocr

            # Mock DB insert
            detection_record = {
                "id": DETECTION_ID,
                "template_id": TEMPLATE_ID,
                "page_index": 0,
                "detected_fields": sample_detected_fields_jsonb,
                "page_dimensions": {"width": 211.67, "height": 132.29},
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            mock_client.table.return_value.insert.return_value.execute.return_value = (
                make_supabase_response([detection_record])
            )

            jpeg_data = _make_jpeg_bytes()
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post(
                    f"/api/forms/import/{TEMPLATE_ID}",
                    headers=_auth_header(valid_admin_token),
                    files={"file": ("cheque.jpg", jpeg_data, "image/jpeg")},
                    params={"page_index": 0},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["template_id"] == TEMPLATE_ID
            assert "detected_fields" in data

    async def test_import_ocr_config_error(self, valid_admin_token, admin_profile):
        """OCR service configuration error should return 500."""
        with (
            patch("app.api.deps.get_supabase_client") as mock_get,
            patch("app.api.routes.forms.get_supabase_client") as mock_route_get,
            patch("app.api.routes.forms.AzureOCRClient") as mock_ocr_cls,
        ):
            mock_client = MagicMock()
            mock_get.return_value = mock_client
            mock_route_get.return_value = mock_client
            _mock_profile_query(mock_client, admin_profile)

            mock_ocr_cls.side_effect = ValueError("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT not configured")

            jpeg_data = _make_jpeg_bytes()
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post(
                    f"/api/forms/import/{TEMPLATE_ID}",
                    headers=_auth_header(valid_admin_token),
                    files={"file": ("cheque.jpg", jpeg_data, "image/jpeg")},
                )
            assert response.status_code == 500
            assert "configuration error" in response.json()["detail"]


# --- T011: GET /forms/{template_id}/detections & DELETE ---


@pytest.mark.asyncio
class TestGetDetections:
    async def test_get_detections_empty(self, valid_admin_token, admin_profile):
        """Template with no detections returns empty list."""
        with (
            patch("app.api.deps.get_supabase_client") as mock_get,
            patch("app.api.routes.forms.get_supabase_client") as mock_route_get,
        ):
            mock_client = MagicMock()
            mock_get.return_value = mock_client
            mock_route_get.return_value = mock_client
            _mock_profile_query(mock_client, admin_profile)

            mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = (
                make_supabase_response([])
            )

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get(
                    f"/api/forms/{TEMPLATE_ID}/detections",
                    headers=_auth_header(valid_admin_token),
                )
            assert response.status_code == 200
            assert response.json() == []

    async def test_get_detections_with_data(
        self, valid_admin_token, admin_profile, sample_detected_fields_jsonb
    ):
        """Template with detections returns list."""
        with (
            patch("app.api.deps.get_supabase_client") as mock_get,
            patch("app.api.routes.forms.get_supabase_client") as mock_route_get,
        ):
            mock_client = MagicMock()
            mock_get.return_value = mock_client
            mock_route_get.return_value = mock_client
            _mock_profile_query(mock_client, admin_profile)

            detection = {
                "id": DETECTION_ID,
                "template_id": TEMPLATE_ID,
                "page_index": 0,
                "detected_fields": sample_detected_fields_jsonb,
                "page_dimensions": {"width": 210.0, "height": 148.5},
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = (
                make_supabase_response([detection])
            )

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get(
                    f"/api/forms/{TEMPLATE_ID}/detections",
                    headers=_auth_header(valid_admin_token),
                )
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert len(data[0]["detected_fields"]) == 3


@pytest.mark.asyncio
class TestDeleteDetection:
    async def test_delete_detection_success(self, valid_admin_token, admin_profile):
        """Delete detection returns success."""
        with (
            patch("app.api.deps.get_supabase_client") as mock_get,
            patch("app.api.routes.forms.get_supabase_client") as mock_route_get,
        ):
            mock_client = MagicMock()
            mock_get.return_value = mock_client
            mock_route_get.return_value = mock_client
            _mock_profile_query(mock_client, admin_profile)

            mock_client.table.return_value.delete.return_value.eq.return_value.execute.return_value = (
                make_supabase_response([{"id": DETECTION_ID}])
            )

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.delete(
                    f"/api/forms/detections/{DETECTION_ID}",
                    headers=_auth_header(valid_admin_token),
                )
            assert response.status_code == 200
            assert "deleted" in response.json()["message"].lower()

    async def test_delete_detection_not_found(self, valid_admin_token, admin_profile):
        """Delete nonexistent detection returns 404."""
        with (
            patch("app.api.deps.get_supabase_client") as mock_get,
            patch("app.api.routes.forms.get_supabase_client") as mock_route_get,
        ):
            mock_client = MagicMock()
            mock_get.return_value = mock_client
            mock_route_get.return_value = mock_client
            _mock_profile_query(mock_client, admin_profile)

            mock_client.table.return_value.delete.return_value.eq.return_value.execute.return_value = (
                make_supabase_response([])
            )

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.delete(
                    f"/api/forms/detections/{DETECTION_ID}",
                    headers=_auth_header(valid_admin_token),
                )
            assert response.status_code == 404


# --- T012: POST /forms/{template_id}/detections/{detection_id}/accept ---


@pytest.mark.asyncio
class TestAcceptDetections:
    async def test_accept_invalid_index(
        self, valid_admin_token, admin_profile, sample_detected_fields_jsonb
    ):
        """Invalid detection index returns 400."""
        with (
            patch("app.api.deps.get_supabase_client") as mock_get,
            patch("app.api.routes.forms.get_supabase_client") as mock_route_get,
        ):
            mock_client = MagicMock()
            mock_get.return_value = mock_client
            mock_route_get.return_value = mock_client
            _mock_profile_query(mock_client, admin_profile)

            detection = {
                "id": DETECTION_ID,
                "template_id": TEMPLATE_ID,
                "page_index": 0,
                "detected_fields": sample_detected_fields_jsonb,
                "page_dimensions": {"width": 210.0, "height": 148.5},
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = (
                make_supabase_response(detection)
            )

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post(
                    f"/api/forms/{TEMPLATE_ID}/detections/{DETECTION_ID}/accept",
                    headers=_auth_header(valid_admin_token),
                    json={"detection_ids": [99], "type_overrides": {}},
                )
            assert response.status_code == 400
            assert "Invalid detection index" in response.json()["detail"]

    async def test_accept_detection_not_found(self, valid_admin_token, admin_profile):
        """Nonexistent detection returns 404."""
        with (
            patch("app.api.deps.get_supabase_client") as mock_get,
            patch("app.api.routes.forms.get_supabase_client") as mock_route_get,
        ):
            mock_client = MagicMock()
            mock_get.return_value = mock_client
            mock_route_get.return_value = mock_client
            _mock_profile_query(mock_client, admin_profile)

            mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value = (
                make_supabase_response(None)
            )

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post(
                    f"/api/forms/{TEMPLATE_ID}/detections/{DETECTION_ID}/accept",
                    headers=_auth_header(valid_admin_token),
                    json={"detection_ids": [0], "type_overrides": {}},
                )
            assert response.status_code == 404

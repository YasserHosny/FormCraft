"""Contract tests for POST /api/tafqeet/preview — written FIRST (TDD Red phase).

These tests MUST fail until app/api/routes/tafqeet.py is implemented and
registered in app/main.py.

Run with: pytest tests/integration/tafqeet/test_tafqeet_route.py -v
"""

from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    return TestClient(app)


def _designer_profile(designer_user_id: str) -> dict:
    return {
        "id": designer_user_id,
        "role": "designer",
        "language": "ar",
        "display_name": "Test Designer",
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "created_by": None,
    }


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# 200 — valid requests
# ---------------------------------------------------------------------------

class TestPreviewSuccess:
    def test_arabic_only(self, client, valid_designer_token, designer_user_id, designer_profile):
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = designer_profile

        with patch("app.api.deps.get_supabase_client", return_value=mock_supabase):
            response = client.post(
                "/api/tafqeet/preview",
                json={
                    "amount": 5500.75,
                    "currency_code": "SAR",
                    "language": "ar",
                    "show_currency": True,
                    "prefix": "none",
                    "suffix": "faqat_la_ghair",
                },
                headers=_auth_headers(valid_designer_token),
            )
        assert response.status_code == 200
        body = response.json()
        assert "result" in body
        assert body["result"] is not None
        assert "ريال سعودي" in body["result"]
        assert body["result"].endswith("فقط لا غير")

    def test_english_only(self, client, valid_designer_token, designer_profile):
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = designer_profile

        with patch("app.api.deps.get_supabase_client", return_value=mock_supabase):
            response = client.post(
                "/api/tafqeet/preview",
                json={
                    "amount": 12500.50,
                    "currency_code": "EGP",
                    "language": "en",
                    "show_currency": True,
                    "prefix": "none",
                    "suffix": "none",
                },
                headers=_auth_headers(valid_designer_token),
            )
        assert response.status_code == 200
        body = response.json()
        assert body["result"] is not None
        assert "Egyptian Pound" in body["result"]
        assert "Piastre" in body["result"]

    def test_both_mode_two_lines(self, client, valid_designer_token, designer_profile):
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = designer_profile

        with patch("app.api.deps.get_supabase_client", return_value=mock_supabase):
            response = client.post(
                "/api/tafqeet/preview",
                json={
                    "amount": 12500.50,
                    "currency_code": "EGP",
                    "language": "both",
                    "show_currency": True,
                    "prefix": "none",
                    "suffix": "faqat_la_ghair",
                },
                headers=_auth_headers(valid_designer_token),
            )
        assert response.status_code == 200
        body = response.json()
        assert body["result"] is not None
        lines = body["result"].split("\n")
        assert len(lines) == 2

    def test_out_of_range_returns_null(self, client, valid_designer_token, designer_profile):
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = designer_profile

        with patch("app.api.deps.get_supabase_client", return_value=mock_supabase):
            response = client.post(
                "/api/tafqeet/preview",
                json={
                    "amount": 9999999999999,
                    "currency_code": "EGP",
                    "language": "ar",
                    "show_currency": True,
                    "prefix": "none",
                    "suffix": "none",
                },
                headers=_auth_headers(valid_designer_token),
            )
        assert response.status_code == 200
        assert response.json()["result"] is None

    def test_negative_returns_null(self, client, valid_designer_token, designer_profile):
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = designer_profile

        with patch("app.api.deps.get_supabase_client", return_value=mock_supabase):
            response = client.post(
                "/api/tafqeet/preview",
                json={
                    "amount": -100,
                    "currency_code": "EGP",
                    "language": "ar",
                    "show_currency": True,
                    "prefix": "none",
                    "suffix": "none",
                },
                headers=_auth_headers(valid_designer_token),
            )
        assert response.status_code == 200
        assert response.json()["result"] is None


# ---------------------------------------------------------------------------
# 401 — unauthorized
# ---------------------------------------------------------------------------

class TestPreviewUnauthorized:
    def test_missing_auth_header(self, client):
        response = client.post(
            "/api/tafqeet/preview",
            json={
                "amount": 100,
                "currency_code": "EGP",
                "language": "ar",
                "show_currency": True,
                "prefix": "none",
                "suffix": "none",
            },
        )
        assert response.status_code == 401

    def test_expired_token(self, client, expired_token):
        response = client.post(
            "/api/tafqeet/preview",
            json={
                "amount": 100,
                "currency_code": "EGP",
                "language": "ar",
                "show_currency": True,
                "prefix": "none",
                "suffix": "none",
            },
            headers=_auth_headers(expired_token),
        )
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# 422 — validation errors
# ---------------------------------------------------------------------------

class TestPreviewValidation:
    def test_suffix_only_with_language_ar(self, client, valid_designer_token, designer_profile):
        """suffix='only' is English-only; combining with language='ar' must return 422."""
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = designer_profile

        with patch("app.api.deps.get_supabase_client", return_value=mock_supabase):
            response = client.post(
                "/api/tafqeet/preview",
                json={
                    "amount": 100,
                    "currency_code": "EGP",
                    "language": "ar",
                    "show_currency": True,
                    "prefix": "none",
                    "suffix": "only",
                },
                headers=_auth_headers(valid_designer_token),
            )
        assert response.status_code == 422

    def test_invalid_currency_code(self, client, valid_designer_token, designer_profile):
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = designer_profile

        with patch("app.api.deps.get_supabase_client", return_value=mock_supabase):
            response = client.post(
                "/api/tafqeet/preview",
                json={
                    "amount": 100,
                    "currency_code": "XYZ",
                    "language": "ar",
                    "show_currency": True,
                    "prefix": "none",
                    "suffix": "none",
                },
                headers=_auth_headers(valid_designer_token),
            )
        assert response.status_code == 422

    def test_invalid_language(self, client, valid_designer_token, designer_profile):
        mock_supabase = MagicMock()
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = designer_profile

        with patch("app.api.deps.get_supabase_client", return_value=mock_supabase):
            response = client.post(
                "/api/tafqeet/preview",
                json={
                    "amount": 100,
                    "currency_code": "EGP",
                    "language": "fr",
                    "show_currency": True,
                    "prefix": "none",
                    "suffix": "none",
                },
                headers=_auth_headers(valid_designer_token),
            )
        assert response.status_code == 422

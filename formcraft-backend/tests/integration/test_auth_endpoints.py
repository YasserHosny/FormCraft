"""Integration tests for authentication endpoints."""

from unittest.mock import MagicMock, patch, PropertyMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import make_supabase_response


@pytest.fixture
def client():
    return TestClient(app)


def _mock_sign_in_response(user_id="11111111-1111-1111-1111-111111111111"):
    """Create a mock Supabase sign_in_with_password response."""
    mock = MagicMock()
    mock.session.access_token = "test-access-token"
    mock.session.refresh_token = "test-refresh-token"
    mock.session.expires_in = 3600
    mock.user.id = user_id
    return mock


class TestLoginEndpoint:
    def test_login_success(self, client):
        mock_client = MagicMock()
        mock_client.auth.sign_in_with_password.return_value = _mock_sign_in_response()
        # Mock audit logger write
        mock_client.table.return_value.insert.return_value.execute.return_value = MagicMock()

        with patch("app.api.routes.auth.get_supabase_client", return_value=mock_client):
            response = client.post(
                "/api/auth/login",
                json={"email": "admin@test.com", "password": "password123"},
            )
        assert response.status_code == 200
        body = response.json()
        assert body["access_token"] == "test-access-token"
        assert body["refresh_token"] == "test-refresh-token"
        assert body["token_type"] == "bearer"
        assert body["expires_in"] == 3600

    def test_login_invalid_credentials(self, client):
        mock_client = MagicMock()
        mock_client.auth.sign_in_with_password.side_effect = Exception("Invalid login")
        mock_client.table.return_value.insert.return_value.execute.return_value = MagicMock()

        with patch("app.api.routes.auth.get_supabase_client", return_value=mock_client):
            response = client.post(
                "/api/auth/login",
                json={"email": "bad@test.com", "password": "wrong"},
            )
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_missing_email(self, client):
        response = client.post(
            "/api/auth/login",
            json={"password": "password123"},
        )
        assert response.status_code == 422


class TestRefreshEndpoint:
    def test_refresh_success(self, client):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.session.access_token = "new-access-token"
        mock_response.session.refresh_token = "new-refresh-token"
        mock_response.session.expires_in = 3600
        mock_client.auth.refresh_session.return_value = mock_response

        with patch("app.api.routes.auth.get_supabase_client", return_value=mock_client):
            response = client.post(
                "/api/auth/refresh",
                json={"refresh_token": "old-refresh-token"},
            )
        assert response.status_code == 200
        assert response.json()["access_token"] == "new-access-token"

    def test_refresh_invalid_token(self, client):
        mock_client = MagicMock()
        mock_client.auth.refresh_session.side_effect = Exception("Invalid token")

        with patch("app.api.routes.auth.get_supabase_client", return_value=mock_client):
            response = client.post(
                "/api/auth/refresh",
                json={"refresh_token": "bad-token"},
            )
        assert response.status_code == 401


class TestRegisterEndpoint:
    def test_register_without_auth_returns_401(self, client):
        response = client.post(
            "/api/auth/register",
            json={
                "email": "new@test.com",
                "password": "password123",
                "role": "viewer",
            },
        )
        assert response.status_code in (401, 422)

    def test_register_with_non_admin_returns_403(
        self, client, valid_designer_token, designer_profile
    ):
        mock_client = MagicMock()
        profile_response = make_supabase_response(designer_profile)
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = profile_response

        with patch("app.api.routes.auth.get_supabase_client", return_value=mock_client), \
             patch("app.api.deps.get_supabase_client", return_value=mock_client):
            response = client.post(
                "/api/auth/register",
                json={
                    "email": "new@test.com",
                    "password": "password123",
                    "role": "viewer",
                },
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        assert response.status_code == 403


class TestLogoutEndpoint:
    def test_logout_without_auth_returns_401(self, client):
        response = client.post("/api/auth/logout")
        assert response.status_code in (401, 422)

    def test_logout_success(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        profile_response = make_supabase_response(admin_profile)
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = profile_response
        mock_client.table.return_value.insert.return_value.execute.return_value = MagicMock()

        with patch("app.api.routes.auth.get_supabase_client", return_value=mock_client):
            with patch("app.api.deps.get_supabase_client", return_value=mock_client):
                response = client.post(
                    "/api/auth/logout",
                    headers={"Authorization": f"Bearer {valid_admin_token}"},
                )
        assert response.status_code == 204

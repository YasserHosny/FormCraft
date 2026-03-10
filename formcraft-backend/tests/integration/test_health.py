"""Integration tests for health check endpoint."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_200_when_healthy(self, client):
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.limit.return_value.execute.return_value = MagicMock(data=[{"id": "x"}])

        with patch("app.api.routes.health.get_supabase_client", return_value=mock_client):
            response = client.get("/api/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert "version" in body
        assert body["checks"]["supabase"] == "healthy"

    def test_health_returns_503_when_supabase_down(self, client):
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.limit.return_value.execute.side_effect = Exception("Connection refused")

        with patch("app.api.routes.health.get_supabase_client", return_value=mock_client):
            response = client.get("/api/health")
        assert response.status_code == 503
        body = response.json()
        assert body["status"] == "degraded"
        assert body["checks"]["supabase"] == "unreachable"

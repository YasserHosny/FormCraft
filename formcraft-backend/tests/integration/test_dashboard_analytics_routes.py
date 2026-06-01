"""Contract tests for dashboard analytics endpoints (054-analytics-real-data)."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import make_supabase_response


@pytest.fixture
def client():
    return TestClient(app)


def _mock_profile_query(mock_client, profile):
    profile_response = make_supabase_response(profile)
    mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = profile_response


def _mock_empty_submissions(mock_client):
    mock_client.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.execute.return_value = make_supabase_response([])


def _patch_supabase(mock_client):
    """Patch the module-level singleton so no real client is ever created."""
    import app.core.supabase as supabase_mod
    original = supabase_mod._client
    supabase_mod._client = mock_client
    return original


def _restore_supabase(original):
    import app.core.supabase as supabase_mod
    supabase_mod._client = original


class TestDashboardSummary:
    def test_summary_returns_200_for_admin(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _mock_profile_query(mock_client, admin_profile)
        _mock_empty_submissions(mock_client)
        original = _patch_supabase(mock_client)
        try:
            response = client.get(
                "/api/analytics/dashboard/summary?period=30d",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        finally:
            _restore_supabase(original)
        assert response.status_code == 200
        body = response.json()
        assert "total_forms_filled" in body
        assert "active_templates" in body
        assert "total_templates" in body
        assert "avg_fill_time_ms" in body
        assert "unique_customers" in body
        assert "new_customers_this_week" in body
        assert "delta_pct" in body
        assert "period" in body
        assert "cache_expires_at" in body

    def test_summary_requires_admin_role(self, client, valid_designer_token, designer_profile):
        # 401 without auth
        response = client.get("/api/analytics/dashboard/summary")
        assert response.status_code == 401

        # 403 with designer token
        mock_client = MagicMock()
        _mock_profile_query(mock_client, designer_profile)
        original = _patch_supabase(mock_client)
        try:
            response = client.get(
                "/api/analytics/dashboard/summary",
                headers={"Authorization": f"Bearer {valid_designer_token}"},
            )
        finally:
            _restore_supabase(original)
        assert response.status_code == 403


class TestDashboardSubmissionsOverTime:
    def test_time_series_daily_granularity(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _mock_profile_query(mock_client, admin_profile)
        _mock_empty_submissions(mock_client)
        original = _patch_supabase(mock_client)
        try:
            response = client.get(
                "/api/analytics/dashboard/submissions-over-time?period=30d",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        finally:
            _restore_supabase(original)
        assert response.status_code == 200
        body = response.json()
        assert body["granularity"] == "daily"
        assert "points" in body
        assert len(body["points"]) == 30
        assert "peak_date" in body
        assert "peak_count" in body
        assert "cache_expires_at" in body

    def test_time_series_monthly_granularity(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _mock_profile_query(mock_client, admin_profile)
        _mock_empty_submissions(mock_client)
        original = _patch_supabase(mock_client)
        try:
            response = client.get(
                "/api/analytics/dashboard/submissions-over-time?period=yearly",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        finally:
            _restore_supabase(original)
        assert response.status_code == 200
        body = response.json()
        assert body["granularity"] == "monthly"
        assert "points" in body
        assert len(body["points"]) == 12


class TestDashboardDepartmentDistribution:
    def test_department_distribution_shape(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _mock_profile_query(mock_client, admin_profile)
        _mock_empty_submissions(mock_client)
        original = _patch_supabase(mock_client)
        try:
            response = client.get(
                "/api/analytics/dashboard/department-distribution?period=30d",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        finally:
            _restore_supabase(original)
        assert response.status_code == 200
        body = response.json()
        assert "departments" in body
        assert "total" in body
        total_pct = 0.0
        for dept in body["departments"]:
            assert "department_id" in dept
            assert "department_name" in dept
            assert "count" in dept
            assert "percentage" in dept
            total_pct += dept["percentage"]
        # Allow ±0.5 tolerance due to rounding; skip for empty data
        if body["departments"]:
            assert abs(total_pct - 100.0) <= 0.5


class TestDashboardTopTemplates:
    def test_top_templates_ordered_desc(self, client, valid_admin_token, admin_profile):
        mock_client = MagicMock()
        _mock_profile_query(mock_client, admin_profile)
        _mock_empty_submissions(mock_client)
        original = _patch_supabase(mock_client)
        try:
            response = client.get(
                "/api/analytics/dashboard/top-templates?period=30d",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        finally:
            _restore_supabase(original)
        assert response.status_code == 200
        body = response.json()
        templates = body["templates"]
        assert len(templates) <= 7
        for i in range(len(templates) - 1):
            assert templates[i]["count"] >= templates[i + 1]["count"]

        # Test limit param
        original = _patch_supabase(mock_client)
        try:
            response = client.get(
                "/api/analytics/dashboard/top-templates?period=30d&limit=3",
                headers={"Authorization": f"Bearer {valid_admin_token}"},
            )
        finally:
            _restore_supabase(original)
        assert response.status_code == 200
        assert len(response.json()["templates"]) <= 3

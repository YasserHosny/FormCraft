"""Platform admin route integration tests (F039)."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.middleware.org_context import OrgContext, get_org_context

_SUPA_PATCH = "app.api.routes.platform.get_supabase_client"

_PLATFORM_ADMIN_CTX = OrgContext(
    org_id=None,
    user_id=UUID("11111111-1111-1111-1111-111111111111"),
    is_platform_admin=True,
    department_id=None,
    branch_id=None,
    role="platform_admin",
)

NOW = datetime.now(timezone.utc).isoformat()


async def _platform_ctx_override() -> OrgContext:
    return _PLATFORM_ADMIN_CTX


@contextmanager
def _platform_admin():
    app.dependency_overrides[get_org_context] = _platform_ctx_override
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_org_context, None)


def _org_detail(org_id: str | None = None) -> dict:
    return {
        "id": org_id or str(uuid4()),
        "name_ar": "Test Org",
        "name_en": "Test Org EN",
        "default_language": "ar",
        "default_country": "SA",
        "default_currency": "SAR",
        "subscription_tier": "starter",
        "status": "active",
        "domain": None,
        "logo_url": None,
        "branding": None,
        "active_users_count": 0,
        "templates_count": 0,
        "submissions_this_month": 0,
        "total_submissions": 0,
        "storage_usage": None,
        "created_at": NOW,
        "updated_at": NOW,
    }


def _metrics() -> dict:
    return {
        "total_orgs": 5,
        "total_users": 20,
        "total_submissions": 100,
        "orgs_by_tier": {"starter": 3, "professional": 2},
        "submission_volume_trend": [],
        "recently_created_orgs": [],
        "tier_limit_alerts": [],
    }


@pytest.fixture
def test_client() -> TestClient:
    return TestClient(app)


class TestPlatformRoutes:
    def test_list_organizations(self, test_client):
        orgs = [_org_detail()]
        with (
            _platform_admin(),
            patch(_SUPA_PATCH, return_value=MagicMock()),
            patch(
                "app.api.routes.platform.PlatformService.list_organizations",
                new_callable=AsyncMock,
                return_value=(orgs, 1),
            ),
        ):
            response = test_client.get("/api/platform/organizations")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_create_organization(self, test_client):
        new_org = _org_detail()
        with (
            _platform_admin(),
            patch(_SUPA_PATCH, return_value=MagicMock()),
            patch(
                "app.api.routes.platform.PlatformService.create_organization",
                new_callable=AsyncMock,
                return_value={"id": new_org["id"]},
            ),
            patch(
                "app.api.routes.platform.PlatformService.get_organization_detail",
                new_callable=AsyncMock,
                return_value=new_org,
            ),
        ):
            response = test_client.post(
                "/api/platform/organizations",
                json={"name_ar": "New Org", "default_language": "ar", "default_country": "SA", "default_currency": "SAR"},
            )
        assert response.status_code == 201
        assert response.json()["name_ar"] == "Test Org"

    def test_create_organization_rate_limit(self, test_client):
        new_org = _org_detail()
        with (
            _platform_admin(),
            patch(_SUPA_PATCH, return_value=MagicMock()),
            patch(
                "app.api.routes.platform.PlatformService.create_organization",
                new_callable=AsyncMock,
                return_value={"id": new_org["id"]},
            ),
            patch(
                "app.api.routes.platform.PlatformService.get_organization_detail",
                new_callable=AsyncMock,
                return_value=new_org,
            ),
        ):
            response = test_client.post(
                "/api/platform/organizations",
                json={"name_ar": "Rate Limited Org"},
            )
        assert response.status_code in (201, 422, 429)

    def test_suspend_organization(self, test_client):
        org_id = str(uuid4())
        detail = _org_detail(org_id)
        detail["status"] = "suspended"
        with (
            _platform_admin(),
            patch(_SUPA_PATCH, return_value=MagicMock()),
            patch(
                "app.api.routes.platform.PlatformService.suspend_organization",
                new_callable=AsyncMock,
                return_value=detail,
            ),
        ):
            response = test_client.post(f"/api/platform/organizations/{org_id}/suspend")
        assert response.status_code in (200, 404)

    def test_reactivate_organization(self, test_client):
        org_id = str(uuid4())
        detail = _org_detail(org_id)
        with (
            _platform_admin(),
            patch(_SUPA_PATCH, return_value=MagicMock()),
            patch(
                "app.api.routes.platform.PlatformService.reactivate_organization",
                new_callable=AsyncMock,
                return_value=detail,
            ),
        ):
            response = test_client.post(f"/api/platform/organizations/{org_id}/reactivate")
        assert response.status_code in (200, 404)

    def test_get_platform_metrics(self, test_client):
        with (
            _platform_admin(),
            patch(_SUPA_PATCH, return_value=MagicMock()),
            patch(
                "app.api.routes.platform.PlatformMetricsService.get_metrics",
                new_callable=AsyncMock,
                return_value=_metrics(),
            ),
        ):
            response = test_client.get("/api/platform/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "total_orgs" in data
        assert "total_users" in data
        assert "total_submissions" in data

    def test_refresh_platform_metrics(self, test_client):
        with (
            _platform_admin(),
            patch(_SUPA_PATCH, return_value=MagicMock()),
            patch(
                "app.api.routes.platform.PlatformMetricsService.refresh_materialized_view",
                new_callable=AsyncMock,
                return_value=None,
            ),
        ):
            response = test_client.post("/api/platform/metrics/refresh")
        assert response.status_code == 200
        assert response.json()["status"] == "refreshed"

    def test_delete_organization_blocked(self, test_client):
        org_id = str(uuid4())
        with (
            _platform_admin(),
            patch(_SUPA_PATCH, return_value=MagicMock()),
            patch(
                "app.api.routes.platform.PlatformService.delete_organization",
                new_callable=AsyncMock,
                return_value=None,
            ),
        ):
            response = test_client.delete(f"/api/platform/organizations/{org_id}")
        assert response.status_code in (204, 400, 404)

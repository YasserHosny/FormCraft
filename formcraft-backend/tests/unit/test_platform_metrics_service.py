"""Platform metrics service tests (F039)."""

from __future__ import annotations

from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from app.services.platform_metrics_service import PlatformMetricsService


class TestPlatformMetricsService:
    @pytest.fixture
    def mock_client(self, mocker: MockerFixture):
        client = mocker.MagicMock()
        client.table.return_value.select.return_value.limit.return_value.single.return_value.execute.return_value = mocker.MagicMock(
            data={
                "total_orgs": 5,
                "total_users": 42,
                "total_submissions": 1200,
                "orgs_by_tier": {"starter": 3, "enterprise": 2},
            }
        )
        return client

    @pytest.fixture
    def service(self, mock_client):
        return PlatformMetricsService(mock_client)

    async def test_get_metrics(self, service, mock_client):
        mock_client.table.return_value.select.return_value.gte.return_value.lt.return_value.execute.return_value = mocker.MagicMock(
            count=100
        )
        mock_client.table.return_value.select.return_value.gte.return_value.order.return_value.limit.return_value.execute.return_value = mocker.MagicMock(
            data=[]
        )
        mock_client.rpc.return_value.execute.return_value = mocker.MagicMock(data=[])

        metrics = await service.get_metrics()
        assert metrics["total_orgs"] == 5
        assert metrics["total_users"] == 42
        assert metrics["total_submissions"] == 1200
        assert "submission_volume_trend" in metrics
        assert "recently_created_orgs" in metrics
        assert "tier_limit_alerts" in metrics

    async def test_refresh_materialized_view(self, service, mock_client):
        mock_client.rpc.return_value.execute.return_value = mocker.MagicMock(data=None)
        await service.refresh_materialized_view()
        mock_client.rpc.assert_called_once_with("refresh_platform_metrics_mv", {})

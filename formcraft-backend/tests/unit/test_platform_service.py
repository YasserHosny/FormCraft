"""Platform admin backend tests (F039)."""

from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi import HTTPException
from pytest_mock import MockerFixture

from app.services.platform_service import PlatformService


class TestPlatformService:
    @pytest.fixture
    def mock_client(self, mocker: MockerFixture):
        client = mocker.MagicMock()
        client.table.return_value.select.return_value.eq.return_value.execute.return_value = mocker.MagicMock(
            data=[], count=0
        )
        # Rate limit chain: .eq("user_id").eq("action").gte("created_at").execute()
        client.table.return_value.select.return_value.eq.return_value.eq.return_value.gte.return_value.execute.return_value = mocker.MagicMock(
            count=0
        )
        return client

    @pytest.fixture
    def service(self, mock_client):
        return PlatformService(mock_client)

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------

    async def test_create_organization_success(self, service, mock_client, mocker: MockerFixture):
        org_id = str(uuid4())
        mock_client.table.return_value.insert.return_value.execute.return_value = mocker.MagicMock(
            data=[{"id": org_id, "name_ar": "Test Org"}]
        )
        result = await service.create_organization(
            data={"name_ar": "Test Org", "subscription_tier": "starter"},
            created_by=uuid4(),
        )
        assert result["name_ar"] == "Test Org"

    async def test_create_organization_domain_conflict(self, service, mock_client, mocker: MockerFixture):
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mocker.MagicMock(
            data=[{"id": str(uuid4())}]
        )
        with pytest.raises(HTTPException) as exc:
            await service.create_organization(
                data={"name_ar": "Test Org", "domain": "example.com"},
                created_by=uuid4(),
            )
        assert exc.value.status_code == 409

    async def test_create_organization_rate_limit(self, service, mock_client, mocker: MockerFixture):
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.gte.return_value.execute.return_value = mocker.MagicMock(
            count=10
        )
        with pytest.raises(HTTPException) as exc:
            await service.create_organization(
                data={"name_ar": "Test Org"},
                created_by=uuid4(),
            )
        assert exc.value.status_code == 429

    # ------------------------------------------------------------------
    # SUSPEND / REACTIVATE
    # ------------------------------------------------------------------

    async def test_suspend_organization(self, service, mock_client, mocker: MockerFixture):
        org_id = uuid4()
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = mocker.MagicMock(
            data=[{"id": str(org_id), "status": "suspended"}]
        )
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mocker.MagicMock(
            data=[]
        )
        result = await service.suspend_organization(org_id=org_id, admin_id=uuid4())
        assert result["status"] == "suspended"

    async def test_reactivate_organization(self, service, mock_client, mocker: MockerFixture):
        org_id = uuid4()
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = mocker.MagicMock(
            data=[{"id": str(org_id), "status": "active"}]
        )
        result = await service.reactivate_organization(org_id=org_id, admin_id=uuid4())
        assert result["status"] == "active"

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------

    async def test_delete_organization_blocked_with_submissions(self, service, mock_client, mocker: MockerFixture):
        org_id = uuid4()
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mocker.MagicMock(
            count=5
        )
        with pytest.raises(HTTPException) as exc:
            await service.delete_organization(org_id=org_id, deleted_by=uuid4())
        assert exc.value.status_code == 400

    # ------------------------------------------------------------------
    # LIST
    # ------------------------------------------------------------------

    async def test_list_organizations_with_filters(self, service, mock_client, mocker: MockerFixture):
        org_id = str(uuid4())
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.or_.return_value.order.return_value.range.return_value.execute.return_value = mocker.MagicMock(
            data=[{"id": org_id, "name_ar": "Org 1"}],
            count=1,
        )
        orgs, total = await service.list_organizations(
            search="Org", tier="starter", status="active", sort_by="name_ar", sort_order="asc"
        )
        assert len(orgs) == 1
        assert total == 1

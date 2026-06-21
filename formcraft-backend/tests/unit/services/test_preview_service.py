import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from app.services.preview_service import PreviewService


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def service(mock_client):
    return PreviewService(mock_client)


class TestGeneratePreview:
    @pytest.mark.asyncio
    async def test_policy_not_found(self, service, mock_client):
        org_id = uuid4()
        policy_id = uuid4()
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value.data = None
        with pytest.raises(ValueError, match="Policy not found"):
            await service.generate_preview(org_id, policy_id)

    @pytest.mark.asyncio
    async def test_preview_success(self, service, mock_client):
        org_id = uuid4()
        policy_id = uuid4()
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.single.return_value.execute.return_value.data = {
            "id": str(policy_id),
            "org_id": str(org_id),
            "data_class": "submission",
            "action": "archive",
            "period_days": 365,
            "effective_date": "2026-05-26T00:00:00+00:00",
            "scope_json": {},
        }
        mock_client.table.return_value.select.return_value.eq.return_value.lt.return_value.limit.return_value.execute.return_value.count = 150
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.count = 3
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.count = 3
        result = await service.generate_preview(org_id, policy_id)
        assert result.affected_count == 150
        assert result.blocked_records == 3

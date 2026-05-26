import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from app.models.retention_policy import RetentionPolicyCreate, RetentionPolicyUpdate
from app.services.retention_policy_service import RetentionPolicyService


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def service(mock_client):
    return RetentionPolicyService(mock_client)


class TestCreatePolicy:
    def test_create_policy_success(self, service, mock_client):
        org_id = uuid4()
        created_by = uuid4()
        data = RetentionPolicyCreate(
            name={"ar": "سياسة", "en": "Policy"},
            data_class="submission",
            action="archive",
            period_days=365,
            effective_date="2026-01-01T00:00:00+00:00",
        )
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        mock_client.table.return_value.insert.return_value.execute.return_value.data = [
            {
                "id": str(uuid4()),
                "org_id": str(org_id),
                "name": '{"ar": "سياسة", "en": "Policy"}',
                "data_class": "submission",
                "action": "archive",
                "period_days": 365,
                "legal_basis": None,
                "approval_required": True,
                "effective_date": "2026-01-01T00:00:00+00:00",
                "created_by": str(created_by),
                "created_at": "2026-01-01T00:00:00+00:00",
                "updated_at": "2026-01-01T00:00:00+00:00",
            }
        ]
        result = service.create_policy(org_id, data, created_by)
        assert result.data_class == "submission"

    def test_create_policy_conflict(self, service, mock_client):
        org_id = uuid4()
        created_by = uuid4()
        data = RetentionPolicyCreate(
            name={"ar": "سياسة", "en": "Policy"},
            data_class="submission",
            action="archive",
            period_days=365,
            effective_date="2026-01-01T00:00:00+00:00",
        )
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
            {"id": str(uuid4())}
        ]
        with pytest.raises(ValueError, match="RETENTION_POLICY_CONFLICT"):
            service.create_policy(org_id, data, created_by)


class TestUpdatePolicy:
    def test_update_blocked_by_active_job(self, service, mock_client):
        org_id = uuid4()
        policy_id = uuid4()
        data = RetentionPolicyUpdate(period_days=180)
        mock_client.table.return_value.select.return_value.eq.return_value.in_.return_value.execute.return_value.data = [
            {"id": str(uuid4())}
        ]
        with pytest.raises(ValueError, match="RETENTION_JOB_ACTIVE"):
            service.update_policy(org_id, policy_id, data)


class TestDeletePolicy:
    def test_delete_blocked_by_existing_job(self, service, mock_client):
        org_id = uuid4()
        policy_id = uuid4()
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": str(uuid4())}
        ]
        with pytest.raises(ValueError, match="RETENTION_JOB_ACTIVE"):
            service.delete_policy(org_id, policy_id)

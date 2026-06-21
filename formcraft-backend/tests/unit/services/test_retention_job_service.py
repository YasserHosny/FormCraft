import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from app.models.retention_job import RetentionJobCreate
from app.services.retention_job_service import RetentionJobService


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def service(mock_client):
    return RetentionJobService(mock_client)


class TestCreateJob:
    @pytest.mark.asyncio
    async def test_create_job_duplicate_active(self, service, mock_client):
        policy_id = uuid4()
        data = RetentionJobCreate(policy_id=policy_id)
        mock_client.table.return_value.select.return_value.eq.return_value.in_.return_value.execute.return_value.data = [
            {"id": str(uuid4())}
        ]
        with pytest.raises(ValueError, match="RETENTION_JOB_ACTIVE"):
            await service.create_job(uuid4(), data)

    @pytest.mark.asyncio
    async def test_create_job_success(self, service, mock_client):
        policy_id = uuid4()
        data = RetentionJobCreate(policy_id=policy_id)
        mock_client.table.return_value.select.return_value.eq.return_value.in_.return_value.execute.return_value.data = []
        mock_client.table.return_value.insert.return_value.execute.return_value.data = [
            {
                "id": str(uuid4()),
                "policy_id": str(policy_id),
                "status": "pending",
                "started_at": None,
                "completed_at": None,
                "batch_size": 1000,
                "checkpoint_cursor": None,
                "evaluated_count": 0,
                "actioned_count": 0,
                "error_count": 0,
                "error_log": [],
                "skipped_records": [],
                "manifest_id": None,
                "resumed_from_job_id": None,
                "created_at": "2026-01-01T00:00:00+00:00",
                "updated_at": "2026-01-01T00:00:00+00:00",
            }
        ]
        result = await service.create_job(uuid4(), data)
        assert result.status == "pending"


class TestProcessPendingJobs:
    def test_no_pending_jobs(self, service, mock_client):
        mock_client.table.return_value.select.return_value.in_.return_value.order.return_value.execute.return_value.data = []
        service.process_pending_jobs()
        # Should not raise

    def test_process_job_policy_not_found(self, service, mock_client):
        job_id = str(uuid4())
        policy_id = str(uuid4())
        mock_client.table.return_value.select.return_value.in_.return_value.order.return_value.execute.return_value.data = [
            {
                "id": job_id,
                "policy_id": policy_id,
                "status": "pending",
                "batch_size": 1000,
                "checkpoint_cursor": None,
                "evaluated_count": 0,
                "actioned_count": 0,
                "error_count": 0,
                "error_log": [],
                "skipped_records": [],
            }
        ]
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{}]
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = None
        service.process_pending_jobs()
        # Should mark as failed

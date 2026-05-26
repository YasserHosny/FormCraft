from uuid import uuid4

from app.services.batch_service import BatchService


class TestBatchService:
    def test_service_init(self):
        svc = BatchService()
        assert svc.data_source_service is not None
        assert svc.validation_service is not None
        assert svc.generation_service is not None

    def test_job_to_dict_roundtrip(self):
        svc = BatchService()
        from app.schemas.batch import BatchJob
        from datetime import datetime
        job = BatchJob(
            id=uuid4(),
            org_id=uuid4(),
            template_id=uuid4(),
            template_version=1,
            created_by=uuid4(),
            name="Test Job",
            data_source_type="csv",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        d = svc._job_to_dict(job)
        restored = svc._dict_to_job(d)
        assert restored.name == job.name
        assert restored.status == job.status

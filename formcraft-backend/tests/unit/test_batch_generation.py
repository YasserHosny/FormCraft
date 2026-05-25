import pytest
import asyncio
from uuid import uuid4

from app.services.batch_generation_service import BatchGenerationService


class TestBatchGenerationService:
    @pytest.mark.asyncio
    async def test_generate_batch_empty(self):
        svc = BatchGenerationService()
        success, fail, errors, artifact = await svc.generate_batch(
            job_id=uuid4(),
            org_id=uuid4(),
            template_id=uuid4(),
            template_version=1,
            rows=[],
            column_mapping={},
            download_format="zip",
            supabase_client=None,
        )
        assert success == 0
        assert fail == 0
        assert errors == []
        assert artifact is None

    @pytest.mark.asyncio
    async def test_generate_batch_single_row(self):
        svc = BatchGenerationService()
        success, fail, errors, artifact = await svc.generate_batch(
            job_id=uuid4(),
            org_id=uuid4(),
            template_id=uuid4(),
            template_version=1,
            rows=[{"name": "Test"}],
            column_mapping={"name": "customer_name"},
            download_format="zip",
            supabase_client=None,
        )
        assert success == 1
        assert fail == 0
        assert artifact is not None

    def test_cancel_job_sets_flag(self):
        svc = BatchGenerationService()
        job_id = uuid4()
        svc.cancel_job(job_id)
        assert svc._cancel_flags[str(job_id)] is True

    def test_build_zip(self):
        svc = BatchGenerationService()
        pdfs = [{"submission_id": uuid4(), "pdf_bytes": b"fake pdf bytes"}]
        zip_bytes = svc._build_zip(pdfs)
        assert isinstance(zip_bytes, bytes)
        assert len(zip_bytes) > 0

from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException

from app.services.signature_evidence_service import SignatureEvidenceService
from tests.conftest import make_supabase_response

REQUEST_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


class TestSignatureEvidenceService:
    def test_compute_document_hash_consistency(self):
        client = MagicMock()
        service = SignatureEvidenceService(client)
        h1 = service.compute_document_hash(b"hello")
        h2 = service.compute_document_hash(b"hello")
        assert h1 == h2
        assert len(h1) == 64

    @pytest.mark.asyncio
    async def test_create_evidence_package_stores_record(self):
        client = MagicMock()
        table = MagicMock()
        chain = MagicMock()
        chain.execute.return_value = make_supabase_response([{"id": str(uuid4())}])
        table.insert.return_value = chain
        client.table.return_value = table

        service = SignatureEvidenceService(client)
        result = await service.create_evidence_package(
            request_id=REQUEST_ID,
            original_pdf_path="original.pdf",
            sealed_pdf_path="sealed.pdf",
            signer_snapshot=[{"name": "Alice"}],
            event_summary=[{"type": "signed"}],
        )
        assert "id" in result
        table.insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_integrity_missing_evidence_raises_404(self):
        client = MagicMock()
        table = MagicMock()
        chain = MagicMock()
        chain.single.return_value = chain
        chain.execute.return_value = make_supabase_response(None)
        table.select.return_value = chain
        client.table.return_value = table

        service = SignatureEvidenceService(client)
        with pytest.raises(HTTPException) as exc:
            await service.verify_integrity(UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"))
        assert exc.value.status_code == 404

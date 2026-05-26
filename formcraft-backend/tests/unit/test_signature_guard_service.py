from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException

from app.services.signature_guard_service import SignatureGuardService
from tests.conftest import make_supabase_response

SUBMISSION_ID = UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")


def _make_client(request_data=None):
    client = MagicMock()
    table = MagicMock()
    chain = MagicMock()
    chain.eq.return_value = chain
    chain.execute.return_value = make_supabase_response(request_data or [])
    table.select.return_value = chain
    client.table.return_value = table
    return client


class TestSignatureGuardService:
    @pytest.mark.asyncio
    async def test_no_signature_requests_allows_modification(self):
        client = _make_client([])
        service = SignatureGuardService(client)
        await service.assert_modification_allowed(SUBMISSION_ID)
        # No exception expected

    @pytest.mark.asyncio
    async def test_active_signature_request_blocks_modification(self):
        client = _make_client([{"id": str(uuid4()), "status": "in_progress"}])
        service = SignatureGuardService(client)
        with pytest.raises(HTTPException) as exc:
            await service.assert_modification_allowed(SUBMISSION_ID)
        assert exc.value.status_code == 409

    @pytest.mark.asyncio
    async def test_canceled_signature_request_allows_modification(self):
        client = _make_client([{"id": str(uuid4()), "status": "canceled"}])
        service = SignatureGuardService(client)
        await service.assert_modification_allowed(SUBMISSION_ID)
        # No exception expected

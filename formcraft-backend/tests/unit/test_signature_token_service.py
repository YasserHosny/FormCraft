from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException

from app.services.signature_token_service import SignatureTokenService
from tests.conftest import make_supabase_response

RECIPIENT_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
REQUEST_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


def _make_client(recipient_data=None):
    client = MagicMock()
    table = MagicMock()
    chain = MagicMock()
    chain.eq.return_value = chain
    chain.single.return_value = chain
    chain.execute.return_value = make_supabase_response(recipient_data or {})
    table.update.return_value = chain
    client.table.return_value = table
    return client


class TestSignatureTokenService:
    @pytest.mark.asyncio
    async def test_generate_token_returns_urlsafe_string(self):
        client = MagicMock()
        service = SignatureTokenService(client)
        token = service.generate_token()
        assert len(token) > 20
        assert " " not in token

    @pytest.mark.asyncio
    async def test_hash_token_is_deterministic(self):
        client = MagicMock()
        service = SignatureTokenService(client)
        t1 = service.hash_token("abc")
        t2 = service.hash_token("abc")
        assert t1 == t2
        assert len(t1) == 64  # SHA-256 hex

    @pytest.mark.asyncio
    async def test_validate_token_not_found_raises_404(self):
        client = _make_client()
        service = SignatureTokenService(client)
        with pytest.raises(HTTPException) as exc:
            await service.validate_token("nonexistent")
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_validate_token_expired_raises_404(self):
        past = "2020-01-01T00:00:00+00:00"
        client = _make_client(
            {
                "id": str(RECIPIENT_ID),
                "token_expires_at": past,
                "signature_requests": {"status": "sent"},
            }
        )
        service = SignatureTokenService(client)
        with pytest.raises(HTTPException) as exc:
            await service.validate_token("some-token")
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_validate_token_canceled_request_raises_410(self):
        client = _make_client(
            {
                "id": str(RECIPIENT_ID),
                "token_expires_at": "2099-01-01T00:00:00+00:00",
                "signature_requests": {"status": "canceled"},
            }
        )
        service = SignatureTokenService(client)
        with pytest.raises(HTTPException) as exc:
            await service.validate_token("some-token")
        assert exc.value.status_code == 410

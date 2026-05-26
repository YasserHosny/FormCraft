from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException

from app.services.signer_identity_service import SignerIdentityService
from tests.conftest import make_supabase_response

RECIPIENT_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


def _make_client(recipient_data=None):
    client = MagicMock()
    table = MagicMock()
    chain = MagicMock()
    chain.eq.return_value = chain
    chain.single.return_value = chain
    chain.execute.return_value = make_supabase_response(recipient_data or {})
    table.update.return_value = chain
    table.select.return_value = chain
    client.table.return_value = table
    return client


class TestSignerIdentityService:
    @pytest.mark.asyncio
    async def test_send_external_otp_generates_6_digit_code(self):
        client = _make_client({"id": str(RECIPIENT_ID), "email": "test@example.com"})
        service = SignerIdentityService(client)
        result = await service.send_external_otp(RECIPIENT_ID, "test@example.com")
        assert result["message"] == "OTP sent"
        assert "expires_at" in result

    @pytest.mark.asyncio
    async def test_verify_external_otp_invalid_returns_false(self):
        client = _make_client(
            {
                "otp_code_hash": "badhash",
                "otp_expires_at": "2099-01-01T00:00:00+00:00",
                "status": "viewed",
            }
        )
        service = SignerIdentityService(client)
        ok = await service.verify_external_otp(RECIPIENT_ID, "123456")
        assert ok is False

    @pytest.mark.asyncio
    async def test_verify_external_otp_expired_returns_false(self):
        client = _make_client(
            {
                "otp_code_hash": "hash",
                "otp_expires_at": "2020-01-01T00:00:00+00:00",
                "status": "viewed",
            }
        )
        service = SignerIdentityService(client)
        ok = await service.verify_external_otp(RECIPIENT_ID, "123456")
        assert ok is False

    @pytest.mark.asyncio
    async def test_mark_internal_verified_updates_status(self):
        client = _make_client()
        service = SignerIdentityService(client)
        await service.mark_internal_verified(RECIPIENT_ID)
        update_call = client.table.return_value.update.call_args
        assert update_call[0][0]["status"] == "verified"

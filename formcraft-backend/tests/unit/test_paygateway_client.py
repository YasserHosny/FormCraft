from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.services.paygateway_client import PayGatewayClient, PayGatewayError


class _Response:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload


@pytest.mark.asyncio
async def test_create_payment_maps_checkout_payload():
    client = PayGatewayClient(base_url="https://pay.example", service_key="key")
    response = _Response(
        payload={
            "payment_id": "pay_1",
            "client_token": "tok_1",
            "requires_action": True,
            "expires_at": "2026-06-19T10:15:00Z",
            "status": "requires_action",
        }
    )
    http_client = MagicMock()
    http_client.request = AsyncMock(return_value=response)

    with patch("app.services.paygateway_client.httpx.AsyncClient") as async_client:
        async_client.return_value.__aenter__.return_value = http_client
        checkout = await client.create_payment(
            purchase_id="purchase-1",
            amount_minor=1000,
            currency="EGP",
            idempotency_key="key-1",
            return_url="https://app.example",
        )

    assert checkout.payment_id == "pay_1"
    assert checkout.client_token == "tok_1"
    assert checkout.requires_action is True


@pytest.mark.asyncio
async def test_get_payment_status_maps_provider_payload():
    client = PayGatewayClient(base_url="https://pay.example", service_key="key")
    http_client = MagicMock()
    http_client.request = AsyncMock(return_value=_Response(payload={"status": "succeeded"}))

    with patch("app.services.paygateway_client.httpx.AsyncClient") as async_client:
        async_client.return_value.__aenter__.return_value = http_client
        status = await client.get_payment_status("pay_1")

    assert status["status"] == "succeeded"


@pytest.mark.asyncio
async def test_refund_payment_uses_idempotency_key():
    client = PayGatewayClient(base_url="https://pay.example", service_key="key")
    http_client = MagicMock()
    http_client.request = AsyncMock(return_value=_Response(payload={"refund_id": "ref_1", "status": "succeeded"}))

    with patch("app.services.paygateway_client.httpx.AsyncClient") as async_client:
        async_client.return_value.__aenter__.return_value = http_client
        refund = await client.refund_payment(
            payment_id="pay_1",
            amount_minor=1000,
            currency="EGP",
            idempotency_key="refund-1",
        )

    assert refund["refund_id"] == "ref_1"
    assert http_client.request.call_args.kwargs["headers"]["Idempotency-Key"] == "refund-1"


@pytest.mark.asyncio
async def test_provider_errors_are_mapped():
    client = PayGatewayClient(base_url="https://pay.example", service_key="key")
    http_client = MagicMock()
    http_client.request = AsyncMock(return_value=_Response(status_code=429, payload={"code": "rate_limited"}))

    with patch("app.services.paygateway_client.httpx.AsyncClient") as async_client:
        async_client.return_value.__aenter__.return_value = http_client
        with pytest.raises(PayGatewayError) as exc_info:
            await client.get_payment_status("pay_1")

    assert exc_info.value.code == "rate_limited"
    assert exc_info.value.status_code == 429


@pytest.mark.asyncio
async def test_timeout_maps_to_provider_timeout():
    client = PayGatewayClient(base_url="https://pay.example", service_key="key")
    http_client = MagicMock()
    http_client.request = AsyncMock(side_effect=httpx.TimeoutException("slow"))

    with patch("app.services.paygateway_client.httpx.AsyncClient") as async_client:
        async_client.return_value.__aenter__.return_value = http_client
        with pytest.raises(PayGatewayError) as exc_info:
            await client.get_payment_status("pay_1")

    assert exc_info.value.code == "provider_timeout"


def test_webhook_signature_verification():
    client = PayGatewayClient(base_url="https://pay.example", service_key="key", webhook_secret="secret")
    import hmac
    import hashlib

    body = b'{"event_id":"evt_1"}'
    signature = hmac.new(b"secret", body, hashlib.sha256).hexdigest()

    assert client.verify_webhook_signature(body=body, signature=signature) is True
    assert client.verify_webhook_signature(body=body, signature="bad") is False

"""Backend-only PayGateway client for F058 billing."""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from app.core.config import settings


class PayGatewayError(RuntimeError):
    def __init__(self, message: str, *, code: str = "provider_error", status_code: int = 503):
        super().__init__(message)
        self.code = code
        self.status_code = status_code


@dataclass(frozen=True)
class PayGatewayCheckout:
    payment_id: str
    client_token: str
    requires_action: bool
    expires_at: datetime
    status: str


class PayGatewayClient:
    def __init__(
        self,
        *,
        base_url: str | None = None,
        service_key: str | None = None,
        webhook_secret: str | None = None,
        timeout: float | None = None,
    ):
        self.base_url = (base_url if base_url is not None else settings.PAYGATEWAY_BASE_URL).rstrip("/")
        self.service_key = service_key if service_key is not None else settings.PAYGATEWAY_SERVICE_KEY
        self.webhook_secret = webhook_secret if webhook_secret is not None else settings.PAYGATEWAY_WEBHOOK_SECRET
        self.timeout = timeout if timeout is not None else settings.PAYGATEWAY_TIMEOUT_SECONDS

    async def create_payment(
        self,
        *,
        purchase_id: str,
        amount_minor: int,
        currency: str,
        idempotency_key: str,
        return_url: str | None,
    ) -> PayGatewayCheckout:
        payload: dict[str, Any] = {
            "amount": amount_minor,
            "currency": currency,
            "metadata": {"purchase_reference": purchase_id},
        }
        if return_url:
            payload["description"] = f"FormCraft purchase {purchase_id}"
        data = await self._request("POST", "/api/v1/payments", json=payload, idempotency_key=idempotency_key)
        pg_status = str(data.get("status", "created"))
        return PayGatewayCheckout(
            payment_id=str(data["id"]),
            client_token=str(data.get("client_secret") or ""),
            requires_action=pg_status in {"requires_action", "requires_authentication"},
            expires_at=self._parse_datetime(data.get("expires_at")),
            status=pg_status,
        )

    async def get_payment_status(self, payment_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/api/v1/payments/{payment_id}")

    async def refund_payment(self, *, payment_id: str, amount_minor: int, currency: str, idempotency_key: str) -> dict[str, Any]:
        payload = {"amount": amount_minor}
        return await self._request("POST", f"/api/v1/payments/{payment_id}/refund", json=payload, idempotency_key=idempotency_key)

    # ------------------------------------------------------------------
    # F059 — Subscription + Customer methods
    # ------------------------------------------------------------------

    async def create_customer(self, *, email: str, name: str) -> dict[str, Any]:
        """Create a Stripe Customer. Returns {"id": "cus_...", "email": "..."}."""
        return await self._request("POST", "/api/v1/customers", json={"email": email, "name": name})

    async def create_subscription(
        self,
        *,
        customer_id: str,
        price_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"customer_id": customer_id, "price_id": price_id, "metadata": metadata or {}}
        return await self._request("POST", "/api/v1/subscriptions", json=payload)

    async def get_subscription(self, subscription_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/api/v1/subscriptions/{subscription_id}")

    async def upgrade_subscription(self, *, subscription_id: str, new_price_id: str) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"/api/v1/subscriptions/{subscription_id}/upgrade",
            json={"new_price_id": new_price_id},
        )

    async def cancel_subscription(self, subscription_id: str) -> dict[str, Any]:
        return await self._request("POST", f"/api/v1/subscriptions/{subscription_id}/cancel")

    async def reactivate_subscription(self, subscription_id: str) -> dict[str, Any]:
        return await self._request("POST", f"/api/v1/subscriptions/{subscription_id}/reactivate")

    async def get_portal_url(self, *, customer_id: str, return_url: str) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"/api/v1/customers/{customer_id}/portal",
            json={"return_url": return_url},
        )

    # ------------------------------------------------------------------

    def verify_webhook_signature(self, *, body: bytes, signature: str | None) -> bool:
        if not self.webhook_secret or not signature:
            return False
        expected = hmac.new(self.webhook_secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    async def _request(self, method: str, path: str, *, json: dict[str, Any] | None = None, idempotency_key: str | None = None) -> dict[str, Any]:
        if not self.base_url or not self.service_key:
            raise PayGatewayError("PayGateway is not configured", code="provider_unavailable")
        headers = {"Authorization": f"Bearer {self.service_key}"}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(method, f"{self.base_url}{path}", json=json, headers=headers)
        except httpx.TimeoutException as exc:
            raise PayGatewayError("PayGateway request timed out", code="provider_timeout") from exc
        except httpx.HTTPError as exc:
            raise PayGatewayError("PayGateway request failed", code="provider_unavailable") from exc
        if response.status_code >= 400:
            code = "provider_error"
            try:
                code = response.json().get("code", code)
            except ValueError:
                pass
            raise PayGatewayError("PayGateway returned an error", code=code, status_code=response.status_code)
        return response.json()

    @staticmethod
    def _parse_datetime(value: Any) -> datetime:
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                pass
        return datetime.now(UTC) + timedelta(minutes=15)

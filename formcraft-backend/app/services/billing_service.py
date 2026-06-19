"""Billing orchestration service for PayGateway purchases (F058)."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import HTTPException, status

from app.core.audit import AuditLogger
from app.schemas.billing import BillingFulfillmentSource, BillingPurpose
from app.services.paygateway_client import PayGatewayClient, PayGatewayError


TIER_ORDER = ["starter", "professional", "enterprise", "platform"]


class BillingService:
    def __init__(self, client, paygateway: PayGatewayClient | None = None):
        self.client = client
        self.paygateway = paygateway or PayGatewayClient()

    async def get_options(self, *, org_id: UUID, purpose: BillingPurpose | None = None, listing_id: UUID | None = None) -> dict:
        org = self._get_org(org_id)
        currency = org.get("default_currency") or "SAR"
        current_tier = org.get("subscription_tier", "starter")
        tiers = self._tier_options(current_tier=current_tier, currency=currency)
        addons = self._addon_options(currency=currency, purpose=purpose, listing_id=listing_id)
        return {"currency": currency, "current_tier": current_tier, "tiers": tiers, "addons": addons}

    async def create_purchase(
        self,
        *,
        org_id: UUID,
        actor_id: UUID,
        purpose: BillingPurpose,
        target: dict,
        quantity: int | None,
        return_url: str | None,
    ) -> dict:
        org = self._get_org(org_id)
        currency = org.get("default_currency") or "SAR"
        amount_minor, normalized_target, normalized_quantity = self._compute_amount(
            org=org,
            purpose=purpose,
            target=target,
            quantity=quantity,
            currency=currency,
        )
        purchase_id = uuid4()
        idempotency_key = f"billing:{purchase_id}"
        row = {
            "id": str(purchase_id),
            "organization_id": str(org_id),
            "created_by": str(actor_id),
            "purpose": purpose.value,
            "target": normalized_target,
            "quantity": normalized_quantity,
            "currency": currency,
            "amount_minor": amount_minor,
            "status": "created",
            "idempotency_key": idempotency_key,
        }
        self.client.table("billing_purchases").insert(row).execute()

        if amount_minor == 0:
            await self.fulfill_purchase_once(purchase_id=purchase_id, actor_id=actor_id, source=BillingFulfillmentSource.ZERO_AMOUNT)
            return {
                "purchase_id": purchase_id,
                "status": "succeeded",
                "amount_minor": amount_minor,
                "currency": currency,
                "checkout": None,
                "message_key": "billing.purchase.fulfilled",
            }

        try:
            checkout = await self.paygateway.create_payment(
                purchase_id=str(purchase_id),
                amount_minor=amount_minor,
                currency=currency,
                idempotency_key=idempotency_key,
                return_url=return_url,
            )
        except PayGatewayError as exc:
            self.client.table("billing_purchases").update(
                {"status": "failed", "failure_code": exc.code, "failure_message_key": self._message_key(exc.code)}
            ).eq("id", str(purchase_id)).execute()
            raise HTTPException(status_code=exc.status_code, detail=self._message_key(exc.code)) from exc

        self.client.table("billing_purchases").update(
            {
                "provider_payment_id": checkout.payment_id,
                "provider_checkout_token_hash": checkout.client_token[:16],
                "provider_status": checkout.status,
                "status": "requires_action" if checkout.requires_action else "created",
            }
        ).eq("id", str(purchase_id)).execute()
        return {
            "purchase_id": purchase_id,
            "status": "requires_action" if checkout.requires_action else "created",
            "amount_minor": amount_minor,
            "currency": currency,
            "checkout": {
                "provider": "paygateway",
                "client_token": checkout.client_token,
                "requires_action": checkout.requires_action,
                "expires_at": checkout.expires_at,
            },
        }

    async def verify_purchase(self, *, org_id: UUID | None, purchase_id: UUID, actor_id: UUID, provider_payment_id: str | None = None) -> dict:
        purchase = self._get_purchase(purchase_id)
        self._assert_org_access(purchase, org_id)
        payment_id = provider_payment_id or purchase.get("provider_payment_id")
        if not payment_id and purchase["amount_minor"] > 0:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "billing.payment_missing")
        if purchase["amount_minor"] == 0:
            fulfilled = await self.fulfill_purchase_once(purchase_id=purchase_id, actor_id=actor_id, source=BillingFulfillmentSource.ZERO_AMOUNT)
            return {"purchase_id": purchase_id, "status": "succeeded", "fulfilled": fulfilled, "message_key": "billing.purchase.fulfilled"}
        status_payload = await self.paygateway.get_payment_status(str(payment_id))
        provider_status = status_payload.get("status")
        if provider_status in {"succeeded", "completed", "paid"}:
            self.client.table("billing_purchases").update({"status": "succeeded", "provider_status": provider_status}).eq("id", str(purchase_id)).execute()
            fulfilled = await self.fulfill_purchase_once(purchase_id=purchase_id, actor_id=actor_id, source=BillingFulfillmentSource.STATUS_POLL)
            return {"purchase_id": purchase_id, "status": "succeeded", "fulfilled": fulfilled, "message_key": "billing.purchase.fulfilled"}
        if provider_status in {"requires_action", "requires_authentication"}:
            self.client.table("billing_purchases").update({"status": "requires_action", "provider_status": provider_status}).eq("id", str(purchase_id)).execute()
            return {"purchase_id": purchase_id, "status": "requires_action", "fulfilled": False, "message_key": "billing.payment.requires_action"}
        self.client.table("billing_purchases").update({"status": "failed", "provider_status": provider_status, "failure_message_key": "billing.payment.failed"}).eq("id", str(purchase_id)).execute()
        return {"purchase_id": purchase_id, "status": "failed", "fulfilled": False, "message_key": "billing.payment.failed"}

    async def fulfill_purchase_once(self, *, purchase_id: UUID, actor_id: UUID, source: BillingFulfillmentSource) -> bool:
        purchase = self._get_purchase(purchase_id)
        existing = self.client.table("billing_fulfillments").select("id").eq("purchase_id", str(purchase_id)).execute()
        if existing.data:
            return False
        purpose = purchase["purpose"]
        effect_type = {
            "subscription_tier": "tier_changed",
            "seats": "seats_added",
            "ocr_batch": "ocr_credited",
            "marketplace_template": "template_copied",
        }[purpose]
        payload = dict(purchase.get("target") or {})
        org_id = purchase["organization_id"]
        if purpose == "subscription_tier":
            org = self._get_org(UUID(str(org_id)))
            self.client.table("billing_purchases").update(
                {
                    "previous_effect_snapshot": {"previous_tier": org.get("subscription_tier")},
                    "status": "succeeded",
                    "fulfilled_at": datetime.now(UTC).isoformat(),
                }
            ).eq("id", str(purchase_id)).execute()
            self.client.table("organizations").update({"subscription_tier": payload["tier"]}).eq("id", org_id).execute()
        elif purpose == "seats":
            self._increment_org_counter(org_id, "purchased_seat_allowance", int(purchase.get("quantity") or 0))
        elif purpose == "ocr_batch":
            self._increment_org_counter(org_id, "ocr_scan_credit_balance", int(purchase.get("quantity") or 0))
        self.client.table("billing_fulfillments").insert(
            {
                "purchase_id": str(purchase_id),
                "organization_id": org_id,
                "effect_type": effect_type,
                "effect_payload": payload,
                "applied_by": str(actor_id),
                "source": source.value,
            }
        ).execute()
        self.client.table("billing_purchases").update({"status": "succeeded"}).eq("id", str(purchase_id)).execute()
        await self._audit(actor_id, "billing.purchase.fulfilled", "billing_purchase", str(purchase_id), payload)
        return True

    def list_purchases(self, *, org_id: UUID | None, status_value: str | None = None, purpose: str | None = None, limit: int = 50) -> list[dict]:
        query = self.client.table("billing_purchases").select("*")
        if org_id:
            query = query.eq("organization_id", str(org_id))
        if status_value:
            query = query.eq("status", status_value)
        if purpose:
            query = query.eq("purpose", purpose)
        return query.order("created_at", desc=True).limit(limit).execute().data or []

    def get_purchase(self, *, purchase_id: UUID, org_id: UUID | None) -> dict:
        purchase = self._get_purchase(purchase_id)
        self._assert_org_access(purchase, org_id)
        return purchase

    def _compute_amount(self, *, org: dict, purpose: BillingPurpose, target: dict, quantity: int | None, currency: str) -> tuple[int, dict, int | None]:
        if purpose == BillingPurpose.SUBSCRIPTION_TIER:
            tier = target.get("tier")
            current = org.get("subscription_tier", "starter")
            if tier not in TIER_ORDER or TIER_ORDER.index(tier) <= TIER_ORDER.index(current):
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "billing.invalid_target")
            price = self._get_price("tier", tier, currency)
            return int(price["unit_amount_minor"]), {"tier": tier}, None
        if purpose == BillingPurpose.SEATS:
            qty = int(quantity or 0)
            if qty <= 0:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "billing.invalid_quantity")
            price = self._get_price("seat", "seat", currency)
            return int(price["unit_amount_minor"]) * qty, {"addon": "seat"}, qty
        if purpose == BillingPurpose.OCR_BATCH:
            qty = int(quantity or target.get("forms") or 0)
            if qty <= 0:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "billing.invalid_quantity")
            price = self._get_price("ocr_batch", str(target.get("package", "forms")), currency)
            return int(price["unit_amount_minor"]) * qty, {"package": target.get("package", "forms"), "forms": qty}, qty
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "billing.invalid_target")

    def _tier_options(self, *, current_tier: str, currency: str) -> list[dict]:
        current_idx = TIER_ORDER.index(current_tier) if current_tier in TIER_ORDER else 0
        return [self._option_for_tier(tier, currency) for tier in TIER_ORDER[current_idx + 1 :]]

    def _option_for_tier(self, tier: str, currency: str) -> dict:
        try:
            price = self._get_price("tier", tier, currency)
            return {"tier": tier, "amount_minor": int(price["unit_amount_minor"]), "currency": currency, "available": True, "unavailable_reason_key": None}
        except HTTPException:
            return {"tier": tier, "amount_minor": None, "currency": currency, "available": False, "unavailable_reason_key": "billing.price_unavailable"}

    def _addon_options(self, *, currency: str, purpose: BillingPurpose | None, listing_id: UUID | None) -> list[dict]:
        options = []
        for price_type, target, billing_purpose in [("seat", "seat", BillingPurpose.SEATS), ("ocr_batch", "forms", BillingPurpose.OCR_BATCH)]:
            if purpose and purpose != billing_purpose:
                continue
            try:
                price = self._get_price(price_type, target, currency)
                options.append({"purpose": billing_purpose.value, "unit_amount_minor": int(price["unit_amount_minor"]), "currency": currency, "min_quantity": price.get("min_quantity"), "max_quantity": price.get("max_quantity"), "available": True})
            except HTTPException:
                options.append({"purpose": billing_purpose.value, "unit_amount_minor": None, "currency": currency, "available": False, "unavailable_reason_key": "billing.price_unavailable"})
        return options

    def _get_price(self, price_type: str, target_key: str, currency: str) -> dict:
        result = self.client.table("billing_prices").select("*").eq("price_type", price_type).eq("target_key", target_key).eq("currency", currency).eq("is_active", True).limit(1).execute()
        if not result.data:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "billing.price_unavailable")
        return result.data[0]

    def _get_org(self, org_id: UUID) -> dict:
        result = self.client.table("organizations").select("*").eq("id", str(org_id)).single().execute()
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "billing.organization_not_found")
        return result.data

    def _get_purchase(self, purchase_id: UUID) -> dict:
        result = self.client.table("billing_purchases").select("*").eq("id", str(purchase_id)).single().execute()
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "billing.purchase_not_found")
        return result.data

    @staticmethod
    def _assert_org_access(purchase: dict, org_id: UUID | None):
        if org_id and str(purchase.get("organization_id")) != str(org_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "billing.purchase_not_found")

    def _increment_org_counter(self, org_id: str, column: str, delta: int):
        org = self._get_org(UUID(str(org_id)))
        self.client.table("organizations").update({column: int(org.get(column) or 0) + delta}).eq("id", org_id).execute()

    async def _audit(self, actor_id: UUID, action: str, resource_type: str, resource_id: str, metadata: dict):
        await AuditLogger(self.client).log_event(
            user_id=str(actor_id),
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata,
        )

    @staticmethod
    def _message_key(code: str) -> str:
        return {
            "provider_timeout": "billing.provider_unavailable",
            "provider_unavailable": "billing.provider_unavailable",
            "rate_limited": "billing.provider_rate_limited",
            "card_declined": "billing.payment.declined",
        }.get(code, "billing.provider_error")

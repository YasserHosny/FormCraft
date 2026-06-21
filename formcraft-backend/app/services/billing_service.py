"""Billing orchestration service for PayGateway purchases (F058)."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID, uuid4

from fastapi import HTTPException, status

from app.core.audit import AuditLogger
from app.schemas.billing import BillingFulfillmentSource, BillingPurpose
from app.services.paygateway_client import PayGatewayClient, PayGatewayError


TIER_ORDER = ["starter", "professional", "enterprise", "platform"]
PUBLISHER_SHARE_PCT = Decimal("0.70")


class BillingService:
    def __init__(self, client, paygateway: PayGatewayClient | None = None):
        self.client = client
        self.paygateway = paygateway or PayGatewayClient()

    # ------------------------------------------------------------------
    # Options
    # ------------------------------------------------------------------

    async def get_options(self, *, org_id: UUID, purpose: BillingPurpose | None = None, listing_id: UUID | None = None) -> dict:
        org = self._get_org(org_id)
        currency = org.get("default_currency") or "SAR"
        current_tier = org.get("subscription_tier", "starter")
        tiers = self._tier_options(current_tier=current_tier, currency=currency)
        addons = self._addon_options(currency=currency, purpose=purpose, listing_id=listing_id)
        return {"currency": currency, "current_tier": current_tier, "tiers": tiers, "addons": addons}

    # ------------------------------------------------------------------
    # Purchase create
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Verify
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Fulfill (idempotent)
    # ------------------------------------------------------------------

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

        elif purpose == "marketplace_template":
            listing_id = payload.get("listing_id")
            if listing_id:
                listing = self._get_listing(listing_id)
                # Clone template into buyer org
                from app.services.marketplace_service import MarketplaceService
                mp = MarketplaceService(self.client)
                await mp.import_listing(
                    listing_id=UUID(str(listing_id)),
                    consumer_org_id=UUID(str(org_id)),
                    actor_id=actor_id,
                )
                # Record the 70/30 split
                gross = purchase["amount_minor"]
                publisher_share = int(Decimal(str(gross)) * PUBLISHER_SHARE_PCT.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
                platform_share = gross - publisher_share
                self.client.table("billing_marketplace_splits").insert({
                    "purchase_id": str(purchase_id),
                    "listing_id": str(listing_id),
                    "publisher_org_id": str(listing["publisher_org_id"]),
                    "buyer_org_id": str(org_id),
                    "gross_amount_minor": gross,
                    "platform_share_minor": platform_share,
                    "publisher_share_minor": publisher_share,
                    "currency": purchase["currency"],
                }).execute()

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
        self.client.table("billing_purchases").update(
            {"status": "succeeded", "fulfilled_at": datetime.now(UTC).isoformat()}
        ).eq("id", str(purchase_id)).execute()
        await self._audit(actor_id, "billing.purchase.fulfilled", "billing_purchase", str(purchase_id), payload)
        return True

    # ------------------------------------------------------------------
    # Refund (G-11 — replaces 501 stub)
    # ------------------------------------------------------------------

    async def refund_purchase(
        self,
        *,
        org_id: UUID | None,
        purchase_id: UUID,
        actor_id: UUID,
        reason: str,
        amount_minor: int | None = None,
    ) -> dict:
        from uuid import uuid4 as _uuid4
        purchase = self._get_purchase(purchase_id)
        self._assert_org_access(purchase, org_id)
        if purchase["status"] not in {"succeeded"}:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "billing.refund_not_eligible")

        # Prevent duplicate refunds
        existing_refund = self.client.table("billing_refunds").select("id,status").eq("purchase_id", str(purchase_id)).execute()
        if existing_refund.data:
            raise HTTPException(status.HTTP_409_CONFLICT, "billing.refund_already_exists")

        refund_amount = amount_minor if amount_minor is not None else purchase["amount_minor"]
        if refund_amount <= 0 or refund_amount > purchase["amount_minor"]:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "billing.refund_amount_invalid")

        is_partial = refund_amount < purchase["amount_minor"]
        refund_id = _uuid4()
        idempotency_key = f"refund:{purchase_id}"

        # Insert refund record
        self.client.table("billing_refunds").insert({
            "id": str(refund_id),
            "purchase_id": str(purchase_id),
            "organization_id": str(purchase["organization_id"]),
            "requested_by": str(actor_id),
            "reason": reason,
            "amount_minor": refund_amount,
            "currency": purchase["currency"],
            "status": "requested",
            "reversal_status": "pending",
        }).execute()

        # Call PayGateway
        provider_refund_id: str | None = None
        try:
            refund_data = await self.paygateway.refund_payment(
                payment_id=str(purchase.get("provider_payment_id") or ""),
                amount_minor=refund_amount,
                currency=purchase["currency"],
                idempotency_key=idempotency_key,
            )
            provider_refund_id = str(refund_data.get("id", ""))
            refund_status = "succeeded"
        except PayGatewayError as exc:
            self.client.table("billing_refunds").update(
                {"status": "failed", "updated_at": datetime.now(UTC).isoformat()}
            ).eq("id", str(refund_id)).execute()
            raise HTTPException(status_code=exc.status_code, detail=self._message_key(exc.code)) from exc

        # Update purchase status
        self.client.table("billing_purchases").update(
            {"status": "refunded", "provider_refund_id": provider_refund_id}
        ).eq("id", str(purchase_id)).execute()

        # Reverse fulfillment (full refunds only — partial refunds don't reverse)
        reversal_payload: dict = {}
        reversal_status = "pending"
        if not is_partial:
            reversal_payload, reversal_status = self._reverse_fulfillment(purchase)

        self.client.table("billing_refunds").update({
            "status": refund_status,
            "provider_refund_id": provider_refund_id,
            "reversal_status": reversal_status,
            "reversal_payload": reversal_payload,
            "applied_at": datetime.now(UTC).isoformat() if reversal_status == "applied" else None,
            "updated_at": datetime.now(UTC).isoformat(),
        }).eq("id", str(refund_id)).execute()

        await self._audit(actor_id, "billing.refund.issued", "billing_refund", str(refund_id), {
            "purchase_id": str(purchase_id),
            "amount_minor": refund_amount,
            "partial": is_partial,
        })
        return {
            "refund_id": refund_id,
            "purchase_id": purchase_id,
            "status": "succeeded",
            "reversal_status": reversal_status,
            "amount_minor": refund_amount,
            "currency": purchase["currency"],
            "message_key": "billing.refund.succeeded",
        }

    def _reverse_fulfillment(self, purchase: dict) -> tuple[dict, str]:
        """Reverse the effect of a fulfilled purchase. Returns (reversal_payload, reversal_status)."""
        purpose = purchase["purpose"]
        org_id = str(purchase["organization_id"])
        payload: dict = dict(purchase.get("target") or {})
        try:
            if purpose == "subscription_tier":
                snapshot = purchase.get("previous_effect_snapshot") or {}
                previous_tier = snapshot.get("previous_tier")
                if previous_tier and previous_tier in TIER_ORDER:
                    self.client.table("organizations").update({"subscription_tier": previous_tier}).eq("id", org_id).execute()
                    payload["reverted_to"] = previous_tier
            elif purpose == "seats":
                qty = int(purchase.get("quantity") or 0)
                if qty > 0:
                    org = self._get_org(UUID(org_id))
                    new_val = max(0, int(org.get("purchased_seat_allowance") or 0) - qty)
                    self.client.table("organizations").update({"purchased_seat_allowance": new_val}).eq("id", org_id).execute()
                    payload["seats_removed"] = qty
            elif purpose == "ocr_batch":
                qty = int(purchase.get("quantity") or 0)
                if qty > 0:
                    org = self._get_org(UUID(org_id))
                    new_val = max(0, int(org.get("ocr_scan_credit_balance") or 0) - qty)
                    self.client.table("organizations").update({"ocr_scan_credit_balance": new_val}).eq("id", org_id).execute()
                    payload["credits_removed"] = qty
            # marketplace_template: template already cloned, no reversal possible
            return payload, "applied"
        except Exception:
            return payload, "failed"

    # ------------------------------------------------------------------
    # List / Get
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Amount computation
    # ------------------------------------------------------------------

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

        if purpose == BillingPurpose.MARKETPLACE_TEMPLATE:
            listing_id = target.get("listing_id")
            if not listing_id:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "billing.invalid_target")
            listing = self._get_listing(str(listing_id))
            if listing.get("price_type") != "premium":
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "billing.listing_not_premium")
            raw_price = Decimal(str(listing.get("price_amount") or "0"))
            # Convert to minor units (×100)
            amount = int((raw_price * 100).to_integral_value(rounding=ROUND_HALF_UP))
            return amount, {"listing_id": str(listing_id), "listing_name": listing.get("name", "")}, None

        raise HTTPException(status.HTTP_400_BAD_REQUEST, "billing.invalid_target")

    # ------------------------------------------------------------------
    # Options helpers
    # ------------------------------------------------------------------

    def _tier_options(self, *, current_tier: str, currency: str) -> list[dict]:
        current_idx = TIER_ORDER.index(current_tier) if current_tier in TIER_ORDER else 0
        return [self._option_for_tier(tier, currency) for tier in TIER_ORDER[current_idx + 1:]]

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

    # ------------------------------------------------------------------
    # Tier limit enforcement (G-1)
    # ------------------------------------------------------------------

    def get_tier_limits(self, org_id: UUID) -> dict | None:
        org = self._get_org(org_id)
        tier = org.get("subscription_tier", "starter")
        result = self.client.table("tier_limits").select("*").eq("tier", tier).limit(1).execute()
        return result.data[0] if result.data else None

    def check_user_limit(self, org_id: UUID) -> None:
        """Raise 402 if org has reached its user capacity (profiles + pending invitations)."""
        org = self._get_org(org_id)
        tier = org.get("subscription_tier", "starter")
        limits_result = self.client.table("tier_limits").select("user_limit").eq("tier", tier).limit(1).execute()
        if not limits_result.data:
            return
        user_limit = int(limits_result.data[0]["user_limit"])
        if user_limit <= 0:
            return  # 0 means unlimited in legacy rows; negative treated same
        seat_allowance = int(org.get("purchased_seat_allowance") or 0)
        effective_limit = user_limit + seat_allowance

        active_count = self.client.table("profiles").select("id", count="exact").eq("org_id", str(org_id)).eq("is_active", True).execute()
        pending_count = self.client.table("user_invitations").select("id", count="exact").eq("org_id", str(org_id)).eq("status", "pending").execute()
        total = (active_count.count or 0) + (pending_count.count or 0)

        if total >= effective_limit:
            raise HTTPException(
                status.HTTP_402_PAYMENT_REQUIRED,
                detail="billing.user_limit_reached",
            )

    def check_submission_limit(self, org_id: UUID) -> None:
        """Raise 402 if org has reached its monthly submission cap (Starter tier only)."""
        org = self._get_org(org_id)
        tier = org.get("subscription_tier", "starter")
        limits_result = self.client.table("tier_limits").select("submissions_per_month_limit").eq("tier", tier).limit(1).execute()
        if not limits_result.data:
            return
        cap = limits_result.data[0].get("submissions_per_month_limit")
        if cap is None or int(cap) < 0:
            return  # -1 = unlimited

        now = datetime.now(UTC)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        count_result = self.client.table("submissions").select("id", count="exact").eq("org_id", str(org_id)).gte("created_at", month_start).execute()
        used = count_result.count or 0
        if used >= int(cap):
            raise HTTPException(
                status.HTTP_402_PAYMENT_REQUIRED,
                detail="billing.submission_limit_reached",
            )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

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

    def _get_listing(self, listing_id: str) -> dict:
        result = self.client.table("marketplace_listings").select("*").eq("id", str(listing_id)).eq("status", "active").single().execute()
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "billing.listing_not_found")
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

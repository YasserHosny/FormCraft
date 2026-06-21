"""Recurring subscription billing service (F059)."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID, uuid4

from fastapi import HTTPException, status

from app.core.audit import AuditLogger
from app.models.enums import NotificationType
from app.services.paygateway_client import PayGatewayClient, PayGatewayError

TIER_ORDER = ["starter", "professional", "enterprise", "platform"]
DEFAULT_DUNNING_THRESHOLD = 3
DUNNING_THRESHOLD_KEY = "billing.dunning_max_failures"

# Platform sentinel user_id written to audit log for system-initiated actions.
PLATFORM_ACTOR_ID = "00000000-0000-0000-0000-000000000000"


class SubscriptionService:
    def __init__(self, client, paygateway: PayGatewayClient | None = None):
        self.client = client
        self.paygateway = paygateway or PayGatewayClient()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_active_subscription(self, org_id: UUID) -> dict | None:
        result = (
            self.client.table("billing_subscriptions")
            .select("*")
            .eq("org_id", str(org_id))
            .in_("status", ["active", "past_due"])
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None

    def _get_dunning_threshold(self, org_id: UUID) -> int:
        result = (
            self.client.table("org_settings")
            .select("value")
            .eq("org_id", str(org_id))
            .eq("key", DUNNING_THRESHOLD_KEY)
            .limit(1)
            .execute()
        )
        if result.data:
            try:
                return int(result.data[0]["value"])
            except (KeyError, TypeError, ValueError):
                pass
        return DEFAULT_DUNNING_THRESHOLD

    def _get_org(self, org_id: UUID) -> dict:
        result = self.client.table("organizations").select("*").eq("id", str(org_id)).single().execute()
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "billing.organization_not_found")
        return result.data

    def _get_org_admin_profile(self, org_id: UUID) -> dict:
        """Return the first admin profile for the org (used for customer creation)."""
        result = (
            self.client.table("profiles")
            .select("id,email,full_name,role")
            .eq("org_id", str(org_id))
            .eq("role", "org_admin")
            .eq("is_active", True)
            .limit(1)
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "billing.org_admin_not_found")
        return result.data[0]

    def _get_price(self, tier: str, billing_interval: str, currency: str) -> dict:
        result = (
            self.client.table("billing_prices")
            .select("*")
            .eq("price_type", "tier")
            .eq("target_key", tier)
            .eq("currency", currency)
            .eq("billing_interval", billing_interval)
            .eq("is_active", True)
            .limit(1)
            .execute()
        )
        if not result.data:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "billing.price_unavailable")
        return result.data[0]

    def compute_proration_preview(self, *, org_id: UUID, new_tier: str) -> int:
        """Server-side proration preview (informational only — Stripe computes the actual charge).

        Formula: (new_amount × days_remaining/period_days) − (old_amount × days_remaining/period_days)
        Returns amount in minor currency units, clamped to >= 0.
        """
        sub = self._get_active_subscription(org_id)
        if not sub:
            return 0
        org = self._get_org(org_id)
        currency = org.get("default_currency") or "SAR"
        billing_interval = sub["billing_interval"]
        now = datetime.now(UTC)
        period_end = datetime.fromisoformat(str(sub["current_period_end"]).replace("Z", "+00:00"))
        period_start = datetime.fromisoformat(str(sub["current_period_start"]).replace("Z", "+00:00"))
        period_days = max(1, (period_end - period_start).days)
        days_remaining = max(0, (period_end - now).days)
        if days_remaining == 0:
            return 0
        new_price_row = self._get_price(new_tier, billing_interval, currency)
        old_price_row = self._get_price(sub["tier"], billing_interval, currency)
        new_amount = Decimal(str(new_price_row["unit_amount_minor"]))
        old_amount = Decimal(str(old_price_row["unit_amount_minor"]))
        ratio = Decimal(str(days_remaining)) / Decimal(str(period_days))
        proration = (new_amount * ratio) - (old_amount * ratio)
        return max(0, int(proration.to_integral_value(rounding=ROUND_HALF_UP)))

    # ------------------------------------------------------------------
    # US1 — Subscribe to a paid tier
    # ------------------------------------------------------------------

    def get_current_subscription(self, org_id: UUID) -> dict | None:
        return self._get_active_subscription(org_id)

    async def create_subscription(
        self,
        *,
        org_id: UUID,
        actor_id: UUID,
        tier: str,
        billing_interval: str,
        return_url: str,
    ) -> dict:
        if tier not in TIER_ORDER or tier == "starter":
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "billing.invalid_target")

        existing = self._get_active_subscription(org_id)
        if existing:
            raise HTTPException(status.HTTP_409_CONFLICT, "billing.subscription_already_active")

        org = self._get_org(org_id)
        currency = org.get("default_currency") or "SAR"

        # Lazily create Stripe Customer if missing
        customer_id: str = org.get("stripe_customer_id") or ""
        if not customer_id:
            profile = self._get_org_admin_profile(org_id)
            try:
                cust = await self.paygateway.create_customer(
                    email=str(profile.get("email") or ""),
                    name=str(profile.get("full_name") or ""),
                )
                customer_id = str(cust["id"])
            except PayGatewayError as exc:
                raise HTTPException(exc.status_code, "billing.provider_error") from exc
            self.client.table("organizations").update({"stripe_customer_id": customer_id}).eq("id", str(org_id)).execute()

        price_row = self._get_price(tier, billing_interval, currency)
        provider_price_id = price_row.get("provider_price_id")
        if not provider_price_id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "billing.price_not_configured")

        try:
            sub_data = await self.paygateway.create_subscription(
                customer_id=customer_id,
                price_id=provider_price_id,
                metadata={"org_id": str(org_id), "tier": tier, "actor_id": str(actor_id)},
            )
        except PayGatewayError as exc:
            raise HTTPException(exc.status_code, "billing.provider_error") from exc

        provider_subscription_id = str(sub_data["id"])
        requires_action = bool(
            sub_data.get("latest_invoice", {})
            .get("payment_intent", {})
            .get("client_secret")
        )
        client_token = (
            sub_data.get("latest_invoice", {})
            .get("payment_intent", {})
            .get("client_secret", "")
        )
        # billing_subscriptions row created by handle_invoice_paid webhook — not here.
        checkout = None
        if requires_action and client_token:
            checkout = {
                "provider": "paygateway",
                "client_token": client_token,
                "requires_action": True,
                "expires_at": None,
            }
        return {"subscription_id": provider_subscription_id, "status": "requires_action" if requires_action else "active", "checkout": checkout}

    async def handle_invoice_paid(self, event: dict) -> None:
        """Handle invoice.paid: insert or update billing_subscriptions row."""
        sub_id = str(event.get("subscription_id") or "")
        invoice_id = str(event.get("invoice_id") or "")
        if not sub_id:
            return

        existing = (
            self.client.table("billing_subscriptions")
            .select("*")
            .eq("provider_subscription_id", sub_id)
            .limit(1)
            .execute()
        )
        row = existing.data[0] if existing.data else None

        # Idempotency: skip if this invoice was already processed
        if row and row.get("last_invoice_id") == invoice_id:
            return

        period_start = str(event.get("period_start") or "")
        period_end = str(event.get("period_end") or "")
        amount_paid = int(event.get("amount_paid_minor") or 0)
        currency = str(event.get("currency") or "SAR")
        metadata = dict(event.get("metadata") or {})
        org_id = metadata.get("org_id")
        tier = metadata.get("tier")

        if row:
            # Existing sub — renewal succeeded
            scheduled_downgrade = row.get("scheduled_downgrade_tier")
            update: dict = {
                "current_period_start": period_start,
                "current_period_end": period_end,
                "next_renewal_amount_minor": amount_paid,
                "currency": currency,
                "status": "active",
                "failed_payment_count": 0,
                "last_invoice_id": invoice_id,
                "updated_at": datetime.now(UTC).isoformat(),
            }
            if scheduled_downgrade:
                update["tier"] = scheduled_downgrade
                update["scheduled_downgrade_tier"] = None
                # Update org tier
                self.client.table("organizations").update({"subscription_tier": scheduled_downgrade}).eq("id", row["org_id"]).execute()
            self.client.table("billing_subscriptions").update(update).eq("id", row["id"]).execute()
            self._write_fulfillment(row["org_id"], str(row["id"]), update.get("tier", row["tier"]), scheduled_downgrade)
        else:
            # First invoice.paid — create the row
            if not org_id or not tier:
                return
            new_row = {
                "id": str(uuid4()),
                "org_id": org_id,
                "provider_subscription_id": sub_id,
                "tier": tier,
                "billing_interval": str(event.get("billing_interval") or "monthly"),
                "current_period_start": period_start,
                "current_period_end": period_end,
                "status": "active",
                "next_renewal_amount_minor": amount_paid,
                "currency": currency,
                "last_invoice_id": invoice_id,
                "failed_payment_count": 0,
                "cancel_at_period_end": False,
            }
            self.client.table("billing_subscriptions").insert(new_row).execute()
            self.client.table("organizations").update({"subscription_tier": tier}).eq("id", org_id).execute()
            self._write_fulfillment(org_id, new_row["id"], tier, None)

    # ------------------------------------------------------------------
    # US2 — Upgrade mid-cycle with proration
    # ------------------------------------------------------------------

    async def upgrade_subscription(self, *, org_id: UUID, new_tier: str) -> dict:
        sub = self._get_active_subscription(org_id)
        if not sub:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "billing.subscription_not_found")

        current_idx = TIER_ORDER.index(sub["tier"]) if sub["tier"] in TIER_ORDER else 0
        new_idx = TIER_ORDER.index(new_tier) if new_tier in TIER_ORDER else 0
        if new_idx <= current_idx:
            raise HTTPException(status.HTTP_409_CONFLICT, "billing.downgrade_requires_schedule")

        org = self._get_org(org_id)
        currency = org.get("default_currency") or "SAR"
        price_row = self._get_price(new_tier, sub["billing_interval"], currency)
        provider_price_id = price_row.get("provider_price_id")
        if not provider_price_id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "billing.price_not_configured")

        proration_minor = self.compute_proration_preview(org_id=org_id, new_tier=new_tier)

        try:
            await self.paygateway.upgrade_subscription(
                subscription_id=sub["provider_subscription_id"],
                new_price_id=provider_price_id,
            )
        except PayGatewayError as exc:
            raise HTTPException(exc.status_code, "billing.provider_error") from exc

        # Optimistic update — confirmed by invoice.paid webhook
        self.client.table("billing_subscriptions").update(
            {"tier": new_tier, "scheduled_downgrade_tier": None, "updated_at": datetime.now(UTC).isoformat()}
        ).eq("id", sub["id"]).execute()
        self.client.table("organizations").update({"subscription_tier": new_tier}).eq("id", str(org_id)).execute()

        return {
            "subscription_id": sub["id"],
            "previous_tier": sub["tier"],
            "new_tier": new_tier,
            "proration_amount_minor": proration_minor,
            "currency": currency,
            "status": "active",
        }

    # ------------------------------------------------------------------
    # US3 — Schedule / cancel a downgrade
    # ------------------------------------------------------------------

    def schedule_downgrade(self, *, org_id: UUID, new_tier: str) -> dict:
        sub = self._get_active_subscription(org_id)
        if not sub:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "billing.subscription_not_found")
        if new_tier == "starter":
            raise HTTPException(status.HTTP_409_CONFLICT, "billing.downgrade_to_starter_requires_cancel")
        current_idx = TIER_ORDER.index(sub["tier"]) if sub["tier"] in TIER_ORDER else 0
        new_idx = TIER_ORDER.index(new_tier) if new_tier in TIER_ORDER else 0
        if new_idx >= current_idx:
            raise HTTPException(status.HTTP_409_CONFLICT, "billing.upgrade_requires_immediate")
        self.client.table("billing_subscriptions").update(
            {"scheduled_downgrade_tier": new_tier, "updated_at": datetime.now(UTC).isoformat()}
        ).eq("id", sub["id"]).execute()
        return {
            "subscription_id": sub["id"],
            "current_tier": sub["tier"],
            "scheduled_downgrade_tier": new_tier,
            "effective_date": sub.get("current_period_end"),
        }

    def cancel_downgrade_schedule(self, org_id: UUID) -> dict:
        sub = self._get_active_subscription(org_id)
        if not sub:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "billing.subscription_not_found")
        if not sub.get("scheduled_downgrade_tier"):
            raise HTTPException(status.HTTP_409_CONFLICT, "billing.no_downgrade_scheduled")
        self.client.table("billing_subscriptions").update(
            {"scheduled_downgrade_tier": None, "updated_at": datetime.now(UTC).isoformat()}
        ).eq("id", sub["id"]).execute()
        return {"subscription_id": sub["id"], "current_tier": sub["tier"], "scheduled_downgrade_tier": None}

    # ------------------------------------------------------------------
    # US4 — Cancel / reactivate
    # ------------------------------------------------------------------

    async def cancel_subscription(self, org_id: UUID) -> dict:
        sub = self._get_active_subscription(org_id)
        if not sub:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "billing.subscription_not_found")
        if sub.get("cancel_at_period_end"):
            raise HTTPException(status.HTTP_409_CONFLICT, "billing.already_cancelled")
        try:
            await self.paygateway.cancel_subscription(sub["provider_subscription_id"])
        except PayGatewayError as exc:
            raise HTTPException(exc.status_code, "billing.provider_error") from exc
        self.client.table("billing_subscriptions").update(
            {"cancel_at_period_end": True, "updated_at": datetime.now(UTC).isoformat()}
        ).eq("id", sub["id"]).execute()
        return {
            "subscription_id": sub["id"],
            "tier": sub["tier"],
            "cancel_at_period_end": True,
            "period_end": sub["current_period_end"],
        }

    async def reactivate_subscription(self, org_id: UUID) -> dict:
        sub = self._get_active_subscription(org_id)
        if not sub:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "billing.subscription_not_found")
        if not sub.get("cancel_at_period_end"):
            raise HTTPException(status.HTTP_409_CONFLICT, "billing.subscription_not_cancelling")
        period_end = datetime.fromisoformat(str(sub["current_period_end"]).replace("Z", "+00:00"))
        if period_end <= datetime.now(UTC):
            raise HTTPException(status.HTTP_409_CONFLICT, "billing.subscription_already_expired")
        try:
            await self.paygateway.reactivate_subscription(sub["provider_subscription_id"])
        except PayGatewayError as exc:
            raise HTTPException(exc.status_code, "billing.provider_error") from exc
        self.client.table("billing_subscriptions").update(
            {"cancel_at_period_end": False, "updated_at": datetime.now(UTC).isoformat()}
        ).eq("id", sub["id"]).execute()
        return {
            "subscription_id": sub["id"],
            "tier": sub["tier"],
            "cancel_at_period_end": False,
            "next_renewal_date": sub["current_period_end"],
        }

    def handle_subscription_deleted(self, event: dict) -> None:
        sub_id = str(event.get("subscription_id") or "")
        if not sub_id:
            return
        result = (
            self.client.table("billing_subscriptions")
            .select("*")
            .eq("provider_subscription_id", sub_id)
            .limit(1)
            .execute()
        )
        if not result.data:
            return
        row = result.data[0]
        self.client.table("billing_subscriptions").update(
            {"status": "cancelled", "updated_at": datetime.now(UTC).isoformat()}
        ).eq("id", row["id"]).execute()
        # Revert org to Starter if still on an elevated tier
        org = self.client.table("organizations").select("subscription_tier").eq("id", row["org_id"]).single().execute()
        if org.data and org.data.get("subscription_tier", "starter") != "starter":
            self.client.table("organizations").update({"subscription_tier": "starter"}).eq("id", row["org_id"]).execute()
            self._write_fulfillment(row["org_id"], row["id"], "starter", None)

    # ------------------------------------------------------------------
    # US5 — Dunning + portal URL
    # ------------------------------------------------------------------

    async def handle_payment_failed(self, event: dict) -> None:
        sub_id = str(event.get("subscription_id") or "")
        invoice_id = str(event.get("invoice_id") or "")
        if not sub_id:
            return
        result = (
            self.client.table("billing_subscriptions")
            .select("*")
            .eq("provider_subscription_id", sub_id)
            .limit(1)
            .execute()
        )
        if not result.data:
            return
        row = result.data[0]

        # Idempotency
        if row.get("last_invoice_id") == invoice_id:
            return

        new_count = int(row.get("failed_payment_count") or 0) + 1
        threshold = self._get_dunning_threshold(UUID(str(row["org_id"])))

        update: dict = {
            "failed_payment_count": new_count,
            "status": "past_due",
            "last_invoice_id": invoice_id,
            "updated_at": datetime.now(UTC).isoformat(),
        }

        if new_count >= threshold:
            update["status"] = "cancelled"
            self.client.table("billing_subscriptions").update(update).eq("id", row["id"]).execute()
            # Downgrade org to Starter
            self.client.table("organizations").update({"subscription_tier": "starter"}).eq("id", row["org_id"]).execute()
            self._write_fulfillment(row["org_id"], row["id"], "starter", None)
            await AuditLogger(self.client).log_event(
                user_id=PLATFORM_ACTOR_ID,
                action="billing.subscription.dunning_downgrade",
                resource_type="billing_subscription",
                resource_id=row["id"],
                metadata={"org_id": row["org_id"], "failed_payment_count": new_count, "threshold": threshold},
            )
        else:
            self.client.table("billing_subscriptions").update(update).eq("id", row["id"]).execute()
            # Notify org admin
            await self._notify_payment_failed(UUID(str(row["org_id"])))

    async def handle_subscription_updated(self, event: dict) -> None:
        """Sync subscription state when Stripe reports a subscription change."""
        sub_id = str(event.get("subscription_id") or "")
        if not sub_id:
            return
        result = (
            self.client.table("billing_subscriptions")
            .select("*")
            .eq("provider_subscription_id", sub_id)
            .limit(1)
            .execute()
        )
        if not result.data:
            return
        row = result.data[0]
        update: dict = {"updated_at": datetime.now(UTC).isoformat()}
        if event.get("period_start"):
            update["current_period_start"] = str(event["period_start"])
        if event.get("period_end"):
            update["current_period_end"] = str(event["period_end"])
        if event.get("amount_paid_minor") is not None:
            update["next_renewal_amount_minor"] = int(event["amount_paid_minor"])
        if event.get("status") and event["status"] in ("active", "past_due", "cancelled"):
            update["status"] = event["status"]
        if len(update) > 1:
            self.client.table("billing_subscriptions").update(update).eq("id", row["id"]).execute()

    async def get_portal_url(self, *, org_id: UUID, return_url: str) -> dict:
        sub = self._get_active_subscription(org_id)
        if not sub:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "billing.subscription_not_found")
        if sub["status"] != "past_due":
            raise HTTPException(status.HTTP_409_CONFLICT, "billing.subscription_not_past_due")
        org = self._get_org(org_id)
        customer_id = org.get("stripe_customer_id")
        if not customer_id:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "billing.no_stripe_customer")
        try:
            data = await self.paygateway.get_portal_url(customer_id=customer_id, return_url=return_url)
        except PayGatewayError as exc:
            raise HTTPException(exc.status_code, "billing.portal_url_error") from exc
        return {"portal_url": str(data["portal_url"]), "expires_at": data.get("expires_at")}

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _write_fulfillment(self, org_id: str, subscription_id: str, tier: str, downgraded_from: str | None) -> None:
        payload: dict = {"tier": tier, "subscription_id": subscription_id}
        if downgraded_from:
            payload["downgraded_from"] = downgraded_from
        # billing_fulfillments requires a purchase_id FK — for webhook-driven events
        # we synthesise a zero-amount purchase to satisfy the constraint.
        purchase_id = str(uuid4())
        self.client.table("billing_purchases").insert({
            "id": purchase_id,
            "organization_id": org_id,
            "created_by": PLATFORM_ACTOR_ID,
            "purpose": "subscription_tier",
            "target": {"tier": tier, "subscription_id": subscription_id},
            "currency": "SAR",
            "amount_minor": 0,
            "status": "succeeded",
            "idempotency_key": f"sub-fulfill:{subscription_id}:{tier}:{purchase_id}",
            "fulfilled_at": datetime.now(UTC).isoformat(),
        }).execute()
        self.client.table("billing_fulfillments").insert({
            "purchase_id": purchase_id,
            "organization_id": org_id,
            "effect_type": "tier_changed",
            "effect_payload": payload,
            "applied_by": None,
            "source": "webhook",
        }).execute()

    async def _notify_payment_failed(self, org_id: UUID) -> None:
        """Dispatch in-app + email notification to org admins on payment failure."""
        try:
            admins = (
                self.client.table("profiles")
                .select("id")
                .eq("org_id", str(org_id))
                .eq("role", "org_admin")
                .eq("is_active", True)
                .execute()
            )
            from app.services.notification_service import NotificationService
            ns = NotificationService(self.client)
            for admin in (admins.data or []):
                content = ns.build_notification_content(
                    NotificationType.SUBSCRIPTION_PAYMENT_FAILED,
                    template_name="",
                    actor_name="",
                )
                self.client.table("notifications").insert({
                    "id": str(uuid4()),
                    "user_id": admin["id"],
                    "org_id": str(org_id),
                    "type": NotificationType.SUBSCRIPTION_PAYMENT_FAILED.value,
                    "title_ar": content["title_ar"],
                    "title_en": content["title_en"],
                    "body_ar": content["body_ar"],
                    "body_en": content["body_en"],
                    "is_read": False,
                    "created_at": datetime.now(UTC).isoformat(),
                }).execute()
        except Exception:
            pass  # Never block the webhook path on notification failure

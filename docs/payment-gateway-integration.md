# Embedding PayGateway in FormCraft

> How to add card payments to the FormCraft web app using the already-built **PayGateway**
> service (FastAPI + Stripe). Tailored to FormCraft's real stack and conventions:
> **Angular 19 standalone + FastAPI + Supabase**, **dual-theme (Classic + Spark)**, and the
> **subscription/add-on revenue model** from [`system-critique-and-vision.md`](system-critique-and-vision.md).
>
> Gateway source of truth: `Payment Gateway/paygateway/docs/integration-plan.md`.

---

## 0. What FormCraft Actually Charges For

This integration is **not** a generic product checkout. It serves FormCraft's documented
revenue model (see [Revenue Model](system-critique-and-vision.md#revenue-model)). Every payment
maps to one of these **billing purposes**, and fulfillment mutates the paying **organization**:

| `purpose` | What the user buys | On success, fulfillment does | Revenue model ref |
|-----------|--------------------|------------------------------|-------------------|
| `subscription` | Upgrade org tier (starter → professional → enterprise → platform) | Sets `organizations.subscription_tier`; new `tier_limits` apply immediately | Tiered pricing |
| `seats` | Extra operator seats beyond the tier cap | Raises the org's effective user limit | Add-on: "Additional operators" |
| `ocr_batch` | One-time OCR onboarding of N paper forms | Credits N form-scan jobs to the org | Add-on: "OCR batch onboarding" |
| `marketplace` | Premium template purchase | Clones the premium template into the buyer org; records 70/30 split | EXT-02 marketplace |

> **Why this matters:** the vision doc names **tier enforcement** as the current revenue
> blocker — tiers are stored and alerted on (`tier_limits`, `get_tier_limit_alerts()`) but not
> *enforced or sellable* through the UI. This payment flow is the missing piece: it turns
> `subscription_tier` from a label into something a customer can **pay to change**, and it plugs
> directly into the **Platform Console → Organization Detail → Subscription tab**
> (`features/platform/organization-detail/tabs/subscription-tab`), which today is read-only.

The `order_id` in the generic gateway guide becomes a FormCraft **`billing_intent_id`**, and the
gateway `metadata` always carries `{ org_id, purpose, target }`.

---

## 1. The One Rule That Drives Everything

> **The PayGateway `X-API-Key` and the Stripe secret key (`sk_*`) NEVER leave the FormCraft
> backend.** The Angular app only ever receives a `client_secret`, scoped to a single payment
> intent — it cannot create new charges or change tiers on its own.

```
┌─────────────────────────────────────────────────────────────────────┐
│  FormCraft                                                            │
│  ┌─────────────────────────┐  /api/billing/*  ┌────────────────────┐ │
│  │ Angular 19 (Classic+Spark)│ ───────────────> │ FastAPI BFF        │ │
│  │ @stripe/stripe-js         │ <─────────────── │ holds X-API-Key    │ │
│  │ (publishable key, --fc-*) │  {clientSecret}  └─────────┬──────────┘ │
│  └─────────────────────────┘                             │            │
└────────────────────────────────────────────────────────────│──────────┘
                                                              │ X-API-Key
                                                              ▼
                                                  ┌────────────────────┐
                                                  │   PayGateway API    │
                                                  │  /api/v1/payments   │
                                                  └─────────┬──────────┘
                                                            ▼  Stripe
```

Fulfillment (changing a tier, adding seats) happens **only** on the backend after server-side
verification — never based on a client-reported status.

---

## 2. Prerequisites (do once)

Owned by whoever operates PayGateway — confirm before writing FormCraft code:

- [ ] PayGateway reachable; `GET https://<gateway>/health` → `{"status":"healthy"}`
- [ ] Stripe keys set in PayGateway `.env` (`STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`)
- [ ] A **service**-role API key issued for FormCraft's backend (`pgw_live_...` / `pgw_test_...`)
- [ ] PayGateway `ALLOWED_ORIGINS` includes the FormCraft backend origin

What FormCraft holds:

| Value | Where | Secret? |
|-------|-------|:-------:|
| PayGateway base URL | backend env `PAYGATEWAY_URL` | no |
| PayGateway service key | backend env `PAYGATEWAY_API_KEY` | **YES — backend only** |
| Stripe publishable key | frontend `environment.stripePublishableKey` | no (safe in browser) |
| Tier price table | backend (DB or config) | no |

---

## 3. Data Model (Supabase migration)

Add a billing-intent table (org-scoped, RLS like every other tenant table) plus a tier price
list. Place under `formcraft-backend/migrations/NNN_billing.sql` (use the next free number).

```sql
-- Tier prices in smallest currency unit (e.g. piasters). Source of truth for amounts.
CREATE TABLE IF NOT EXISTS tier_prices (
    tier        text PRIMARY KEY REFERENCES tier_limits(tier),
    amount      integer NOT NULL,      -- e.g. 0, 49900, 199900 ...
    currency    text NOT NULL DEFAULT 'EGP',
    interval    text NOT NULL DEFAULT 'month'  -- 'month' | 'year'
);

CREATE TABLE IF NOT EXISTS billing_intents (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          uuid NOT NULL REFERENCES organizations(id),
    purpose         text NOT NULL,     -- subscription | seats | ocr_batch | marketplace
    target          jsonb NOT NULL,    -- {tier:'professional'} | {seats:10} | {forms:300} | {template_id:...}
    amount          integer NOT NULL,  -- computed server-side, never from client
    currency        text NOT NULL,
    paygateway_id   text,              -- PayGateway payment id
    status          text NOT NULL DEFAULT 'created', -- created|succeeded|failed|refunded
    created_by      uuid NOT NULL REFERENCES profiles(id),
    created_at      timestamptz NOT NULL DEFAULT now(),
    fulfilled_at    timestamptz
);

ALTER TABLE billing_intents ENABLE ROW LEVEL SECURITY;
CREATE POLICY billing_intents_org_isolation ON billing_intents
    USING (org_id = current_setting('app.current_org_id', true)::uuid);
```

Fulfillment is logged to the existing `audit_logs` (new actions: `SUBSCRIPTION_UPGRADED`,
`SEATS_ADDED`, `OCR_BATCH_PURCHASED`, `MARKETPLACE_PURCHASED`) — consistent with AC-04 in the
vision doc.

---

## 4. Backend (FastAPI BFF) — matches existing route conventions

Mirrors `app/api/routes/platform.py`: `APIRouter`, `Annotated[OrgContext, Depends(...)]`,
a service layer, `get_supabase_client()`, org-scoped queries.

### 4.1 Settings

```python
# app/core/config.py
class Settings(BaseSettings):
    # ... existing ...
    PAYGATEWAY_URL: str            # e.g. https://pay.formcraft.io
    PAYGATEWAY_API_KEY: str        # pgw_live_... — NEVER sent to the client
```

### 4.2 Schemas

```python
# app/schemas/billing.py
from typing import Literal
from pydantic import BaseModel

Purpose = Literal["subscription", "seats", "ocr_batch", "marketplace"]

class CreateBillingIntent(BaseModel):
    purpose: Purpose
    target: dict          # {"tier": "professional"} | {"seats": 10} | {"forms": 300} | {"template_id": "..."}

class BillingIntentResponse(BaseModel):
    billing_intent_id: str
    client_secret: str
    amount: int
    currency: str

class ConfirmBilling(BaseModel):
    billing_intent_id: str
    payment_method_id: str

class BillingStatus(BaseModel):
    status: str
    purpose: str
    failure_code: str | None = None
    failure_message: str | None = None
```

### 4.3 Router

```python
# app/api/routes/billing.py
from typing import Annotated
import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.core.config import settings
from app.core.supabase import get_supabase_client
from app.middleware.org_context import OrgContext, require_org_admin
from app.schemas.billing import (
    CreateBillingIntent, BillingIntentResponse, ConfirmBilling, BillingStatus,
)
from app.services.billing_service import BillingService

router = APIRouter(prefix="/billing", tags=["Billing"])


def _pgw_headers(idempotency_key: str) -> dict:
    return {
        "Content-Type": "application/json",
        "X-API-Key": settings.PAYGATEWAY_API_KEY,   # stays server-side
        "Idempotency-Key": idempotency_key,
    }


@router.post("/create", response_model=BillingIntentResponse)
async def create_intent(
    body: CreateBillingIntent,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],   # only org admins buy/upgrade
):
    svc = BillingService(get_supabase_client())

    # Amount is ALWAYS computed server-side from the price table — never trusted from client.
    intent = await svc.create_intent(
        org_id=ctx.org_id, created_by=ctx.user_id,
        purpose=body.purpose, target=body.target,
    )

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"{settings.PAYGATEWAY_URL}/api/v1/payments",
            json={
                "amount": intent["amount"],
                "currency": intent["currency"],
                "metadata": {
                    "org_id": str(ctx.org_id),
                    "purpose": body.purpose,
                    "billing_intent_id": intent["id"],
                },
            },
            headers=_pgw_headers(f"create-{intent['id']}"),
        )
    if r.status_code >= 400:
        raise HTTPException(r.status_code, detail=r.json())
    p = r.json()
    await svc.attach_paygateway_id(intent["id"], p["id"])
    return BillingIntentResponse(
        billing_intent_id=intent["id"], client_secret=p["client_secret"],
        amount=intent["amount"], currency=intent["currency"],
    )


@router.post("/confirm", response_model=BillingStatus)
async def confirm(
    body: ConfirmBilling,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    svc = BillingService(get_supabase_client())
    intent = await svc.get_intent(body.billing_intent_id, org_id=ctx.org_id)  # org-scoped
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"{settings.PAYGATEWAY_URL}/api/v1/payments/{intent['paygateway_id']}/confirm",
            json={"payment_method_id": body.payment_method_id},
            headers=_pgw_headers(f"confirm-{intent['id']}"),
        )
    if r.status_code >= 400:
        raise HTTPException(r.status_code, detail=r.json())
    p = r.json()
    return BillingStatus(status=p["status"], purpose=intent["purpose"],
                         failure_code=p.get("failure_code"),
                         failure_message=p.get("failure_message"))


@router.get("/{billing_intent_id}/status", response_model=BillingStatus)
async def status(
    billing_intent_id: str,
    ctx: Annotated[OrgContext, Depends(require_org_admin())],
):
    """Authoritative check + fulfillment. Tiers/seats change ONLY here, server-side."""
    svc = BillingService(get_supabase_client())
    intent = await svc.get_intent(billing_intent_id, org_id=ctx.org_id)
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(
            f"{settings.PAYGATEWAY_URL}/api/v1/payments/{intent['paygateway_id']}",
            headers={"X-API-Key": settings.PAYGATEWAY_API_KEY},
        )
    if r.status_code >= 400:
        raise HTTPException(r.status_code, detail=r.json())
    p = r.json()

    if p["status"] == "succeeded":
        # Idempotent: applies the tier/seat/ocr/marketplace change + writes audit_logs
        await svc.fulfill(intent, actor=ctx.user_id)

    return BillingStatus(status=p["status"], purpose=intent["purpose"],
                         failure_code=p.get("failure_code"),
                         failure_message=p.get("failure_message"))
```

### 4.4 Fulfillment service (where revenue model meets the data)

```python
# app/services/billing_service.py (sketch — purpose → org mutation)
class BillingService:
    def __init__(self, client): self.client = client

    async def create_intent(self, *, org_id, created_by, purpose, target):
        amount, currency = await self._price(purpose, target, org_id)
        row = self.client.table("billing_intents").insert({
            "org_id": str(org_id), "created_by": str(created_by),
            "purpose": purpose, "target": target,
            "amount": amount, "currency": currency, "status": "created",
        }).execute().data[0]
        return row

    async def _price(self, purpose, target, org_id) -> tuple[int, str]:
        if purpose == "subscription":
            row = self.client.table("tier_prices").select("*") \
                .eq("tier", target["tier"]).single().execute().data
            return row["amount"], row["currency"]
        if purpose == "seats":
            return target["seats"] * SEAT_PRICE, "EGP"
        if purpose == "ocr_batch":
            return target["forms"] * OCR_FORM_PRICE, "EGP"
        if purpose == "marketplace":
            return await self._marketplace_price(target["template_id"]), "EGP"
        raise ValueError(purpose)

    async def fulfill(self, intent, *, actor):
        if intent.get("fulfilled_at"):       # idempotency guard
            return
        p, t, org = intent["purpose"], intent["target"], intent["org_id"]
        if p == "subscription":
            self.client.table("organizations").update(
                {"subscription_tier": t["tier"]}).eq("id", org).execute()
            self._audit(actor, org, "SUBSCRIPTION_UPGRADED", t)
        elif p == "seats":
            self._add_seats(org, t["seats"]); self._audit(actor, org, "SEATS_ADDED", t)
        elif p == "ocr_batch":
            self._credit_ocr(org, t["forms"]); self._audit(actor, org, "OCR_BATCH_PURCHASED", t)
        elif p == "marketplace":
            self._clone_template(org, t["template_id"])   # records 70/30 split
            self._audit(actor, org, "MARKETPLACE_PURCHASED", t)
        self.client.table("billing_intents").update(
            {"status": "succeeded", "fulfilled_at": "now()"}).eq("id", intent["id"]).execute()
```

> After a `subscription` fulfillment the org's new `subscription_tier` immediately drives
> `tier_limits` and `get_tier_limit_alerts()` — closing the enforcement loop the vision doc
> flagged. Pair this with the seat/submission **gates** at invite/submit time (out of scope here,
> tracked in the vision doc's revenue section).

### 4.5 Refunds (platform/admin only)

Gate behind `require_platform_admin()` (or `require_org_admin()` for self-serve downgrades) and
call `POST /api/v1/payments/{id}/refund` with an `Idempotency-Key`. On refund, reverse the
fulfillment (downgrade tier / remove seats) and audit it. Valid reasons: `customer_request`,
`duplicate`, `fraudulent`.

### 4.6 Register the router

```python
# app/main.py
from app.api.routes import billing
app.include_router(billing.router, prefix="/api")
```

---

## 5. Frontend — one component, both themes

The backend is theme-agnostic. On the frontend, build **one shared standalone component** that
is styled exclusively with FormCraft's `--fc-*` CSS variables and `.fc-btn` classes, so it adopts
**whichever theme is active** with zero forking. Then route it under **both** Classic and Spark.

### 5.1 Dependency & env

```bash
npm install @stripe/stripe-js
```

```typescript
// src/environments/environment.ts
export const environment = {
  // ... existing ...
  stripePublishableKey: 'pk_test_...',   // publishable key only
};
```

### 5.2 Billing service (`core/`, providedIn: 'root')

```typescript
// src/app/core/billing/billing.service.ts
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { loadStripe, Stripe, StripeCardElement } from '@stripe/stripe-js';
import { firstValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';

export type BillingPurpose = 'subscription' | 'seats' | 'ocr_batch' | 'marketplace';
interface CreateResp { billing_intent_id: string; client_secret: string; amount: number; currency: string; }
interface StatusResp { status: string; purpose: string; failure_code?: string; failure_message?: string; }

@Injectable({ providedIn: 'root' })
export class BillingService {
  private http = inject(HttpClient);
  private bff = '/api/billing';                          // FormCraft backend — never PayGateway directly
  private stripe = loadStripe(environment.stripePublishableKey);

  async checkout(purpose: BillingPurpose, target: Record<string, unknown>,
                 card: StripeCardElement): Promise<string> {
    const stripe = await this.stripe;
    if (!stripe) throw new Error('Stripe failed to load');

    const created = await firstValueFrom(
      this.http.post<CreateResp>(`${this.bff}/create`, { purpose, target }));

    const { paymentMethod, error } = await stripe.createPaymentMethod({ type: 'card', card });
    if (error) throw error;

    let { status } = await firstValueFrom(
      this.http.post<StatusResp>(`${this.bff}/confirm`,
        { billing_intent_id: created.billing_intent_id, payment_method_id: paymentMethod!.id }));

    if (status === 'requires_action') {
      const res = await stripe.confirmCardPayment(created.client_secret);
      if (res.error) throw res.error;
      status = res.paymentIntent?.status ?? 'failed';
    }

    // Authoritative verify + server-side fulfillment (tier/seat change happens there)
    const verified = await firstValueFrom(
      this.http.get<StatusResp>(`${this.bff}/${created.billing_intent_id}/status`));
    return verified.status;
  }
}
```

### 5.3 Shared, theme-aware checkout component

Lives in `shared/` so both themes import it. Critically, the **Stripe card Element is styled
from the live `--fc-*` variables**, so it matches Classic or Spark automatically, including RTL.

```typescript
// src/app/shared/billing/checkout.component.ts
import { Component, ElementRef, Input, OnDestroy, OnInit, ViewChild, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { loadStripe, StripeCardElement, StripeElements } from '@stripe/stripe-js';
import { BillingService, BillingPurpose } from '../../core/billing/billing.service';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'fc-checkout',
  standalone: true,
  imports: [CommonModule, TranslateModule],
  template: `
    <form class="fc-checkout" (submit)="onSubmit($event)">
      <div #cardEl class="fc-card-input"></div>
      <button type="submit" class="fc-btn primary" [disabled]="processing">
        {{ (processing ? 'billing.processing' : 'billing.pay') | translate }}
      </button>
      <p *ngIf="errorMessage" class="fc-error">{{ errorMessage }}</p>
    </form>
  `,
  styles: [`
    .fc-checkout { display:flex; flex-direction:column; gap:16px; }
    .fc-card-input {
      padding:12px; border:1px solid var(--fc-border); border-radius:8px;
      background: var(--fc-surface);
    }
    .fc-error { color: var(--fc-danger, #d32f2f); font-size:14px; }
  `],
})
export class CheckoutComponent implements OnInit, OnDestroy {
  @Input({ required: true }) purpose!: BillingPurpose;
  @Input({ required: true }) target!: Record<string, unknown>;
  @ViewChild('cardEl', { static: true }) cardRef!: ElementRef<HTMLDivElement>;

  private billing = inject(BillingService);
  private elements?: StripeElements;
  private card?: StripeCardElement;
  processing = false;
  errorMessage = '';

  async ngOnInit() {
    const stripe = await loadStripe(environment.stripePublishableKey);
    this.elements = stripe!.elements();

    // Pull theme tokens so the Stripe iframe matches Classic OR Spark, LTR or RTL.
    const css = getComputedStyle(document.documentElement);
    this.card = this.elements.create('card', {
      style: {
        base: {
          color: css.getPropertyValue('--fc-text').trim() || '#1a1a1a',
          fontFamily: css.getPropertyValue('--fc-font').trim() || 'inherit',
          '::placeholder': { color: css.getPropertyValue('--fc-text-2').trim() || '#888' },
        },
      },
    });
    this.card.mount(this.cardRef.nativeElement);
  }

  ngOnDestroy() { this.card?.destroy(); }

  async onSubmit(e: Event) {
    e.preventDefault();
    if (!this.card) return;
    this.processing = true; this.errorMessage = '';
    try {
      const status = await this.billing.checkout(this.purpose, this.target, this.card);
      if (status === 'succeeded') {
        // emit success / navigate — tier already applied server-side
      } else {
        this.errorMessage = ''; // surface via translate key in real impl
      }
    } catch (err: any) {
      this.errorMessage = this.toUserMessage(err);
    } finally { this.processing = false; }
  }

  private toUserMessage(err: any): string {
    // Map to ngx-translate keys (EN + AR) in real impl; codes below mirror the gateway guide.
    const code = err?.code ?? err?.error?.detail?.error?.code;
    const keys: Record<string,string> = {
      card_declined: 'billing.err.declined',
      insufficient_funds: 'billing.err.funds',
      expired_card: 'billing.err.expired',
      incorrect_cvc: 'billing.err.cvc',
      RATE_LIMITED: 'billing.err.rate_limited',
      PROVIDER_ERROR: 'billing.err.provider',
    };
    return keys[code] ?? 'billing.err.generic';   // translate() at the call site
  }
}
```

> **RTL / Arabic-first:** the component inherits the document's `dir`. Keep all user strings in
> `ngx-translate` keys (`billing.*`) with EN + AR entries, exactly like the rest of FormCraft —
> no hard-coded copy. The `--fc-*` styling means dark/light and both themes are covered.

### 5.4 Wire it into BOTH themes

**Classic route** (root-level, alongside other classic features):

```typescript
// wherever classic admin routes are declared
{
  path: 'admin/billing',
  canActivate: [RoleGuard],
  data: { roles: ['admin'] },
  loadComponent: () => import('./features/billing/billing-page.component')
    .then(m => m.BillingPageComponent),   // hosts <fc-checkout> in the classic shell
}
```

**Spark route** (under the Spark `LayoutComponent`, in `ui-redesign.routes.ts`):

```typescript
// features/ui-redesign/ui-redesign.routes.ts — child of LayoutComponent
{
  path: 'admin/billing',
  canActivate: [RoleGuard],
  data: { roles: ['admin'] },
  loadComponent: () => import('./admin/billing.component')
    .then(m => m.BillingComponent),       // Spark wrapper hosting the SAME <fc-checkout>
}
```

Both wrappers are thin — they render the shared `<fc-checkout [purpose] [target]>`; the shell
(toolbar, nav, theme tokens) comes from whichever layout the route sits in.

**Register the theme toggle mapping** so switching Classic↔Spark preserves the page —
add to `ROUTE_MAPPINGS` in `core/services/theme-preference.service.ts`:

```typescript
{
  classicPattern: /^\/admin\/billing$/,
  newPattern: /^\/ui\/admin\/billing$/,
  classicTemplate: '/admin/billing',
  newTemplate: '/ui/admin/billing',
  params: [],
  productionReady: true,          // set false while the Spark page is still WIP (see below)
  fallbackClassic: '/admin/billing',
  fallbackNew: '/ui/admin/billing',
},
```

**If you ship the Spark page later**, don't block the toggle: set `productionReady: false` and
point the Spark route at the existing bridge so it stays inside the Spark shell with an
"Open in Classic" button:

```typescript
{
  path: 'admin/billing',
  component: SparkFeatureBridgeComponent,
  data: { roles: ['admin'], featureName: 'nav.billing', featureIcon: 'credit_card',
          classicRoute: '/admin/billing' },
}
```

### 5.5 Plug into the Platform Console Subscription tab

The most valuable placement: the read-only
`features/platform/organization-detail/tabs/subscription-tab` becomes actionable. Add an
**"Upgrade tier"** button that opens the shared `<fc-checkout [purpose]="'subscription'"
[target]="{ tier: selectedTier }">`. This is the concrete fix for the vision doc's
"tier is display-only" revenue gap.

---

## 6. End-to-End Flow

1. Org admin opens billing (Classic `/admin/billing` **or** Spark `/ui/admin/billing`) — same
   `<fc-checkout>`, themed by the active shell.
2. Picks a tier/add-on → Angular calls `POST /api/billing/create`.
3. Backend computes the **authoritative amount** from `tier_prices`, creates a `billing_intent`,
   calls PayGateway with `X-API-Key`, returns `{billing_intent_id, client_secret}`.
4. Angular tokenizes the card → confirms via `POST /api/billing/confirm`.
5. 3DS handled via `stripe.confirmCardPayment(client_secret)` if `requires_action`.
6. Angular calls `GET /api/billing/{id}/status`; backend verifies and **fulfills** —
   sets `subscription_tier` / adds seats / credits OCR / clones template — and writes `audit_logs`.
7. New `tier_limits` apply immediately to the org.

---

## 7. Testing (test mode)

| Scenario | Card |
|----------|------|
| Succeeds | `4242 4242 4242 4242`, exp `12/34`, CVC `123` |
| 3DS required | `4000 0025 0000 3155` |
| Declined | `4000 0000 0000 9995` |
| Server-side PM | `pm_card_visa` |

Checklist:

- [ ] `/api/billing/create` returns `client_secret` and a server-computed `amount`
- [ ] Amount cannot be overridden by the client (tamper a request → backend ignores it)
- [ ] Confirm → `succeeded`; `GET /status` fulfills exactly once (idempotent)
- [ ] On success, `organizations.subscription_tier` updated and `audit_logs` row written
- [ ] Decline + 3DS handled gracefully, **localized EN + AR** messages
- [ ] Checkout renders correctly in **Classic** and **Spark**, **LTR and RTL**, light/dark
- [ ] Theme toggle on `/admin/billing` lands on `/ui/admin/billing` (and back)
- [ ] Only `admin` reaches billing routes (RoleGuard); operators/viewers blocked
- [ ] Org A's admin cannot read/fulfill Org B's `billing_intent` (RLS holds)
- [ ] `X-API-Key` never appears in browser devtools / network tab

---

## 8. Go Live

- [ ] Live keys: PayGateway `sk_live_`/`pk_live_`, FormCraft frontend `pk_live_`
- [ ] PayGateway `STRIPE_WEBHOOK_SECRET` → live secret; `ENVIRONMENT=production`
- [ ] TLS on FormCraft backend + PayGateway domains
- [ ] PayGateway `ALLOWED_ORIGINS` = production FormCraft origins only
- [ ] `PAYGATEWAY_API_KEY` in a secret manager, not the repo
- [ ] `tier_prices` populated for all sellable tiers/currencies (EGP/SAR/AED)
- [ ] One real low-value upgrade before launch; verify tier + audit + limits
- [ ] Rotate the FormCraft service API key every 90 days

---

## 9. API Quick Reference

| Step | Frontend (both themes) | Backend → PayGateway (with `X-API-Key`) |
|------|------------------------|------------------------------------------|
| Create | `POST /api/billing/create` | `POST /api/v1/payments` |
| Confirm | `POST /api/billing/confirm` | `POST /api/v1/payments/{id}/confirm` |
| Verify + fulfill | `GET /api/billing/{id}/status` | `GET /api/v1/payments/{id}` |
| Refund / downgrade | (admin UI) | `POST /api/v1/payments/{id}/refund` |

All PayGateway calls require `X-API-Key`; all `POST`s require `Idempotency-Key`.
All FormCraft billing endpoints require an authenticated **org admin** and are **org-scoped**.

---

## 10. How This Satisfies the Three Constraints

| Constraint | How it's met |
|------------|--------------|
| **Dual theme (Classic + Spark)** | One shared `<fc-checkout>` styled only with `--fc-*` tokens + `.fc-btn`; routed under both `/admin/billing` and `/ui/admin/billing`; `ROUTE_MAPPINGS` entry for the toggle; `SparkFeatureBridgeComponent` fallback while the Spark page is WIP; Stripe Element reads live theme vars, inherits `dir` for RTL |
| **Current project conventions** | Standalone components + `inject()` + lazy `loadComponent`; `providedIn: 'root'` service in `core/`; `RoleGuard` with `data.roles`; FastAPI `APIRouter` + `Annotated[OrgContext, Depends(require_org_admin())]` + service layer + `get_supabase_client()`; Supabase migration with RLS org-isolation; `audit_logs`; `ngx-translate` EN + AR |
| **Revenue model** | Payments map to the vision doc's tiers + add-ons (subscription/seats/ocr_batch/marketplace); fulfillment mutates `organizations.subscription_tier` and feeds `tier_limits`; makes the Platform Console Subscription tab actionable — directly closing the documented "tiers are display-only, not enforced/sellable" revenue gap |

For gateway internals see the PayGateway repo: `docs/api-reference.md`, `docs/authentication.md`,
`docs/webhooks.md`, `docs/integration-plan.md`.

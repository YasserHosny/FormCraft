import {
  AfterViewInit,
  Component,
  ElementRef,
  Inject,
  OnDestroy,
  ViewChild,
} from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { TranslateService } from '@ngx-translate/core';
import { loadStripe, Stripe, StripeCardElement } from '@stripe/stripe-js';
import { environment } from '../../../../environments/environment';
import { BillingService } from '../../../core/services/billing.service';
import {
  BillingInterval,
  BillingPurchaseCreateRequest,
  BillingPurchaseCreateResponse,
  BillingPurchaseVerifyResponse,
} from '../../../shared/models/billing.models';

export interface CheckoutDialogData {
  /** 'subscribe' | 'upgrade' | legacy purchase mode (no mode field) */
  mode?: 'subscribe' | 'upgrade';
  tier?: string;
  // Legacy fields (F058 one-off purchases)
  purpose?: string;
  target?: Record<string, unknown>;
  quantity?: number;
}

@Component({
  selector: 'fc-checkout-dialog',
  standalone: false,
  templateUrl: './checkout-dialog.component.html',
  styleUrls: ['./checkout-dialog.component.scss'],
})
export class CheckoutDialogComponent implements AfterViewInit, OnDestroy {
  @ViewChild('cardMount') cardMount!: ElementRef<HTMLDivElement>;

  loading = false;
  cardReady = false;
  result?: BillingPurchaseCreateResponse;
  verifyResult?: BillingPurchaseVerifyResponse;
  errorKey?: string;

  /** Selected billing interval for new subscriptions */
  billingInterval: BillingInterval = 'monthly';

  private stripe: Stripe | null = null;
  private cardElement: StripeCardElement | null = null;

  constructor(
    @Inject(MAT_DIALOG_DATA) public data: CheckoutDialogData,
    private dialogRef: MatDialogRef<CheckoutDialogComponent>,
    private billing: BillingService,
    private translate: TranslateService,
  ) {}

  get isSubscribeMode(): boolean { return this.data.mode === 'subscribe'; }
  get isUpgradeMode(): boolean { return this.data.mode === 'upgrade'; }

  async ngAfterViewInit(): Promise<void> {
    this.stripe = await loadStripe(environment.stripePublishableKey);
    if (!this.stripe) return;

    const style = this.buildCardStyle();
    const elements = this.stripe.elements({ locale: this.stripeLocale() });
    this.cardElement = elements.create('card', { style, hidePostalCode: true });
    this.cardElement.mount(this.cardMount.nativeElement);
    this.cardElement.on('ready', () => { this.cardReady = true; });
    this.cardElement.on('change', (event) => {
      this.errorKey = event.error ? this.mapStripeError(event.error.code) : undefined;
    });
  }

  ngOnDestroy(): void {
    this.cardElement?.unmount();
  }

  async pay(): Promise<void> {
    if (!this.stripe || !this.cardElement) return;
    this.loading = true;
    this.errorKey = undefined;

    if (this.isSubscribeMode && this.data.tier) {
      this.billing.createSubscription({
        tier: this.data.tier,
        billing_interval: this.billingInterval,
        return_url: window.location.href,
      }).subscribe({
        next: async (res) => {
          const clientSecret = res.checkout?.client_token;
          if (!clientSecret) {
            this.loading = false;
            this.dialogRef.close({ subscribed: true });
            return;
          }
          await this.confirmCardForSubscription(clientSecret);
        },
        error: (err) => {
          this.loading = false;
          this.errorKey = err?.error?.detail || 'billing.providerError';
        },
      });
      return;
    }

    if (this.isUpgradeMode && this.data.tier) {
      this.billing.upgradeSubscription({ tier: this.data.tier }).subscribe({
        next: () => { this.loading = false; this.dialogRef.close({ upgraded: true }); },
        error: (err) => { this.loading = false; this.errorKey = err?.error?.detail || 'billing.providerError'; },
      });
      return;
    }

    // Legacy one-off purchase (F058)
    const legacyData = this.data as unknown as BillingPurchaseCreateRequest;
    this.billing.createPurchase({ ...legacyData, return_url: window.location.href }).subscribe({
      next: async (res) => {
        this.result = res;
        const clientSecret = res.checkout?.client_token;
        if (!clientSecret) {
          this.loading = false;
          this.dialogRef.close({ ...res, fulfilled: true });
          return;
        }
        await this.confirmCard(res.purchase_id, clientSecret);
      },
      error: (err) => {
        this.loading = false;
        const code = err?.error?.detail || 'billing.providerError';
        this.errorKey = code;
      },
    });
  }

  private async confirmCardForSubscription(clientSecret: string): Promise<void> {
    const { paymentIntent, error } = await this.stripe!.confirmCardPayment(clientSecret, {
      payment_method: { card: this.cardElement! },
    });
    if (error) {
      this.loading = false;
      this.errorKey = this.mapStripeError(error.code);
      return;
    }
    if (paymentIntent?.status === 'succeeded' || paymentIntent?.status === 'requires_capture') {
      this.loading = false;
      this.dialogRef.close({ subscribed: true });
    } else {
      this.loading = false;
      this.errorKey = 'billing.payment.failed';
    }
  }

  private async confirmCard(purchaseId: string, clientSecret: string): Promise<void> {
    const { paymentIntent, error } = await this.stripe!.confirmCardPayment(clientSecret, {
      payment_method: { card: this.cardElement! },
    });

    if (error) {
      this.loading = false;
      this.errorKey = this.mapStripeError(error.code);
      return;
    }

    if (paymentIntent?.status === 'succeeded' || paymentIntent?.status === 'requires_capture') {
      this.billing.verifyPurchase(purchaseId, paymentIntent.id).subscribe({
        next: (verify) => {
          this.verifyResult = verify;
          this.loading = false;
          this.dialogRef.close({ ...this.result, fulfilled: verify.fulfilled });
        },
        error: () => {
          this.loading = false;
          this.errorKey = 'billing.providerError';
        },
      });
    } else {
      this.loading = false;
      this.errorKey = 'billing.payment.failed';
    }
  }

  close(): void {
    this.dialogRef.close(this.result);
  }

  private buildCardStyle(): Record<string, unknown> {
    const cs = getComputedStyle(document.documentElement);
    const get = (v: string) => cs.getPropertyValue(v).trim();
    return {
      base: {
        color: get('--fc-text') || '#1a1a1a',
        fontFamily: get('--fc-font-family') || 'inherit',
        fontSize: '14px',
        '::placeholder': { color: get('--fc-text-2') || '#888888' },
      },
      invalid: { color: '#b00020', iconColor: '#b00020' },
    };
  }

  private stripeLocale(): 'ar' | 'en' {
    return this.translate.currentLang === 'ar' ? 'ar' : 'en';
  }

  private mapStripeError(code: string | undefined): string {
    switch (code) {
      case 'card_declined': return 'billing.payment.declined';
      case 'insufficient_funds': return 'billing.payment.declined';
      case 'authentication_required': return 'billing.payment.requires_action';
      default: return 'billing.payment.failed';
    }
  }
}

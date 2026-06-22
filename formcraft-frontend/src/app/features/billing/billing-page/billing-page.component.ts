import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { BillingService } from '../../../core/services/billing.service';
import {
  BillingInterval,
  BillingOptionsResponse,
  BillingTierOption,
  SubscriptionResponse,
} from '../../../shared/models/billing.models';
import { CheckoutDialogComponent } from '../checkout-dialog/checkout-dialog.component';

// Tier order for ranking comparisons
const TIER_ORDER = ['starter', 'professional', 'enterprise', 'platform'];

// Features displayed per tier (i18n keys)
export const TIER_FEATURES: Record<string, string[]> = {
  starter: [
    'billing.features.designers_1',
    'billing.features.operators_3',
    'billing.features.submissions_100',
    'billing.features.templates_basic',
    'billing.features.pdf_export',
    'billing.features.overlay_print',
  ],
  professional: [
    'billing.features.designers_5',
    'billing.features.operators_25',
    'billing.features.submissions_unlimited',
    'billing.features.templates_unlimited',
    'billing.features.pdf_export',
    'billing.features.overlay_print',
    'billing.features.batch_processing',
    'billing.features.analytics',
    'billing.features.reference_data',
  ],
  enterprise: [
    'billing.features.designers_unlimited',
    'billing.features.operators_unlimited',
    'billing.features.submissions_unlimited',
    'billing.features.templates_unlimited',
    'billing.features.pdf_export',
    'billing.features.overlay_print',
    'billing.features.batch_processing',
    'billing.features.analytics',
    'billing.features.sso',
    'billing.features.custom_domain',
    'billing.features.api_access',
    'billing.features.dedicated_support',
    'billing.features.sla',
  ],
  platform: [
    'billing.features.all_enterprise',
    'billing.features.external_portal',
    'billing.features.template_marketplace',
    'billing.features.custom_integrations',
    'billing.features.white_label',
    'billing.features.custom_analytics',
  ],
};

@Component({
  selector: 'fc-billing-page',
  standalone: false,
  templateUrl: './billing-page.component.html',
  styleUrls: ['./billing-page.component.scss'],
})
export class BillingPageComponent implements OnInit {
  options?: BillingOptionsResponse;
  currentSubscription: SubscriptionResponse | null = null;
  loading = false;
  subLoading = false;
  cancelConfirming = false;
  billingInterval: BillingInterval = 'monthly';

  readonly tierFeatures = TIER_FEATURES;

  constructor(private billing: BillingService, private dialog: MatDialog) {}

  ngOnInit(): void {
    this.loading = true;
    this.billing.getOptions().subscribe({
      next: (options) => { this.options = options; this.loading = false; },
      error: () => { this.loading = false; },
    });
    this.billing.getCurrentSubscription().subscribe({
      next: (sub) => {
        this.currentSubscription = sub;
        if (sub?.billing_interval) this.billingInterval = sub.billing_interval;
      },
      error: () => { this.currentSubscription = null; },
    });
  }

  getTierIndex(tier: string): number {
    return TIER_ORDER.indexOf(tier);
  }

  isUpgrade(tier: BillingTierOption): boolean {
    if (!this.options) return false;
    return this.getTierIndex(tier.tier) > this.getTierIndex(this.options.current_tier);
  }

  isDowngrade(tier: BillingTierOption): boolean {
    if (!this.options) return false;
    return this.getTierIndex(tier.tier) < this.getTierIndex(this.options.current_tier);
  }

  isCustomPricing(tier: BillingTierOption): boolean {
    return tier.tier === 'enterprise' || tier.tier === 'platform';
  }

  buyOrUpgrade(tier: BillingTierOption): void {
    if (this.currentSubscription && this.currentSubscription.status !== 'cancelled') {
      this.dialog.open(CheckoutDialogComponent, {
        width: '520px',
        data: { mode: 'upgrade', tier: tier.tier },
      }).afterClosed().subscribe((result) => {
        if (result?.upgraded) this.ngOnInit();
      });
    } else {
      this.dialog.open(CheckoutDialogComponent, {
        width: '520px',
        data: { mode: 'subscribe', tier: tier.tier, billingInterval: this.billingInterval },
      }).afterClosed().subscribe((result) => {
        if (result?.subscribed) this.ngOnInit();
      });
    }
  }

  scheduleDowngrade(tier: string): void {
    this.subLoading = true;
    this.billing.scheduleDowngrade({ tier }).subscribe({
      next: () => { this.ngOnInit(); this.subLoading = false; },
      error: () => { this.subLoading = false; },
    });
  }

  cancelScheduledDowngrade(): void {
    this.subLoading = true;
    this.billing.cancelDowngradeSchedule().subscribe({
      next: () => { this.ngOnInit(); this.subLoading = false; },
      error: () => { this.subLoading = false; },
    });
  }

  cancelSubscription(): void {
    this.subLoading = true;
    this.billing.cancelSubscription().subscribe({
      next: () => { this.ngOnInit(); this.subLoading = false; this.cancelConfirming = false; },
      error: () => { this.subLoading = false; },
    });
  }

  reactivateSubscription(): void {
    this.subLoading = true;
    this.billing.reactivateSubscription().subscribe({
      next: () => { this.ngOnInit(); this.subLoading = false; },
      error: () => { this.subLoading = false; },
    });
  }

  openPaymentPortal(): void {
    this.billing.getPortalUrl(window.location.href).subscribe({
      next: (res) => { window.open(res.portal_url, '_blank'); },
    });
  }

  get renewalDate(): string {
    return this.currentSubscription?.current_period_end?.substring(0, 10) ?? '';
  }

  get downgradeDate(): string {
    return this.currentSubscription?.current_period_end?.substring(0, 10) ?? '';
  }
}

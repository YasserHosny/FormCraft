import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { BillingService } from '../../../core/services/billing.service';
import { BillingOptionsResponse, SubscriptionResponse } from '../../../shared/models/billing.models';
import { CheckoutDialogComponent } from '../checkout-dialog/checkout-dialog.component';

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

  constructor(private billing: BillingService, private dialog: MatDialog) {}

  ngOnInit(): void {
    this.loading = true;
    this.billing.getOptions().subscribe({
      next: (options) => {
        this.options = options;
        this.loading = false;
      },
      error: () => { this.loading = false; },
    });
    this.billing.getCurrentSubscription().subscribe({
      next: (sub) => { this.currentSubscription = sub; },
      error: () => { this.currentSubscription = null; },
    });
  }

  buyTier(tier: string): void {
    if (this.currentSubscription && this.currentSubscription.status !== 'cancelled') {
      // Upgrade path
      this.dialog.open(CheckoutDialogComponent, {
        width: '520px',
        data: { mode: 'upgrade', tier },
      }).afterClosed().subscribe((result) => {
        if (result?.upgraded) this.ngOnInit();
      });
    } else {
      // New subscription
      this.dialog.open(CheckoutDialogComponent, {
        width: '520px',
        data: { mode: 'subscribe', tier },
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

import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { BillingService } from '../../../core/services/billing.service';
import { BillingOptionsResponse } from '../../../shared/models/billing.models';
import { CheckoutDialogComponent } from '../checkout-dialog/checkout-dialog.component';

@Component({
  selector: 'fc-billing-page',
  standalone: false,
  templateUrl: './billing-page.component.html',
  styleUrls: ['./billing-page.component.scss'],
})
export class BillingPageComponent implements OnInit {
  options?: BillingOptionsResponse;
  loading = false;

  constructor(private billing: BillingService, private dialog: MatDialog) {}

  ngOnInit(): void {
    this.loading = true;
    this.billing.getOptions().subscribe({
      next: (options) => {
        this.options = options;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      },
    });
  }

  buyTier(tier: string): void {
    this.dialog.open(CheckoutDialogComponent, {
      width: '520px',
      data: {
        purpose: 'subscription_tier',
        target: { tier },
      },
    });
  }
}

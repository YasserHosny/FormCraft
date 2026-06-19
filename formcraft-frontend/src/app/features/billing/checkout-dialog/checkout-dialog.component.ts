import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { BillingService } from '../../../core/services/billing.service';
import { BillingPurchaseCreateRequest, BillingPurchaseCreateResponse } from '../../../shared/models/billing.models';

@Component({
  selector: 'fc-checkout-dialog',
  standalone: false,
  templateUrl: './checkout-dialog.component.html',
  styleUrls: ['./checkout-dialog.component.scss'],
})
export class CheckoutDialogComponent {
  loading = false;
  result?: BillingPurchaseCreateResponse;
  errorKey?: string;

  constructor(
    @Inject(MAT_DIALOG_DATA) public data: BillingPurchaseCreateRequest,
    private dialogRef: MatDialogRef<CheckoutDialogComponent>,
    private billing: BillingService
  ) {}

  start(): void {
    this.loading = true;
    this.errorKey = undefined;
    this.billing.createPurchase({ ...this.data, return_url: window.location.href }).subscribe({
      next: (result) => {
        this.result = result;
        this.loading = false;
        if (!result.checkout) {
          this.dialogRef.close(result);
        }
      },
      error: (error) => {
        this.loading = false;
        this.errorKey = error?.error?.detail || 'billing.providerError';
      },
    });
  }

  close(): void {
    this.dialogRef.close(this.result);
  }
}

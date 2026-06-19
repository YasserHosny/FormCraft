import { Component, OnInit } from '@angular/core';
import { BillingService } from '../../../core/services/billing.service';
import { BillingPurchase } from '../../../shared/models/billing.models';

@Component({
  selector: 'fc-purchase-history',
  standalone: false,
  templateUrl: './purchase-history.component.html',
  styleUrls: ['./purchase-history.component.scss'],
})
export class PurchaseHistoryComponent implements OnInit {
  purchases: BillingPurchase[] = [];
  loading = false;

  constructor(private billing: BillingService) {}

  ngOnInit(): void {
    this.loading = true;
    this.billing.listPurchases().subscribe({
      next: (result) => {
        this.purchases = result.items;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      },
    });
  }
}

import { NgModule } from '@angular/core';
import { SharedModule } from '../../shared/shared.module';
import { BillingRoutingModule } from './billing-routing.module';
import { BillingPageComponent } from './billing-page/billing-page.component';
import { CheckoutDialogComponent } from './checkout-dialog/checkout-dialog.component';
import { PurchaseHistoryComponent } from './purchase-history/purchase-history.component';

@NgModule({
  declarations: [
    BillingPageComponent,
    CheckoutDialogComponent,
    PurchaseHistoryComponent,
  ],
  imports: [SharedModule, BillingRoutingModule],
})
export class BillingModule {}

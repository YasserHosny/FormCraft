import { Component, Input } from '@angular/core';
import { Router } from '@angular/router';
import { OrganizationDetail } from '@shared/models/platform.models';

@Component({
  standalone: false,
  selector: 'app-subscription-tab',
  template: `
    <div class="tab-content" *ngIf="org">
      <p><strong>{{ 'PLATFORM.SUBSCRIPTION_TIER' | translate }}:</strong> {{ org.subscription_tier }}</p>
      <p><strong>{{ 'PLATFORM.STATUS' | translate }}:</strong> {{ org.status }}</p>
      <p>{{ 'PLATFORM.SUBSCRIPTION_INFO' | translate }}</p>
      <button mat-raised-button color="primary" (click)="startTierPurchase()">
        {{ 'billing.platform.startTierPurchase' | translate }}
      </button>
    </div>
  `,
  styles: [` .tab-content { padding: 16px; } `],
})
export class SubscriptionTabComponent {
  @Input() org: OrganizationDetail | null = null;

  constructor(private router: Router) {}

  startTierPurchase(): void {
    this.router.navigate(['/billing'], {
      queryParams: this.org ? { organization_id: this.org.id, purpose: 'subscription_tier' } : { purpose: 'subscription_tier' },
    });
  }
}

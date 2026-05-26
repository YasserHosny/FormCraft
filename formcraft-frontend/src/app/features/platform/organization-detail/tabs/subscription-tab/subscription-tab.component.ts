import { Component, Input } from '@angular/core';
import { OrganizationDetail } from '../../../../shared/models/platform.models';

@Component({
  selector: 'app-subscription-tab',
  template: `
    <div class="tab-content" *ngIf="org">
      <p><strong>{{ 'PLATFORM.SUBSCRIPTION_TIER' | translate }}:</strong> {{ org.subscription_tier }}</p>
      <p><strong>{{ 'PLATFORM.STATUS' | translate }}:</strong> {{ org.status }}</p>
      <p>{{ 'PLATFORM.SUBSCRIPTION_INFO' | translate }}</p>
    </div>
  `,
  styles: [` .tab-content { padding: 16px; } `],
})
export class SubscriptionTabComponent {
  @Input() org: OrganizationDetail | null = null;
}

import { Component, Input } from '@angular/core';
import { OrganizationDetail } from '@shared/models/platform.models';

@Component({
  standalone: false,
  selector: 'app-users-tab',
  template: `
    <div class="tab-content" *ngIf="org">
      <p><strong>{{ 'PLATFORM.ACTIVE_USERS' | translate }}:</strong> {{ org.active_users_count }}</p>
      <p>{{ 'PLATFORM.USERS_READ_ONLY' | translate }}</p>
    </div>
  `,
  styles: [` .tab-content { padding: 16px; } `],
})
export class UsersTabComponent {
  @Input() org: OrganizationDetail | null = null;
}

import { Component, Input } from '@angular/core';
import { OrganizationDetail } from '@shared/models/platform.models';

@Component({
  standalone: false,
  selector: 'app-profile-tab',
  template: `
    <div class="tab-content" *ngIf="org">
      <p><strong>{{ 'PLATFORM.ORG_NAME_AR' | translate }}:</strong> {{ org.name_ar }}</p>
      <p><strong>{{ 'PLATFORM.ORG_NAME_EN' | translate }}:</strong> {{ org.name_en }}</p>
      <p><strong>{{ 'PLATFORM.DOMAIN' | translate }}:</strong> {{ org.domain || '-' }}</p>
      <p><strong>{{ 'PLATFORM.LOGO' | translate }}:</strong> {{ org.logo_url || '-' }}</p>
      <p><strong>{{ 'PLATFORM.BRANDING' | translate }}:</strong> {{ org.branding | json }}</p>
    </div>
  `,
  styles: [` .tab-content { padding: 16px; } `],
})
export class ProfileTabComponent {
  @Input() org: OrganizationDetail | null = null;
}

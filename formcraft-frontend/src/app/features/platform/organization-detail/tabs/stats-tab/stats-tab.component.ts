import { Component, Input } from '@angular/core';
import { OrganizationDetail } from '@shared/models/platform.models';

@Component({
  standalone: false,
  selector: 'app-stats-tab',
  template: `
    <div class="tab-content" *ngIf="org">
      <p><strong>{{ 'PLATFORM.TEMPLATES' | translate }}:</strong> {{ org.templates_count }}</p>
      <p><strong>{{ 'PLATFORM.SUBMISSIONS_THIS_MONTH' | translate }}:</strong> {{ org.submissions_this_month }}</p>
      <p><strong>{{ 'PLATFORM.TOTAL_SUBMISSIONS' | translate }}:</strong> {{ org.total_submissions }}</p>
      <p><strong>{{ 'PLATFORM.STORAGE_USAGE' | translate }}:</strong> {{ org.storage_usage || '-' }}</p>
    </div>
  `,
  styles: [` .tab-content { padding: 16px; } `],
})
export class StatsTabComponent {
  @Input() org: OrganizationDetail | null = null;
}

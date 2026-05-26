import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { TranslateModule } from '@ngx-translate/core';

import { AnalyticsService } from '../../services/analytics.service';

@Component({
  selector: 'app-template-usage-analytics',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatTableModule, TranslateModule],
  template: `
    <div class="template-usage-analytics">
      <h2>{{ 'analytics.templateUsage' | translate }}</h2>
      <mat-card>
        <div class="funnel" *ngIf="funnel">
          <div class="funnel-stage">
            <div class="count">{{ funnel.startedCount }}</div>
            <div class="label">{{ 'analytics.funnel.started' | translate }}</div>
          </div>
          <div class="funnel-stage">
            <div class="count">{{ funnel.draftCount }}</div>
            <div class="label">{{ 'analytics.funnel.draft' | translate }}</div>
          </div>
          <div class="funnel-stage">
            <div class="count">{{ funnel.submittedCount }}</div>
            <div class="label">{{ 'analytics.funnel.submitted' | translate }}</div>
          </div>
          <div class="funnel-stage">
            <div class="count">{{ funnel.printedCount }}</div>
            <div class="label">{{ 'analytics.funnel.printed' | translate }}</div>
          </div>
        </div>
      </mat-card>
    </div>
  `,
  styles: [`
    .template-usage-analytics { padding: 16px; }
    .funnel { display: flex; justify-content: space-around; padding: 24px 0; }
    .funnel-stage { text-align: center; }
    .funnel-stage .count { font-size: 2rem; font-weight: bold; }
    .funnel-stage .label { color: rgba(0,0,0,0.6); margin-top: 4px; }
  `],
})
export class TemplateUsageAnalyticsComponent implements OnInit {
  funnel: any = null;

  constructor(private analyticsService: AnalyticsService) {}

  ngOnInit(): void {
    // TODO: Wire to service in Phase 6
  }
}

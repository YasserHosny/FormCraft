import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule } from '@ngx-translate/core';

import { AnalyticsService } from '../../services/analytics.service';

@Component({
  selector: 'app-compliance-analytics',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatIconModule, TranslateModule],
  template: `
    <div class="compliance-analytics">
      <h2>{{ 'analytics.complianceAnalytics' | translate }}</h2>
      <div class="scorecards" *ngIf="scorecard">
        <mat-card class="scorecard">
          <mat-icon>verified</mat-icon>
          <div class="value">{{ scorecard.validatorCoveragePct | number:'1.1-1' }}%</div>
          <div class="label">{{ 'analytics.validatorCoverage' | translate }}</div>
        </mat-card>
        <mat-card class="scorecard">
          <mat-icon>translate</mat-icon>
          <div class="value">{{ scorecard.bilingualLabelPct | number:'1.1-1' }}%</div>
          <div class="label">{{ 'analytics.bilingualLabels' | translate }}</div>
        </mat-card>
        <mat-card class="scorecard">
          <mat-icon>stars</mat-icon>
          <div class="value">{{ scorecard.qualityScoreAvg | number:'1.1-1' }}</div>
          <div class="label">{{ 'analytics.qualityScore' | translate }}</div>
        </mat-card>
      </div>
      <div class="alert-banner" *ngIf="scorecard?.customerDataAccessSpike">
        <mat-icon color="warn">notification_important</mat-icon>
        {{ 'analytics.accessSpikeAlert' | translate }}
      </div>
    </div>
  `,
  styles: [`
    .compliance-analytics { padding: 16px; }
    .scorecards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 16px; }
    .scorecard { text-align: center; padding: 24px; }
    .scorecard .value { font-size: 2rem; font-weight: bold; margin: 8px 0; }
    .scorecard .label { color: rgba(0,0,0,0.6); }
    .alert-banner { display: flex; align-items: center; gap: 8px; padding: 12px; background: rgba(255,0,0,0.05); border-radius: 4px; }
  `],
})
export class ComplianceAnalyticsComponent implements OnInit {
  scorecard: any = null;

  constructor(private analyticsService: AnalyticsService) {}

  ngOnInit(): void {
    // TODO: Wire to service in Phase 5
  }
}

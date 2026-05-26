import { Component, OnInit } from '@angular/core';
import { PlatformService } from '../../../core/services/platform.service';
import { PlatformMetrics } from '../../../shared/models/platform.models';

@Component({
  selector: 'app-platform-dashboard',
  template: `
    <div class="dashboard-container">
      <h1>{{ 'PLATFORM.DASHBOARD_TITLE' | translate }}</h1>

      <div class="summary-cards">
        <mat-card>
          <mat-card-title>{{ metrics?.total_orgs ?? 0 }}</mat-card-title>
          <mat-card-content>{{ 'PLATFORM.TOTAL_ORGS' | translate }}</mat-card-content>
        </mat-card>
        <mat-card>
          <mat-card-title>{{ metrics?.total_users ?? 0 }}</mat-card-title>
          <mat-card-content>{{ 'PLATFORM.TOTAL_USERS' | translate }}</mat-card-content>
        </mat-card>
        <mat-card>
          <mat-card-title>{{ metrics?.total_submissions ?? 0 }}</mat-card-title>
          <mat-card-content>{{ 'PLATFORM.TOTAL_SUBMISSIONS' | translate }}</mat-card-content>
        </mat-card>
      </div>

      <div class="charts-row" *ngIf="metrics">
        <mat-card class="chart-card">
          <mat-card-header>
            <mat-card-title>{{ 'PLATFORM.ORGS_BY_TIER' | translate }}</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <canvas baseChart
              [type]="'pie'"
              [data]="tierChartData"
              [options]="{ responsive: true }">
            </canvas>
          </mat-card-content>
        </mat-card>

        <mat-card class="chart-card">
          <mat-card-header>
            <mat-card-title>{{ 'PLATFORM.SUBMISSION_TREND' | translate }}</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <canvas baseChart
              [type]="'line'"
              [data]="trendChartData"
              [options]="{ responsive: true }">
            </canvas>
          </mat-card-content>
        </mat-card>
      </div>

      <mat-card *ngIf="metrics?.tier_limit_alerts?.length">
        <mat-card-header>
          <mat-card-title>{{ 'PLATFORM.TIER_ALERTS' | translate }}</mat-card-title>
        </mat-card-header>
        <mat-card-content>
          <mat-list>
            <mat-list-item *ngFor="let alert of metrics.tier_limit_alerts">
              {{ alert.org_name }} — {{ alert.limit_type }}: {{ alert.current_usage }}/{{ alert.limit_value }}
            </mat-list-item>
          </mat-list>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [
    `.dashboard-container { padding: 16px; }`,
    `.summary-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }`,
    `.charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }`,
    `.chart-card { min-height: 300px; }`,
  ],
})
export class PlatformDashboardComponent implements OnInit {
  metrics: PlatformMetrics | null = null;

  tierChartData: any = { labels: [], datasets: [] };
  trendChartData: any = { labels: [], datasets: [] };

  constructor(private platformService: PlatformService) {}

  ngOnInit(): void {
    this.platformService.getMetrics().subscribe((m) => {
      this.metrics = m;
      this.buildCharts(m);
    });
  }

  private buildCharts(m: PlatformMetrics): void {
    this.tierChartData = {
      labels: Object.keys(m.orgs_by_tier),
      datasets: [
        {
          data: Object.values(m.orgs_by_tier),
          backgroundColor: ['#3f51b5', '#e91e63', '#009688', '#ff9800'],
        },
      ],
    };

    this.trendChartData = {
      labels: m.submission_volume_trend.map((t) => t.month),
      datasets: [
        {
          label: 'Submissions',
          data: m.submission_volume_trend.map((t) => t.count),
          borderColor: '#3f51b5',
          fill: false,
        },
      ],
    };
  }
}

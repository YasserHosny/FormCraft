import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule } from '@ngx-translate/core';
import { ThemePreferenceService } from '../../../core/services/theme-preference.service';

/**
 * Shown inside the Spark layout when a feature has no Spark page yet.
 * Stays within the Spark shell (toolbar visible) and offers a single
 * "Open in Classic Mode" button that switches the theme and navigates.
 */
@Component({
  selector: 'fc-spark-feature-bridge',
  standalone: true,
  imports: [CommonModule, MatIconModule, TranslateModule],
  template: `
    <div class="bridge-page">
      <div class="bridge-card">
        <div class="bridge-icon">
          <mat-icon>{{ icon }}</mat-icon>
        </div>
        <h2 class="bridge-title">{{ featureName | translate }}</h2>
        <p class="bridge-body">{{ 'nav.bridge_body' | translate }}</p>
        <button class="fc-btn primary bridge-btn" (click)="openInClassic()">
          <mat-icon>history</mat-icon>
          {{ 'nav.bridge_open_classic' | translate }}
        </button>
      </div>
    </div>
  `,
  styles: [`
    .bridge-page {
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: calc(100vh - 64px);
      padding: 32px;
      background: var(--fc-bg);
    }
    .bridge-card {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 16px;
      max-width: 420px;
      text-align: center;
      padding: 40px 32px;
      background: var(--fc-surface);
      border: 1px solid var(--fc-border);
      border-radius: 12px;
      box-shadow: 0 2px 12px rgba(0,0,0,.06);
    }
    .bridge-icon {
      width: 72px;
      height: 72px;
      border-radius: 50%;
      background: var(--fc-primary-light, rgba(63,81,181,.1));
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .bridge-icon mat-icon {
      font-size: 36px;
      width: 36px;
      height: 36px;
      color: var(--fc-primary);
    }
    .bridge-title {
      margin: 0;
      font-size: 20px;
      font-weight: 600;
      color: var(--fc-text);
    }
    .bridge-body {
      margin: 0;
      font-size: 14px;
      color: var(--fc-text-2);
      line-height: 1.6;
    }
    .bridge-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      margin-top: 8px;
    }
  `],
})
export class SparkFeatureBridgeComponent implements OnInit {
  featureName = '';
  icon = 'open_in_new';
  private classicRoute = '/';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private themePreference: ThemePreferenceService,
  ) {}

  ngOnInit(): void {
    const data = this.route.snapshot.data;
    this.featureName = data['featureName'] ?? '';
    this.icon = data['featureIcon'] ?? 'open_in_new';
    this.classicRoute = data['classicRoute'] ?? '/';
  }

  openInClassic(): void {
    this.themePreference.setPreference('classic');
    this.router.navigate([this.classicRoute], { replaceUrl: true });
  }
}

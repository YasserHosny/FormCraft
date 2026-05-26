import { Component } from '@angular/core';
import { MatTabsModule } from '@angular/material/tabs';
import { RouterModule } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-analytics-dashboard',
  standalone: true,
  imports: [RouterModule, MatTabsModule, TranslateModule],
  template: `
    <div class="analytics-dashboard">
      <h1>{{ 'analytics.title' | translate }}</h1>
      <nav mat-tab-nav-bar>
        <a mat-tab-link
           routerLink="fields"
           routerLinkActive #rlaFields="routerLinkActive"
           [active]="rlaFields.isActive">
          {{ 'analytics.fieldAnalytics' | translate }}
        </a>
        <a mat-tab-link
           routerLink="operators"
           routerLinkActive #rlaOps="routerLinkActive"
           [active]="rlaOps.isActive">
          {{ 'analytics.operatorAnalytics' | translate }}
        </a>
        <a mat-tab-link
           routerLink="compliance"
           routerLinkActive #rlaComp="routerLinkActive"
           [active]="rlaComp.isActive">
          {{ 'analytics.complianceAnalytics' | translate }}
        </a>
        <a mat-tab-link
           routerLink="templates"
           routerLinkActive #rlaTpl="routerLinkActive"
           [active]="rlaTpl.isActive">
          {{ 'analytics.templateUsage' | translate }}
        </a>
      </nav>
      <router-outlet></router-outlet>
    </div>
  `,
  styles: [`
    .analytics-dashboard { padding: 16px; }
    h1 { margin-bottom: 16px; }
  `],
})
export class AnalyticsDashboardComponent {}

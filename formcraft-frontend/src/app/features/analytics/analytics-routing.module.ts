import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./components/analytics-dashboard/analytics-dashboard.component').then(m => m.AnalyticsDashboardComponent),
    children: [
      { path: 'fields', loadComponent: () => import('./components/field-analytics/field-analytics.component').then(m => m.FieldAnalyticsComponent) },
      { path: 'operators', loadComponent: () => import('./components/operator-analytics/operator-analytics.component').then(m => m.OperatorAnalyticsComponent) },
      { path: 'compliance', loadComponent: () => import('./components/compliance-analytics/compliance-analytics.component').then(m => m.ComplianceAnalyticsComponent) },
      { path: 'templates', loadComponent: () => import('./components/template-usage-analytics/template-usage-analytics.component').then(m => m.TemplateUsageAnalyticsComponent) },
      { path: '', redirectTo: 'fields', pathMatch: 'full' },
    ],
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class AnalyticsRoutingModule {}

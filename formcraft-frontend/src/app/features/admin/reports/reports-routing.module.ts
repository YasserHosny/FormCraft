import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  {
    path: 'transactions',
    loadComponent: () => import('./transaction-register/transaction-register.component').then(m => m.TransactionRegisterComponent),
  },
  {
    path: 'reconciliation',
    loadComponent: () => import('./daily-reconciliation/daily-reconciliation.component').then(m => m.DailyReconciliationComponent),
  },
  {
    path: 'period-summary',
    loadComponent: () => import('./period-summary/period-summary.component').then(m => m.PeriodSummaryComponent),
  },
  {
    path: 'builder',
    loadComponent: () => import('./report-builder/report-builder.component').then(m => m.ReportBuilderComponent),
  },
  {
    path: 'financial/beneficiary',
    loadComponent: () => import('./financial-reports/beneficiary-report.component').then(m => m.BeneficiaryReportComponent),
  },
  {
    path: 'financial/void-reprint',
    loadComponent: () => import('./financial-reports/void-reprint-register.component').then(m => m.VoidReprintRegisterComponent),
  },
  {
    path: 'financial/signatory-usage',
    loadComponent: () => import('./financial-reports/signatory-usage.component').then(m => m.SignatoryUsageComponent),
  },
  {
    path: 'schedules',
    loadComponent: () => import('./report-schedules/report-schedules.component').then(m => m.ReportSchedulesComponent),
  },
  { path: '', redirectTo: 'transactions', pathMatch: 'full' },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class ReportsRoutingModule {}

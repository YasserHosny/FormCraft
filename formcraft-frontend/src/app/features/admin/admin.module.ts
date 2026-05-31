import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { ReviewQueueComponent } from './review-queue/review-queue.component';
import { GovernanceDashboardComponent } from './governance-dashboard/governance-dashboard.component';
import { ReviewTimelineComponent } from './review-timeline/review-timeline.component';
import { TemplateFeedbackOverviewComponent } from './template-feedback/template-feedback-overview.component';
import { PrinterProfilesComponent } from './printer-profiles/printer-profiles.component';
import { ReferenceDataListComponent } from './reference-data/reference-data-list.component';
import { ReferenceEntriesComponent } from './reference-data/reference-entries.component';
import { OrgSettingsComponent } from './org-settings/org-settings.component';
import { DepartmentsComponent } from './departments/departments.component';
import { UserManagementComponent } from './users/user-management.component';
import { InvitationsComponent } from './invitations/invitations.component';
import { TemplateGovernanceComponent } from './template-governance/template-governance.component';
import { DataExportComponent } from './data-export/data-export.component';
import { ExportSchedulesComponent } from './export-schedules/export-schedules.component';
import { IntegrationsComponent } from './integrations/integrations.component';
import { PortalAdminComponent } from './portal/portal-admin.component';
import { ValidatorsAdminComponent } from './validators/validators-admin.component';

const routes: Routes = [
  { path: '', redirectTo: 'settings', pathMatch: 'full' },
  { path: 'reviews', component: ReviewQueueComponent },
  { path: 'governance', component: GovernanceDashboardComponent },
  { path: 'review-timeline/:template_id', component: ReviewTimelineComponent },
  { path: 'template-feedback', component: TemplateFeedbackOverviewComponent },
  { path: 'templates', component: TemplateGovernanceComponent },
  { path: 'printer-profiles', component: PrinterProfilesComponent },
  { path: 'reference-data', component: ReferenceDataListComponent },
  { path: 'reference-data/:listId/entries', component: ReferenceEntriesComponent },
  { path: 'settings', component: OrgSettingsComponent },
  { path: 'departments', component: DepartmentsComponent },
  { path: 'users', component: UserManagementComponent },
  { path: 'invitations', component: InvitationsComponent },
  { path: 'export', component: DataExportComponent },
  { path: 'export/schedules', component: ExportSchedulesComponent },
  { path: 'integrations', component: IntegrationsComponent },
  { path: 'reports', loadChildren: () => import('./reports/reports.module').then(m => m.ReportsModule) },
  { path: 'portal', component: PortalAdminComponent },
  { path: 'validators', component: ValidatorsAdminComponent },
  { path: 'batch-schedules', loadChildren: () => import('./batch-schedules/batch-schedules.module').then(m => m.BatchSchedulesModule) },
  { path: 'retention', loadChildren: () => import('./retention/retention-routing.module').then(m => m.RetentionRoutingModule) },
];

@NgModule({
  declarations: [],
  imports: [
    SharedModule,
    RouterModule.forChild(routes),
    ReviewQueueComponent,
    GovernanceDashboardComponent,
    ReviewTimelineComponent,
    TemplateFeedbackOverviewComponent,
    PrinterProfilesComponent,
    ReferenceDataListComponent,
    ReferenceEntriesComponent,
    OrgSettingsComponent,
    DepartmentsComponent,
    UserManagementComponent,
    InvitationsComponent,
    TemplateGovernanceComponent,
    DataExportComponent,
    ExportSchedulesComponent,
    IntegrationsComponent,
    PortalAdminComponent,
    ValidatorsAdminComponent,
  ],
})
export class AdminModule {}

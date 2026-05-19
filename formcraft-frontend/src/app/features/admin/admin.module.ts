import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { ReviewQueueComponent } from './review-queue/review-queue.component';
import { TemplateFeedbackOverviewComponent } from './template-feedback/template-feedback-overview.component';
import { PrinterProfilesComponent } from './printer-profiles/printer-profiles.component';
import { ReferenceDataListComponent } from './reference-data/reference-data-list.component';
import { ReferenceEntriesComponent } from './reference-data/reference-entries.component';
import { OrgSettingsComponent } from './org-settings/org-settings.component';
import { DepartmentsComponent } from './departments/departments.component';
import { UserManagementComponent } from './users/user-management.component';
import { InvitationsComponent } from './invitations/invitations.component';

const routes: Routes = [
  { path: 'reviews', component: ReviewQueueComponent },
  { path: 'template-feedback', component: TemplateFeedbackOverviewComponent },
  { path: 'printer-profiles', component: PrinterProfilesComponent },
  { path: 'reference-data', component: ReferenceDataListComponent },
  { path: 'reference-data/:listId/entries', component: ReferenceEntriesComponent },
  { path: 'settings', component: OrgSettingsComponent },
  { path: 'departments', component: DepartmentsComponent },
  { path: 'users', component: UserManagementComponent },
  { path: 'invitations', component: InvitationsComponent },
];

@NgModule({
  declarations: [],
  imports: [
    SharedModule,
    RouterModule.forChild(routes),
    ReviewQueueComponent,
    TemplateFeedbackOverviewComponent,
    PrinterProfilesComponent,
    ReferenceDataListComponent,
    ReferenceEntriesComponent,
    OrgSettingsComponent,
    DepartmentsComponent,
    UserManagementComponent,
    InvitationsComponent,
  ],
})
export class AdminModule {}

import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { ReviewQueueComponent } from './review-queue/review-queue.component';
import { TemplateFeedbackOverviewComponent } from './template-feedback/template-feedback-overview.component';
import { PrinterProfilesComponent } from './printer-profiles/printer-profiles.component';
import { ReferenceDataListComponent } from './reference-data/reference-data-list.component';
import { ReferenceEntriesComponent } from './reference-data/reference-entries.component';

const routes: Routes = [
  { path: 'reviews', component: ReviewQueueComponent },
  { path: 'template-feedback', component: TemplateFeedbackOverviewComponent },
  { path: 'printer-profiles', component: PrinterProfilesComponent },
  { path: 'reference-data', component: ReferenceDataListComponent },
  { path: 'reference-data/:listId/entries', component: ReferenceEntriesComponent },
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
  ],
})
export class AdminModule {}

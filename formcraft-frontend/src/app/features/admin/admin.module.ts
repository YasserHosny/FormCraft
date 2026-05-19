import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { ReviewQueueComponent } from './review-queue/review-queue.component';
import { TemplateFeedbackOverviewComponent } from './template-feedback/template-feedback-overview.component';
import { PrinterProfilesComponent } from './printer-profiles/printer-profiles.component';

const routes: Routes = [
  { path: 'reviews', component: ReviewQueueComponent },
  { path: 'template-feedback', component: TemplateFeedbackOverviewComponent },
  { path: 'printer-profiles', component: PrinterProfilesComponent },
];

@NgModule({
  declarations: [],
  imports: [SharedModule, RouterModule.forChild(routes), ReviewQueueComponent, TemplateFeedbackOverviewComponent, PrinterProfilesComponent],
})
export class AdminModule {}
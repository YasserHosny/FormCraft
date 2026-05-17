import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { ReviewQueueComponent } from './review-queue/review-queue.component';
import { TemplateFeedbackOverviewComponent } from './template-feedback/template-feedback-overview.component';

const routes: Routes = [
  { path: 'reviews', component: ReviewQueueComponent },
  { path: 'template-feedback', component: TemplateFeedbackOverviewComponent },
];

@NgModule({
  declarations: [],
  imports: [SharedModule, RouterModule.forChild(routes), ReviewQueueComponent, TemplateFeedbackOverviewComponent],
})
export class AdminModule {}
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { ReviewQueueComponent } from './review-queue/review-queue.component';

const routes: Routes = [
  { path: 'reviews', component: ReviewQueueComponent },
];

@NgModule({
  declarations: [ReviewQueueComponent],
  imports: [SharedModule, RouterModule.forChild(routes)],
})
export class AdminModule {}
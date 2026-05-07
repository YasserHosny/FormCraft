import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { FeedbackAdminComponent } from './components/feedback-admin/feedback-admin.component';

const routes: Routes = [
  { path: '', component: FeedbackAdminComponent },
];

@NgModule({
  declarations: [FeedbackAdminComponent],
  imports: [SharedModule, RouterModule.forChild(routes)],
})
export class FeedbackModule {}
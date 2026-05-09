import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { SharedModule } from '../../shared/shared.module';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatPaginatorModule } from '@angular/material/paginator';

import { MyFeedbackComponent } from './components/my-feedback/my-feedback.component';
import { MyFeedbackService } from './services/my-feedback.service';

const routes: Routes = [
  { path: '', component: MyFeedbackComponent },
];

@NgModule({
  declarations: [MyFeedbackComponent],
  imports: [
    SharedModule,
    MatExpansionModule,
    MatPaginatorModule,
    RouterModule.forChild(routes),
  ],
  providers: [MyFeedbackService],
})
export class MyFeedbackModule {}

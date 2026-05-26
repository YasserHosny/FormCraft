import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { OcrBatchCreateComponent } from './ocr-batch-create.component';
import { OcrBatchDetailComponent } from './ocr-batch-detail.component';
import { OcrBatchListComponent } from './ocr-batch-list.component';

const routes: Routes = [
  { path: '', component: OcrBatchListComponent },
  { path: 'new', component: OcrBatchCreateComponent },
  { path: ':batchId', component: OcrBatchDetailComponent },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class OcrOnboardingRoutingModule {}

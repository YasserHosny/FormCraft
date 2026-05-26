import { NgModule } from '@angular/core';

import { SharedModule } from '../../../shared/shared.module';
import { OcrBatchCreateComponent } from './ocr-batch-create.component';
import { OcrBatchDetailComponent } from './ocr-batch-detail.component';
import { OcrBatchListComponent } from './ocr-batch-list.component';
import { OcrOnboardingRoutingModule } from './ocr-onboarding-routing.module';

@NgModule({
  imports: [
    SharedModule,
    OcrOnboardingRoutingModule,
    OcrBatchCreateComponent,
    OcrBatchDetailComponent,
    OcrBatchListComponent,
  ],
})
export class OcrOnboardingModule {}

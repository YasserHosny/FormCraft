import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatStepperModule } from '@angular/material/stepper';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialogModule } from '@angular/material/dialog';

import { BatchListComponent } from './batch-list/batch-list.component';
import { BatchCreateWizardComponent } from './batch-create-wizard/batch-create-wizard.component';
import { StepTemplateComponent } from './batch-create-wizard/step-template/step-template.component';
import { StepDataSourceComponent } from './batch-create-wizard/step-data-source/step-data-source.component';
import { StepColumnMapperComponent } from './batch-create-wizard/step-column-mapper/column-mapper.component';
import { StepValidationComponent } from './batch-create-wizard/step-validation/step-validation.component';
import { StepGenerateComponent } from './batch-create-wizard/step-generate/step-generate.component';
import { BatchDetailComponent } from './batch-detail/batch-detail.component';
import { BatchErrorReportComponent } from './batch-error-report/batch-error-report.component';

const routes: Routes = [
  { path: '', component: BatchListComponent },
  { path: 'new', component: BatchCreateWizardComponent },
  { path: ':id', component: BatchDetailComponent },
];

@NgModule({
  declarations: [
    BatchListComponent,
    BatchCreateWizardComponent,
    StepTemplateComponent,
    StepDataSourceComponent,
    StepColumnMapperComponent,
    StepValidationComponent,
    StepGenerateComponent,
    BatchDetailComponent,
    BatchErrorReportComponent,
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    RouterModule.forChild(routes),
    MatStepperModule,
    MatButtonModule,
    MatIconModule,
    MatProgressBarModule,
    MatTableModule,
    MatPaginatorModule,
    MatCardModule,
    MatChipsModule,
    MatDialogModule,
  ],
})
export class BatchQueueModule {}

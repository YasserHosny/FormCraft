import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { SharedModule } from '../../../shared/shared.module';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialogModule } from '@angular/material/dialog';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatBadgeModule } from '@angular/material/badge';
import { MatDividerModule } from '@angular/material/divider';
import { MatMenuModule } from '@angular/material/menu';

import { FillComponent } from './fill.component';
import { FieldRendererComponent } from '../components/field-renderer/field-renderer.component';
import { FormToolbarComponent } from '../components/form-toolbar/form-toolbar.component';
import { ErrorSummaryComponent } from '../components/error-summary/error-summary.component';
import { VersionWarningComponent } from '../components/version-warning/version-warning.component';
import { TemplateFeedbackDialogComponent } from '../components/template-feedback-dialog/template-feedback-dialog.component';
import { OfflineSyncPanelComponent } from '../offline/offline-sync-panel.component';
const routes: Routes = [
  { path: ':templateId', component: FillComponent },
];

@NgModule({
  declarations: [
    FillComponent,
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    SharedModule,
    RouterModule.forChild(routes),
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatDialogModule,
    MatToolbarModule,
    MatBadgeModule,
    MatDividerModule,
    MatMenuModule,
    FieldRendererComponent,
    FormToolbarComponent,
    ErrorSummaryComponent,
    VersionWarningComponent,
    TemplateFeedbackDialogComponent,
    OfflineSyncPanelComponent,
  ],
  providers: [],
})
export class FormFillerModule {}

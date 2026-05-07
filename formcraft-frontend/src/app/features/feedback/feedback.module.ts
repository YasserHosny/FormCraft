import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { MatDialogModule } from '@angular/material/dialog';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatChipsModule } from '@angular/material/chips';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { ReactiveFormsModule } from '@angular/forms';
import { FeedbackAdminComponent } from './components/feedback-admin/feedback-admin.component';
import { LabelManagerComponent } from './components/label-manager/label-manager.component';

const routes: Routes = [
  { path: '', component: FeedbackAdminComponent },
];

@NgModule({
  declarations: [FeedbackAdminComponent, LabelManagerComponent],
  imports: [
    SharedModule,
    RouterModule.forChild(routes),
    MatDialogModule,
    MatAutocompleteModule,
    MatChipsModule,
    MatDatepickerModule,
    MatNativeDateModule,
    ReactiveFormsModule,
  ],
})
export class FeedbackModule {}
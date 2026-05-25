import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';

import { BatchScheduleAdminComponent } from './batch-schedule-admin.component';

const routes: Routes = [
  { path: '', component: BatchScheduleAdminComponent },
];

@NgModule({
  declarations: [BatchScheduleAdminComponent],
  imports: [
    CommonModule,
    RouterModule.forChild(routes),
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatTableModule,
  ],
})
export class BatchSchedulesModule {}

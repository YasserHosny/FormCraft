import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialogModule } from '@angular/material/dialog';

@Component({
  selector: 'app-schedule-form-dialog',
  standalone: true,
  imports: [CommonModule, MatDialogModule],
  template: `<h2 mat-dialog-title>{{ 'reports.schedule_form' | translate }}</h2>`,
})
export class ScheduleFormDialogComponent {}

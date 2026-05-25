import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';

@Component({
  selector: 'app-report-schedules',
  standalone: true,
  imports: [CommonModule, MatCardModule],
  template: `<mat-card><mat-card-title>{{ 'reports.schedules' | translate }}</mat-card-title></mat-card>`,
})
export class ReportSchedulesComponent {}

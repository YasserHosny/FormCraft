import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';

@Component({
  selector: 'app-report-builder',
  standalone: true,
  imports: [CommonModule, MatCardModule],
  template: `<mat-card><mat-card-title>{{ 'reports.report_builder' | translate }}</mat-card-title></mat-card>`,
})
export class ReportBuilderComponent {}

import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';

@Component({
  selector: 'app-beneficiary-report',
  standalone: true,
  imports: [CommonModule, MatCardModule],
  template: `<mat-card><mat-card-title>{{ 'reports.beneficiary_report' | translate }}</mat-card-title></mat-card>`,
})
export class BeneficiaryReportComponent {}

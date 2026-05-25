import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';

@Component({
  selector: 'app-daily-reconciliation',
  standalone: true,
  imports: [CommonModule, MatCardModule],
  template: `<mat-card><mat-card-title>{{ 'reports.daily_reconciliation' | translate }}</mat-card-title></mat-card>`,
})
export class DailyReconciliationComponent {}

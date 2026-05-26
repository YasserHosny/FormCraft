import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { MatCardModule } from '@angular/material/card';

@Component({
  selector: 'app-daily-reconciliation',
  standalone: true,
  imports: [CommonModule, MatCardModule, TranslateModule],
  template: `<mat-card><mat-card-title>{{ 'reports.daily_reconciliation' | translate }}</mat-card-title></mat-card>`,
})
export class DailyReconciliationComponent {}

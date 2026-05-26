import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { MatCardModule } from '@angular/material/card';

@Component({
  selector: 'app-period-summary',
  standalone: true,
  imports: [CommonModule, MatCardModule, TranslateModule],
  template: `<mat-card><mat-card-title>{{ 'reports.period_summary' | translate }}</mat-card-title></mat-card>`,
})
export class PeriodSummaryComponent {}

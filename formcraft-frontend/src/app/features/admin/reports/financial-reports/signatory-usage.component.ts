import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';

@Component({
  selector: 'app-signatory-usage',
  standalone: true,
  imports: [CommonModule, MatCardModule],
  template: `<mat-card><mat-card-title>{{ 'reports.signatory_usage' | translate }}</mat-card-title></mat-card>`,
})
export class SignatoryUsageComponent {}

import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-export-dialog',
  standalone: true,
  imports: [CommonModule, MatDialogModule, MatButtonModule, MatFormFieldModule, MatSelectModule, TranslateModule],
  template: `
    <h2 mat-dialog-title>{{ 'analytics.export' | translate }}</h2>
    <mat-dialog-content>
      <mat-form-field appearance="fill">
        <mat-label>{{ 'analytics.export' | translate }}</mat-label>
        <mat-select [(value)]="selectedFormat">
          <mat-option value="csv">{{ 'analytics.exportCsv' | translate }}</mat-option>
          <mat-option value="png">{{ 'analytics.exportPng' | translate }}</mat-option>
          <mat-option value="pdf">{{ 'analytics.exportPdf' | translate }}</mat-option>
        </mat-select>
      </mat-form-field>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>{{ 'common.cancel' | translate }}</button>
      <button mat-raised-button color="primary" (click)="export()">{{ 'analytics.export' | translate }}</button>
    </mat-dialog-actions>
  `,
})
export class ExportDialogComponent {
  selectedFormat = 'csv';

  export(): void {
    // TODO: Trigger export via AnalyticsService
  }
}

import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-report-export-button',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatIconModule, MatMenuModule, TranslateModule],
  template: `
    <button mat-stroked-button [matMenuTriggerFor]="exportMenu" [disabled]="loading">
      <mat-icon>download</mat-icon>
      {{ 'reports.export' | translate }}
    </button>
    <mat-menu #exportMenu="matMenu">
      <button mat-menu-item (click)="export.emit('xlsx')">
        <mat-icon>table_view</mat-icon>
        <span>{{ 'reports.export_excel' | translate }}</span>
      </button>
      <button mat-menu-item (click)="export.emit('csv')">
        <mat-icon>text_snippet</mat-icon>
        <span>{{ 'reports.export_csv' | translate }}</span>
      </button>
      <button mat-menu-item (click)="export.emit('pdf')">
        <mat-icon>picture_as_pdf</mat-icon>
        <span>{{ 'reports.export_pdf' | translate }}</span>
      </button>
    </mat-menu>
  `
})
export class ReportExportButtonComponent {
  @Input() loading = false;
  @Output() export = new EventEmitter<'xlsx' | 'csv' | 'pdf'>();
}

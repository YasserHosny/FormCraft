import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatSelectModule } from '@angular/material/select';
import { MatNativeDateModule } from '@angular/material/core';
import { TranslateModule } from '@ngx-translate/core';

export interface FilterPanelConfig {
  showDateRange: boolean;
  showTemplate: boolean;
  showBranch: boolean;
  showDepartment: boolean;
  showOperator: boolean;
  showStatus: boolean;
  showCustomerQuery: boolean;
}

@Component({
  selector: 'app-report-filter-panel',
  standalone: true,
  imports: [CommonModule, FormsModule, MatFormFieldModule, MatInputModule, MatDatepickerModule, MatSelectModule, MatNativeDateModule, TranslateModule],
  template: `
    <div class="filter-panel">
      <div class="filter-row">
        <mat-form-field *ngIf="config.showDateRange" appearance="outline">
          <mat-label>{{ 'reports.date_from' | translate }}</mat-label>
          <input matInput [matDatepicker]="fromPicker" [(ngModel)]="filters.dateFrom" (ngModelChange)="onChange()">
          <mat-datepicker-toggle matSuffix [for]="fromPicker"></mat-datepicker-toggle>
          <mat-datepicker #fromPicker></mat-datepicker>
        </mat-form-field>
        <mat-form-field *ngIf="config.showDateRange" appearance="outline">
          <mat-label>{{ 'reports.date_to' | translate }}</mat-label>
          <input matInput [matDatepicker]="toPicker" [(ngModel)]="filters.dateTo" (ngModelChange)="onChange()">
          <mat-datepicker-toggle matSuffix [for]="toPicker"></mat-datepicker-toggle>
          <mat-datepicker #toPicker></mat-datepicker>
        </mat-form-field>
        <mat-form-field *ngIf="config.showTemplate" appearance="outline">
          <mat-label>{{ 'reports.template' | translate }}</mat-label>
          <mat-select [(ngModel)]="filters.templateId" (selectionChange)="onChange()">
            <mat-option *ngFor="let t of templates" [value]="t.id">{{ t.name }}</mat-option>
          </mat-select>
        </mat-form-field>
        <mat-form-field *ngIf="config.showBranch" appearance="outline">
          <mat-label>{{ 'reports.branch' | translate }}</mat-label>
          <mat-select [(ngModel)]="filters.branchId" (selectionChange)="onChange()">
            <mat-option *ngFor="let b of branches" [value]="b.id">{{ b.name }}</mat-option>
          </mat-select>
        </mat-form-field>
      </div>
    </div>
  `,
  styles: [`
    .filter-panel { padding: 16px; }
    .filter-row { display: flex; gap: 16px; flex-wrap: wrap; }
    mat-form-field { min-width: 200px; }
  `]
})
export class ReportFilterPanelComponent {
  @Input() config: FilterPanelConfig = {
    showDateRange: true,
    showTemplate: true,
    showBranch: true,
    showDepartment: false,
    showOperator: false,
    showStatus: false,
    showCustomerQuery: false,
  };
  @Input() templates: any[] = [];
  @Input() branches: any[] = [];
  @Input() departments: any[] = [];
  @Input() operators: any[] = [];
  @Input() filters: any = {};
  @Output() filtersChange = new EventEmitter<any>();

  onChange() {
    this.filtersChange.emit(this.filters);
  }
}

import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, FormArray, FormControl } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSelectModule } from '@angular/material/select';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'fc-table-config-panel',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatSlideToggleModule,
    MatSelectModule,
    TranslateModule,
  ],
  template: `
    <div class="table-config" [formGroup]="form">
      <h4>{{ 'table.title' | translate }}</h4>

      <mat-slide-toggle formControlName="show_header">
        {{ 'table.showHeader' | translate }}
      </mat-slide-toggle>
      <mat-slide-toggle formControlName="show_borders">
        {{ 'table.showBorders' | translate }}
      </mat-slide-toggle>
      <mat-slide-toggle formControlName="show_footer">
        {{ 'table.showFooter' | translate }}
      </mat-slide-toggle>

      <div class="prop-row">
        <mat-form-field appearance="outline">
          <mat-label>{{ 'table.minRows' | translate }}</mat-label>
          <input matInput type="number" formControlName="min_rows" min="0" />
        </mat-form-field>
        <mat-form-field appearance="outline">
          <mat-label>{{ 'table.maxRows' | translate }}</mat-label>
          <input matInput type="number" formControlName="max_rows" min="1" />
        </mat-form-field>
      </div>

      <h4>Columns</h4>
      <div formArrayName="columns">
        <div *ngFor="let col of columnsArray.controls; let i = index" [formGroupName]="i" class="column-row">
          <mat-form-field appearance="outline" class="col-key">
            <mat-label>{{ 'table.columnKey' | translate }}</mat-label>
            <input matInput formControlName="key" />
          </mat-form-field>
          <mat-form-field appearance="outline" class="col-header">
            <mat-label>{{ 'table.headerAr' | translate }}</mat-label>
            <input matInput formControlName="header_ar" />
          </mat-form-field>
          <mat-form-field appearance="outline" class="col-header">
            <mat-label>{{ 'table.headerEn' | translate }}</mat-label>
            <input matInput formControlName="header_en" />
          </mat-form-field>
          <mat-form-field appearance="outline" class="col-type">
            <mat-label>{{ 'table.columnType' | translate }}</mat-label>
            <mat-select formControlName="type">
              <mat-option value="text">Text</mat-option>
              <mat-option value="number">Number</mat-option>
              <mat-option value="date">Date</mat-option>
            </mat-select>
          </mat-form-field>
          <mat-form-field appearance="outline" class="col-width">
            <mat-label>{{ 'table.columnWidth' | translate }}</mat-label>
            <input matInput type="number" formControlName="width_mm" />
          </mat-form-field>
          <mat-slide-toggle formControlName="auto_sum" class="col-sum">
            {{ 'table.autoSum' | translate }}
          </mat-slide-toggle>
          <button mat-icon-button color="warn" (click)="removeColumn(i)">
            <mat-icon>delete</mat-icon>
          </button>
        </div>
      </div>

      <button mat-stroked-button (click)="addColumn()">
        <mat-icon>add</mat-icon>
        {{ 'table.addColumn' | translate }}
      </button>
    </div>
  `,
  styles: [`
    .table-config { display: flex; flex-direction: column; gap: 8px; }
    .prop-row { display: flex; gap: 8px; }
    .prop-row mat-form-field { flex: 1; }
    .column-row {
      display: flex; flex-wrap: wrap; gap: 4px; align-items: center;
      padding: 8px 0; border-bottom: 1px solid #eee;
    }
    .col-key { flex: 1; min-width: 60px; }
    .col-header { flex: 1; min-width: 80px; }
    .col-type { flex: 0.8; min-width: 80px; }
    .col-width { flex: 0.5; min-width: 60px; }
    .col-sum { flex: 0 0 auto; }
    h4 { margin: 8px 0 4px; }
  `],
})
export class TableConfigPanelComponent {
  @Input() set element(el: any) {
    if (!el) return;
    const data = el.data || el;
    const props = data.properties || data.formatting || {};
    const cols = props.columns || [];

    this.form.patchValue({
      show_header: props.show_header ?? true,
      show_borders: props.show_borders ?? true,
      show_footer: props.show_footer ?? true,
      min_rows: props.min_rows ?? 1,
      max_rows: props.max_rows ?? 20,
    });

    while (this.columnsArray.length > 0) this.columnsArray.removeAt(0);
    cols.forEach((c: any) => this.addColumn(c));
  }
  @Output() propertyChange = new EventEmitter<any>();

  form: FormGroup;

  constructor(private fb: FormBuilder) {
    this.form = this.fb.group({
      show_header: [true],
      show_borders: [true],
      show_footer: [true],
      min_rows: [1],
      max_rows: [20],
      columns: this.fb.array([]),
    });

    this.form.valueChanges.subscribe(() => this.emitChange());
  }

  get columnsArray(): FormArray {
    return this.form.get('columns') as FormArray;
  }

  addColumn(col?: any): void {
    this.columnsArray.push(this.fb.group({
      key: [col?.key || ''],
      header_ar: [col?.header_ar || ''],
      header_en: [col?.header_en || ''],
      type: [col?.type || 'text'],
      width_mm: [col?.width_mm || 40],
      auto_sum: [col?.auto_sum || false],
    }));
  }

  removeColumn(index: number): void {
    this.columnsArray.removeAt(index);
  }

  private emitChange(): void {
    const val = this.form.value;
    this.propertyChange.emit({
      show_header: val.show_header,
      show_borders: val.show_borders,
      show_footer: val.show_footer,
      min_rows: val.min_rows,
      max_rows: val.max_rows,
      columns: val.columns,
    });
  }
}
import { Component, Input, Output, EventEmitter, OnChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormArray, FormControl, ReactiveFormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { TranslateModule } from '@ngx-translate/core';
import { TemplateElement } from '../../services/form-filler.service';

interface ColumnDef {
  key: string;
  header_ar: string;
  header_en: string;
  type: string;
  width_mm: number;
  auto_sum: boolean;
}

@Component({
  selector: 'fc-table-input',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatInputModule,
    MatFormFieldModule,
    TranslateModule,
  ],
  template: `
    <div class="table-input-container" [dir]="element?.direction || 'rtl'">
      <label class="table-label" *ngIf="label">{{ label }}</label>
      <table mat-table [dataSource]="rows" class="data-table">
        <ng-container *ngFor="let col of columns" [matColumnDef]="col.key">
          <th mat-header-cell *matHeaderCellDef>{{ getHeader(col) }}</th>
          <td mat-cell *matCellDef="let row; let rowIndex = index">
            <input matInput
              [type]="getInputType(col.type)"
              [formControl]="getControl(rowIndex, col.key)"
              class="cell-input"
              [placeholder]="getHeader(col)" />
          </td>
          <td mat-footer-cell *matFooterCellDef *ngIf="showFooter">
            <span *ngIf="col.auto_sum" class="sum-value">{{ getSum(col.key) | number:'1.2-2' }}</span>
          </td>
        </ng-container>

        <ng-container matColumnDef="actions">
          <th mat-header-cell *matHeaderCellDef></th>
          <td mat-cell *matCellDef="let row; let rowIndex = index">
            <button mat-icon-button *ngIf="canRemoveRow" (click)="removeRow(rowIndex)" matTooltip="{{ 'table.removeRow' | translate }}">
              <mat-icon>remove_circle_outline</mat-icon>
            </button>
          </td>
          <td mat-footer-cell *matFooterCellDef *ngIf="showFooter"></td>
        </ng-container>

        <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
        <tr mat-row *matMatRowDef="let row; columns: displayedColumns;"></tr>
        <tr mat-footer-row *matFooterRowDef="displayedColumns" *ngIf="showFooter"></tr>
      </table>

      <div class="table-actions">
        <button mat-stroked-button (click)="addRow()" [disabled]="!canAddRow">
          <mat-icon>add</mat-icon>
          {{ 'table.addRow' | translate }}
        </button>
      </div>
    </div>
  `,
  styles: [`
    .table-input-container {
      width: 100%;
      margin-bottom: 16px;
    }
    .table-label {
      display: block;
      font-size: 14px;
      color: rgba(0,0,0,0.87);
      margin-bottom: 8px;
    }
    .data-table {
      width: 100%;
    }
    .cell-input {
      width: 100%;
      font-size: 13px;
    }
    .sum-value {
      font-weight: bold;
      font-size: 13px;
    }
    .table-actions {
      display: flex;
      justify-content: flex-start;
      margin-top: 8px;
    }
    :host-context([dir='rtl']) .table-label {
      text-align: right;
    }
  `],
})
export class TableInputComponent implements OnChanges {
  @Input() element: TemplateElement | null = null;
  @Input() label = '';
  @Output() valueChange = new EventEmitter<any[]>();

  columns: ColumnDef[] = [];
  displayedColumns: string[] = [];
  showFooter = true;
  maxRows = 20;
  minRows = 1;

  rows: any[] = [];
  formArray = new FormArray<FormGroup>([]);

  get canAddRow(): boolean {
    return this.rows.length < this.maxRows;
  }
  get canRemoveRow(): boolean {
    return this.rows.length > this.minRows;
  }

  ngOnChanges(): void {
    if (!this.element) return;
    const props = (this.element as any).properties || (this.element as any).formatting || {};
    this.columns = props.columns || [];
    this.displayedColumns = [...this.columns.map(c => c.key), 'actions'];
    this.showFooter = props.show_footer !== false;
    this.minRows = props.min_rows ?? 1;
    this.maxRows = props.max_rows ?? 20;
  }

  getHeader(col: ColumnDef): string {
    const dir = (this.element as any)?.direction || 'rtl';
    return dir === 'ltr' ? (col.header_en || col.key) : (col.header_ar || col.key);
  }

  getInputType(colType: string): string {
    switch (colType) {
      case 'number': return 'number';
      case 'date': return 'date';
      default: return 'text';
    }
  }

  getSum(colKey: string): number {
    let sum = 0;
    for (const row of this.rows) {
      const val = parseFloat(row[colKey]);
      if (!isNaN(val)) sum += val;
    }
    return sum;
  }

  getControl(rowIndex: number, colKey: string): FormControl {
    while (this.formArray.length <= rowIndex) {
      this.addRow();
    }
    const group = this.formArray.at(rowIndex) as FormGroup;
    if (!group.contains(colKey)) {
      group.addControl(colKey, new FormControl(''));
    }
    return group.get(colKey) as FormControl;
  }

  addRow(): void {
    if (!this.canAddRow) return;
    const row: any = {};
    this.columns.forEach(c => { row[c.key] = ''; });
    this.rows.push(row);
    const group = this.fb.group(
      Object.fromEntries(this.columns.map(c => [c.key, '']))
    );
    this.formArray.push(group);
    group.valueChanges.subscribe(() => this.emitValue());
    this.emitValue();
  }

  removeRow(index: number): void {
    if (!this.canRemoveRow) return;
    this.rows.splice(index, 1);
    this.formArray.removeAt(index);
    this.emitValue();
  }

  private emitValue(): void {
    this.valueChange.emit([...this.rows]);
  }

  constructor(private fb: FormBuilder) {}
}
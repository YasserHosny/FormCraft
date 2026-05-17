import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, FormArray } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { TranslateModule } from '@ngx-translate/core';

export interface ConditionItem {
  field: string;
  operator: string;
  value: string | number | boolean | null;
}

export interface ConditionObject {
  conditions: ConditionItem[];
  logic: 'AND';
}

@Component({
  selector: 'fc-condition-builder',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatSelectModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    TranslateModule,
  ],
  template: `
    <div class="condition-builder">
      <label class="cb-title">{{ title | translate }}</label>
      <div class="cb-hint" *ngIf="conditions.length === 0">
        {{ 'conditions.no_conditions' | translate }}
      </div>

      <div *ngFor="let cond of conditions.controls; let i = index" [formGroup]="getGroup(i)" class="cb-row">
        <mat-form-field appearance="outline" class="cb-field">
          <mat-select formControlName="field" [placeholder]="'conditions.field' | translate">
            <mat-option *ngFor="let f of availableFields" [value]="f.key">{{ f.label }}</mat-option>
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline" class="cb-operator">
          <mat-select formControlName="operator" [placeholder]="'conditions.operator' | translate">
            <mat-option *ngFor="let op of operators" [value]="op.value">
              {{ 'conditions.operators.' + op.value | translate }}
            </mat-option>
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline" class="cb-value"
          *ngIf="!isUnaryOperator(getGroup(i).get('operator')?.value)">
          <input matInput formControlName="value" [placeholder]="'conditions.value' | translate" />
        </mat-form-field>

        <button mat-icon-button color="warn" (click)="removeCondition(i)" class="cb-remove">
          <mat-icon>close</mat-icon>
        </button>
      </div>

      <button mat-stroked-button (click)="addCondition()" class="cb-add">
        <mat-icon>add</mat-icon>
        {{ 'conditions.add_condition' | translate }}
      </button>
    </div>
  `,
  styles: [`
    .condition-builder { display: flex; flex-direction: column; gap: 8px; }
    .cb-title { font-size: 13px; font-weight: 500; color: rgba(0,0,0,0.7); }
    .cb-hint { font-size: 12px; color: #999; font-style: italic; }
    .cb-row { display: flex; gap: 8px; align-items: flex-start; }
    .cb-field { flex: 2; }
    .cb-operator { flex: 2; }
    .cb-value { flex: 2; }
    .cb-remove { margin-top: 8px; }
    .cb-add { align-self: flex-start; }
    mat-form-field { font-size: 13px; }
  `],
})
export class ConditionBuilderComponent implements OnInit {
  @Input() title = 'conditions.visible_when';
  @Input() availableFields: { key: string; label: string }[] = [];
  @Input() value: ConditionObject | null = null;
  @Output() valueChange = new EventEmitter<ConditionObject | null>();

  form!: FormGroup;

  operators = [
    { value: 'equals' },
    { value: 'not_equals' },
    { value: 'contains' },
    { value: 'greater_than' },
    { value: 'less_than' },
    { value: 'is_empty' },
    { value: 'is_not_empty' },
  ];

  constructor(private fb: FormBuilder) {}

  ngOnInit(): void {
    this.form = this.fb.group({
      conditions: this.fb.array([]),
    });

    if (this.value?.conditions) {
      for (const c of this.value.conditions) {
        this.conditions.push(this.createConditionGroup(c));
      }
    }

    this.form.valueChanges.subscribe(() => this.emitValue());
  }

  get conditions(): FormArray {
    return this.form.get('conditions') as FormArray;
  }

  getGroup(index: number): FormGroup {
    return this.conditions.at(index) as FormGroup;
  }

  addCondition(): void {
    this.conditions.push(this.createConditionGroup({ field: '', operator: 'equals', value: '' }));
  }

  removeCondition(index: number): void {
    this.conditions.removeAt(index);
  }

  isUnaryOperator(op: string | null | undefined): boolean {
    return op === 'is_empty' || op === 'is_not_empty';
  }

  private createConditionGroup(item: ConditionItem): FormGroup {
    return this.fb.group({
      field: [item.field],
      operator: [item.operator],
      value: [item.value ?? ''],
    });
  }

  private emitValue(): void {
    const conditions = this.conditions.value as ConditionItem[];
    const valid = conditions.filter((c) => c.field && c.operator);
    if (valid.length === 0) {
      this.valueChange.emit(null);
    } else {
      this.valueChange.emit({ conditions: valid, logic: 'AND' });
    }
  }
}

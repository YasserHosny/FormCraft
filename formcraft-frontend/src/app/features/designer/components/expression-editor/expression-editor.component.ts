import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormControl } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule } from '@ngx-translate/core';
import { debounceTime } from 'rxjs/operators';

@Component({
  selector: 'fc-expression-editor',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatAutocompleteModule,
    MatIconModule,
    TranslateModule,
  ],
  template: `
    <div class="expression-editor">
      <label class="ee-title">{{ 'computed.title' | translate }}</label>

      <mat-form-field appearance="outline" class="ee-input">
        <mat-label>{{ 'computed.expression' | translate }}</mat-label>
        <input matInput [formControl]="expressionControl"
          [placeholder]="'computed.expression_placeholder' | translate" />
        <mat-icon matSuffix *ngIf="isValid">check_circle</mat-icon>
        <mat-icon matSuffix *ngIf="!isValid && expressionControl.value" color="warn">error</mat-icon>
        <mat-error *ngIf="!isValid && expressionControl.value">
          {{ errorMessage | translate }}
        </mat-error>
      </mat-form-field>

      <div class="ee-fields" *ngIf="availableFields.length > 0">
        <span class="ee-fields-label">{{ 'conditions.field' | translate }}:</span>
        <span *ngFor="let f of availableFields" class="ee-field-chip" (click)="insertField(f.key)">
          {{ f.key }}
        </span>
      </div>

      <div class="ee-preview" *ngIf="isValid && previewResult !== null">
        {{ 'computed.preview' | translate }}: <strong>{{ previewResult }}</strong>
      </div>
    </div>
  `,
  styles: [`
    .expression-editor { display: flex; flex-direction: column; gap: 8px; }
    .ee-title { font-size: 13px; font-weight: 500; color: rgba(0,0,0,0.7); }
    .ee-input { width: 100%; }
    .ee-fields { display: flex; flex-wrap: wrap; gap: 4px; align-items: center; }
    .ee-fields-label { font-size: 11px; color: #666; }
    .ee-field-chip {
      font-size: 11px;
      background: #e3f2fd;
      color: #1565c0;
      padding: 2px 8px;
      border-radius: 12px;
      cursor: pointer;
      user-select: none;
    }
    .ee-field-chip:hover { background: #bbdefb; }
    .ee-preview { font-size: 12px; color: #4caf50; }
  `],
})
export class ExpressionEditorComponent implements OnInit {
  @Input() availableFields: { key: string; label: string }[] = [];
  @Input() value: string | null = null;
  @Output() valueChange = new EventEmitter<string | null>();

  expressionControl = new FormControl('');
  isValid = true;
  errorMessage = '';
  previewResult: number | null = null;

  ngOnInit(): void {
    if (this.value) {
      this.expressionControl.setValue(this.value, { emitEvent: false });
    }

    this.expressionControl.valueChanges
      .pipe(debounceTime(300))
      .subscribe((val) => {
        this.validate(val || '');
        this.valueChange.emit(val || null);
      });

    if (this.value) this.validate(this.value);
  }

  insertField(key: string): void {
    const current = this.expressionControl.value || '';
    const newVal = current ? `${current} ${key}` : key;
    this.expressionControl.setValue(newVal);
  }

  private validate(expr: string): void {
    if (!expr) {
      this.isValid = true;
      this.previewResult = null;
      return;
    }

    try {
      const refs = this.getReferences(expr);
      const knownKeys = new Set(this.availableFields.map((f) => f.key));
      for (const ref of refs) {
        if (!knownKeys.has(ref)) {
          this.isValid = false;
          this.errorMessage = 'computed.field_not_found';
          this.previewResult = null;
          return;
        }
      }

      const sampleValues: Record<string, number> = {};
      for (const f of this.availableFields) {
        sampleValues[f.key] = 1;
      }
      this.previewResult = this.evalExpression(expr, sampleValues);
      this.isValid = true;
      this.errorMessage = '';
    } catch {
      this.isValid = false;
      this.errorMessage = 'computed.invalid_expression';
      this.previewResult = null;
    }
  }

  private getReferences(expr: string): string[] {
    const refs: string[] = [];
    const regex = /[a-zA-Z_][a-zA-Z0-9_]*/g;
    let match: RegExpExecArray | null;
    while ((match = regex.exec(expr)) !== null) {
      if (!refs.includes(match[0])) refs.push(match[0]);
    }
    return refs;
  }

  private evalExpression(expr: string, values: Record<string, number>): number {
    const sanitized = expr.replace(/[a-zA-Z_][a-zA-Z0-9_]*/g, (m) => {
      return String(values[m] ?? 0);
    });
    if (!/^[\d\s+\-*/.()]+$/.test(sanitized)) {
      throw new Error('Invalid expression');
    }
    const result = Function(`"use strict"; return (${sanitized});`)();
    return typeof result === 'number' && isFinite(result) ? result : 0;
  }
}

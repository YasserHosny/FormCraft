import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef } from '@angular/material/dialog';
import { TemplateService } from '../../../core/services/template.service';

@Component({
  selector: 'fc-template-create-dialog',
  standalone: false,
  template: `
    <h2 mat-dialog-title>{{ 'templates.create' | translate }}</h2>
    <mat-dialog-content>
      <form [formGroup]="form">
        <mat-form-field appearance="outline" class="full-width">
          <mat-label>{{ 'templates.name' | translate }}</mat-label>
          <input matInput formControlName="name" fcAutoDir />
        </mat-form-field>

        <mat-form-field appearance="outline" class="full-width">
          <mat-label>{{ 'templates.description' | translate }}</mat-label>
          <textarea matInput formControlName="description" rows="3" fcAutoDir></textarea>
        </mat-form-field>

        <mat-form-field appearance="outline" class="full-width">
          <mat-label>{{ 'templates.category' | translate }}</mat-label>
          <mat-select formControlName="category">
            <mat-option value="general">General</mat-option>
            <mat-option value="government">Government</mat-option>
            <mat-option value="finance">Finance</mat-option>
            <mat-option value="healthcare">Healthcare</mat-option>
            <mat-option value="education">Education</mat-option>
          </mat-select>
        </mat-form-field>

        <div class="row">
          <mat-form-field appearance="outline">
            <mat-label>{{ 'templates.language' | translate }}</mat-label>
            <mat-select formControlName="language">
              <mat-option value="ar">العربية</mat-option>
              <mat-option value="en">English</mat-option>
            </mat-select>
          </mat-form-field>

          <mat-form-field appearance="outline">
            <mat-label>{{ 'templates.country' | translate }}</mat-label>
            <mat-select formControlName="country">
              <mat-option value="EG">{{ 'countries.EG' | translate }}</mat-option>
              <mat-option value="SA">{{ 'countries.SA' | translate }}</mat-option>
              <mat-option value="AE">{{ 'countries.AE' | translate }}</mat-option>
            </mat-select>
          </mat-form-field>
        </div>

        <div *ngIf="errorMessage" class="error-message">{{ errorMessage }}</div>
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>{{ 'common.cancel' | translate }}</button>
      <button
        mat-raised-button
        color="primary"
        [disabled]="form.invalid || saving"
        (click)="onCreate()"
      >
        <mat-spinner *ngIf="saving" diameter="18"></mat-spinner>
        <span *ngIf="!saving">{{ 'common.save' | translate }}</span>
      </button>
    </mat-dialog-actions>
  `,
  styles: [`
    .full-width { width: 100%; }
    mat-form-field { margin-bottom: 8px; }
    .row {
      display: flex;
      gap: 16px;
    }
    .row mat-form-field { flex: 1; }
    .error-message {
      color: #f44336;
      margin-bottom: 12px;
      font-size: 14px;
    }
  `],
})
export class TemplateCreateDialogComponent {
  form: FormGroup;
  saving = false;
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<TemplateCreateDialogComponent>,
    private templateService: TemplateService
  ) {
    this.form = this.fb.group({
      name: ['', [Validators.required, Validators.maxLength(200)]],
      description: [''],
      category: ['general', Validators.required],
      language: ['ar', Validators.required],
      country: ['EG', Validators.required],
    });
  }

  onCreate(): void {
    if (this.form.invalid) return;
    this.saving = true;
    this.errorMessage = '';

    this.templateService.create(this.form.value).subscribe({
      next: (result) => {
        this.saving = false;
        this.dialogRef.close(result);
      },
      error: (err) => {
        this.saving = false;
        this.errorMessage = err.error?.detail || 'Failed to create template';
      },
    });
  }
}

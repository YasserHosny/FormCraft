import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { TemplateService } from '../../../core/services/template.service';

@Component({
  selector: 'fc-redesign-clone-dialog',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, MatDialogModule, MatFormFieldModule, MatInputModule, MatButtonModule],
  template: `
    <h2 mat-dialog-title>استنساخ النموذج</h2>
    <mat-dialog-content>
      <p>أدخل اسماً للنموذج المستنسخ:</p>
      <mat-form-field appearance="outline" class="full-width">
        <mat-label>اسم النموذج</mat-label>
        <input matInput [formControl]="nameControl" />
      </mat-form-field>
      <p *ngIf="errorMessage" class="error">{{ errorMessage }}</p>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button (click)="onCancel()">إلغاء</button>
      <button mat-raised-button color="primary" (click)="onClone()" [disabled]="form.invalid || saving">
        استنساخ
      </button>
    </mat-dialog-actions>
  `,
  styles: [`
    .full-width { width: 100%; }
    .error { color: #C62828; font-size: 13px; }
  `],
})
export class RedesignCloneDialogComponent {
  form: FormGroup;
  saving = false;
  errorMessage = '';

  get nameControl(): FormControl {
    return this.form.get('name') as FormControl;
  }

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<RedesignCloneDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { templateId: string; templateName: string },
    private templateService: TemplateService,
  ) {
    this.form = this.fb.group({
      name: [`${data.templateName} (نسخة)`, [Validators.required, Validators.maxLength(200)]],
    });
  }

  onClone(): void {
    if (this.form.invalid) return;
    this.saving = true;
    this.errorMessage = '';
    this.templateService.clone(this.data.templateId, this.form.value.name).subscribe({
      next: (result: any) => {
        this.saving = false;
        this.dialogRef.close(result);
      },
      error: (err: any) => {
        this.saving = false;
        this.errorMessage = err.error?.detail || 'فشل استنساخ النموذج';
      },
    });
  }

  onCancel(): void {
    this.dialogRef.close(null);
  }
}

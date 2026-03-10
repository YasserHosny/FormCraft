import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef } from '@angular/material/dialog';
import { TemplateService } from '../../../core/services/template.service';

@Component({
  selector: 'fc-template-create-dialog',
  standalone: false,
  templateUrl: './template-create-dialog.component.html',
  styleUrls: ['./template-create-dialog.component.scss'],
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

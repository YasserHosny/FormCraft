import { Component, Inject } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { TemplateService } from '../../../core/services/template.service';

@Component({
  selector: 'fc-clone-dialog',
  standalone: false,
  templateUrl: './clone-dialog.component.html',
  styleUrls: ['./clone-dialog.component.scss'],
})
export class CloneDialogComponent {
  form: FormGroup;
  saving = false;
  errorMessage = '';

  get nameControl(): FormControl {
    return this.form.get('name') as FormControl;
  }

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<CloneDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { templateId: string; templateName: string },
    private templateService: TemplateService,
  ) {
    this.form = this.fb.group({
      name: [`${data.templateName} (Copy)`, [Validators.required, Validators.maxLength(200)]],
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
        this.errorMessage = err.error?.detail || 'Failed to clone template';
      },
    });
  }

  onCancel(): void {
    this.dialogRef.close(null);
  }
}
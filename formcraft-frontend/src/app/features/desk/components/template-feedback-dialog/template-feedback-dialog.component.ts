import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { CommonModule } from '@angular/common';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { TemplateFeedbackService } from '../../services/template-feedback.service';

export interface FeedbackDialogData {
  templateId: string;
  templateName?: string;
  templateVersion?: number;
  pageNumber?: number | null;
  elementKey?: string | null;
}

@Component({
  selector: 'fc-template-feedback-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    MatSnackBarModule,
    TranslateModule,
  ],
  template: `
    <h2 mat-dialog-title>{{ 'template_feedback.dialog.title' | translate }}</h2>
    <form [formGroup]="form" (ngSubmit)="onSubmit()">
      <mat-dialog-content>
        <div class="feedback-context" *ngIf="data.templateName || data.templateVersion">
          <div *ngIf="data.templateName">
            <strong>{{ 'history.col_template' | translate }}:</strong>
            <span>{{ data.templateName }}</span>
          </div>
          <div *ngIf="data.templateVersion">
            <strong>{{ 'desk.version' | translate:{ version: data.templateVersion } }}:</strong>
            <span>{{ data.templateVersion }}</span>
          </div>
        </div>

        <mat-form-field appearance="outline" class="full-width">
          <mat-label>{{ 'template_feedback.dialog.category' | translate }}</mat-label>
          <mat-select formControlName="category">
            <mat-option value="layout">{{ 'template_feedback.dialog.categoryLayout' | translate }}</mat-option>
            <mat-option value="readability">{{ 'template_feedback.dialog.categoryReadability' | translate }}</mat-option>
            <mat-option value="logical">{{ 'template_feedback.dialog.categoryLogical' | translate }}</mat-option>
            <mat-option value="other">{{ 'template_feedback.dialog.categoryOther' | translate }}</mat-option>
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline" class="full-width">
          <mat-label>{{ 'template_feedback.dialog.comment' | translate }}</mat-label>
          <textarea matInput formControlName="comment" rows="4"
            [placeholder]="'template_feedback.dialog.comment' | translate"></textarea>
          <mat-error *ngIf="form.get('comment')?.hasError('required')">
            {{ 'template_feedback.dialog.commentRequired' | translate }}
          </mat-error>
        </mat-form-field>
      </mat-dialog-content>

      <mat-dialog-actions align="end">
        <button mat-button type="button" mat-dialog-close>{{ 'common.cancel' | translate }}</button>
        <button mat-raised-button color="primary" type="submit" [disabled]="form.invalid || submitting">
          <mat-icon>send</mat-icon>
          {{ 'template_feedback.dialog.submit' | translate }}
        </button>
      </mat-dialog-actions>
    </form>
  `,
  styles: [`
    .full-width { width: 100%; }
    mat-dialog-content { display: flex; flex-direction: column; gap: 16px; }
    .feedback-context {
      display: grid;
      gap: 4px;
      padding: 12px;
      border-radius: 4px;
      background: rgba(63, 81, 181, 0.08);
    }
    .feedback-context div {
      display: flex;
      gap: 8px;
      align-items: center;
    }
  `],
})
export class TemplateFeedbackDialogComponent {
  form: FormGroup;
  submitting = false;

  constructor(
    private dialogRef: MatDialogRef<TemplateFeedbackDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: FeedbackDialogData,
    private feedbackService: TemplateFeedbackService,
    private snackBar: MatSnackBar,
    private translate: TranslateService,
  ) {
    this.form = new FormGroup({
      category: new FormControl('layout', Validators.required),
      comment: new FormControl('', Validators.required),
    });
  }

  onSubmit(): void {
    if (this.form.invalid || this.submitting) return;
    this.submitting = true;

    const value = this.form.value;
    this.feedbackService.submitFeedback(this.data.templateId, {
      category: value.category,
      comment: value.comment,
      page_number: this.data.pageNumber ?? null,
      element_key: this.data.elementKey ?? null,
    }).subscribe({
      next: () => {
        this.snackBar.open(this.translate.instant('template_feedback.dialog.success'), '', { duration: 3000 });
        this.dialogRef.close(true);
      },
      error: () => {
        this.submitting = false;
      },
    });
  }
}

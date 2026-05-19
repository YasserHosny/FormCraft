import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSliderModule } from '@angular/material/slider';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { TranslateModule } from '@ngx-translate/core';
import {
  PrinterProfile,
  PrinterProfileService,
} from '../../../core/services/printer-profile.service';

@Component({
  selector: 'app-printer-profile-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSliderModule,
    MatCheckboxModule,
    TranslateModule,
  ],
  template: `
    <h2 mat-dialog-title>
      {{ (isEdit ? 'printer_profiles.edit' : 'printer_profiles.add') | translate }}
    </h2>
    <mat-dialog-content>
      <mat-form-field appearance="outline" class="full-width">
        <mat-label>{{ 'printer_profiles.name' | translate }}</mat-label>
        <input matInput [(ngModel)]="form.name" required />
      </mat-form-field>

      <mat-form-field appearance="outline" class="full-width">
        <mat-label>{{ 'printer_profiles.description' | translate }}</mat-label>
        <textarea matInput [(ngModel)]="form.description" rows="2"></textarea>
      </mat-form-field>

      <div class="offset-row">
        <mat-form-field appearance="outline">
          <mat-label>X Offset (mm)</mat-label>
          <input matInput type="number" [(ngModel)]="form.x_offset_mm" min="-50" max="50" step="0.5" />
        </mat-form-field>
        <mat-form-field appearance="outline">
          <mat-label>Y Offset (mm)</mat-label>
          <input matInput type="number" [(ngModel)]="form.y_offset_mm" min="-50" max="50" step="0.5" />
        </mat-form-field>
      </div>

      <mat-checkbox [(ngModel)]="form.is_default" *ngIf="!isEdit">
        {{ 'printer_profiles.set_default' | translate }}
      </mat-checkbox>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>{{ 'common.cancel' | translate }}</button>
      <button mat-raised-button color="primary" (click)="save()" [disabled]="!form.name">
        {{ 'common.save' | translate }}
      </button>
    </mat-dialog-actions>
  `,
  styles: [`
    .full-width { width: 100%; }
    .offset-row { display: flex; gap: 16px; }
    .offset-row mat-form-field { flex: 1; }
  `],
})
export class PrinterProfileDialogComponent {
  isEdit: boolean;
  form = {
    name: '',
    description: '',
    x_offset_mm: 0,
    y_offset_mm: 0,
    is_default: false,
  };

  constructor(
    private dialogRef: MatDialogRef<PrinterProfileDialogComponent>,
    private service: PrinterProfileService,
    @Inject(MAT_DIALOG_DATA) private data: PrinterProfile | null
  ) {
    this.isEdit = !!data;
    if (data) {
      this.form.name = data.name;
      this.form.description = data.description || '';
      this.form.x_offset_mm = data.x_offset_mm;
      this.form.y_offset_mm = data.y_offset_mm;
    }
  }

  save(): void {
    if (this.isEdit && this.data) {
      this.service
        .update(this.data.id, {
          name: this.form.name,
          description: this.form.description || undefined,
          x_offset_mm: this.form.x_offset_mm,
          y_offset_mm: this.form.y_offset_mm,
        })
        .subscribe(() => this.dialogRef.close(true));
    } else {
      this.service.create(this.form).subscribe(() => this.dialogRef.close(true));
    }
  }
}

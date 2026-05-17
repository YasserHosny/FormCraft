import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatButtonModule } from '@angular/material/button';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { ReferenceDataService, ColumnSchema, ReferenceEntry } from '../../../core/services/reference-data.service';

interface EntryDialogData {
  schema: ColumnSchema[];
  listId: string;
  entry?: ReferenceEntry;
}

@Component({
  selector: 'fc-reference-entry-form-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatButtonModule,
    MatSnackBarModule,
    TranslateModule,
  ],
  template: `
    <h2 mat-dialog-title>
      {{ (isEdit ? 'REFERENCE_DATA.EDIT_ENTRY' : 'REFERENCE_DATA.ADD_ENTRY') | translate }}
    </h2>
    <mat-dialog-content>
      <form #entryForm="ngForm">
        <div *ngFor="let col of data.schema" class="field-row">
          <!-- Text field -->
          <mat-form-field *ngIf="col.type === 'text'" appearance="outline" class="full-width">
            <mat-label>{{ col.label_en }}</mat-label>
            <input matInput [(ngModel)]="values[col.key]" [name]="col.key" [required]="col.required" />
          </mat-form-field>

          <!-- Number field -->
          <mat-form-field *ngIf="col.type === 'number'" appearance="outline" class="full-width">
            <mat-label>{{ col.label_en }}</mat-label>
            <input matInput type="number" [(ngModel)]="values[col.key]" [name]="col.key" [required]="col.required" />
          </mat-form-field>

          <!-- Date field -->
          <mat-form-field *ngIf="col.type === 'date'" appearance="outline" class="full-width">
            <mat-label>{{ col.label_en }}</mat-label>
            <input matInput [matDatepicker]="picker" [(ngModel)]="values[col.key]" [name]="col.key" [required]="col.required" />
            <mat-datepicker-toggle matIconSuffix [for]="picker"></mat-datepicker-toggle>
            <mat-datepicker #picker></mat-datepicker>
          </mat-form-field>

          <!-- Dropdown field -->
          <mat-form-field *ngIf="col.type === 'dropdown'" appearance="outline" class="full-width">
            <mat-label>{{ col.label_en }}</mat-label>
            <mat-select [(ngModel)]="values[col.key]" [name]="col.key" [required]="col.required">
              <mat-option *ngFor="let opt of col.options" [value]="opt">{{ opt }}</mat-option>
            </mat-select>
          </mat-form-field>
        </div>
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>{{ 'COMMON.CANCEL' | translate }}</button>
      <button mat-raised-button color="primary" [disabled]="saving || !entryForm.valid" (click)="save()">
        <span *ngIf="!saving">{{ (isEdit ? 'COMMON.UPDATE' : 'COMMON.CREATE') | translate }}</span>
        <span *ngIf="saving">{{ 'COMMON.SAVING' | translate }}</span>
      </button>
    </mat-dialog-actions>
  `,
  styles: [`
    .full-width { width: 100%; }
    .field-row { margin-bottom: 4px; }
  `],
})
export class ReferenceEntryFormDialogComponent {
  isEdit: boolean;
  saving = false;
  values: Record<string, any> = {};

  constructor(
    private dialogRef: MatDialogRef<ReferenceEntryFormDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: EntryDialogData,
    private refDataService: ReferenceDataService,
    private snackBar: MatSnackBar,
    private translate: TranslateService,
  ) {
    this.isEdit = !!data.entry;
    if (data.entry) {
      this.values = { ...data.entry.values };
    } else {
      data.schema.forEach((col) => {
        this.values[col.key] = col.type === 'number' ? null : '';
      });
    }
  }

  save(): void {
    this.saving = true;
    const request$ = this.isEdit
      ? this.refDataService.updateEntry(this.data.listId, this.data.entry!.id, this.values)
      : this.refDataService.createEntry(this.data.listId, this.values);

    request$.subscribe({
      next: () => {
        this.saving = false;
        this.dialogRef.close(true);
      },
      error: () => {
        this.saving = false;
        this.snackBar.open(this.translate.instant('REFERENCE_DATA.SAVE_ERROR'), '', { duration: 3000 });
      },
    });
  }
}

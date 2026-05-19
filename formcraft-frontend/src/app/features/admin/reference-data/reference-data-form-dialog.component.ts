import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { ReferenceDataService, ReferenceList, ColumnSchema } from '../../../core/services/reference-data.service';

@Component({
  selector: 'fc-reference-data-form-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatSelectModule,
    MatCheckboxModule,
    MatSnackBarModule,
    TranslateModule,
  ],
  template: `
    <h2 mat-dialog-title>
      {{ (isEdit ? 'REFERENCE_DATA.EDIT_LIST' : 'REFERENCE_DATA.CREATE_LIST') | translate }}
    </h2>
    <mat-dialog-content>
      <form #listForm="ngForm">
        <mat-form-field appearance="outline" class="full-width">
          <mat-label>{{ 'REFERENCE_DATA.NAME_AR' | translate }}</mat-label>
          <input matInput [(ngModel)]="model.name_ar" name="name_ar" required />
        </mat-form-field>

        <mat-form-field appearance="outline" class="full-width">
          <mat-label>{{ 'REFERENCE_DATA.NAME_EN' | translate }}</mat-label>
          <input matInput [(ngModel)]="model.name_en" name="name_en" required />
        </mat-form-field>

        <mat-form-field appearance="outline" class="full-width">
          <mat-label>{{ 'REFERENCE_DATA.DESCRIPTION' | translate }}</mat-label>
          <textarea matInput [(ngModel)]="model.description" name="description" rows="3"></textarea>
        </mat-form-field>

        <div class="columns-section">
          <div class="columns-header">
            <h3>{{ 'REFERENCE_DATA.COLUMN_SCHEMA' | translate }}</h3>
            <button mat-stroked-button type="button" (click)="addColumn()">
              <mat-icon>add</mat-icon>
              {{ 'REFERENCE_DATA.ADD_COLUMN' | translate }}
            </button>
          </div>

          <div *ngFor="let col of model.columns; let i = index" class="column-row">
            <div class="column-fields">
              <mat-form-field appearance="outline" class="col-field">
                <mat-label>{{ 'REFERENCE_DATA.COL_KEY' | translate }}</mat-label>
                <input matInput [(ngModel)]="col.key" [name]="'col_key_' + i" required />
              </mat-form-field>

              <mat-form-field appearance="outline" class="col-field">
                <mat-label>{{ 'REFERENCE_DATA.COL_LABEL_AR' | translate }}</mat-label>
                <input matInput [(ngModel)]="col.label_ar" [name]="'col_label_ar_' + i" required />
              </mat-form-field>

              <mat-form-field appearance="outline" class="col-field">
                <mat-label>{{ 'REFERENCE_DATA.COL_LABEL_EN' | translate }}</mat-label>
                <input matInput [(ngModel)]="col.label_en" [name]="'col_label_en_' + i" required />
              </mat-form-field>

              <mat-form-field appearance="outline" class="col-field">
                <mat-label>{{ 'REFERENCE_DATA.COL_TYPE' | translate }}</mat-label>
                <mat-select [(ngModel)]="col.type" [name]="'col_type_' + i" required>
                  <mat-option value="text">{{ 'REFERENCE_DATA.TYPE_TEXT' | translate }}</mat-option>
                  <mat-option value="number">{{ 'REFERENCE_DATA.TYPE_NUMBER' | translate }}</mat-option>
                  <mat-option value="date">{{ 'REFERENCE_DATA.TYPE_DATE' | translate }}</mat-option>
                  <mat-option value="dropdown">{{ 'REFERENCE_DATA.TYPE_DROPDOWN' | translate }}</mat-option>
                </mat-select>
              </mat-form-field>
            </div>

            <div class="column-options">
              <mat-checkbox [(ngModel)]="col.required" [name]="'col_req_' + i">
                {{ 'REFERENCE_DATA.REQUIRED' | translate }}
              </mat-checkbox>
              <mat-checkbox [(ngModel)]="col.unique_key" [name]="'col_unique_' + i">
                {{ 'REFERENCE_DATA.UNIQUE_KEY' | translate }}
              </mat-checkbox>
              <button mat-icon-button color="warn" type="button" (click)="removeColumn(i)"
                      [disabled]="model.columns.length <= 1">
                <mat-icon>delete</mat-icon>
              </button>
            </div>

            <mat-form-field *ngIf="col.type === 'dropdown'" appearance="outline" class="full-width">
              <mat-label>{{ 'REFERENCE_DATA.DROPDOWN_OPTIONS' | translate }}</mat-label>
              <textarea matInput [(ngModel)]="col._optionsText" [name]="'col_opts_' + i"
                        [placeholder]="'REFERENCE_DATA.DROPDOWN_OPTIONS_HINT' | translate"
                        rows="2"></textarea>
            </mat-form-field>
          </div>
        </div>
      </form>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>{{ 'COMMON.CANCEL' | translate }}</button>
      <button mat-raised-button color="primary" [disabled]="saving || !listForm.valid" (click)="save()">
        <span *ngIf="!saving">{{ (isEdit ? 'COMMON.UPDATE' : 'COMMON.CREATE') | translate }}</span>
        <span *ngIf="saving">{{ 'COMMON.SAVING' | translate }}</span>
      </button>
    </mat-dialog-actions>
  `,
  styles: [`
    .full-width { width: 100%; }
    .columns-section { margin-top: 16px; }
    .columns-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
    .column-row { border: 1px solid #e0e0e0; border-radius: 8px; padding: 16px; margin-bottom: 12px; }
    .column-fields { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 8px; }
    .column-options { display: flex; align-items: center; gap: 16px; margin-top: 4px; }
    .col-field { width: 100%; }
  `],
})
export class ReferenceDataFormDialogComponent {
  isEdit: boolean;
  saving = false;
  model: {
    name_ar: string;
    name_en: string;
    description: string;
    columns: (ColumnSchema & { _optionsText?: string })[];
  };

  constructor(
    private dialogRef: MatDialogRef<ReferenceDataFormDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: ReferenceList | null,
    private refDataService: ReferenceDataService,
    private snackBar: MatSnackBar,
    private translate: TranslateService,
  ) {
    this.isEdit = !!data;
    if (data) {
      this.model = {
        name_ar: data.name_ar,
        name_en: data.name_en,
        description: data.description || '',
        columns: data.columns.map((c) => ({
          ...c,
          _optionsText: c.options ? c.options.join('\n') : '',
        })),
      };
    } else {
      this.model = {
        name_ar: '',
        name_en: '',
        description: '',
        columns: [this.newColumn()],
      };
    }
  }

  newColumn(): ColumnSchema & { _optionsText?: string } {
    return { key: '', label_ar: '', label_en: '', type: 'text', required: false, unique_key: false, _optionsText: '' };
  }

  addColumn(): void {
    this.model.columns.push(this.newColumn());
  }

  removeColumn(index: number): void {
    if (this.model.columns.length > 1) {
      this.model.columns.splice(index, 1);
    }
  }

  save(): void {
    this.saving = true;
    const columns: ColumnSchema[] = this.model.columns.map((c) => {
      const col: ColumnSchema = {
        key: c.key,
        label_ar: c.label_ar,
        label_en: c.label_en,
        type: c.type,
        required: c.required,
        unique_key: c.unique_key,
      };
      if (c.type === 'dropdown' && c._optionsText) {
        col.options = c._optionsText.split('\n').map((o) => o.trim()).filter((o) => o.length > 0);
      }
      return col;
    });

    const payload = {
      name_ar: this.model.name_ar,
      name_en: this.model.name_en,
      description: this.model.description,
      schema: columns,
    };

    const request$ = this.isEdit
      ? this.refDataService.updateList(this.data!.id, payload)
      : this.refDataService.createList(payload);

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

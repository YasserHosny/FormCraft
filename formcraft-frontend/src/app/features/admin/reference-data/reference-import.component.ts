import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatStepperModule } from '@angular/material/stepper';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { ReferenceDataService, ColumnSchema, ImportPreviewResult } from '../../../core/services/reference-data.service';

interface ImportDialogData {
  listId: string;
  columns: ColumnSchema[];
}

@Component({
  selector: 'fc-reference-import',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatStepperModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    MatTableModule,
    MatCheckboxModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    TranslateModule,
  ],
  template: `
    <h2 mat-dialog-title>{{ 'REFERENCE_DATA.IMPORT_TITLE' | translate }}</h2>
    <mat-dialog-content>
      <mat-stepper linear #stepper>
        <!-- Step 1: File Upload -->
        <mat-step [completed]="!!selectedFile">
          <ng-template matStepLabel>{{ 'REFERENCE_DATA.IMPORT_STEP_UPLOAD' | translate }}</ng-template>
          <div class="step-content">
            <div class="file-upload-area">
              <input type="file" accept=".csv" (change)="onFileSelected($event)" #fileInput hidden />
              <button mat-stroked-button (click)="fileInput.click()">
                <mat-icon>upload_file</mat-icon>
                {{ 'REFERENCE_DATA.SELECT_CSV' | translate }}
              </button>
              <span *ngIf="selectedFile" class="file-name">{{ selectedFile.name }}</span>
            </div>
            <mat-form-field appearance="outline" class="full-width mode-field">
              <mat-label>{{ 'REFERENCE_DATA.IMPORT_MODE' | translate }}</mat-label>
              <mat-select [(ngModel)]="importMode" name="importMode">
                <mat-option value="insert">{{ 'REFERENCE_DATA.MODE_INSERT' | translate }}</mat-option>
                <mat-option value="update">{{ 'REFERENCE_DATA.MODE_UPDATE' | translate }}</mat-option>
              </mat-select>
            </mat-form-field>
            <div class="step-actions">
              <button mat-raised-button color="primary" [disabled]="!selectedFile || uploading" (click)="uploadPreview(stepper)">
                <span *ngIf="!uploading">{{ 'COMMON.NEXT' | translate }}</span>
                <mat-spinner *ngIf="uploading" diameter="20"></mat-spinner>
              </button>
            </div>
          </div>
        </mat-step>

        <!-- Step 2: Column Mapping -->
        <mat-step [completed]="!!previewResult">
          <ng-template matStepLabel>{{ 'REFERENCE_DATA.IMPORT_STEP_MAPPING' | translate }}</ng-template>
          <div class="step-content" *ngIf="previewResult">
            <table mat-table [dataSource]="columnMappings" class="full-width">
              <ng-container matColumnDef="csv_header">
                <th mat-header-cell *matHeaderCellDef>{{ 'REFERENCE_DATA.CSV_HEADER' | translate }}</th>
                <td mat-cell *matCellDef="let row">{{ row.csvHeader }}</td>
              </ng-container>
              <ng-container matColumnDef="list_column">
                <th mat-header-cell *matHeaderCellDef>{{ 'REFERENCE_DATA.LIST_COLUMN' | translate }}</th>
                <td mat-cell *matCellDef="let row">
                  <mat-select [(ngModel)]="row.mappedTo" [name]="'map_' + row.csvHeader">
                    <mat-option value="">-- {{ 'REFERENCE_DATA.SKIP' | translate }} --</mat-option>
                    <mat-option *ngFor="let col of data.columns" [value]="col.key">{{ col.label_en }} ({{ col.key }})</mat-option>
                  </mat-select>
                </td>
              </ng-container>
              <tr mat-header-row *matHeaderRowDef="['csv_header', 'list_column']"></tr>
              <tr mat-row *matRowDef="let row; columns: ['csv_header', 'list_column'];"></tr>
            </table>
            <div class="step-actions">
              <button mat-button matStepperPrevious>{{ 'COMMON.BACK' | translate }}</button>
              <button mat-raised-button color="primary" matStepperNext>{{ 'COMMON.NEXT' | translate }}</button>
            </div>
          </div>
        </mat-step>

        <!-- Step 3: Preview -->
        <mat-step [completed]="confirmed">
          <ng-template matStepLabel>{{ 'REFERENCE_DATA.IMPORT_STEP_PREVIEW' | translate }}</ng-template>
          <div class="step-content" *ngIf="previewResult">
            <div class="preview-summary">
              <div class="stat valid">
                <span class="stat-label">{{ 'REFERENCE_DATA.VALID_ROWS' | translate }}</span>
                <span class="stat-value">{{ previewResult.valid_count }}</span>
              </div>
              <div class="stat invalid">
                <span class="stat-label">{{ 'REFERENCE_DATA.INVALID_ROWS' | translate }}</span>
                <span class="stat-value">{{ previewResult.invalid_count }}</span>
              </div>
            </div>

            <table *ngIf="previewResult.errors.length > 0" mat-table [dataSource]="previewResult.errors" class="full-width error-table">
              <ng-container matColumnDef="row">
                <th mat-header-cell *matHeaderCellDef>{{ 'REFERENCE_DATA.ERROR_ROW' | translate }}</th>
                <td mat-cell *matCellDef="let err">{{ err.row }}</td>
              </ng-container>
              <ng-container matColumnDef="column">
                <th mat-header-cell *matHeaderCellDef>{{ 'REFERENCE_DATA.ERROR_COLUMN' | translate }}</th>
                <td mat-cell *matCellDef="let err">{{ err.column }}</td>
              </ng-container>
              <ng-container matColumnDef="message">
                <th mat-header-cell *matHeaderCellDef>{{ 'REFERENCE_DATA.ERROR_MESSAGE' | translate }}</th>
                <td mat-cell *matCellDef="let err">{{ err.message }}</td>
              </ng-container>
              <tr mat-header-row *matHeaderRowDef="['row', 'column', 'message']"></tr>
              <tr mat-row *matRowDef="let row; columns: ['row', 'column', 'message'];"></tr>
            </table>

            <mat-checkbox *ngIf="previewResult.invalid_count > 0" [(ngModel)]="importValidOnly" name="importValidOnly">
              {{ 'REFERENCE_DATA.IMPORT_VALID_ONLY' | translate }}
            </mat-checkbox>

            <div class="step-actions">
              <button mat-button matStepperPrevious>{{ 'COMMON.BACK' | translate }}</button>
              <button mat-raised-button color="primary" matStepperNext
                      [disabled]="previewResult.valid_count === 0">
                {{ 'COMMON.NEXT' | translate }}
              </button>
            </div>
          </div>
        </mat-step>

        <!-- Step 4: Confirm -->
        <mat-step>
          <ng-template matStepLabel>{{ 'REFERENCE_DATA.IMPORT_STEP_CONFIRM' | translate }}</ng-template>
          <div class="step-content">
            <p>{{ 'REFERENCE_DATA.IMPORT_CONFIRM_MSG' | translate }}</p>
            <div class="step-actions">
              <button mat-button matStepperPrevious>{{ 'COMMON.BACK' | translate }}</button>
              <button mat-raised-button color="primary" [disabled]="confirming" (click)="confirmImport()">
                <span *ngIf="!confirming">{{ 'REFERENCE_DATA.CONFIRM_IMPORT' | translate }}</span>
                <mat-spinner *ngIf="confirming" diameter="20"></mat-spinner>
              </button>
            </div>
          </div>
        </mat-step>
      </mat-stepper>
    </mat-dialog-content>
  `,
  styles: [`
    .step-content { padding: 16px 0; }
    .full-width { width: 100%; }
    .file-upload-area { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
    .file-name { color: rgba(0,0,0,0.6); }
    .mode-field { margin-top: 8px; }
    .step-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 16px; }
    .preview-summary { display: flex; gap: 24px; margin-bottom: 16px; }
    .stat { display: flex; flex-direction: column; align-items: center; padding: 16px 24px; border-radius: 8px; }
    .stat.valid { background: #e8f5e9; }
    .stat.invalid { background: #ffebee; }
    .stat-label { font-size: 12px; color: rgba(0,0,0,0.6); }
    .stat-value { font-size: 24px; font-weight: 500; }
    .error-table { margin-bottom: 16px; }
  `],
})
export class ReferenceImportComponent {
  selectedFile: File | null = null;
  importMode: 'insert' | 'update' = 'insert';
  uploading = false;
  confirming = false;
  confirmed = false;
  importValidOnly = false;
  previewResult: ImportPreviewResult | null = null;
  columnMappings: { csvHeader: string; mappedTo: string }[] = [];

  constructor(
    private dialogRef: MatDialogRef<ReferenceImportComponent>,
    @Inject(MAT_DIALOG_DATA) public data: ImportDialogData,
    private refDataService: ReferenceDataService,
    private snackBar: MatSnackBar,
    private translate: TranslateService,
  ) {}

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedFile = input.files[0];
    }
  }

  uploadPreview(stepper: any): void {
    if (!this.selectedFile) return;
    this.uploading = true;
    this.refDataService.importPreview(this.data.listId, this.selectedFile, this.importMode).subscribe({
      next: (result) => {
        this.previewResult = result;
        this.columnMappings = result.csv_headers.map((header) => {
          const autoMatch = this.data.columns.find((c) => c.key === header || c.label_en === header);
          return { csvHeader: header, mappedTo: autoMatch ? autoMatch.key : '' };
        });
        this.uploading = false;
        stepper.next();
      },
      error: () => {
        this.uploading = false;
        this.snackBar.open(this.translate.instant('REFERENCE_DATA.IMPORT_ERROR'), '', { duration: 3000 });
      },
    });
  }

  confirmImport(): void {
    if (!this.previewResult) return;
    this.confirming = true;
    this.refDataService.importConfirm(this.data.listId, this.previewResult.token, this.importValidOnly).subscribe({
      next: (result) => {
        this.confirming = false;
        this.confirmed = true;
        this.snackBar.open(
          this.translate.instant('REFERENCE_DATA.IMPORT_SUCCESS', { count: result.imported }),
          '',
          { duration: 3000 },
        );
        this.dialogRef.close(true);
      },
      error: () => {
        this.confirming = false;
        this.snackBar.open(this.translate.instant('REFERENCE_DATA.IMPORT_ERROR'), '', { duration: 3000 });
      },
    });
  }
}

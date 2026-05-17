import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { ReferenceDataService, ReferenceList } from '../../../core/services/reference-data.service';
import { ReferenceDataFormDialogComponent } from './reference-data-form-dialog.component';
import { ReferenceImportComponent } from './reference-import.component';

@Component({
  selector: 'fc-reference-data-list',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatTooltipModule,
    MatDialogModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
    TranslateModule,
  ],
  template: `
    <div class="reference-data-list">
      <div class="header">
        <h2>{{ 'REFERENCE_DATA.TITLE' | translate }}</h2>
        <button mat-raised-button color="primary" (click)="openCreateDialog()">
          <mat-icon>add</mat-icon>
          {{ 'REFERENCE_DATA.CREATE_LIST' | translate }}
        </button>
      </div>

      <div *ngIf="loading" class="spinner-container">
        <mat-spinner diameter="40"></mat-spinner>
      </div>

      <table mat-table [dataSource]="lists" *ngIf="!loading" class="mat-elevation-z2 full-width">
        <ng-container matColumnDef="name">
          <th mat-header-cell *matHeaderCellDef>{{ 'REFERENCE_DATA.NAME' | translate }}</th>
          <td mat-cell *matCellDef="let row">
            <div class="name-cell">
              <span class="name-ar">{{ row.name_ar }}</span>
              <span class="name-en">{{ row.name_en }}</span>
            </div>
          </td>
        </ng-container>

        <ng-container matColumnDef="column_count">
          <th mat-header-cell *matHeaderCellDef>{{ 'REFERENCE_DATA.COLUMNS' | translate }}</th>
          <td mat-cell *matCellDef="let row">{{ row.column_count }}</td>
        </ng-container>

        <ng-container matColumnDef="entry_count">
          <th mat-header-cell *matHeaderCellDef>{{ 'REFERENCE_DATA.ENTRIES' | translate }}</th>
          <td mat-cell *matCellDef="let row">{{ row.entry_count }}</td>
        </ng-container>

        <ng-container matColumnDef="status">
          <th mat-header-cell *matHeaderCellDef>{{ 'REFERENCE_DATA.STATUS' | translate }}</th>
          <td mat-cell *matCellDef="let row">
            <mat-chip-listbox>
              <mat-chip [color]="row.status === 'active' ? 'primary' : 'warn'" selected>
                {{ 'REFERENCE_DATA.STATUS_' + row.status.toUpperCase() | translate }}
              </mat-chip>
            </mat-chip-listbox>
          </td>
        </ng-container>

        <ng-container matColumnDef="actions">
          <th mat-header-cell *matHeaderCellDef>{{ 'REFERENCE_DATA.ACTIONS' | translate }}</th>
          <td mat-cell *matCellDef="let row">
            <button mat-icon-button [matTooltip]="'REFERENCE_DATA.EDIT' | translate" (click)="openEditDialog(row)">
              <mat-icon>edit</mat-icon>
            </button>
            <button mat-icon-button [matTooltip]="'REFERENCE_DATA.VIEW_ENTRIES' | translate"
                    [routerLink]="['/admin/reference-data', row.id, 'entries']">
              <mat-icon>list</mat-icon>
            </button>
            <button mat-icon-button [matTooltip]="'REFERENCE_DATA.IMPORT' | translate" (click)="openImportDialog(row)">
              <mat-icon>upload_file</mat-icon>
            </button>
            <button mat-icon-button
                    [matTooltip]="(row.status === 'active' ? 'REFERENCE_DATA.ARCHIVE' : 'REFERENCE_DATA.UNARCHIVE') | translate"
                    (click)="toggleArchive(row)">
              <mat-icon>{{ row.status === 'active' ? 'archive' : 'unarchive' }}</mat-icon>
            </button>
            <button mat-icon-button [matTooltip]="'REFERENCE_DATA.DELETE' | translate"
                    color="warn"
                    [disabled]="row.entry_count > 0"
                    (click)="deleteList(row)">
              <mat-icon>delete</mat-icon>
            </button>
          </td>
        </ng-container>

        <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
        <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
      </table>

      <div *ngIf="!loading && lists.length === 0" class="empty-state">
        <mat-icon>folder_open</mat-icon>
        <p>{{ 'REFERENCE_DATA.NO_LISTS' | translate }}</p>
      </div>
    </div>
  `,
  styles: [`
    .reference-data-list { padding: 24px; }
    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
    .full-width { width: 100%; }
    .name-cell { display: flex; flex-direction: column; }
    .name-ar { font-weight: 500; }
    .name-en { font-size: 12px; color: rgba(0,0,0,0.54); }
    .spinner-container { display: flex; justify-content: center; padding: 48px; }
    .empty-state { text-align: center; padding: 48px; color: rgba(0,0,0,0.54); }
    .empty-state mat-icon { font-size: 48px; width: 48px; height: 48px; }
  `],
})
export class ReferenceDataListComponent implements OnInit {
  lists: ReferenceList[] = [];
  displayedColumns = ['name', 'column_count', 'entry_count', 'status', 'actions'];
  loading = true;

  constructor(
    private refDataService: ReferenceDataService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
    private router: Router,
    private translate: TranslateService,
  ) {}

  ngOnInit(): void {
    this.loadLists();
  }

  loadLists(): void {
    this.loading = true;
    this.refDataService.listLists().subscribe({
      next: (lists) => {
        this.lists = lists;
        this.loading = false;
      },
      error: () => {
        this.snackBar.open(this.translate.instant('REFERENCE_DATA.LOAD_ERROR'), '', { duration: 3000 });
        this.loading = false;
      },
    });
  }

  openCreateDialog(): void {
    const dialogRef = this.dialog.open(ReferenceDataFormDialogComponent, {
      width: '700px',
      data: null,
    });
    dialogRef.afterClosed().subscribe((result) => {
      if (result) this.loadLists();
    });
  }

  openEditDialog(list: ReferenceList): void {
    const dialogRef = this.dialog.open(ReferenceDataFormDialogComponent, {
      width: '700px',
      data: list,
    });
    dialogRef.afterClosed().subscribe((result) => {
      if (result) this.loadLists();
    });
  }

  openImportDialog(list: ReferenceList): void {
    const dialogRef = this.dialog.open(ReferenceImportComponent, {
      width: '750px',
      data: { listId: list.id, columns: list.columns },
    });
    dialogRef.afterClosed().subscribe((result) => {
      if (result) this.loadLists();
    });
  }

  toggleArchive(list: ReferenceList): void {
    const action$ = list.status === 'active'
      ? this.refDataService.archiveList(list.id)
      : this.refDataService.unarchiveList(list.id);
    action$.subscribe({
      next: () => this.loadLists(),
      error: () => this.snackBar.open(this.translate.instant('REFERENCE_DATA.ACTION_ERROR'), '', { duration: 3000 }),
    });
  }

  deleteList(list: ReferenceList): void {
    if (list.entry_count > 0) return;
    if (!confirm(this.translate.instant('REFERENCE_DATA.DELETE_CONFIRM'))) return;
    this.refDataService.deleteList(list.id).subscribe({
      next: () => this.loadLists(),
      error: () => this.snackBar.open(this.translate.instant('REFERENCE_DATA.DELETE_ERROR'), '', { duration: 3000 }),
    });
  }
}

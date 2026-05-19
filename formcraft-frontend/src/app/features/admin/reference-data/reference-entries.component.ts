import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatChipsModule } from '@angular/material/chips';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { ReferenceDataService, ReferenceList, ReferenceEntry, ColumnSchema } from '../../../core/services/reference-data.service';
import { ReferenceEntryFormDialogComponent } from './reference-entry-form-dialog.component';

@Component({
  selector: 'fc-reference-entries',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatTooltipModule,
    MatChipsModule,
    MatButtonToggleModule,
    MatDialogModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
    TranslateModule,
  ],
  template: `
    <div class="entries-container" *ngIf="list">
      <div class="header">
        <div class="header-left">
          <button mat-icon-button routerLink="/admin/reference-data">
            <mat-icon>arrow_back</mat-icon>
          </button>
          <h2>{{ list.name_ar }} / {{ list.name_en }}</h2>
        </div>
        <div class="header-actions">
          <mat-button-toggle-group [(value)]="activeFilter" (change)="loadEntries()">
            <mat-button-toggle value="all">{{ 'REFERENCE_DATA.FILTER_ALL' | translate }}</mat-button-toggle>
            <mat-button-toggle value="active">{{ 'REFERENCE_DATA.FILTER_ACTIVE' | translate }}</mat-button-toggle>
            <mat-button-toggle value="inactive">{{ 'REFERENCE_DATA.FILTER_INACTIVE' | translate }}</mat-button-toggle>
          </mat-button-toggle-group>
          <button mat-raised-button color="primary" (click)="openAddDialog()">
            <mat-icon>add</mat-icon>
            {{ 'REFERENCE_DATA.ADD_ENTRY' | translate }}
          </button>
        </div>
      </div>

      <div *ngIf="loading" class="spinner-container">
        <mat-spinner diameter="40"></mat-spinner>
      </div>

      <table mat-table [dataSource]="entries" *ngIf="!loading" class="mat-elevation-z2 full-width">
        <ng-container *ngFor="let col of list.columns" [matColumnDef]="col.key">
          <th mat-header-cell *matHeaderCellDef>{{ col.label_en }}</th>
          <td mat-cell *matCellDef="let row" [class.inactive-row]="!row.is_active">
            {{ row.values[col.key] }}
          </td>
        </ng-container>

        <ng-container matColumnDef="is_active">
          <th mat-header-cell *matHeaderCellDef>{{ 'REFERENCE_DATA.ACTIVE' | translate }}</th>
          <td mat-cell *matCellDef="let row">
            <mat-chip-listbox>
              <mat-chip [color]="row.is_active ? 'primary' : 'warn'" selected>
                {{ (row.is_active ? 'REFERENCE_DATA.ACTIVE' : 'REFERENCE_DATA.INACTIVE') | translate }}
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
            <button mat-icon-button
                    [matTooltip]="(row.is_active ? 'REFERENCE_DATA.DEACTIVATE' : 'REFERENCE_DATA.ACTIVATE') | translate"
                    (click)="toggleActive(row)">
              <mat-icon>{{ row.is_active ? 'block' : 'check_circle' }}</mat-icon>
            </button>
          </td>
        </ng-container>

        <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
        <tr mat-row *matRowDef="let row; columns: displayedColumns;"
            [class.inactive-row]="!row.is_active"></tr>
      </table>

      <div *ngIf="!loading && entries.length === 0" class="empty-state">
        <mat-icon>inbox</mat-icon>
        <p>{{ 'REFERENCE_DATA.NO_ENTRIES' | translate }}</p>
      </div>
    </div>
  `,
  styles: [`
    .entries-container { padding: 24px; }
    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 8px; }
    .header-left { display: flex; align-items: center; gap: 8px; }
    .header-actions { display: flex; align-items: center; gap: 12px; }
    .full-width { width: 100%; }
    .inactive-row { opacity: 0.5; }
    .spinner-container { display: flex; justify-content: center; padding: 48px; }
    .empty-state { text-align: center; padding: 48px; color: rgba(0,0,0,0.54); }
    .empty-state mat-icon { font-size: 48px; width: 48px; height: 48px; }
  `],
})
export class ReferenceEntriesComponent implements OnInit {
  list!: ReferenceList;
  entries: ReferenceEntry[] = [];
  displayedColumns: string[] = [];
  loading = true;
  activeFilter: 'all' | 'active' | 'inactive' = 'all';

  private listId!: string;

  constructor(
    private route: ActivatedRoute,
    private refDataService: ReferenceDataService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
    private translate: TranslateService,
  ) {}

  ngOnInit(): void {
    this.listId = this.route.snapshot.paramMap.get('listId')!;
    this.refDataService.getList(this.listId).subscribe({
      next: (list) => {
        this.list = list;
        this.displayedColumns = [...list.columns.map((c) => c.key), 'is_active', 'actions'];
        this.loadEntries();
      },
      error: () => {
        this.snackBar.open(this.translate.instant('REFERENCE_DATA.LOAD_ERROR'), '', { duration: 3000 });
        this.loading = false;
      },
    });
  }

  loadEntries(): void {
    this.loading = true;
    const params: any = {};
    if (this.activeFilter === 'active') params.is_active = true;
    if (this.activeFilter === 'inactive') params.is_active = false;

    this.refDataService.getEntries(this.listId, params).subscribe({
      next: (res) => {
        this.entries = res.data;
        this.loading = false;
      },
      error: () => {
        this.snackBar.open(this.translate.instant('REFERENCE_DATA.LOAD_ERROR'), '', { duration: 3000 });
        this.loading = false;
      },
    });
  }

  openAddDialog(): void {
    const dialogRef = this.dialog.open(ReferenceEntryFormDialogComponent, {
      width: '600px',
      data: { schema: this.list.columns, listId: this.listId },
    });
    dialogRef.afterClosed().subscribe((result) => {
      if (result) this.loadEntries();
    });
  }

  openEditDialog(entry: ReferenceEntry): void {
    const dialogRef = this.dialog.open(ReferenceEntryFormDialogComponent, {
      width: '600px',
      data: { schema: this.list.columns, listId: this.listId, entry },
    });
    dialogRef.afterClosed().subscribe((result) => {
      if (result) this.loadEntries();
    });
  }

  toggleActive(entry: ReferenceEntry): void {
    const action$ = entry.is_active
      ? this.refDataService.deactivateEntry(this.listId, entry.id)
      : this.refDataService.activateEntry(this.listId, entry.id);
    action$.subscribe({
      next: () => this.loadEntries(),
      error: () => this.snackBar.open(this.translate.instant('REFERENCE_DATA.ACTION_ERROR'), '', { duration: 3000 }),
    });
  }
}

import { Component, OnInit, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDialogModule, MatDialog, MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatChipsModule } from '@angular/material/chips';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { TranslateModule } from '@ngx-translate/core';
import {
  OrgAdminService,
  Department,
  DepartmentPayload,
  Branch,
  BranchPayload,
} from '../../../core/services/org-admin.service';

/* ================================================================== */
/*  Department Form Dialog                                             */
/* ================================================================== */

@Component({
  selector: 'fc-department-form-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    TranslateModule,
  ],
  template: `
    <h2 mat-dialog-title>
      {{ (data.department ? 'departments.edit' : 'departments.create') | translate }}
    </h2>
    <mat-dialog-content>
      <mat-form-field appearance="outline" class="full-width">
        <mat-label>{{ 'departments.name_ar' | translate }}</mat-label>
        <input matInput [(ngModel)]="form.name_ar" dir="rtl" required />
      </mat-form-field>
      <mat-form-field appearance="outline" class="full-width">
        <mat-label>{{ 'departments.name_en' | translate }}</mat-label>
        <input matInput [(ngModel)]="form.name_en" required />
      </mat-form-field>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>{{ 'common.cancel' | translate }}</button>
      <button
        mat-raised-button
        color="primary"
        [disabled]="!form.name_ar || !form.name_en"
        (click)="submit()"
      >
        {{ 'common.save' | translate }}
      </button>
    </mat-dialog-actions>
  `,
  styles: [`.full-width { width: 100%; margin-bottom: 8px; }`],
})
export class DepartmentFormDialog {
  form: DepartmentPayload;

  constructor(
    private dialogRef: MatDialogRef<DepartmentFormDialog>,
    @Inject(MAT_DIALOG_DATA) public data: { department: Department | null },
  ) {
    this.form = {
      name_ar: data.department?.name_ar || '',
      name_en: data.department?.name_en || '',
    };
  }

  submit(): void {
    this.dialogRef.close(this.form);
  }
}

/* ================================================================== */
/*  Branch Form Dialog                                                 */
/* ================================================================== */

@Component({
  selector: 'fc-branch-form-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    TranslateModule,
  ],
  template: `
    <h2 mat-dialog-title>
      {{ (data.branch ? 'branches.edit' : 'branches.create') | translate }}
    </h2>
    <mat-dialog-content>
      <mat-form-field appearance="outline" class="full-width">
        <mat-label>{{ 'branches.name_ar' | translate }}</mat-label>
        <input matInput [(ngModel)]="form.name_ar" dir="rtl" required />
      </mat-form-field>
      <mat-form-field appearance="outline" class="full-width">
        <mat-label>{{ 'branches.name_en' | translate }}</mat-label>
        <input matInput [(ngModel)]="form.name_en" required />
      </mat-form-field>
      <mat-form-field appearance="outline" class="full-width">
        <mat-label>{{ 'branches.location' | translate }}</mat-label>
        <input matInput [(ngModel)]="form.location" />
      </mat-form-field>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>{{ 'common.cancel' | translate }}</button>
      <button
        mat-raised-button
        color="primary"
        [disabled]="!form.name_ar || !form.name_en"
        (click)="submit()"
      >
        {{ 'common.save' | translate }}
      </button>
    </mat-dialog-actions>
  `,
  styles: [`.full-width { width: 100%; margin-bottom: 8px; }`],
})
export class BranchFormDialog {
  form: BranchPayload;

  constructor(
    private dialogRef: MatDialogRef<BranchFormDialog>,
    @Inject(MAT_DIALOG_DATA) public data: { branch: Branch | null },
  ) {
    this.form = {
      name_ar: data.branch?.name_ar || '',
      name_en: data.branch?.name_en || '',
      location: data.branch?.location || '',
    };
  }

  submit(): void {
    this.dialogRef.close(this.form);
  }
}

/* ================================================================== */
/*  Departments Component (T035 + T036 branches inline)                */
/* ================================================================== */

@Component({
  selector: 'fc-departments',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatDialogModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
    MatChipsModule,
    MatTooltipModule,
    TranslateModule,
  ],
  template: `
    <div class="departments-container">
      <div class="header-row">
        <h2>{{ 'departments.title' | translate }}</h2>
        <button mat-raised-button color="primary" (click)="openDepartmentDialog()">
          <mat-icon>add</mat-icon>
          {{ 'departments.create' | translate }}
        </button>
      </div>

      <div *ngIf="loading" class="center-spinner">
        <mat-spinner diameter="48"></mat-spinner>
      </div>

      <div *ngIf="!loading && departments.length === 0" class="empty-state">
        {{ 'departments.no_departments' | translate }}
      </div>

      <table mat-table [dataSource]="departments" *ngIf="!loading && departments.length > 0" class="full-width">
        <ng-container matColumnDef="name_ar">
          <th mat-header-cell *matHeaderCellDef>{{ 'departments.name_ar' | translate }}</th>
          <td mat-cell *matCellDef="let dept">{{ dept.name_ar }}</td>
        </ng-container>

        <ng-container matColumnDef="name_en">
          <th mat-header-cell *matHeaderCellDef>{{ 'departments.name_en' | translate }}</th>
          <td mat-cell *matCellDef="let dept">{{ dept.name_en }}</td>
        </ng-container>

        <ng-container matColumnDef="branch_count">
          <th mat-header-cell *matHeaderCellDef>{{ 'departments.branch_count' | translate }}</th>
          <td mat-cell *matCellDef="let dept">{{ dept.branch_count }}</td>
        </ng-container>

        <ng-container matColumnDef="user_count">
          <th mat-header-cell *matHeaderCellDef>{{ 'departments.user_count' | translate }}</th>
          <td mat-cell *matCellDef="let dept">{{ dept.user_count }}</td>
        </ng-container>

        <ng-container matColumnDef="is_active">
          <th mat-header-cell *matHeaderCellDef>{{ 'departments.active' | translate }}</th>
          <td mat-cell *matCellDef="let dept">
            <mat-icon [class.active]="dept.is_active" [class.inactive]="!dept.is_active">
              {{ dept.is_active ? 'check_circle' : 'cancel' }}
            </mat-icon>
          </td>
        </ng-container>

        <ng-container matColumnDef="actions">
          <th mat-header-cell *matHeaderCellDef>{{ 'common.actions' | translate }}</th>
          <td mat-cell *matCellDef="let dept">
            <button mat-icon-button (click)="openDepartmentDialog(dept); $event.stopPropagation()"
                    [matTooltip]="'departments.edit' | translate">
              <mat-icon>edit</mat-icon>
            </button>
            <button mat-icon-button color="warn"
                    (click)="deactivateDepartment(dept); $event.stopPropagation()"
                    *ngIf="dept.is_active"
                    [matTooltip]="'user_management.deactivate' | translate">
              <mat-icon>block</mat-icon>
            </button>
          </td>
        </ng-container>

        <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
        <tr mat-row *matRowDef="let dept; columns: displayedColumns;"
            class="dept-row"
            [class.expanded]="expandedDepartment?.id === dept.id"
            (click)="toggleBranches(dept)">
        </tr>
      </table>

      <!-- Branches inline panel (T036) -->
      <div *ngIf="expandedDepartment" class="branches-panel">
        <div class="branches-header">
          <h3>{{ 'branches.title' | translate }} - {{ expandedDepartment.name_en }}</h3>
          <button mat-stroked-button color="primary" (click)="openBranchDialog()">
            <mat-icon>add</mat-icon>
            {{ 'branches.create' | translate }}
          </button>
        </div>

        <div *ngIf="branchesLoading" class="center-spinner">
          <mat-spinner diameter="32"></mat-spinner>
        </div>

        <div *ngIf="!branchesLoading && branches.length === 0" class="empty-state">
          {{ 'branches.no_branches' | translate }}
        </div>

        <table mat-table [dataSource]="branches" *ngIf="!branchesLoading && branches.length > 0" class="full-width branches-table">
          <ng-container matColumnDef="name_ar">
            <th mat-header-cell *matHeaderCellDef>{{ 'branches.name_ar' | translate }}</th>
            <td mat-cell *matCellDef="let branch">{{ branch.name_ar }}</td>
          </ng-container>

          <ng-container matColumnDef="name_en">
            <th mat-header-cell *matHeaderCellDef>{{ 'branches.name_en' | translate }}</th>
            <td mat-cell *matCellDef="let branch">{{ branch.name_en }}</td>
          </ng-container>

          <ng-container matColumnDef="location">
            <th mat-header-cell *matHeaderCellDef>{{ 'branches.location' | translate }}</th>
            <td mat-cell *matCellDef="let branch">{{ branch.location || '-' }}</td>
          </ng-container>

          <ng-container matColumnDef="user_count">
            <th mat-header-cell *matHeaderCellDef>{{ 'branches.user_count' | translate }}</th>
            <td mat-cell *matCellDef="let branch">{{ branch.user_count }}</td>
          </ng-container>

          <ng-container matColumnDef="actions">
            <th mat-header-cell *matHeaderCellDef>{{ 'common.actions' | translate }}</th>
            <td mat-cell *matCellDef="let branch">
              <button mat-icon-button (click)="openBranchDialog(branch)"
                      [matTooltip]="'branches.edit' | translate">
                <mat-icon>edit</mat-icon>
              </button>
              <button mat-icon-button color="warn"
                      (click)="deactivateBranch(branch)"
                      *ngIf="branch.is_active"
                      [matTooltip]="'user_management.deactivate' | translate">
                <mat-icon>block</mat-icon>
              </button>
            </td>
          </ng-container>

          <tr mat-header-row *matHeaderRowDef="branchColumns"></tr>
          <tr mat-row *matRowDef="let row; columns: branchColumns;"></tr>
        </table>
      </div>
    </div>
  `,
  styles: [`
    .departments-container {
      max-width: 1100px;
      margin: 24px auto;
      padding: 0 16px;
    }
    .header-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }
    .full-width { width: 100%; }
    .dept-row { cursor: pointer; }
    .dept-row:hover { background: rgba(0,0,0,0.04); }
    .dept-row.expanded { background: rgba(63,81,181,0.08); }
    .active { color: #4caf50; }
    .inactive { color: #f44336; }
    .branches-panel {
      background: #fafafa;
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      padding: 16px;
      margin: 8px 0 24px;
    }
    .branches-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }
    .branches-table { background: white; }
    .empty-state {
      text-align: center;
      padding: 32px;
      color: rgba(0,0,0,0.54);
    }
    .center-spinner {
      display: flex;
      justify-content: center;
      padding: 32px;
    }
  `],
})
export class DepartmentsComponent implements OnInit {
  departments: Department[] = [];
  loading = true;
  displayedColumns = ['name_ar', 'name_en', 'branch_count', 'user_count', 'is_active', 'actions'];

  expandedDepartment: Department | null = null;
  branches: Branch[] = [];
  branchesLoading = false;
  branchColumns = ['name_ar', 'name_en', 'location', 'user_count', 'actions'];

  constructor(
    private orgAdmin: OrgAdminService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit(): void {
    this.loadDepartments();
  }

  loadDepartments(): void {
    this.loading = true;
    this.orgAdmin.getDepartments().subscribe({
      next: (d) => { this.departments = d; this.loading = false; },
      error: () => { this.loading = false; },
    });
  }

  openDepartmentDialog(dept?: Department): void {
    const ref = this.dialog.open(DepartmentFormDialog, {
      width: '480px',
      data: { department: dept || null },
    });
    ref.afterClosed().subscribe((result: DepartmentPayload | undefined) => {
      if (!result) return;
      const op = dept
        ? this.orgAdmin.updateDepartment(dept.id, result)
        : this.orgAdmin.createDepartment(result);
      op.subscribe({
        next: () => this.loadDepartments(),
        error: () => this.snackBar.open('Operation failed', '', { duration: 3000 }),
      });
    });
  }

  deactivateDepartment(dept: Department): void {
    if (!confirm('Deactivate this department?')) return;
    this.orgAdmin.deactivateDepartment(dept.id).subscribe({
      next: () => this.loadDepartments(),
      error: () => this.snackBar.open('Deactivation failed', '', { duration: 3000 }),
    });
  }

  /* ---------- Branches (T036) ---------- */

  toggleBranches(dept: Department): void {
    if (this.expandedDepartment?.id === dept.id) {
      this.expandedDepartment = null;
      this.branches = [];
      return;
    }
    this.expandedDepartment = dept;
    this.loadBranches(dept.id);
  }

  private loadBranches(departmentId: string): void {
    this.branchesLoading = true;
    this.orgAdmin.getBranchesByDepartment(departmentId).subscribe({
      next: (b) => { this.branches = b; this.branchesLoading = false; },
      error: () => { this.branchesLoading = false; },
    });
  }

  openBranchDialog(branch?: Branch): void {
    const ref = this.dialog.open(BranchFormDialog, {
      width: '480px',
      data: { branch: branch || null },
    });
    ref.afterClosed().subscribe((result: BranchPayload | undefined) => {
      if (!result || !this.expandedDepartment) return;
      const op = branch
        ? this.orgAdmin.updateBranch(branch.id, result)
        : this.orgAdmin.createBranch(this.expandedDepartment.id, result);
      op.subscribe({
        next: () => {
          this.loadBranches(this.expandedDepartment!.id);
          this.loadDepartments();
        },
        error: () => this.snackBar.open('Operation failed', '', { duration: 3000 }),
      });
    });
  }

  deactivateBranch(branch: Branch): void {
    if (!confirm('Deactivate this branch?')) return;
    this.orgAdmin.deactivateBranch(branch.id).subscribe({
      next: () => {
        this.loadBranches(this.expandedDepartment!.id);
        this.loadDepartments();
      },
      error: () => this.snackBar.open('Deactivation failed', '', { duration: 3000 }),
    });
  }
}

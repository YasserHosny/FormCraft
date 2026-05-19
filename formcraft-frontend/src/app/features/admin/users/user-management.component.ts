import { Component, OnInit, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDialogModule, MatDialog, MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatChipsModule } from '@angular/material/chips';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { TranslateModule } from '@ngx-translate/core';
import {
  OrgAdminService,
  OrgUser,
  UserAssignment,
  Department,
  Branch,
} from '../../../core/services/org-admin.service';

/* ================================================================== */
/*  Edit Assignment Dialog                                             */
/* ================================================================== */

@Component({
  selector: 'fc-edit-assignment-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatSelectModule,
    MatButtonModule,
    TranslateModule,
  ],
  template: `
    <h2 mat-dialog-title>{{ 'user_management.edit_assignment' | translate }}</h2>
    <mat-dialog-content>
      <p>{{ data.user.display_name || data.user.email }}</p>
      <mat-form-field appearance="outline" class="full-width">
        <mat-label>{{ 'auth.role' | translate }}</mat-label>
        <mat-select [(ngModel)]="form.role">
          <mat-option value="admin">{{ 'roles.admin' | translate }}</mat-option>
          <mat-option value="designer">{{ 'roles.designer' | translate }}</mat-option>
          <mat-option value="operator">{{ 'roles.operator' | translate }}</mat-option>
          <mat-option value="viewer">{{ 'roles.viewer' | translate }}</mat-option>
        </mat-select>
      </mat-form-field>
      <mat-form-field appearance="outline" class="full-width">
        <mat-label>{{ 'user_management.department_filter' | translate }}</mat-label>
        <mat-select [(ngModel)]="form.department_id" (selectionChange)="onDeptChange()">
          <mat-option [value]="null">{{ 'common.none' | translate }}</mat-option>
          <mat-option *ngFor="let d of data.departments" [value]="d.id">
            {{ d.name_en }}
          </mat-option>
        </mat-select>
      </mat-form-field>
      <mat-form-field appearance="outline" class="full-width">
        <mat-label>{{ 'user_management.branch_filter' | translate }}</mat-label>
        <mat-select [(ngModel)]="form.branch_id">
          <mat-option [value]="null">{{ 'common.none' | translate }}</mat-option>
          <mat-option *ngFor="let b of filteredBranches" [value]="b.id">
            {{ b.name_en }}
          </mat-option>
        </mat-select>
      </mat-form-field>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>{{ 'common.cancel' | translate }}</button>
      <button mat-raised-button color="primary" (click)="submit()">
        {{ 'common.save' | translate }}
      </button>
    </mat-dialog-actions>
  `,
  styles: [`.full-width { width: 100%; margin-bottom: 8px; }`],
})
export class EditAssignmentDialog {
  form: UserAssignment;
  filteredBranches: Branch[] = [];

  constructor(
    private dialogRef: MatDialogRef<EditAssignmentDialog>,
    @Inject(MAT_DIALOG_DATA) public data: {
      user: OrgUser;
      departments: Department[];
      branches: Branch[];
    },
  ) {
    this.form = {
      role: data.user.role,
      department_id: data.user.department_id,
      branch_id: data.user.branch_id,
    };
    this.filterBranches();
  }

  onDeptChange(): void {
    this.form.branch_id = null;
    this.filterBranches();
  }

  private filterBranches(): void {
    this.filteredBranches = this.form.department_id
      ? this.data.branches.filter((b) => b.department_id === this.form.department_id)
      : this.data.branches;
  }

  submit(): void {
    this.dialogRef.close(this.form);
  }
}

/* ================================================================== */
/*  User Management Component (T037)                                   */
/* ================================================================== */

@Component({
  selector: 'fc-user-management',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatSelectModule,
    MatFormFieldModule,
    MatInputModule,
    MatDialogModule,
    MatChipsModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
    TranslateModule,
  ],
  template: `
    <div class="user-mgmt-container">
      <h2>{{ 'user_management.title' | translate }}</h2>

      <!-- Filters -->
      <div class="filter-row">
        <mat-form-field appearance="outline">
          <mat-label>{{ 'user_management.department_filter' | translate }}</mat-label>
          <mat-select [(ngModel)]="filters.department_id" (selectionChange)="loadUsers()">
            <mat-option value="">{{ 'user_management.all_departments' | translate }}</mat-option>
            <mat-option *ngFor="let d of departments" [value]="d.id">{{ d.name_en }}</mat-option>
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>{{ 'user_management.branch_filter' | translate }}</mat-label>
          <mat-select [(ngModel)]="filters.branch_id" (selectionChange)="loadUsers()">
            <mat-option value="">{{ 'user_management.all_branches' | translate }}</mat-option>
            <mat-option *ngFor="let b of allBranches" [value]="b.id">{{ b.name_en }}</mat-option>
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>{{ 'user_management.role_filter' | translate }}</mat-label>
          <mat-select [(ngModel)]="filters.role" (selectionChange)="loadUsers()">
            <mat-option value="">{{ 'user_management.all_roles' | translate }}</mat-option>
            <mat-option value="admin">{{ 'roles.admin' | translate }}</mat-option>
            <mat-option value="designer">{{ 'roles.designer' | translate }}</mat-option>
            <mat-option value="operator">{{ 'roles.operator' | translate }}</mat-option>
            <mat-option value="viewer">{{ 'roles.viewer' | translate }}</mat-option>
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>{{ 'user_management.status_filter' | translate }}</mat-label>
          <mat-select [(ngModel)]="filters.is_active" (selectionChange)="loadUsers()">
            <mat-option value="">{{ 'user_management.all_users' | translate }}</mat-option>
            <mat-option value="true">{{ 'user_management.active_only' | translate }}</mat-option>
          </mat-select>
        </mat-form-field>
      </div>

      <div *ngIf="loading" class="center-spinner">
        <mat-spinner diameter="48"></mat-spinner>
      </div>

      <table mat-table [dataSource]="users" *ngIf="!loading" class="full-width">
        <ng-container matColumnDef="display_name">
          <th mat-header-cell *matHeaderCellDef>{{ 'invitations.display_name' | translate }}</th>
          <td mat-cell *matCellDef="let u">{{ u.display_name || '-' }}</td>
        </ng-container>

        <ng-container matColumnDef="email">
          <th mat-header-cell *matHeaderCellDef>{{ 'auth.email' | translate }}</th>
          <td mat-cell *matCellDef="let u">{{ u.email }}</td>
        </ng-container>

        <ng-container matColumnDef="role">
          <th mat-header-cell *matHeaderCellDef>{{ 'auth.role' | translate }}</th>
          <td mat-cell *matCellDef="let u">{{ 'roles.' + u.role | translate }}</td>
        </ng-container>

        <ng-container matColumnDef="department">
          <th mat-header-cell *matHeaderCellDef>{{ 'departments.title' | translate }}</th>
          <td mat-cell *matCellDef="let u">{{ u.department_name || '-' }}</td>
        </ng-container>

        <ng-container matColumnDef="branch">
          <th mat-header-cell *matHeaderCellDef>{{ 'branches.title' | translate }}</th>
          <td mat-cell *matCellDef="let u">{{ u.branch_name || '-' }}</td>
        </ng-container>

        <ng-container matColumnDef="is_active">
          <th mat-header-cell *matHeaderCellDef>{{ 'departments.active' | translate }}</th>
          <td mat-cell *matCellDef="let u">
            <mat-icon [class.active]="u.is_active" [class.inactive]="!u.is_active">
              {{ u.is_active ? 'check_circle' : 'cancel' }}
            </mat-icon>
          </td>
        </ng-container>

        <ng-container matColumnDef="last_login">
          <th mat-header-cell *matHeaderCellDef>{{ 'user_management.last_login' | translate }}</th>
          <td mat-cell *matCellDef="let u">
            {{ u.last_login ? (u.last_login | date:'short') : ('user_management.never_logged_in' | translate) }}
          </td>
        </ng-container>

        <ng-container matColumnDef="actions">
          <th mat-header-cell *matHeaderCellDef>{{ 'common.actions' | translate }}</th>
          <td mat-cell *matCellDef="let u">
            <button mat-icon-button (click)="openAssignmentDialog(u)"
                    [matTooltip]="'user_management.edit_assignment' | translate">
              <mat-icon>edit</mat-icon>
            </button>
            <button mat-icon-button color="warn" *ngIf="u.is_active"
                    (click)="deactivateUser(u)"
                    [matTooltip]="'user_management.deactivate' | translate">
              <mat-icon>person_off</mat-icon>
            </button>
            <button mat-icon-button color="primary" *ngIf="!u.is_active"
                    (click)="activateUser(u)"
                    [matTooltip]="'user_management.activate' | translate">
              <mat-icon>person_add</mat-icon>
            </button>
          </td>
        </ng-container>

        <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
        <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
      </table>
    </div>
  `,
  styles: [`
    .user-mgmt-container {
      max-width: 1200px;
      margin: 24px auto;
      padding: 0 16px;
    }
    .filter-row {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin-bottom: 16px;
    }
    .filter-row mat-form-field {
      flex: 1;
      min-width: 180px;
    }
    .full-width { width: 100%; }
    .active { color: #4caf50; }
    .inactive { color: #f44336; }
    .center-spinner {
      display: flex;
      justify-content: center;
      padding: 48px;
    }
  `],
})
export class UserManagementComponent implements OnInit {
  users: OrgUser[] = [];
  departments: Department[] = [];
  allBranches: Branch[] = [];
  loading = true;
  displayedColumns = ['display_name', 'email', 'role', 'department', 'branch', 'is_active', 'last_login', 'actions'];

  filters = {
    department_id: '',
    branch_id: '',
    role: '',
    is_active: '',
  };

  constructor(
    private orgAdmin: OrgAdminService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit(): void {
    this.orgAdmin.getDepartments().subscribe((d) => (this.departments = d));
    this.orgAdmin.getAllBranches().subscribe((b) => (this.allBranches = b));
    this.loadUsers();
  }

  loadUsers(): void {
    this.loading = true;
    const params: any = {};
    if (this.filters.department_id) params.department_id = this.filters.department_id;
    if (this.filters.branch_id) params.branch_id = this.filters.branch_id;
    if (this.filters.role) params.role = this.filters.role;
    if (this.filters.is_active === 'true') params.is_active = true;
    this.orgAdmin.getUsers(params).subscribe({
      next: (u) => { this.users = u; this.loading = false; },
      error: () => { this.loading = false; },
    });
  }

  openAssignmentDialog(user: OrgUser): void {
    const ref = this.dialog.open(EditAssignmentDialog, {
      width: '480px',
      data: { user, departments: this.departments, branches: this.allBranches },
    });
    ref.afterClosed().subscribe((result: UserAssignment | undefined) => {
      if (!result) return;
      this.orgAdmin.updateUser(user.id, result).subscribe({
        next: () => this.loadUsers(),
        error: () => this.snackBar.open('Update failed', '', { duration: 3000 }),
      });
    });
  }

  deactivateUser(user: OrgUser): void {
    if (!confirm(`Deactivate ${user.display_name || user.email}?`)) return;
    this.orgAdmin.deactivateUser(user.id).subscribe({
      next: () => this.loadUsers(),
      error: () => this.snackBar.open('Deactivation failed', '', { duration: 3000 }),
    });
  }

  activateUser(user: OrgUser): void {
    this.orgAdmin.activateUser(user.id).subscribe({
      next: () => this.loadUsers(),
      error: () => this.snackBar.open('Activation failed', '', { duration: 3000 }),
    });
  }
}

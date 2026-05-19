import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { TranslateModule } from '@ngx-translate/core';
import {
  OrgAdminService,
  Invitation,
  InvitationPayload,
  Department,
  Branch,
} from '../../../core/services/org-admin.service';

@Component({
  selector: 'fc-invitations',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatChipsModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
    TranslateModule,
  ],
  template: `
    <div class="invitations-container">
      <h2>{{ 'invitations.title' | translate }}</h2>

      <!-- Invite Form -->
      <mat-card class="invite-card">
        <mat-card-header>
          <mat-card-title>{{ 'invitations.invite_user' | translate }}</mat-card-title>
        </mat-card-header>
        <mat-card-content>
          <div class="invite-form">
            <mat-form-field appearance="outline">
              <mat-label>{{ 'invitations.email' | translate }}</mat-label>
              <input matInput type="email" [(ngModel)]="inviteForm.email" />
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>{{ 'invitations.role' | translate }}</mat-label>
              <mat-select [(ngModel)]="inviteForm.role">
                <mat-option value="designer">{{ 'roles.designer' | translate }}</mat-option>
                <mat-option value="operator">{{ 'roles.operator' | translate }}</mat-option>
                <mat-option value="viewer">{{ 'roles.viewer' | translate }}</mat-option>
              </mat-select>
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>{{ 'invitations.department' | translate }}</mat-label>
              <mat-select [(ngModel)]="inviteForm.department_id" (selectionChange)="onDeptChange()">
                <mat-option value="">{{ 'common.none' | translate }}</mat-option>
                <mat-option *ngFor="let d of departments" [value]="d.id">{{ d.name_en }}</mat-option>
              </mat-select>
            </mat-form-field>

            <mat-form-field appearance="outline">
              <mat-label>{{ 'invitations.branch' | translate }}</mat-label>
              <mat-select [(ngModel)]="inviteForm.branch_id">
                <mat-option value="">{{ 'common.none' | translate }}</mat-option>
                <mat-option *ngFor="let b of filteredBranches" [value]="b.id">{{ b.name_en }}</mat-option>
              </mat-select>
            </mat-form-field>

            <button
              mat-raised-button
              color="primary"
              (click)="sendInvitation()"
              [disabled]="!inviteForm.email || !inviteForm.role || sending"
            >
              <mat-spinner *ngIf="sending" diameter="18"></mat-spinner>
              <span *ngIf="!sending">{{ 'invitations.invite_user' | translate }}</span>
            </button>
          </div>
        </mat-card-content>
      </mat-card>

      <!-- Invitations List -->
      <div *ngIf="loading" class="center-spinner">
        <mat-spinner diameter="48"></mat-spinner>
      </div>

      <div *ngIf="!loading && invitations.length === 0" class="empty-state">
        {{ 'invitations.no_invitations' | translate }}
      </div>

      <table mat-table [dataSource]="invitations" *ngIf="!loading && invitations.length > 0" class="full-width">
        <ng-container matColumnDef="email">
          <th mat-header-cell *matHeaderCellDef>{{ 'invitations.email' | translate }}</th>
          <td mat-cell *matCellDef="let inv">{{ inv.email }}</td>
        </ng-container>

        <ng-container matColumnDef="role">
          <th mat-header-cell *matHeaderCellDef>{{ 'invitations.role' | translate }}</th>
          <td mat-cell *matCellDef="let inv">{{ 'roles.' + inv.role | translate }}</td>
        </ng-container>

        <ng-container matColumnDef="department">
          <th mat-header-cell *matHeaderCellDef>{{ 'invitations.department' | translate }}</th>
          <td mat-cell *matCellDef="let inv">{{ inv.department_name || '-' }}</td>
        </ng-container>

        <ng-container matColumnDef="branch">
          <th mat-header-cell *matHeaderCellDef>{{ 'invitations.branch' | translate }}</th>
          <td mat-cell *matCellDef="let inv">{{ inv.branch_name || '-' }}</td>
        </ng-container>

        <ng-container matColumnDef="status">
          <th mat-header-cell *matHeaderCellDef>{{ 'invitations.status' | translate }}</th>
          <td mat-cell *matCellDef="let inv">
            <span class="status-chip" [ngClass]="inv.status">
              {{ 'invitations.' + inv.status | translate }}
            </span>
          </td>
        </ng-container>

        <ng-container matColumnDef="expires_at">
          <th mat-header-cell *matHeaderCellDef>{{ 'invitations.expires_at' | translate }}</th>
          <td mat-cell *matCellDef="let inv">{{ inv.expires_at | date:'short' }}</td>
        </ng-container>

        <ng-container matColumnDef="actions">
          <th mat-header-cell *matHeaderCellDef>{{ 'common.actions' | translate }}</th>
          <td mat-cell *matCellDef="let inv">
            <button mat-icon-button color="warn"
                    *ngIf="inv.status === 'pending'"
                    (click)="cancelInvitation(inv)"
                    [matTooltip]="'invitations.cancel' | translate">
              <mat-icon>cancel</mat-icon>
            </button>
          </td>
        </ng-container>

        <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
        <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
      </table>
    </div>
  `,
  styles: [`
    .invitations-container {
      max-width: 1100px;
      margin: 24px auto;
      padding: 0 16px;
    }
    .invite-card {
      margin-bottom: 24px;
    }
    .invite-form {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      align-items: flex-start;
    }
    .invite-form mat-form-field {
      flex: 1;
      min-width: 180px;
    }
    .invite-form button {
      margin-top: 4px;
      align-self: center;
    }
    .full-width { width: 100%; }
    .status-chip {
      display: inline-block;
      padding: 2px 10px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 500;
    }
    .status-chip.pending { background: #fff3e0; color: #e65100; }
    .status-chip.accepted { background: #e8f5e9; color: #2e7d32; }
    .status-chip.expired { background: #fbe9e7; color: #bf360c; }
    .empty-state {
      text-align: center;
      padding: 32px;
      color: rgba(0,0,0,0.54);
    }
    .center-spinner {
      display: flex;
      justify-content: center;
      padding: 48px;
    }
  `],
})
export class InvitationsComponent implements OnInit {
  invitations: Invitation[] = [];
  departments: Department[] = [];
  allBranches: Branch[] = [];
  filteredBranches: Branch[] = [];
  loading = true;
  sending = false;
  displayedColumns = ['email', 'role', 'department', 'branch', 'status', 'expires_at', 'actions'];

  inviteForm: InvitationPayload & { department_id: string; branch_id: string } = {
    email: '',
    role: 'operator',
    department_id: '',
    branch_id: '',
  };

  constructor(
    private orgAdmin: OrgAdminService,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit(): void {
    this.orgAdmin.getDepartments().subscribe((d) => (this.departments = d));
    this.orgAdmin.getAllBranches().subscribe((b) => {
      this.allBranches = b;
      this.filteredBranches = b;
    });
    this.loadInvitations();
  }

  onDeptChange(): void {
    this.inviteForm.branch_id = '';
    this.filteredBranches = this.inviteForm.department_id
      ? this.allBranches.filter((b) => b.department_id === this.inviteForm.department_id)
      : this.allBranches;
  }

  loadInvitations(): void {
    this.loading = true;
    this.orgAdmin.getInvitations().subscribe({
      next: (inv) => { this.invitations = inv; this.loading = false; },
      error: () => { this.loading = false; },
    });
  }

  sendInvitation(): void {
    this.sending = true;
    const payload: InvitationPayload = {
      email: this.inviteForm.email,
      role: this.inviteForm.role,
    };
    if (this.inviteForm.department_id) payload.department_id = this.inviteForm.department_id;
    if (this.inviteForm.branch_id) payload.branch_id = this.inviteForm.branch_id;

    this.orgAdmin.createInvitation(payload).subscribe({
      next: () => {
        this.sending = false;
        this.snackBar.open('Invitation sent', '', { duration: 2000 });
        this.inviteForm = { email: '', role: 'operator', department_id: '', branch_id: '' };
        this.loadInvitations();
      },
      error: (err) => {
        this.sending = false;
        const msg = err?.error?.detail || 'Failed to send invitation';
        this.snackBar.open(msg, '', { duration: 3000 });
      },
    });
  }

  cancelInvitation(inv: Invitation): void {
    if (!confirm('Cancel this invitation?')) return;
    this.orgAdmin.cancelInvitation(inv.id).subscribe({
      next: () => this.loadInvitations(),
      error: () => this.snackBar.open('Cancel failed', '', { duration: 3000 }),
    });
  }
}

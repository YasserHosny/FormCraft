import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { TranslateModule } from '@ngx-translate/core';
import { OrgAdminService, InvitationInfo } from '../../../core/services/org-admin.service';

@Component({
  selector: 'fc-invitation-accept',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatProgressBarModule,
    TranslateModule,
  ],
  template: `
    <div class="invitation-container">
      <div *ngIf="loading" class="center-spinner">
        <mat-spinner diameter="48"></mat-spinner>
      </div>

      <mat-card class="invitation-card" *ngIf="!loading && info">
        <mat-card-header>
          <mat-card-title>{{ 'invitations.accept_title' | translate }}</mat-card-title>
        </mat-card-header>
        <mat-card-content>
          <p class="invite-message">
            {{ 'invitations.accept_message' | translate }}
            <strong>{{ info.org_name }}</strong>
          </p>
          <p class="invite-role">
            {{ 'auth.role' | translate }}: <strong>{{ 'roles.' + info.role | translate }}</strong>
          </p>
          <p class="invite-email">
            {{ 'auth.email' | translate }}: <strong>{{ info.email }}</strong>
          </p>

          <mat-form-field appearance="outline" class="full-width">
            <mat-label>{{ 'invitations.display_name' | translate }}</mat-label>
            <input matInput [(ngModel)]="displayName" />
          </mat-form-field>

          <mat-form-field appearance="outline" class="full-width">
            <mat-label>{{ 'invitations.set_password' | translate }}</mat-label>
            <input matInput [type]="showPassword ? 'text' : 'password'" [(ngModel)]="password" />
            <button mat-icon-button matSuffix (click)="showPassword = !showPassword" type="button">
              <mat-icon>{{ showPassword ? 'visibility_off' : 'visibility' }}</mat-icon>
            </button>
          </mat-form-field>

          <!-- Password strength indicator -->
          <div class="strength-bar" *ngIf="password">
            <mat-progress-bar
              mode="determinate"
              [value]="passwordStrength"
              [color]="passwordStrength < 40 ? 'warn' : 'primary'"
            ></mat-progress-bar>
            <span class="strength-label">{{ strengthLabel }}</span>
          </div>

          <div *ngIf="errorMessage" class="error-message">{{ errorMessage }}</div>

          <button
            mat-raised-button
            color="primary"
            class="full-width submit-btn"
            (click)="accept()"
            [disabled]="!displayName || !password || password.length < 6 || submitting"
          >
            <mat-spinner *ngIf="submitting" diameter="18"></mat-spinner>
            <span *ngIf="!submitting">{{ 'invitations.accept_title' | translate }}</span>
          </button>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .invitation-container {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 80vh;
      padding: 16px;
    }
    .invitation-card {
      max-width: 480px;
      width: 100%;
    }
    .invite-message, .invite-role, .invite-email {
      margin-bottom: 8px;
    }
    .full-width { width: 100%; }
    .strength-bar {
      margin-bottom: 16px;
    }
    .strength-label {
      font-size: 12px;
      color: rgba(0,0,0,0.6);
    }
    .submit-btn {
      margin-top: 8px;
    }
    .error-message {
      color: #f44336;
      margin-bottom: 8px;
    }
    .center-spinner {
      display: flex;
      justify-content: center;
      padding: 48px;
    }
  `],
})
export class InvitationAcceptComponent implements OnInit {
  token = '';
  info: InvitationInfo | null = null;
  loading = true;
  submitting = false;
  showPassword = false;

  displayName = '';
  password = '';
  errorMessage = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private orgAdmin: OrgAdminService,
  ) {}

  ngOnInit(): void {
    this.token = this.route.snapshot.paramMap.get('token') || '';
    if (!this.token) {
      this.router.navigate(['/auth/login']);
      return;
    }
    this.orgAdmin.getInvitationInfo(this.token).subscribe({
      next: (info) => { this.info = info; this.loading = false; },
      error: () => {
        this.loading = false;
        this.router.navigate(['/invite/expired']);
      },
    });
  }

  get passwordStrength(): number {
    const p = this.password;
    if (!p) return 0;
    let score = 0;
    if (p.length >= 6) score += 20;
    if (p.length >= 10) score += 20;
    if (/[A-Z]/.test(p)) score += 20;
    if (/[0-9]/.test(p)) score += 20;
    if (/[^a-zA-Z0-9]/.test(p)) score += 20;
    return score;
  }

  get strengthLabel(): string {
    const s = this.passwordStrength;
    if (s <= 20) return 'Weak';
    if (s <= 40) return 'Fair';
    if (s <= 60) return 'Good';
    if (s <= 80) return 'Strong';
    return 'Very Strong';
  }

  accept(): void {
    this.submitting = true;
    this.errorMessage = '';
    this.orgAdmin.acceptInvitation(this.token, {
      display_name: this.displayName,
      password: this.password,
    }).subscribe({
      next: () => {
        this.submitting = false;
        this.router.navigate(['/auth/login']);
      },
      error: (err) => {
        this.submitting = false;
        this.errorMessage = err?.error?.detail || 'Failed to accept invitation';
      },
    });
  }
}

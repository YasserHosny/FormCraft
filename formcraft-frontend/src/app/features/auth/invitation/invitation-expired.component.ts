import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'fc-invitation-expired',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    TranslateModule,
  ],
  template: `
    <div class="expired-container">
      <mat-card class="expired-card">
        <mat-card-content class="expired-content">
          <mat-icon class="expired-icon" color="warn">link_off</mat-icon>
          <h2>{{ 'invitations.invitation_expired' | translate }}</h2>
          <p>{{ 'invitations.contact_admin' | translate }}</p>
          <button mat-raised-button color="primary" routerLink="/auth/login">
            {{ 'auth.login' | translate }}
          </button>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .expired-container {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 80vh;
      padding: 16px;
    }
    .expired-card {
      max-width: 480px;
      width: 100%;
    }
    .expired-content {
      text-align: center;
      padding: 32px 16px;
    }
    .expired-icon {
      font-size: 64px;
      width: 64px;
      height: 64px;
      margin-bottom: 16px;
    }
    h2 {
      margin-bottom: 8px;
    }
    p {
      color: rgba(0,0,0,0.6);
      margin-bottom: 24px;
    }
  `],
})
export class InvitationExpiredComponent {}

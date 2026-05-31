import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { Subject, takeUntil } from 'rxjs';
import { AuthService, User } from '../../../../core/auth/auth.service';
import { PageHeaderComponent } from './page-header.component';

@Component({
  selector: 'fc-profile',
  standalone: true,
  imports: [CommonModule, MatIconModule, PageHeaderComponent],
  template: `
    <fc-page-header [title]="'الملف الشخصي'" [subtitle]="'عرض وتعديل معلوماتك الشخصية'">
    </fc-page-header>

    <div class="page-body">
      <div class="fc-card profile-card" *ngIf="user">
        <div class="profile-header">
          <div class="avatar-large">{{ userInitials }}</div>
          <div class="profile-info">
            <h2>{{ user.display_name || user.email }}</h2>
            <p class="role-label">{{ roleLabel }}</p>
            <p class="email">{{ user.email }}</p>
          </div>
        </div>

        <div class="profile-section">
          <h3>معلومات الحساب</h3>
          <div class="info-group">
            <label>الاسم:</label>
            <span>{{ user.display_name || user.email }}</span>
          </div>
          <div class="info-group">
            <label>البريد الإلكتروني:</label>
            <span>{{ user.email }}</span>
          </div>
          <div class="info-group">
            <label>الدور:</label>
            <span>{{ roleLabel }}</span>
          </div>
        </div>

        <div class="profile-section coming-soon">
          <mat-icon>construction</mat-icon>
          <h4>قيد التطوير</h4>
          <p>سيتم إضافة خيارات التحرير والإعدادات قريباً في الواجهة الجديدة</p>
          <button class="fc-btn primary" (click)="editInClassicTheme()">
            <mat-icon>edit</mat-icon>
            تعديل في الواجهة الكلاسيكية
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .page-body {
      padding: 24px;
    }
    .profile-card {
      max-width: 600px;
      margin: 0 auto;
    }
    .profile-header {
      display: flex;
      gap: 24px;
      align-items: flex-start;
      padding-bottom: 24px;
      border-bottom: 1px solid var(--fc-border);
    }
    .avatar-large {
      width: 100px;
      height: 100px;
      border-radius: 50%;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 36px;
      font-weight: 700;
      flex-shrink: 0;
    }
    .profile-info h2 {
      margin: 0 0 4px;
      color: var(--fc-text);
      font-size: 20px;
    }
    .profile-info .role-label {
      margin: 0 0 8px;
      color: var(--fc-text-2);
      font-size: 14px;
    }
    .profile-info .email {
      margin: 0;
      color: var(--fc-text-3);
      font-size: 13px;
    }
    .profile-section {
      padding: 24px 0;
      border-bottom: 1px solid var(--fc-border);
    }
    .profile-section:last-child {
      border-bottom: none;
    }
    .profile-section h3 {
      margin: 0 0 16px;
      color: var(--fc-text);
      font-size: 14px;
      font-weight: 600;
    }
    .info-group {
      display: flex;
      justify-content: space-between;
      padding: 12px 0;
      align-items: center;
    }
    .info-group label {
      color: var(--fc-text-2);
      font-size: 13px;
      font-weight: 500;
    }
    .info-group span {
      color: var(--fc-text);
      font-size: 13px;
    }
    .coming-soon {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 32px 24px;
      background: var(--fc-surface-hover);
      border-radius: 8px;
      text-align: center;
      gap: 12px;
    }
    .coming-soon mat-icon {
      font-size: 48px;
      width: 48px;
      height: 48px;
      color: var(--fc-text-3);
    }
    .coming-soon h4 {
      margin: 0;
      color: var(--fc-text);
      font-size: 14px;
    }
    .coming-soon p {
      margin: 0;
      color: var(--fc-text-2);
      font-size: 12px;
    }
    .coming-soon .fc-btn {
      margin-top: 12px;
    }
  `],
})
export class ProfileComponent implements OnInit, OnDestroy {
  user: User | null = null;
  userInitials = '؟';
  roleLabel = '';

  private destroy$ = new Subject<void>();

  constructor(
    private authService: AuthService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.authService.currentUser$
      .pipe(takeUntil(this.destroy$))
      .subscribe((user) => {
        if (user) {
          this.user = user;
          this.userInitials = this.getInitials(user.display_name || user.email);
          this.roleLabel = this.getRoleLabel(user.role);
        }
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  editInClassicTheme(): void {
    this.router.navigate(['/auth/profile']);
  }

  private getInitials(name: string): string {
    const parts = name.trim().split(/\s+/).filter(Boolean);
    if (!parts.length) return '؟';
    return parts.slice(0, 2).map((part) => part[0]).join('');
  }

  private getRoleLabel(role: string): string {
    const labels: Record<string, string> = {
      admin: 'مسؤول',
      designer: 'مصمم',
      operator: 'مشغل',
      viewer: 'مشاهد',
      branch_manager: 'مدير فرع',
    };
    return labels[role] || role;
  }
}

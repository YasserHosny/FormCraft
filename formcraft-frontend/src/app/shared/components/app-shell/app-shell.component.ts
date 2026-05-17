import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { Subject, takeUntil } from 'rxjs';
import { AuthService, User } from '../../../core/auth/auth.service';
import { LanguageService } from '../../../core/i18n/language.service';
import { FeedbackRealtimeService } from '../../../features/feedback/services/feedback-realtime.service';
import { MyFeedbackService } from '../../../features/my-feedback/services/my-feedback.service';
import { OrgAdminService } from '../../../core/services/org-admin.service';

@Component({
  selector: 'fc-app-shell',
  standalone: false,
  template: `
    <mat-toolbar color="primary" class="app-toolbar">
      <!-- T046: Org logo in nav bar -->
      <img *ngIf="orgLogoUrl" [src]="orgLogoUrl" alt="Org logo" class="org-nav-logo" />
      <span class="app-title" routerLink="/templates">FormCraft</span>
      <span class="spacer"></span>

      <ng-container *ngIf="user">
        <button mat-button routerLink="/templates">
          {{ 'templates.title' | translate }}
        </button>
        <button mat-button [matMenuTriggerFor]="adminMenu" *ngIf="user.role === 'admin'">
          <mat-icon>admin_panel_settings</mat-icon>
        </button>
        <mat-menu #adminMenu="matMenu">
          <button mat-menu-item routerLink="/admin/settings">
            <mat-icon>business</mat-icon>
            {{ 'org.title' | translate }}
          </button>
          <button mat-menu-item routerLink="/admin/departments">
            <mat-icon>account_tree</mat-icon>
            {{ 'departments.title' | translate }}
          </button>
          <button mat-menu-item routerLink="/admin/users">
            <mat-icon>group</mat-icon>
            {{ 'user_management.title' | translate }}
          </button>
          <button mat-menu-item routerLink="/admin/invitations">
            <mat-icon>mail</mat-icon>
            {{ 'invitations.title' | translate }}
          </button>
          <button mat-menu-item routerLink="/auth/register">
            <mat-icon>person_add</mat-icon>
            {{ 'auth.register' | translate }}
          </button>
        </mat-menu>

        <!-- My Feedback link with notification badge (non-admin only) -->
        <button
          mat-button
          routerLink="/my-feedback"
          *ngIf="user.role !== 'admin'"
          [matBadge]="unreadCount > 0 ? unreadCount.toString() : null"
          matBadgeColor="warn"
          [matTooltip]="'notifications.badge_title' | translate"
        >
          <mat-icon>feedback</mat-icon>
          {{ 'my_feedback.title' | translate }}
        </button>

        <button mat-icon-button [matMenuTriggerFor]="userMenu">
          <mat-icon>account_circle</mat-icon>
        </button>
        <mat-menu #userMenu="matMenu">
          <div mat-menu-item disabled class="user-info">
            {{ user.display_name || user.email }}
            <br />
            <small>{{ 'roles.' + user.role | translate }}</small>
          </div>
          <mat-divider></mat-divider>
          <button mat-menu-item routerLink="/auth/profile">
            <mat-icon>person</mat-icon>
            {{ 'auth.profile' | translate }}
          </button>
          <button mat-menu-item (click)="toggleLanguage()">
            <mat-icon>language</mat-icon>
            {{ currentLang === 'ar' ? 'English' : 'العربية' }}
          </button>
          <mat-divider></mat-divider>
          <button mat-menu-item (click)="logout()">
            <mat-icon>logout</mat-icon>
            {{ 'auth.logout' | translate }}
          </button>
        </mat-menu>
      </ng-container>
    </mat-toolbar>

    <div class="shell-content">
      <router-outlet></router-outlet>
    </div>
  `,
  styles: [`
    .app-toolbar {
      position: sticky;
      top: 0;
      z-index: 100;
    }
    .org-nav-logo {
      max-height: 32px;
      max-width: 80px;
      object-fit: contain;
      margin-right: 8px;
      border-radius: 4px;
    }
    .app-title {
      cursor: pointer;
      font-weight: 700;
      font-size: 18px;
    }
    .spacer {
      flex: 1 1 auto;
    }
    .shell-content {
      height: calc(100vh - 64px);
      overflow: auto;
    }
    .user-info {
      line-height: 1.4;
      opacity: 0.9;
    }
  `],
})
export class AppShellComponent implements OnInit, OnDestroy {
  user: User | null = null;
  currentLang = 'ar';
  /** Unread notification count shown in the badge. */
  unreadCount = 0;
  /** T046: Org logo URL for the nav bar */
  orgLogoUrl: string | null = null;

  private destroy$ = new Subject<void>();

  constructor(
    private authService: AuthService,
    private languageService: LanguageService,
    private router: Router,
    private realtimeService: FeedbackRealtimeService,
    private myFeedbackService: MyFeedbackService,
    private orgAdminService: OrgAdminService,
  ) {}

  ngOnInit(): void {
    this.authService.currentUser$.pipe(takeUntil(this.destroy$)).subscribe((u) => {
      this.user = u;
      if (u) {
        // T046: Fetch org logo
        this.orgAdminService.getOrgSettings().subscribe({
          next: (settings) => (this.orgLogoUrl = settings.logo_url),
          error: () => (this.orgLogoUrl = null),
        });
        if (u.role !== 'admin') {
          this.initNotifications(u.id);
        } else {
          this.unreadCount = 0;
        }
      } else {
        // Reset on logout
        this.unreadCount = 0;
        this.orgLogoUrl = null;
      }
    });
    this.currentLang = this.languageService.getLanguage();
  }

  ngOnDestroy(): void {
    this.realtimeService.destroy();
    this.destroy$.next();
    this.destroy$.complete();
  }

  private initNotifications(userId: string): void {
    // Seed unread count from server
    this.myFeedbackService.getNotifications().subscribe((response) => {
      this.unreadCount = response.unread_count;
    });

    // Start global Realtime channel
    this.realtimeService.initNotificationChannel(userId);

    // Increment badge on each live event
    this.realtimeService.notificationEvents$
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.unreadCount += 1;
      });
  }

  toggleLanguage(): void {
    this.languageService.toggleLanguage();
    this.currentLang = this.languageService.getLanguage();
  }

  logout(): void {
    this.realtimeService.destroy();
    this.unreadCount = 0;
    this.authService.logout();
    this.router.navigate(['/auth/login']);
  }
}

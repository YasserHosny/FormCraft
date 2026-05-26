import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { Subject, takeUntil, filter } from 'rxjs';
import { AuthService, User } from '../../../core/auth/auth.service';
import { LanguageService } from '../../../core/i18n/language.service';
import { FeedbackRealtimeService } from '../../../features/feedback/services/feedback-realtime.service';
import { MyFeedbackService } from '../../../features/my-feedback/services/my-feedback.service';
import { OrgAdminService } from '../../../core/services/org-admin.service';
import { GlobalSearchBarComponent } from '../global-search/global-search-bar.component';

interface ModeTab {
  key: string;
  icon: string;
  route: string;
  labelKey: string;
  roles: string[];
}

const MODE_TABS: ModeTab[] = [
  { key: 'studio', icon: 'brush', route: '/templates', labelKey: 'nav.studio', roles: ['admin', 'designer'] },
  { key: 'desk', icon: 'assignment', route: '/desk', labelKey: 'nav.desk', roles: ['admin', 'designer', 'operator', 'branch_manager'] },
  { key: 'admin', icon: 'admin_panel_settings', route: '/admin', labelKey: 'nav.admin', roles: ['admin'] },
  { key: 'adminExport', icon: 'file_download', route: '/admin/export', labelKey: 'adminExport.title', roles: ['admin'] },
  { key: 'portal', icon: 'public', route: '/admin/portal', labelKey: 'portalAdmin.title', roles: ['admin'] },
  { key: 'integrations', icon: 'hub', route: '/admin/integrations', labelKey: 'integrations.title', roles: ['admin'] },
  { key: 'platform', icon: 'cloud', route: '/platform', labelKey: 'nav.platform', roles: ['admin'] },
];

/** Returns the role-based default route for post-login redirect. */
export function getDefaultRouteForRole(role: string): string {
  switch (role) {
    case 'operator':
    case 'branch_manager':
      return '/desk';
    case 'designer':
      return '/templates';
    case 'admin':
    default:
      return '/templates';
  }
}

@Component({
  selector: 'fc-app-shell',
  standalone: false,
  template: `
    <mat-toolbar color="primary" class="app-toolbar">
      <!-- T046: Org logo in nav bar -->
      <img *ngIf="orgLogoUrl" [src]="orgLogoUrl" alt="Org logo" class="org-nav-logo" />
      <span class="app-title" (click)="navigateHome()">FormCraft</span>

      <!-- F15: Mode-switching tabs -->
      <ng-container *ngIf="user">
        <nav class="mode-tabs">
          <a
            *ngFor="let tab of visibleTabs"
            class="mode-tab"
            [class.active]="activeMode === tab.key"
            [routerLink]="tab.route"
          >
            <mat-icon class="mode-tab-icon">{{ tab.icon }}</mat-icon>
            <span class="mode-tab-label">{{ tab.labelKey | translate }}</span>
          </a>
        </nav>
      </ng-container>

      <!-- F037: Global Search Bar -->
      <ng-container *ngIf="user && showSearchBar">
        <fc-global-search-bar class="global-search-bar"></fc-global-search-bar>
      </ng-container>

      <span class="spacer"></span>

      <ng-container *ngIf="user">
        <!-- My Feedback link with notification badge (non-admin only) -->
        <button
          mat-icon-button
          routerLink="/my-feedback"
          *ngIf="user.role !== 'admin'"
          [matBadge]="unreadCount > 0 ? unreadCount.toString() : null"
          matBadgeColor="warn"
          [matTooltip]="'notifications.badge_title' | translate"
        >
          <mat-icon>feedback</mat-icon>
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
      gap: 4px;
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
      margin-inline-end: 8px;
    }
    .mode-tabs {
      display: flex;
      align-items: center;
      gap: 2px;
      height: 100%;
    }
    .mode-tab {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 6px 16px;
      border-radius: 8px;
      color: rgba(255, 255, 255, 0.7);
      text-decoration: none;
      font-size: 14px;
      font-weight: 500;
      transition: background 0.15s, color 0.15s;
      cursor: pointer;
      white-space: nowrap;
    }
    .mode-tab:hover {
      background: rgba(255, 255, 255, 0.12);
      color: #fff;
    }
    .mode-tab.active {
      background: rgba(255, 255, 255, 0.22);
      color: #fff;
    }
    .mode-tab-icon {
      font-size: 20px;
      width: 20px;
      height: 20px;
    }
    .spacer {
      flex: 1 1 auto;
    }
    .global-search-bar {
      margin: 0 16px;
      max-width: 400px;
      width: 100%;
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
  /** F15: Tabs visible for current user role */
  visibleTabs: ModeTab[] = [];
  /** F15: Currently active mode key (studio, desk, admin) */
  activeMode = '';
  /** F037: Show global search bar for desk and studio modes */
  showSearchBar = false;

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
    // F15: Track active mode from route changes
    this.router.events.pipe(
      filter((e): e is NavigationEnd => e instanceof NavigationEnd),
      takeUntil(this.destroy$),
    ).subscribe((e) => {
      this.activeMode = this.detectModeFromUrl(e.urlAfterRedirects || e.url);
      this.showSearchBar = this.activeMode === 'desk' || this.activeMode === 'studio';
    });
    // Set initial active mode
    this.activeMode = this.detectModeFromUrl(this.router.url);
    this.showSearchBar = this.activeMode === 'desk' || this.activeMode === 'studio';

    this.authService.currentUser$.pipe(takeUntil(this.destroy$)).subscribe((u) => {
      this.user = u;
      if (u) {
        // F15: Compute visible tabs for this role
        this.visibleTabs = MODE_TABS.filter((tab) => tab.roles.includes(u.role));
        // F039: Show Platform tab only for platform admins
        if (!u.is_platform_admin) {
          this.visibleTabs = this.visibleTabs.filter((tab) => tab.key !== 'platform');
        }

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
        this.visibleTabs = [];
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

  /** F15: Navigate to role-appropriate home when clicking the logo/title. */
  navigateHome(): void {
    const role = this.user?.role || 'operator';
    this.router.navigate([getDefaultRouteForRole(role)]);
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

  /** F15: Detect which mode tab is active based on the current URL. */
  private detectModeFromUrl(url: string): string {
    if (url.startsWith('/platform')) return 'platform';
    if (url.startsWith('/admin/export')) return 'adminExport';
    if (url.startsWith('/admin/integrations')) return 'integrations';
    if (url.startsWith('/admin/portal')) return 'portal';
    if (url.startsWith('/admin')) return 'admin';
    if (url.startsWith('/desk')) return 'desk';
    // /templates and /designer are both part of "studio"
    return 'studio';
  }
}

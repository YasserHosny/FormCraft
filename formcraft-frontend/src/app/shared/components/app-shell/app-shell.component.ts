import { Component, HostListener, OnInit, OnDestroy } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { BreakpointObserver } from '@angular/cdk/layout';
import { Subject, takeUntil, filter } from 'rxjs';
import { AuthService, User } from '../../../core/auth/auth.service';
import { LanguageService } from '../../../core/i18n/language.service';
import { FeedbackRealtimeService } from '../../../features/feedback/services/feedback-realtime.service';
import { MyFeedbackService } from '../../../features/my-feedback/services/my-feedback.service';
import { OrgAdminService } from '../../../core/services/org-admin.service';
import { GlobalSearchBarComponent } from '../global-search/global-search-bar.component';
import { ThemePreferenceService } from '../../../core/services/theme-preference.service';

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
      <button
        mat-icon-button
        class="mobile-menu-button"
        *ngIf="user"
        (click)="showMobileMenu = true"
        [attr.aria-expanded]="showMobileMenu"
      >
        <mat-icon>menu</mat-icon>
      </button>

      <!-- T046: Org logo in nav bar -->
      <img *ngIf="orgLogoUrl" [src]="orgLogoUrl" alt="Org logo" class="org-nav-logo" />
      <span class="app-title" (click)="navigateHome()">FormCraft</span>

      <!-- F15: Mode-switching tabs — 3 primary always visible; the rest in "More ▾" -->
      <ng-container *ngIf="user">
        <nav class="mode-tabs">
          <a
            *ngFor="let tab of primaryTabs"
            class="mode-tab"
            [class.active]="activeMode === tab.key"
            [routerLink]="tab.route"
            [matTooltip]="tab.labelKey | translate"
            matTooltipPosition="below"
          >
            <mat-icon class="mode-tab-icon">{{ tab.icon }}</mat-icon>
            <span class="mode-tab-label">{{ tab.labelKey | translate }}</span>
          </a>
          <!-- Overflow menu for secondary admin tabs -->
          <button *ngIf="moreTabs.length"
                  class="mode-tab more-tab"
                  [class.active]="moreTabActive"
                  [matMenuTriggerFor]="moreTabsMenu"
                  type="button">
            <mat-icon class="mode-tab-icon">more_horiz</mat-icon>
            <span class="mode-tab-label">{{ 'nav.more' | translate }}</span>
          </button>
          <mat-menu #moreTabsMenu="matMenu">
            <a *ngFor="let tab of moreTabs"
               mat-menu-item
               [routerLink]="tab.route"
               style="color:inherit;text-decoration:none;">
              <mat-icon>{{ tab.icon }}</mat-icon>
              {{ tab.labelKey | translate }}
            </a>
          </mat-menu>
        </nav>
      </ng-container>

      <!-- F037: Global Search Bar -->
      <ng-container *ngIf="user && showSearchBar">
        <fc-global-search-bar class="global-search-bar"></fc-global-search-bar>
      </ng-container>

      <a class="spark-badge" *ngIf="user" (click)="switchToNewTheme()">
        <mat-icon>auto_awesome</mat-icon>
        <span>{{ 'nav.new_theme' | translate }}</span>
      </a>

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

    <div class="mobile-drawer-backdrop" [class.open]="showMobileMenu" (click)="showMobileMenu = false"></div>
    <aside class="mobile-mode-drawer" [class.open]="showMobileMenu">
      <a
        *ngFor="let tab of visibleTabs"
        class="mode-tab drawer-mode-tab"
        [class.active]="activeMode === tab.key"
        [routerLink]="tab.route"
        [title]="tab.labelKey | translate"
        (click)="showMobileMenu = false"
      >
        <mat-icon class="mode-tab-icon">{{ tab.icon }}</mat-icon>
        <span class="mode-tab-label">{{ tab.labelKey | translate }}</span>
      </a>
      <a class="spark-badge drawer-spark" *ngIf="user" (click)="switchToNewTheme(); showMobileMenu = false">
        <mat-icon>auto_awesome</mat-icon>
        <span>{{ 'nav.new_theme' | translate }}</span>
      </a>
    </aside>

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
    .mobile-menu-button {
      display: none;
    }
    .org-nav-logo {
      max-height: 32px;
      max-width: 80px;
      object-fit: contain;
      margin-inline-end: 8px;
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
      margin: 0 8px;
      max-width: 280px;
      width: 100%;
      flex: 0 1 280px;
    }
    // Reset <button> so it looks identical to the <a> mode-tab
    .more-tab {
      background: transparent;
      border: none;
      font-family: inherit;
      font-size: 14px;
    }
    .spark-badge {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      height: 30px;
      padding: 0 12px 0 9px;
      border-radius: 15px;
      background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
      color: #fff;
      font-size: 12.5px;
      font-weight: 700;
      letter-spacing: 0.02em;
      white-space: nowrap;
      cursor: pointer;
      text-decoration: none;
      box-shadow: 0 0 0 0 rgba(139, 92, 246, 0.5);
      animation: spark-pulse 3s ease-in-out infinite;
      transition: transform 0.15s, box-shadow 0.15s;
    }
    .spark-badge:hover {
      transform: translateY(-1px) scale(1.03);
      box-shadow: 0 4px 14px rgba(99, 102, 241, 0.55);
      animation: none;
    }
    .spark-badge mat-icon {
      font-size: 15px;
      width: 15px;
      height: 15px;
      animation: spark-spin 4s linear infinite;
    }
    @keyframes spark-pulse {
      0%, 100% { box-shadow: 0 0 0 0 rgba(139, 92, 246, 0.45); }
      50%       { box-shadow: 0 0 0 5px rgba(139, 92, 246, 0); }
    }
    @keyframes spark-spin {
      0%   { transform: rotate(0deg)   scale(1); }
      25%  { transform: rotate(15deg)  scale(1.15); }
      50%  { transform: rotate(0deg)   scale(1); }
      75%  { transform: rotate(-15deg) scale(1.15); }
      100% { transform: rotate(0deg)   scale(1); }
    }
    .drawer-spark {
      min-height: 44px;
      border-radius: 8px;
      height: 44px;
      width: calc(100% - 0px);
      justify-content: flex-start;
      padding: 0 16px;
    }
    .shell-content {
      height: calc(100vh - 64px);
      overflow: auto;
    }
    .user-info {
      line-height: 1.4;
      opacity: 0.9;
    }
    .mobile-drawer-backdrop,
    .mobile-mode-drawer {
      display: none;
    }

    @media (min-width: 600px) and (max-width: 959px) {
      .mobile-menu-button {
        display: inline-flex;
      }
      .mode-tab {
        padding-inline: 10px;
      }
      .mode-tab-label,
      .global-search-bar {
        display: none;
      }
    }

    @media (max-width: 599px) {
      .app-toolbar {
        min-height: 48px;
        height: 48px;
        padding-inline: 4px;
      }
      .mobile-menu-button {
        display: inline-flex;
      }
      .org-nav-logo {
        max-width: 44px;
        max-height: 28px;
        margin-inline-end: 4px;
      }
      .app-title {
        font-size: 16px;
        margin-inline-end: 4px;
      }
      .mode-tabs,
      .global-search-bar,
      .theme-switch-link {
        display: none;
      }
      .mobile-drawer-backdrop {
        display: block;
        position: fixed;
        inset: 48px 0 0;
        z-index: 90;
        background: rgba(0, 0, 0, 0.38);
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.2s ease;
      }
      .mobile-drawer-backdrop.open {
        opacity: 1;
        pointer-events: auto;
      }
      .mobile-mode-drawer {
        display: flex;
        flex-direction: column;
        gap: 4px;
        position: fixed;
        top: 48px;
        bottom: 0;
        inset-inline-start: 0;
        z-index: 101;
        width: min(280px, 84vw);
        padding: 12px;
        background: #fff;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.22);
        transform: translateX(-100%);
        transition: transform 0.25s ease;
      }
      :host-context([dir="rtl"]) .mobile-mode-drawer {
        transform: translateX(100%);
      }
      .mobile-mode-drawer.open,
      :host-context([dir="rtl"]) .mobile-mode-drawer.open {
        transform: translateX(0);
      }
      .drawer-mode-tab {
        color: rgba(0, 0, 0, 0.78);
        min-height: 44px;
      }
      .drawer-mode-tab.active {
        background: rgba(63, 81, 181, 0.12);
        color: #26358c;
      }
      .shell-content {
        height: calc(100vh - 48px);
      }
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
  isMobile = false;
  isTablet = false;
  showMobileMenu = false;

  /** Studio, Desk and Admin Console always appear in the bar; rest go into "More ▾". */
  private readonly PRIMARY_TAB_KEYS = ['studio', 'desk', 'admin'];

  get primaryTabs(): ModeTab[] {
    return this.visibleTabs.filter((t) => this.PRIMARY_TAB_KEYS.includes(t.key));
  }

  get moreTabs(): ModeTab[] {
    return this.visibleTabs.filter((t) => !this.PRIMARY_TAB_KEYS.includes(t.key));
  }

  get moreTabActive(): boolean {
    return this.moreTabs.some((t) => t.key === this.activeMode);
  }

  private destroy$ = new Subject<void>();

  constructor(
    private authService: AuthService,
    private languageService: LanguageService,
    private router: Router,
    private realtimeService: FeedbackRealtimeService,
    private myFeedbackService: MyFeedbackService,
    private orgAdminService: OrgAdminService,
    private themePreference: ThemePreferenceService,
    private breakpointObserver: BreakpointObserver,
  ) {}

  ngOnInit(): void {
    this.breakpointObserver.observe([
      '(max-width: 599px)',
      '(min-width: 600px) and (max-width: 959px)',
    ]).pipe(takeUntil(this.destroy$)).subscribe((state) => {
      this.isMobile = state.breakpoints['(max-width: 599px)'] || false;
      this.isTablet = state.breakpoints['(min-width: 600px) and (max-width: 959px)'] || false;
      if (!this.isMobile) {
        this.showMobileMenu = false;
      }
    });

    // F15: Track active mode from route changes
    this.router.events.pipe(
      filter((e): e is NavigationEnd => e instanceof NavigationEnd),
      takeUntil(this.destroy$),
    ).subscribe((e) => {
      this.activeMode = this.detectModeFromUrl(e.urlAfterRedirects || e.url);
      this.showSearchBar = this.activeMode === 'desk' || this.activeMode === 'studio';
      this.showMobileMenu = false;
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

  switchToNewTheme(): void {
    this.themePreference.setPreference('new');
    const target = this.themePreference.mapRouteToTheme(this.router.url, 'new', this.user?.role || 'admin', this.isMobile);
    this.router.navigate([target]);
  }

  logout(): void {
    this.realtimeService.destroy();
    this.unreadCount = 0;
    this.authService.logout();
    this.router.navigate(['/auth/login']);
  }

  @HostListener('document:keydown.escape')
  closeMobileMenu(): void {
    this.showMobileMenu = false;
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

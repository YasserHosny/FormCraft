import { Component, EventEmitter, Input, OnDestroy, OnInit, Output, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { BreakpointObserver } from '@angular/cdk/layout';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDividerModule } from '@angular/material/divider';
import { TranslateModule } from '@ngx-translate/core';
import { Subject, takeUntil } from 'rxjs';
import { AuthService, User } from '../../../core/auth/auth.service';
import { LanguageService } from '../../../core/i18n/language.service';
import { ThemePreferenceService } from '../../../core/services/theme-preference.service';
import { OrgAdminService } from '../../../core/services/org-admin.service';
import { MyFeedbackService } from '../../my-feedback/services/my-feedback.service';
import { FeedbackRealtimeService } from '../../feedback/services/feedback-realtime.service';
import { GlobalSearchBarComponent } from '../../../shared/components/global-search/global-search-bar.component';

interface ModeTab {
  key: string;
  icon: string;
  labelKey: string;
  route: string;
  roles: string[];
  /** When true, tab is only shown to users with is_platform_admin === true */
  requiresPlatformAdmin?: boolean;
}

const ALL_TABS: ModeTab[] = [
  { key: 'studio',       icon: 'brush',               labelKey: 'nav.studio',       route: '/ui/studio/templates',   roles: ['admin', 'designer'] },
  { key: 'desk',         icon: 'assignment',           labelKey: 'nav.desk',         route: '/ui/desk',               roles: ['admin', 'branch_manager', 'operator'] },
  { key: 'admin',        icon: 'admin_panel_settings', labelKey: 'nav.admin',        route: '/ui/admin/analytics',    roles: ['admin'] },
  { key: 'adminExport',  icon: 'file_download',        labelKey: 'nav.adminExport',  route: '/ui/admin/export',       roles: ['admin'] },
  { key: 'portal',       icon: 'public',               labelKey: 'nav.portal',       route: '/ui/admin/portal',       roles: ['admin'] },
  { key: 'integrations', icon: 'hub',                  labelKey: 'nav.integrations', route: '/ui/admin/integrations', roles: ['admin'] },
  { key: 'platform',     icon: 'cloud',                labelKey: 'nav.platform',     route: '/ui/admin/platform',     roles: ['admin'], requiresPlatformAdmin: true },
];

@Component({
  selector: 'fc-redesign-toolbar',
  standalone: true,
  imports: [CommonModule, RouterModule, MatIconModule, MatMenuModule, MatTooltipModule, MatDividerModule, TranslateModule, GlobalSearchBarComponent],
  templateUrl: './toolbar.component.html',
  styleUrl: './toolbar.component.scss',
})
export class ToolbarComponent implements OnInit, OnDestroy {
  @Input() activeMode: 'studio' | 'desk' | 'admin' = 'studio';
  @Output() menuRequested = new EventEmitter<void>();

  private destroy$ = new Subject<void>();
  private currentUser: User | null = null;

  isMobile = signal(false);
  tabs: ModeTab[] = [];
  unreadCount = 0;
  orgLogoUrl: string | null = null;
  userRole = '';
  user = { name: 'مستخدم', role: '', initials: '؟' };

  get currentLang(): string {
    return this.languageService.getLanguage();
  }

  constructor(
    private authService: AuthService,
    private router: Router,
    private languageService: LanguageService,
    private themePreference: ThemePreferenceService,
    private orgAdminService: OrgAdminService,
    private myFeedbackService: MyFeedbackService,
    private realtimeService: FeedbackRealtimeService,
    private breakpointObserver: BreakpointObserver,
  ) {}

  ngOnInit(): void {
    this.breakpointObserver.observe('(max-width: 599px)')
      .pipe(takeUntil(this.destroy$))
      .subscribe((state) => {
        this.isMobile.set(state.matches);
      });

    this.authService.currentUser$
      .pipe(takeUntil(this.destroy$))
      .subscribe((user) => {
        if (!user) return;
        this.currentUser = user;
        this.userRole = user.role;
        this.user = this.toToolbarUser(user);
        this.tabs = ALL_TABS.filter((tab) => {
          if (!tab.roles.includes(user.role)) return false;
          if (tab.requiresPlatformAdmin && !user.is_platform_admin) return false;
          return true;
        });
        this.initNotifications(user);
        this.loadOrgLogo();
      });
  }

  ngOnDestroy(): void {
    this.realtimeService.destroy();
    this.destroy$.next();
    this.destroy$.complete();
  }

  switchToClassic(): void {
    this.themePreference.setPreference('classic');
    const role = this.currentUser?.role || 'admin';
    const target = this.themePreference.mapRouteToTheme(this.router.url, 'classic', role, this.isMobile());
    this.router.navigate([target]);
  }

  toggleLanguage(): void {
    this.languageService.toggleLanguage();
  }

  logout(): void {
    this.realtimeService.destroy();
    this.unreadCount = 0;
    this.authService.logout();
    this.router.navigate(['/auth/login']);
  }

  private initNotifications(user: User): void {
    if (user.role === 'admin') {
      this.unreadCount = 0;
      return;
    }
    this.myFeedbackService.getNotifications().subscribe({
      next: (response) => { this.unreadCount = response.unread_count; },
      error: () => { this.unreadCount = 0; },
    });
    this.realtimeService.initNotificationChannel(user.id);
    this.realtimeService.notificationEvents$
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => { this.unreadCount += 1; });
  }

  private loadOrgLogo(): void {
    this.orgAdminService.getOrgSettings().subscribe({
      next: (settings) => { this.orgLogoUrl = settings.logo_url; },
      error: () => { this.orgLogoUrl = null; },
    });
  }

  private toToolbarUser(user: User): { name: string; role: string; initials: string } {
    const name = user.display_name || user.email;
    return {
      name,
      role: this.roleLabel(user.role),
      initials: this.initials(name),
    };
  }

  private roleLabel(role: User['role']): string {
    const keys: Record<User['role'], string> = {
      admin: 'nav.role_admin',
      designer: 'nav.role_designer',
      operator: 'nav.role_operator',
      viewer: 'nav.role_viewer',
      branch_manager: 'nav.role_branch_manager',
    };
    return keys[role] || role;
  }

  private initials(name: string): string {
    const parts = name.trim().split(/\s+/).filter(Boolean);
    if (!parts.length) return '؟';
    return parts.slice(0, 2).map((part) => part[0]).join('');
  }
}

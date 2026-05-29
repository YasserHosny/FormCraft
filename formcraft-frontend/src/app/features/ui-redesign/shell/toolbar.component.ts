import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDividerModule } from '@angular/material/divider';
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
  label: string;
  route: string;
  roles: string[];
}

const ALL_TABS: ModeTab[] = [
  { key: 'studio', icon: 'brush', label: 'استوديو التصميم', route: '/ui/studio/templates', roles: ['admin', 'designer'] },
  { key: 'desk', icon: 'assignment', label: 'مكتب النماذج', route: '/ui/desk', roles: ['admin', 'branch_manager', 'operator'] },
  { key: 'admin', icon: 'admin_panel_settings', label: 'لوحة الإدارة', route: '/ui/admin/analytics', roles: ['admin'] },
  { key: 'adminExport', icon: 'file_download', label: 'التصدير', route: '/admin/export', roles: ['admin'] },
  { key: 'portal', icon: 'public', label: 'البوابة', route: '/admin/portal', roles: ['admin'] },
  { key: 'integrations', icon: 'hub', label: 'التكاملات', route: '/admin/integrations', roles: ['admin'] },
  { key: 'platform', icon: 'cloud', label: 'المنصة', route: '/platform', roles: ['admin'] },
];

@Component({
  selector: 'fc-redesign-toolbar',
  standalone: true,
  imports: [CommonModule, RouterModule, MatIconModule, MatMenuModule, MatTooltipModule, MatDividerModule, GlobalSearchBarComponent],
  templateUrl: './toolbar.component.html',
  styleUrl: './toolbar.component.scss',
})
export class ToolbarComponent implements OnInit, OnDestroy {
  @Input() activeMode: 'studio' | 'desk' | 'admin' = 'studio';

  private destroy$ = new Subject<void>();
  private currentUser: User | null = null;

  tabs: ModeTab[] = [];
  unreadCount = 0;
  orgLogoUrl: string | null = null;
  currentLang = 'ar';
  userRole = '';
  user = { name: 'مستخدم', role: '', initials: '؟' };

  constructor(
    private authService: AuthService,
    private router: Router,
    private languageService: LanguageService,
    private themePreference: ThemePreferenceService,
    private orgAdminService: OrgAdminService,
    private myFeedbackService: MyFeedbackService,
    private realtimeService: FeedbackRealtimeService,
  ) {}

  ngOnInit(): void {
    this.currentLang = this.languageService.getLanguage();

    this.authService.currentUser$
      .pipe(takeUntil(this.destroy$))
      .subscribe((user) => {
        if (!user) return;
        this.currentUser = user;
        this.userRole = user.role;
        this.user = this.toToolbarUser(user);
        this.tabs = ALL_TABS.filter((tab) => tab.roles.includes(user.role));
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
    const target = this.themePreference.mapRouteToTheme(this.router.url, 'classic', role);
    this.router.navigate([target]);
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
    const labels: Record<User['role'], string> = {
      admin: 'مسؤول',
      designer: 'مصمم',
      operator: 'مشغل',
      viewer: 'مشاهد',
      branch_manager: 'مدير فرع',
    };
    return labels[role] || role;
  }

  private initials(name: string): string {
    const parts = name.trim().split(/\s+/).filter(Boolean);
    if (!parts.length) return '؟';
    return parts.slice(0, 2).map((part) => part[0]).join('');
  }
}

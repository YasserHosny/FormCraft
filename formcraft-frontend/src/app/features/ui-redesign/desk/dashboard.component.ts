import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { PageHeaderComponent } from '../shared/components/page-header.component';
import { StatusChipComponent } from '../shared/components/status-chip.component';
import { AvatarComponent } from '../shared/components/avatar.component';
import { KpiCardComponent } from '../shared/components/kpi-card.component';
import { DraftListComponent } from '../../../features/desk/components/draft-list/draft-list.component';
import { TemplateService } from '../../../core/services/template.service';
import { DeskService } from '../../../features/desk/services/desk.service';
import { HistoryService } from '../../../features/desk/services/history.service';
import { AuthService, User } from '../../../core/auth/auth.service';
import { LanguageService } from '../../../core/i18n/language.service';
import { Subject, merge } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: 'fc-desk-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, MatIconModule, TranslateModule, PageHeaderComponent, StatusChipComponent, AvatarComponent, KpiCardComponent, DraftListComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class DashboardComponent implements OnInit, OnDestroy {
  publishedTemplates: { id: string; name: string; code: string }[] = [];
  loading = true;
  error: string | null = null;
  isEmpty = false;

  // Real KPI data
  todaySubmissions: number = 0;
  pendingDrafts: number = 0;
  activeTemplates: number = 0;

  // Real activity data
  activities: any[] = [];

  // Real drafts data
  drafts: any[] = [];

  // Real pinned templates
  pinnedTemplates: any[] = [];

  // User greeting — rebuilt on user change or language switch
  userGreeting: string = '';
  pageSubtitle: string = '';

  private currentUser: User | null = null;
  private destroy$ = new Subject<void>();

  constructor(
    private router: Router,
    private templateService: TemplateService,
    private deskService: DeskService,
    private historyService: HistoryService,
    private authService: AuthService,
    private translate: TranslateService,
    private languageService: LanguageService,
  ) {}

  ngOnInit(): void {
    this.loading = true;

    // Rebuild greeting whenever the user or language changes
    merge(
      this.authService.currentUser$,
      this.translate.onLangChange,
    ).pipe(takeUntil(this.destroy$))
      .subscribe(() => this.buildGreeting());

    this.loadDashboardData();
  }

  private buildGreeting(): void {
    this.currentUser = this.authService.getCurrentUser();
    if (!this.currentUser) return;

    const name = this.currentUser.display_name || this.currentUser.email || '';
    this.userGreeting = this.translate.instant('desk.dashboard.greeting', { name });

    const lang = this.languageService.getLanguage();
    const locale = lang === 'ar' ? 'ar-AE' : 'en-GB';
    const opts: Intl.DateTimeFormatOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    this.pageSubtitle = new Date().toLocaleDateString(locale, opts);
  }

  private loadDashboardData(): void {
    this.deskService.getDashboard({})
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (dashboardData) => {
          this.pendingDrafts = dashboardData.drafts?.length || 0;
          this.activeTemplates = dashboardData.templates?.total || 0;

          this.pinnedTemplates = (dashboardData.pinned || [])
            .filter((p: any) => p.is_published === true)
            .slice(0, 6);

          this.drafts = dashboardData.drafts || [];

          const today = new Date().toISOString().split('T')[0];
          this.historyService.getSubmissions({ date_from: today, limit: 1 })
            .pipe(takeUntil(this.destroy$))
            .subscribe({
              next: (submissionsResponse) => {
                this.todaySubmissions = submissionsResponse.total || 0;
                this.loading = false;
                this.error = null;
                this.isEmpty = this.todaySubmissions === 0 && this.pendingDrafts === 0 && this.activeTemplates === 0;
              },
              error: (err) => {
                console.error('Failed to load submissions:', err);
                this.loading = false;
                this.error = 'Failed to load submissions data';
              },
            });

          this.historyService.getSubmissions({ limit: 10, sort_by: 'created_at', sort_dir: 'desc' })
            .pipe(takeUntil(this.destroy$))
            .subscribe({
              next: (response) => { this.activities = response.items || []; },
              error: (err) => {
                console.error('Failed to load activities:', err);
                this.activities = [];
              },
            });
        },
        error: (err) => {
          console.error('Failed to load dashboard:', err);
          this.loading = false;
          this.error = 'Failed to load dashboard data';
        },
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  fillNewForm(): void {
    this.router.navigate(['/ui/desk/templates']);
  }

  viewAllTransactions(): void {
    this.router.navigate(['/ui/desk/history']);
  }

  viewAllCustomers(): void {
    this.router.navigate(['/ui/desk/customers']);
  }

  resumeDraft(draft: any): void {
    this.router.navigate(['/ui/desk/fill', draft.template_id], { queryParams: { draftId: draft.id } });
  }

  fillTemplate(templateId: string): void {
    this.router.navigate(['/ui/desk/fill', templateId]);
  }
}

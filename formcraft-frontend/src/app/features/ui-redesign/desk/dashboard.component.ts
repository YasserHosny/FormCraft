import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { PageHeaderComponent } from '../shared/components/page-header.component';
import { StatusChipComponent } from '../shared/components/status-chip.component';
import { AvatarComponent } from '../shared/components/avatar.component';
import { KpiCardComponent } from '../shared/components/kpi-card.component';
import { TemplateService } from '../../../core/services/template.service';
import { DeskService } from '../../../features/desk/services/desk.service';
import { HistoryService } from '../../../features/desk/services/history.service';

@Component({
  selector: 'fc-desk-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, MatIconModule, PageHeaderComponent, StatusChipComponent, AvatarComponent, KpiCardComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class DashboardComponent implements OnInit {
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

  constructor(
    private router: Router,
    private templateService: TemplateService,
    private deskService: DeskService,
    private historyService: HistoryService
  ) {}

  ngOnInit(): void {
    this.loading = true;
    this.loadDashboardData();
  }

  private loadDashboardData(): void {
    this.deskService.getDashboard({}).subscribe({
      next: (dashboardData) => {
        // T007: Extract KPI counts from dashboard
        this.pendingDrafts = dashboardData.drafts?.length || 0;
        this.activeTemplates = dashboardData.templates?.total || 0;

        // Extract pinned templates (max 6, published only)
        this.pinnedTemplates = (dashboardData.pinned || [])
          .filter((p: any) => p.is_published === true)
          .slice(0, 6);

        // Extract drafts
        this.drafts = dashboardData.drafts || [];

        // T008: Get today's submissions count
        const today = new Date().toISOString().split('T')[0];
        this.historyService.getSubmissions({ date_from: today, limit: 1 }).subscribe({
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

        // Load recent activity
        this.historyService.getSubmissions({ limit: 10, sort_by: 'created_at', sort_dir: 'desc' }).subscribe({
          next: (response) => {
            this.activities = response.items || [];
          },
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

  fillNewForm(): void {
    this.router.navigate(['/desk']);
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

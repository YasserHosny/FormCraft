import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subject, takeUntil } from 'rxjs';
import { HistoryService, SubmissionListItem, HistoryFilterParams } from '../services/history.service';
import { TranslateService } from '@ngx-translate/core';
import { Router } from '@angular/router';

@Component({
  selector: 'fc-history',
  templateUrl: './history.component.html',
  styleUrls: ['./history.component.scss'],
})
export class HistoryComponent implements OnInit, OnDestroy {
  submissions: SubmissionListItem[] = [];
  total = 0;
  page = 1;
  limit = 25;
  loading = true;

  search = '';
  selectedTemplate = '';
  selectedStatus = '';
  dateFrom = '';
  dateTo = '';

  private destroy$ = new Subject<void>();

  constructor(
    private historyService: HistoryService,
    private translate: TranslateService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.loadSubmissions();
  }

  loadSubmissions(): void {
    this.loading = true;
    const params: HistoryFilterParams = {
      page: this.page,
      limit: this.limit,
      sort_by: 'created_at',
      sort_dir: 'desc',
      scope: 'own',
    };
    if (this.search) params.search = this.search;
    if (this.selectedTemplate) params.template_id = this.selectedTemplate;
    if (this.selectedStatus) params.status = this.selectedStatus;
    if (this.dateFrom) params.date_from = this.formatDateForApi(this.dateFrom);
    if (this.dateTo) params.date_to = this.formatDateForApi(this.dateTo);

    this.historyService.getSubmissions(params).pipe(takeUntil(this.destroy$)).subscribe({
      next: (response) => {
        this.submissions = response.items;
        this.total = response.total;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      },
    });
  }

  onPageChange(event: any): void {
    this.page = event.pageIndex + 1;
    this.limit = event.pageSize;
    this.loadSubmissions();
  }

  onSearch(): void {
    this.page = 1;
    this.loadSubmissions();
  }

  onClearFilters(): void {
    this.search = '';
    this.selectedTemplate = '';
    this.selectedStatus = '';
    this.dateFrom = '';
    this.dateTo = '';
    this.page = 1;
    this.loadSubmissions();
  }

  onView(submission: SubmissionListItem): void {
    // TODO: Implement submission detail view when submission detail module is available
    console.log('View submission details:', submission.id);
    // this.router.navigate(['/desk/history', submission.id]);
  }

  getStatusClass(status: string): string {
    switch (status) {
      case 'printed': return 'status-printed';
      case 'submitted': return 'status-submitted';
      default: return '';
    }
  }

  private formatDateForApi(date: Date | string): string {
    if (date instanceof Date) {
      return date.toISOString().split('T')[0]; // YYYY-MM-DD
    }
    return date; // Assume already in correct format if string
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
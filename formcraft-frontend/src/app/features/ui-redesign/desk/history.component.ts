import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { Subject, takeUntil } from 'rxjs';
import { PageHeaderComponent } from '../shared/components/page-header.component';
import { HistoryService, SubmissionListItem, HistoryFilterParams } from '../../../features/desk/services/history.service';

@Component({
  selector: 'fc-desk-history',
  standalone: true,
  imports: [CommonModule, FormsModule, MatIconModule, PageHeaderComponent],
  templateUrl: './history.component.html',
  styleUrl: './history.component.scss',
})
export class HistoryComponent implements OnInit, OnDestroy {
  submissions: SubmissionListItem[] = [];
  total = 0;
  page = 1;
  limit = 25;
  loading = true;
  error: string | null = null;

  search = '';
  selectedStatus = '';
  dateFrom = '';
  dateTo = '';

  private destroy$ = new Subject<void>();

  constructor(
    private historyService: HistoryService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.loadSubmissions();
  }

  loadSubmissions(): void {
    this.loading = true;
    this.error = null;
    const params: HistoryFilterParams = {
      page: this.page,
      limit: this.limit,
      sort_by: 'created_at',
      sort_dir: 'desc',
      scope: 'own',
    };
    if (this.search) params.search = this.search;
    if (this.selectedStatus) params.status = this.selectedStatus;
    if (this.dateFrom) params.date_from = this.dateFrom;
    if (this.dateTo) params.date_to = this.dateTo;

    this.historyService.getSubmissions(params).pipe(takeUntil(this.destroy$)).subscribe({
      next: (response) => {
        this.submissions = response.items;
        this.total = response.total;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.error = 'تعذّر تحميل سجل الإرسالات';
      },
    });
  }

  onSearch(): void {
    this.page = 1;
    this.loadSubmissions();
  }

  onClearFilters(): void {
    this.search = '';
    this.selectedStatus = '';
    this.dateFrom = '';
    this.dateTo = '';
    this.page = 1;
    this.loadSubmissions();
  }

  onReprint(submission: SubmissionListItem, event: Event): void {
    event.stopPropagation();
    this.historyService.requestReprint(submission.id).pipe(takeUntil(this.destroy$)).subscribe({
      next: (blob) => {
        const url = URL.createObjectURL(blob);
        const win = window.open(url, '_blank');
        win?.print();
      },
    });
  }

  onCloneAsNew(submission: SubmissionListItem, event: Event): void {
    event.stopPropagation();
    this.router.navigate(['/ui/desk/fill', submission.template_id], {
      queryParams: { clone: submission.id },
    });
  }

  prevPage(): void {
    if (this.page > 1) {
      this.page--;
      this.loadSubmissions();
    }
  }

  nextPage(): void {
    if (this.page < this.totalPages) {
      this.page++;
      this.loadSubmissions();
    }
  }

  get totalPages(): number {
    return Math.ceil(this.total / this.limit);
  }

  get pageStart(): number {
    return (this.page - 1) * this.limit + 1;
  }

  get pageEnd(): number {
    return Math.min(this.page * this.limit, this.total);
  }

  getStatusLabel(status: string): string {
    const map: Record<string, string> = {
      printed: 'مطبوع',
      submitted: 'مُرسَل',
    };
    return map[status] ?? status;
  }

  getStatusClass(status: string): string {
    return `status-${status}`;
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}

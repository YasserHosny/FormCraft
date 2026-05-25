import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatBadgeModule } from '@angular/material/badge';
import { TranslateModule } from '@ngx-translate/core';
import { FormsModule } from '@angular/forms';
import { ReviewQueueService } from '../../../core/services/review-queue.service';
import { TemplateService } from '../../../core/services/template.service';
import { ReviewQueueItem, ReviewQueueResponse } from '../../../shared/models/review.models';

@Component({
  selector: 'fc-review-queue',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    FormsModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
    MatBadgeModule,
    TranslateModule,
  ],
  templateUrl: './review-queue.component.html',
  styleUrls: ['./review-queue.component.scss'],
})
export class ReviewQueueComponent implements OnInit {
  items: ReviewQueueItem[] = [];
  displayedColumns = ['name', 'category', 'designer', 'department', 'submittedAt', 'daysWaiting', 'status', 'actions'];
  loading = true;
  total = 0;
  overdueCount = 0;

  // Filters
  statusFilter = '';
  departmentFilter = '';
  designerFilter = '';
  sortBy = 'submitted_at';
  sortDir = 'asc';

  constructor(
    private reviewQueueService: ReviewQueueService,
    private templateService: TemplateService,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit(): void {
    this.loadQueue();
  }

  loadQueue(): void {
    this.loading = true;
    this.reviewQueueService.getQueue({
      status: this.statusFilter || undefined,
      sort_by: this.sortBy,
      sort_dir: this.sortDir,
    }).subscribe({
      next: (response: ReviewQueueResponse) => {
        this.items = response.items;
        this.total = response.total;
        this.overdueCount = response.overdue_count;
        this.loading = false;
      },
      error: (err: any) => {
        this.loading = false;
        this.snackBar.open(err.error?.detail || 'Failed to load review queue', '', { duration: 3000 });
      },
    });
  }

  onFilterChange(): void {
    this.loadQueue();
  }

  toggleSort(column: string): void {
    if (this.sortBy === column) {
      this.sortDir = this.sortDir === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortBy = column;
      this.sortDir = 'asc';
    }
    this.loadQueue();
  }

  approve(item: ReviewQueueItem): void {
    this.templateService.transitionStatus(item.template_id, 'approved').subscribe({
      next: () => {
        this.snackBar.open('Template approved', '', { duration: 3000 });
        this.loadQueue();
      },
      error: (err: any) => {
        this.snackBar.open(err.error?.detail || 'Approval failed', '', { duration: 3000 });
      },
    });
  }

  reject(item: ReviewQueueItem): void {
    const comment = prompt('Enter rejection comment:');
    if (!comment) return;
    this.templateService.transitionStatus(item.template_id, 'rejected', comment).subscribe({
      next: () => {
        this.snackBar.open('Template rejected', '', { duration: 3000 });
        this.loadQueue();
      },
      error: (err: any) => {
        this.snackBar.open(err.error?.detail || 'Rejection failed', '', { duration: 3000 });
      },
    });
  }

  getStatusColor(status: string): string {
    switch (status) {
      case 'draft': return 'default';
      case 'submitted_for_review': return 'primary';
      case 'approved': return 'accent';
      case 'rejected': return 'warn';
      case 'published': return 'primary';
      default: return 'default';
    }
  }

  getStatusLabel(status: string): string {
    switch (status) {
      case 'submitted_for_review': return 'Submitted';
      case 'approved': return 'Approved';
      case 'rejected': return 'Rejected';
      default: return status;
    }
  }
}

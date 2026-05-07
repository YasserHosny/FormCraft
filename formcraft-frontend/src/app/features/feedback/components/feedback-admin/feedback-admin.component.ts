import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { FeedbackService, FeedbackAdminItem } from '../../services/feedback.service';

@Component({
  selector: 'fc-feedback-admin',
  standalone: false,
  templateUrl: './feedback-admin.component.html',
  styleUrls: ['./feedback-admin.component.scss'],
})
export class FeedbackAdminComponent implements OnInit {
  feedbackItems: FeedbackAdminItem[] = [];
  totalItems = 0;
  currentPage = 1;
  pageSize = 50;
  isLoading = false;
  expandedRowId: string | null = null;
  statusFilter = new FormControl('all');

  displayedColumns = ['date', 'user', 'page', 'message', 'attachments', 'status'];

  constructor(private feedbackService: FeedbackService) {}

  ngOnInit(): void {
    this.loadFeedback();
    this.statusFilter.valueChanges.subscribe(() => {
      this.currentPage = 1;
      this.loadFeedback();
    });
  }

  loadFeedback(): void {
    this.isLoading = true;
    const status = this.statusFilter.value === 'all' ? undefined : this.statusFilter.value || undefined;
    this.feedbackService.listFeedback({
      page: this.currentPage,
      limit: this.pageSize,
      status,
    }).subscribe({
      next: (response) => {
        this.feedbackItems = response.data;
        this.totalItems = response.total;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      },
    });
  }

  toggleRow(itemId: string): void {
    this.expandedRowId = this.expandedRowId === itemId ? null : itemId;
  }

  updateStatus(item: FeedbackAdminItem, newStatus: string): void {
    this.feedbackService.updateStatus(item.id, newStatus).subscribe({
      next: () => {
        this.loadFeedback();
      },
    });
  }

  getStatusChipClass(status: string): string {
    switch (status) {
      case 'new': return 'status-new';
      case 'reviewed': return 'status-reviewed';
      case 'resolved': return 'status-resolved';
      default: return '';
    }
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadFeedback();
  }

  get totalPages(): number {
    return Math.ceil(this.totalItems / this.pageSize);
  }
}
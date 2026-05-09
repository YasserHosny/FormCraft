import { Component, OnInit, OnDestroy } from '@angular/core';
import { FormControl } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { Subject, debounceTime, distinctUntilChanged, takeUntil } from 'rxjs';
import { FeedbackService, FeedbackAdminItem, LabelResponse, SubmitterItem } from '../../services/feedback.service';
import { FeedbackFilterStateService } from '../../services/feedback-filter-state.service';
import { FeedbackRealtimeService } from '../../services/feedback-realtime.service';
import { LabelManagerComponent } from '../label-manager/label-manager.component';
import { ReplyResponse } from '../../models/reply.models';

interface ThreadState {
  replies: ReplyResponse[];
  hasEarlier: boolean;
  loading: boolean;
  collapse$: Subject<void>;
}

@Component({
  selector: 'fc-feedback-admin',
  standalone: false,
  templateUrl: './feedback-admin.component.html',
  styleUrls: ['./feedback-admin.component.scss'],
})
export class FeedbackAdminComponent implements OnInit, OnDestroy {
  feedbackItems: FeedbackAdminItem[] = [];
  totalItems = 0;
  currentPage = 1;
  pageSize = 50;
  isLoading = false;
  expandedRowId: string | null = null;
  statusFilter = new FormControl('all');
  searchControl = new FormControl('');
  submitterFilter = new FormControl('');
  dateFromControl = new FormControl();
  dateToControl = new FormControl();

  submitters: SubmitterItem[] = [];
  allLabels: LabelResponse[] = [];

  displayedColumns = ['date', 'user', 'page', 'message', 'attachments', 'labels', 'status'];

  /** Per-submission thread state keyed by submission id. */
  threadMap = new Map<string, ThreadState>();

  private destroy$ = new Subject<void>();

  constructor(
    private feedbackService: FeedbackService,
    private filterStateService: FeedbackFilterStateService,
    private realtimeService: FeedbackRealtimeService,
    private dialog: MatDialog,
  ) {}

  ngOnInit(): void {
    this.loadSubmitters();
    this.loadLabels();

    this.statusFilter.valueChanges.pipe(takeUntil(this.destroy$)).subscribe(() => {
      this.currentPage = 1;
      this.filterStateService.setFilter({ status: this.statusFilter.value || 'all' });
    });

    this.searchControl.valueChanges
      .pipe(debounceTime(400), distinctUntilChanged(), takeUntil(this.destroy$))
      .subscribe((value) => {
        this.currentPage = 1;
        this.filterStateService.setFilter({ search: value || '' });
      });

    this.submitterFilter.valueChanges.pipe(takeUntil(this.destroy$)).subscribe((value) => {
      this.currentPage = 1;
      this.filterStateService.setFilter({ submitterId: value || null });
    });

    this.dateFromControl.valueChanges.pipe(takeUntil(this.destroy$)).subscribe((value) => {
      this.currentPage = 1;
      this.filterStateService.setFilter({ dateFrom: value ? new Date(value).toISOString().split('T')[0] : null });
    });

    this.dateToControl.valueChanges.pipe(takeUntil(this.destroy$)).subscribe((value) => {
      this.currentPage = 1;
      this.filterStateService.setFilter({ dateTo: value ? new Date(value).toISOString().split('T')[0] : null });
    });

    this.filterStateService.state$.pipe(takeUntil(this.destroy$)).subscribe(() => {
      this.loadFeedback();
    });
  }

  ngOnDestroy(): void {
    // Tear down all open thread channels
    this.threadMap.forEach((state, id) => {
      state.collapse$.next();
      state.collapse$.complete();
      this.realtimeService.unsubscribeThread(id);
    });
    this.threadMap.clear();
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadFeedback(): void {
    this.isLoading = true;
    const state = this.filterStateService.snapshot;
    const status = state.status === 'all' ? undefined : state.status || undefined;
    this.feedbackService.listFeedback({
      page: this.currentPage,
      limit: this.pageSize,
      status,
      search: state.search || undefined,
      labelIds: state.labelIds.length > 0 ? state.labelIds : undefined,
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

  loadSubmitters(): void {
    this.feedbackService.getSubmitters().subscribe({
      next: (submitters) => {
        this.submitters = submitters;
      },
    });
  }

  loadLabels(): void {
    this.feedbackService.getLabels().subscribe({
      next: (labels) => {
        this.allLabels = labels;
      },
    });
  }

  toggleRow(itemId: string): void {
    const isExpanding = this.expandedRowId !== itemId;
    const previousId = this.expandedRowId;

    // Collapse previous row's thread if any
    if (previousId && previousId !== itemId) {
      this.collapseThread(previousId);
    }

    this.expandedRowId = isExpanding ? itemId : null;

    if (isExpanding) {
      this.openThread(itemId);
    } else {
      this.collapseThread(itemId);
    }
  }

  private openThread(feedbackId: string): void {
    const collapse$ = new Subject<void>();
    const state: ThreadState = { replies: [], hasEarlier: false, loading: true, collapse$ };
    this.threadMap.set(feedbackId, state);

    // Load initial replies
    this.feedbackService.getAdminReplies(feedbackId).subscribe({
      next: (thread) => {
        state.replies = thread.replies;
        state.hasEarlier = thread.has_earlier;
        state.loading = false;
      },
      error: () => {
        state.loading = false;
      },
    });

    // Subscribe to Realtime live replies
    this.realtimeService
      .subscribeToThread(feedbackId)
      .pipe(takeUntil(collapse$))
      .subscribe((reply) => {
        state.replies = [...state.replies, reply];
      });

    // Mark unread user replies as read
    const item = this.feedbackItems.find((f) => f.id === feedbackId);
    if (item?.has_unread_user_reply) {
      this.feedbackService.markFeedbackRead(feedbackId).subscribe({
        next: () => {
          if (item) item.has_unread_user_reply = false;
        },
      });
    }
  }

  private collapseThread(feedbackId: string): void {
    const state = this.threadMap.get(feedbackId);
    if (!state) return;
    state.collapse$.next();
    state.collapse$.complete();
    this.realtimeService.unsubscribeThread(feedbackId);
    this.threadMap.delete(feedbackId);
  }

  getThreadState(feedbackId: string): ThreadState | null {
    return this.threadMap.get(feedbackId) ?? null;
  }

  onLoadEarlier(feedbackId: string, beforeId: string): void {
    const state = this.threadMap.get(feedbackId);
    if (!state) return;
    state.loading = true;
    this.feedbackService.getAdminReplies(feedbackId, 20, beforeId).subscribe({
      next: (thread) => {
        state.replies = [...thread.replies, ...state.replies];
        state.hasEarlier = thread.has_earlier;
        state.loading = false;
      },
      error: () => {
        state.loading = false;
      },
    });
  }

  onSendReply(feedbackId: string, text: string): void {
    const state = this.threadMap.get(feedbackId);
    this.feedbackService.postAdminReply(feedbackId, text).subscribe({
      next: (reply) => {
        if (state) {
          state.replies = [...state.replies, reply];
        }
        // Refresh list to update reply_count
        this.loadFeedback();
      },
    });
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

  openLabelManager(): void {
    const dialogRef = this.dialog.open(LabelManagerComponent, {
      width: '500px',
    });
    dialogRef.afterClosed().subscribe(() => {
      this.loadLabels();
    });
  }

  toggleLabel(labelId: string): void {
    const state = this.filterStateService.snapshot;
    const labelIds = state.labelIds.includes(labelId)
      ? state.labelIds.filter((id) => id !== labelId)
      : [...state.labelIds, labelId];
    this.filterStateService.setFilter({ labelIds });
  }

  isLabelSelected(labelId: string): boolean {
    return this.filterStateService.snapshot.labelIds.includes(labelId);
  }

  hasActiveFilters(): boolean {
    return this.filterStateService.hasActiveFilters();
  }

  clearAllFilters(): void {
    this.filterStateService.clearAll();
    this.statusFilter.setValue('all', { emitEvent: false });
    this.searchControl.setValue('', { emitEvent: false });
    this.submitterFilter.setValue('', { emitEvent: false });
    this.dateFromControl.setValue(null);
    this.dateToControl.setValue(null);
  }

  assignLabelToSubmission(item: FeedbackAdminItem, labelId: string): void {
    const currentLabelIds = (item as any).label_ids ?? [];
    if (currentLabelIds.length >= 5) return;
    const newLabelIds = [...currentLabelIds, labelId];
    this.feedbackService.assignLabels(item.id, newLabelIds).subscribe({
      next: () => {
        this.loadFeedback();
      },
    });
  }

  removeLabelFromSubmission(item: FeedbackAdminItem, labelId: string): void {
    const currentLabelIds: string[] = (item as any).label_ids ?? [];
    const newLabelIds = currentLabelIds.filter((id: string) => id !== labelId);
    this.feedbackService.assignLabels(item.id, newLabelIds).subscribe({
      next: () => {
        this.loadFeedback();
      },
    });
  }

  getLabelById(id: string): LabelResponse | undefined {
    return this.allLabels.find((l) => l.id === id);
  }
}
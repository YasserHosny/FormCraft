import {
  Component,
  OnInit,
  OnDestroy,
  ViewChildren,
  QueryList,
  AfterViewInit,
} from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { MatExpansionPanel } from '@angular/material/expansion';
import { Subject, takeUntil } from 'rxjs';

import { MyFeedbackItem, NotificationResponse, ReplyResponse } from '../../../feedback/models/reply.models';
import { MyFeedbackService } from '../../services/my-feedback.service';
import { FeedbackRealtimeService } from '../../../feedback/services/feedback-realtime.service';

interface ThreadState {
  replies: ReplyResponse[];
  hasEarlier: boolean;
  loading: boolean;
  collapse$: Subject<void>;
  unreadNotificationIds: string[];
}

@Component({
  selector: 'fc-my-feedback',
  standalone: false,
  templateUrl: './my-feedback.component.html',
  styleUrls: ['./my-feedback.component.scss'],
})
export class MyFeedbackComponent implements OnInit, AfterViewInit, OnDestroy {
  items: MyFeedbackItem[] = [];
  totalItems = 0;
  currentPage = 1;
  pageSize = 20;
  isLoading = false;

  /** Keyed by feedback_id → open thread state. */
  threadMap = new Map<string, ThreadState>();

  /** notification_id → feedback_id for quick lookup. */
  private notificationIndex = new Map<string, string>();

  /** feedback_id of the item to auto-expand (from ?expand= query param). */
  private expandTargetId: string | null = null;

  @ViewChildren(MatExpansionPanel) panels!: QueryList<MatExpansionPanel>;

  private destroy$ = new Subject<void>();

  constructor(
    private myFeedbackService: MyFeedbackService,
    private realtimeService: FeedbackRealtimeService,
    private route: ActivatedRoute,
  ) {}

  ngOnInit(): void {
    this.route.queryParams.pipe(takeUntil(this.destroy$)).subscribe((params) => {
      this.expandTargetId = params['expand'] ?? null;
    });

    // Load initial notifications to build the index for mark-as-read
    this.myFeedbackService.getNotifications().subscribe((response) => {
      response.notifications.forEach((n) => {
        this.notificationIndex.set(n.id, n.feedback_id);
      });
    });

    this.loadMyFeedback();
  }

  ngAfterViewInit(): void {
    // Auto-expand after panels render; re-check when panel list changes
    this.panels.changes.pipe(takeUntil(this.destroy$)).subscribe(() => {
      this.tryAutoExpand();
    });
  }

  ngOnDestroy(): void {
    this.threadMap.forEach((state, id) => {
      state.collapse$.next();
      state.collapse$.complete();
      this.realtimeService.unsubscribeThread(id);
    });
    this.threadMap.clear();
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadMyFeedback(): void {
    this.isLoading = true;
    this.myFeedbackService.getMyFeedback(this.currentPage, this.pageSize).subscribe({
      next: (response) => {
        this.items = response.results;
        this.totalItems = response.total;
        this.isLoading = false;
        // Attempt auto-expand after data loads (panels may already be in DOM)
        setTimeout(() => this.tryAutoExpand(), 50);
      },
      error: () => {
        this.isLoading = false;
      },
    });
  }

  private tryAutoExpand(): void {
    if (!this.expandTargetId) return;
    const idx = this.items.findIndex((i) => i.id === this.expandTargetId);
    if (idx === -1) return;
    const panelArray = this.panels.toArray();
    if (panelArray[idx]) {
      panelArray[idx].open();
      panelArray[idx]._body?.nativeElement?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      this.expandTargetId = null; // Only auto-expand once
    }
  }

  onPanelOpened(feedbackId: string): void {
    if (this.threadMap.has(feedbackId)) return;

    const collapse$ = new Subject<void>();
    const state: ThreadState = {
      replies: [],
      hasEarlier: false,
      loading: true,
      collapse$,
      unreadNotificationIds: [],
    };
    this.threadMap.set(feedbackId, state);

    // Load replies
    this.myFeedbackService.getReplies(feedbackId).subscribe({
      next: (thread) => {
        state.replies = thread.replies;
        state.hasEarlier = thread.has_earlier;
        state.loading = false;
      },
      error: () => {
        state.loading = false;
      },
    });

    // Subscribe to live Realtime updates
    this.realtimeService
      .subscribeToThread(feedbackId)
      .pipe(takeUntil(collapse$))
      .subscribe((reply) => {
        state.replies = [...state.replies, reply];
      });

    // Mark unread notifications for this submission as read
    const unreadIds = [...this.notificationIndex.entries()]
      .filter(([, fid]) => fid === feedbackId)
      .map(([nid]) => nid);

    unreadIds.forEach((nid) => {
      this.myFeedbackService.markNotificationRead(nid).subscribe({
        next: () => {
          this.notificationIndex.delete(nid);
          // Clear local has_unread_admin_reply badge
          const item = this.items.find((i) => i.id === feedbackId);
          if (item) item.has_unread_admin_reply = false;
        },
      });
    });
  }

  onPanelClosed(feedbackId: string): void {
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
    this.myFeedbackService.getReplies(feedbackId, 20, beforeId).subscribe({
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
    this.myFeedbackService.postReply(feedbackId, text).subscribe({
      next: (reply) => {
        if (state) state.replies = [...state.replies, reply];
        // Refresh list to update reply_count
        this.loadMyFeedback();
      },
    });
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadMyFeedback();
  }

  get totalPages(): number {
    return Math.ceil(this.totalItems / this.pageSize);
  }
}

import { Injectable, OnDestroy } from '@angular/core';
import { createClient, SupabaseClient, RealtimeChannel } from '@supabase/supabase-js';
import { Observable, Subject } from 'rxjs';
import { environment } from '../../../../environments/environment';
import { NotificationResponse, ReplyResponse } from '../models/reply.models';

interface ThreadEntry {
  channel: RealtimeChannel;
  subject: Subject<ReplyResponse>;
}

/**
 * Singleton Angular service that owns all Supabase Realtime channel subscriptions
 * for feedback threading & notifications (Feature 014).
 *
 * Channel strategy:
 * - One **global** notification channel per session (always active while logged in).
 * - One **per-thread** channel per open submission panel (torn down on close).
 */
@Injectable({ providedIn: 'root' })
export class FeedbackRealtimeService implements OnDestroy {
  private supabase: SupabaseClient;
  private threadChannels = new Map<string, ThreadEntry>();
  private notificationChannel: RealtimeChannel | null = null;

  /** Emits when a new notification INSERT arrives for the logged-in user. */
  notificationEvents$ = new Subject<NotificationResponse>();

  constructor() {
    this.supabase = createClient(
      environment.supabaseUrl,
      environment.supabaseAnonKey,
    );
  }

  /**
   * Subscribe to live INSERT events on feedback_replies for the given submission.
   * Returns an Observable that emits each new ReplyResponse until the panel closes.
   * Call unsubscribeThread(feedbackId) to complete the Observable and clean up.
   */
  subscribeToThread(feedbackId: string): Observable<ReplyResponse> {
    // Reuse existing subscription if already open
    if (this.threadChannels.has(feedbackId)) {
      return this.threadChannels.get(feedbackId)!.subject.asObservable();
    }

    const subject = new Subject<ReplyResponse>();
    const channelName = `thread:${feedbackId}`;

    const channel = this.supabase
      .channel(channelName)
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'feedback_replies',
          filter: `feedback_id=eq.${feedbackId}`,
        },
        (payload) => {
          const row = payload.new as Record<string, any>;
          subject.next({
            id: row['id'],
            author_role: row['author_role'],
            author_name: row['author_name'] ?? 'Unknown',
            text_content: row['text_content'],
            created_at: row['created_at'],
          });
        },
      )
      .subscribe();

    this.threadChannels.set(feedbackId, { channel, subject });
    return subject.asObservable();
  }

  /** Unsubscribe the per-thread channel and complete its Observable. */
  unsubscribeThread(feedbackId: string): void {
    const entry = this.threadChannels.get(feedbackId);
    if (!entry) return;
    entry.channel.unsubscribe();
    entry.subject.complete();
    this.threadChannels.delete(feedbackId);
  }

  /**
   * Activate the global notification channel for the authenticated user.
   * Must be called once after login with the user's UUID.
   * Emits on notificationEvents$ for each new INSERT on feedback_notifications.
   */
  initNotificationChannel(userId: string): void {
    if (this.notificationChannel) return; // already active

    this.notificationChannel = this.supabase
      .channel(`notifications:${userId}`)
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'feedback_notifications',
          filter: `recipient_user_id=eq.${userId}`,
        },
        (payload) => {
          const row = payload.new as Record<string, any>;
          this.notificationEvents$.next({
            id: row['id'],
            feedback_id: row['feedback_id'],
            reply_id: row['reply_id'],
            created_at: row['created_at'],
            delivered_at: row['delivered_at'] ?? null,
            read_at: row['read_at'] ?? null,
          });
        },
      )
      .subscribe();
  }

  /** Remove all active channels. Call on logout. */
  destroy(): void {
    this.threadChannels.forEach(({ channel, subject }) => {
      channel.unsubscribe();
      subject.complete();
    });
    this.threadChannels.clear();

    if (this.notificationChannel) {
      this.notificationChannel.unsubscribe();
      this.notificationChannel = null;
    }
  }

  ngOnDestroy(): void {
    this.destroy();
  }
}

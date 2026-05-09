import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../../environments/environment';
import {
  MyFeedbackResponse,
  NotificationsResponse,
  ReplyResponse,
  ThreadResponse,
} from '../../feedback/models/reply.models';

@Injectable({ providedIn: 'root' })
export class MyFeedbackService {
  private feedbackBase = `${environment.apiBaseUrl}/feedback`;
  private apiBase = environment.apiBaseUrl;

  constructor(private http: HttpClient) {}

  getMyFeedback(page = 1, pageSize = 20): Observable<MyFeedbackResponse> {
    const params = new HttpParams()
      .set('page', page)
      .set('page_size', pageSize);
    return this.http.get<MyFeedbackResponse>(`${this.apiBase}/my-feedback`, { params });
  }

  getReplies(feedbackId: string, limit = 20, beforeId?: string): Observable<ThreadResponse> {
    let params = new HttpParams().set('limit', limit);
    if (beforeId) params = params.set('before_id', beforeId);
    return this.http.get<ThreadResponse>(`${this.feedbackBase}/${feedbackId}/replies`, { params });
  }

  postReply(feedbackId: string, text: string): Observable<ReplyResponse> {
    return this.http.post<ReplyResponse>(
      `${this.feedbackBase}/${feedbackId}/replies`,
      { text_content: text },
    );
  }

  getNotifications(): Observable<NotificationsResponse> {
    return this.http.get<NotificationsResponse>(`${this.apiBase}/notifications`);
  }

  markNotificationRead(notificationId: string): Observable<void> {
    return this.http.patch<void>(`${this.apiBase}/notifications/${notificationId}/read`, {});
  }
}

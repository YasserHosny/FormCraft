import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  ReviewQueueResponse,
  GovernanceMetrics,
  TimelineResponse,
  DefaultReviewer,
} from '../../shared/models/review.models';

@Injectable({ providedIn: 'root' })
export class ReviewQueueService {
  private baseUrl = `${environment.apiBaseUrl}/admin/review-queue`;

  constructor(private http: HttpClient) {}

  getQueue(params?: {
    status?: string;
    department_id?: string;
    designer_id?: string;
    sort_by?: string;
    sort_dir?: string;
  }): Observable<ReviewQueueResponse> {
    let httpParams = new HttpParams();
    if (params?.status) httpParams = httpParams.set('status', params.status);
    if (params?.department_id) httpParams = httpParams.set('department_id', params.department_id);
    if (params?.designer_id) httpParams = httpParams.set('designer_id', params.designer_id);
    if (params?.sort_by) httpParams = httpParams.set('sort_by', params.sort_by);
    if (params?.sort_dir) httpParams = httpParams.set('sort_dir', params.sort_dir);
    return this.http.get<ReviewQueueResponse>(this.baseUrl, { params: httpParams });
  }

  getMetrics(since?: string): Observable<GovernanceMetrics> {
    let httpParams = new HttpParams();
    if (since) httpParams = httpParams.set('since', since);
    return this.http.get<GovernanceMetrics>(`${this.baseUrl}/metrics`, { params: httpParams });
  }

  getTimeline(templateId: string): Observable<TimelineResponse> {
    return this.http.get<TimelineResponse>(`${this.baseUrl}/${templateId}/timeline`);
  }

  getDefaultReviewer(departmentId: string): Observable<DefaultReviewer> {
    return this.http.get<DefaultReviewer>(
      `${this.baseUrl}/departments/${departmentId}/default-reviewer`
    );
  }

  setDefaultReviewer(departmentId: string, reviewerId: string): Observable<DefaultReviewer> {
    return this.http.put<DefaultReviewer>(
      `${this.baseUrl}/departments/${departmentId}/default-reviewer`,
      { reviewer_id: reviewerId }
    );
  }

  removeDefaultReviewer(departmentId: string): Observable<void> {
    return this.http.delete<void>(
      `${this.baseUrl}/departments/${departmentId}/default-reviewer`
    );
  }
}

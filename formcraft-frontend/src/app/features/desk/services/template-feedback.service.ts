import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';

export interface TemplateFeedbackItem {
  id: string;
  template_id: string;
  page_number: number | null;
  element_key: string | null;
  category: string;
  comment: string;
  screenshot_path: string | null;
  status: string;
  created_by: string;
  created_by_name: string | null;
  resolved_by: string | null;
  resolved_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface TemplateFeedbackListResponse {
  items: TemplateFeedbackItem[];
  total: number;
}

export interface TemplateFeedbackAdminOverviewItem {
  template_id: string;
  template_name: string;
  total_feedback: number;
  new_count: number;
  acknowledged_count: number;
  resolved_count: number;
}

export interface TemplateFeedbackAdminOverviewResponse {
  items: TemplateFeedbackAdminOverviewItem[];
}

@Injectable({ providedIn: 'root' })
export class TemplateFeedbackService {
  private baseUrl = `${environment.apiBaseUrl}/templates`;

  constructor(private http: HttpClient) {}

  submitFeedback(
    templateId: string,
    data: {
      category: string;
      comment: string;
      page_number?: number | null;
      element_key?: string | null;
      screenshot_path?: string | null;
    },
  ): Observable<TemplateFeedbackItem> {
    return this.http.post<TemplateFeedbackItem>(
      `${this.baseUrl}/${templateId}/feedback`,
      data,
    );
  }

  listFeedback(
    templateId: string,
    params?: { status?: string; page?: number; limit?: number },
  ): Observable<TemplateFeedbackListResponse> {
    let httpParams = new HttpParams();
    if (params?.status) httpParams = httpParams.set('status', params.status);
    if (params?.page) httpParams = httpParams.set('page', params.page);
    if (params?.limit) httpParams = httpParams.set('limit', params.limit);
    return this.http.get<TemplateFeedbackListResponse>(
      `${this.baseUrl}/${templateId}/feedback`,
      { params: httpParams },
    );
  }

  updateFeedbackStatus(
    templateId: string,
    feedbackId: string,
    newStatus: string,
  ): Observable<TemplateFeedbackItem> {
    return this.http.patch<TemplateFeedbackItem>(
      `${this.baseUrl}/${templateId}/feedback/${feedbackId}`,
      { status: newStatus },
    );
  }

  getAdminOverview(orgId?: string): Observable<TemplateFeedbackAdminOverviewResponse> {
    let params = new HttpParams();
    if (orgId) params = params.set('org_id', orgId);
    return this.http.get<TemplateFeedbackAdminOverviewResponse>(
      `${environment.apiBaseUrl}/admin/template-feedback`,
      { params },
    );
  }
}
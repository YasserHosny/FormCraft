import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';

export interface SubmissionListItem {
  id: string;
  reference_number: string;
  template_id: string;
  template_name: string;
  template_version: number;
  status: string;
  created_at: string;
  key_summary: string[];
}

export interface SubmissionListResponse {
  items: SubmissionListItem[];
  total: number;
  page: number;
  limit: number;
}

export interface SubmissionDetail {
  id: string;
  reference_number: string;
  template_id: string;
  template_name: string;
  template_version: number;
  status: string;
  operator_id: string;
  operator_name: string;
  org_id: string;
  field_values: Record<string, any>;
  created_at: string;
}

export interface HistoryFilterParams {
  search?: string;
  template_id?: string;
  status?: string;
  date_from?: string;
  date_to?: string;
  page?: number;
  limit?: number;
  sort_by?: string;
  sort_dir?: string;
  scope?: string;
}

@Injectable({ providedIn: 'root' })
export class HistoryService {
  private readonly apiUrl = `${environment.apiBaseUrl}/submissions`;

  constructor(private http: HttpClient) {}

  getSubmissions(params: HistoryFilterParams): Observable<SubmissionListResponse> {
    let httpParams = new HttpParams();
    if (params.search) httpParams = httpParams.set('search', params.search);
    if (params.template_id) httpParams = httpParams.set('template_id', params.template_id);
    if (params.status) httpParams = httpParams.set('status', params.status);
    if (params.date_from) httpParams = httpParams.set('date_from', params.date_from);
    if (params.date_to) httpParams = httpParams.set('date_to', params.date_to);
    if (params.page) httpParams = httpParams.set('page', params.page.toString());
    if (params.limit) httpParams = httpParams.set('limit', params.limit.toString());
    if (params.sort_by) httpParams = httpParams.set('sort_by', params.sort_by);
    if (params.sort_dir) httpParams = httpParams.set('sort_dir', params.sort_dir);
    if (params.scope) httpParams = httpParams.set('scope', params.scope);

    return this.http.get<SubmissionListResponse>(this.apiUrl, { params: httpParams });
  }

  getSubmission(id: string): Observable<SubmissionDetail> {
    return this.http.get<SubmissionDetail>(`${this.apiUrl}/${id}`);
  }

  requestReprint(id: string): Observable<Blob> {
    return this.http.post(`${this.apiUrl}/${id}/reprint`, {}, {
      responseType: 'blob',
    });
  }

  exportSubmission(id: string, format: 'json' | 'csv'): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/${id}/export`, {
      params: { format },
      responseType: 'blob',
    });
  }
}
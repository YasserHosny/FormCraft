import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  GovernanceTemplateListResponse,
  BulkActionRequest,
  BulkActionResponse,
  ComplianceDashboardResponse,
  RegulatoryAlert,
} from '../../shared/models/governance.models';

@Injectable({ providedIn: 'root' })
export class TemplateGovernanceService {
  private baseUrl = `${environment.apiBaseUrl}/admin/templates`;

  constructor(private http: HttpClient) {}

  list(params: {
    page?: number;
    page_size?: number;
    status?: string;
    department_id?: string;
    designer_id?: string;
    category?: string;
    search?: string;
    sort_by?: string;
    sort_dir?: string;
  } = {}): Observable<GovernanceTemplateListResponse> {
    let httpParams = new HttpParams()
      .set('page', (params.page || 1).toString())
      .set('page_size', (params.page_size || 25).toString())
      .set('sort_by', params.sort_by || 'updated_at')
      .set('sort_dir', params.sort_dir || 'desc');

    if (params.status) httpParams = httpParams.set('status', params.status);
    if (params.department_id) httpParams = httpParams.set('department_id', params.department_id);
    if (params.designer_id) httpParams = httpParams.set('designer_id', params.designer_id);
    if (params.category) httpParams = httpParams.set('category', params.category);
    if (params.search) httpParams = httpParams.set('search', params.search);

    return this.http.get<GovernanceTemplateListResponse>(this.baseUrl, { params: httpParams });
  }

  bulkAction(request: BulkActionRequest): Observable<BulkActionResponse> {
    return this.http.post<BulkActionResponse>(`${this.baseUrl}/bulk-actions`, request);
  }

  getComplianceDashboard(): Observable<ComplianceDashboardResponse> {
    return this.http.get<ComplianceDashboardResponse>(`${this.baseUrl}/compliance`);
  }

  getRegulatoryAlerts(): Observable<RegulatoryAlert[]> {
    return this.http.get<RegulatoryAlert[]>(`${this.baseUrl}/regulatory-alerts`);
  }
}

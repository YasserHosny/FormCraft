import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import {
  BusiestHoursResponse,
  ComplianceScorecardResponse,
  DashboardFilter,
  DashboardSummaryResponse,
  DepartmentDistributionResponse,
  ExportRequest,
  ExportResponse,
  FieldAnalyticsResponse,
  OperatorAnalyticsResponse,
  SubmissionsOverTimeResponse,
  TemplatesNeedingAttentionResponse,
  TemplateUsageResponse,
  TopTemplatesResponse,
  VersionAdoptionResponse,
} from '../models/analytics.model';

@Injectable({ providedIn: 'root' })
export class AnalyticsService {
  private readonly baseUrl = '/api/analytics';

  constructor(private http: HttpClient) {}

  getFieldAnalytics(templateId: string, from?: string, to?: string): Observable<FieldAnalyticsResponse> {
    let params: any = { template_id: templateId };
    if (from) params.from = from;
    if (to) params.to = to;
    return this.http.get<FieldAnalyticsResponse>(`${this.baseUrl}/fields`, { params });
  }

  getOperatorAnalytics(periodType = 'week', from?: string, to?: string, branchId?: string): Observable<OperatorAnalyticsResponse> {
    let params: any = { period_type: periodType };
    if (from) params.from = from;
    if (to) params.to = to;
    if (branchId) params.branch_id = branchId;
    return this.http.get<OperatorAnalyticsResponse>(`${this.baseUrl}/operators`, { params });
  }

  getBusiestHours(from?: string, to?: string, branchId?: string): Observable<BusiestHoursResponse> {
    let params: any = {};
    if (from) params.from = from;
    if (to) params.to = to;
    if (branchId) params.branch_id = branchId;
    return this.http.get<BusiestHoursResponse>(`${this.baseUrl}/operators/busiest-hours`, { params });
  }

  getComplianceScorecard(): Observable<ComplianceScorecardResponse> {
    return this.http.get<ComplianceScorecardResponse>(`${this.baseUrl}/compliance`);
  }

  getTemplatesNeedingAttention(): Observable<TemplatesNeedingAttentionResponse> {
    return this.http.get<TemplatesNeedingAttentionResponse>(`${this.baseUrl}/compliance/templates-needing-attention`);
  }

  getTemplateUsage(templateId?: string, from?: string, to?: string, groupBy?: string): Observable<TemplateUsageResponse> {
    let params: any = {};
    if (templateId) params.template_id = templateId;
    if (from) params.from = from;
    if (to) params.to = to;
    if (groupBy) params.group_by = groupBy;
    return this.http.get<TemplateUsageResponse>(`${this.baseUrl}/templates/usage`, { params });
  }

  getVersionAdoption(templateId: string, from?: string, to?: string): Observable<VersionAdoptionResponse> {
    let params: any = { template_id: templateId };
    if (from) params.from = from;
    if (to) params.to = to;
    return this.http.get<VersionAdoptionResponse>(`${this.baseUrl}/templates/version-adoption`, { params });
  }

  exportReport(request: ExportRequest): Observable<ExportResponse> {
    return this.http.post<ExportResponse>(`${this.baseUrl}/export`, request);
  }

  getDashboardSummary(filter: DashboardFilter): Observable<DashboardSummaryResponse> {
    let params: any = { period: filter.period };
    if (filter.departmentId) params.department_id = filter.departmentId;
    if (filter.branchId) params.branch_id = filter.branchId;
    return this.http.get<DashboardSummaryResponse>(`${this.baseUrl}/dashboard/summary`, { params });
  }

  getSubmissionsOverTime(filter: DashboardFilter): Observable<SubmissionsOverTimeResponse> {
    let params: any = { period: filter.period };
    if (filter.departmentId) params.department_id = filter.departmentId;
    if (filter.branchId) params.branch_id = filter.branchId;
    return this.http.get<SubmissionsOverTimeResponse>(`${this.baseUrl}/dashboard/submissions-over-time`, { params });
  }

  getDepartmentDistribution(filter: Omit<DashboardFilter, 'departmentId'>): Observable<DepartmentDistributionResponse> {
    let params: any = { period: filter.period };
    if (filter.branchId) params.branch_id = filter.branchId;
    return this.http.get<DepartmentDistributionResponse>(`${this.baseUrl}/dashboard/department-distribution`, { params });
  }

  getTopTemplates(filter: DashboardFilter, limit?: number): Observable<TopTemplatesResponse> {
    let params: any = { period: filter.period };
    if (filter.departmentId) params.department_id = filter.departmentId;
    if (filter.branchId) params.branch_id = filter.branchId;
    if (limit !== undefined) params.limit = limit;
    return this.http.get<TopTemplatesResponse>(`${this.baseUrl}/dashboard/top-templates`, { params });
  }
}

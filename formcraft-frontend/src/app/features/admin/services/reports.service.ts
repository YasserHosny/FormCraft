import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';

export interface TransactionFilter {
  template_id?: string;
  date_from: string;
  date_to: string;
  branch_id?: string;
  department_id?: string;
  operator_id?: string;
  status?: string;
  customer_query?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    page_size: number;
    total_count: number;
    total_pages: number;
  };
}

export interface ExportRequest {
  filters: TransactionFilter;
  format: 'xlsx' | 'csv' | 'pdf';
}

export interface ExportSuccess {
  download_url: string;
  file_name: string;
  record_count: number;
  archive_id: string;
}

export interface ExportAsync {
  job_id: string;
  status: string;
  estimated_seconds: number;
}

export interface ExportJobStatus {
  job_id: string;
  status: 'generating' | 'completed' | 'failed';
  progress_pct: number;
  download_url: string | null;
  error: string | null;
}

export interface ReportSchedule {
  id: string;
  report_template_id: string;
  frequency: 'daily' | 'weekly' | 'monthly';
  schedule_time: string;
  day_of_week?: number;
  day_of_month?: number;
  recipients: string[];
  export_format: 'xlsx' | 'csv' | 'pdf';
  no_data_behavior: 'send_empty' | 'skip_delivery';
  is_active: boolean;
  last_run_at?: string;
  next_run_at?: string;
  last_status: 'pending' | 'success' | 'failed';
  last_error?: string;
}

export interface ReportArchive {
  id: string;
  report_type: string;
  file_name: string;
  export_format: string;
  record_count: number;
  file_size_bytes: number;
  generation_method: 'manual' | 'scheduled';
  generated_by?: string;
  created_at: string;
  download_url?: string;
}

@Injectable({
  providedIn: 'root'
})
export class ReportsService {
  private readonly apiUrl = `${environment.apiUrl}/reports`;

  constructor(private http: HttpClient) {}

  getTransactions(filter: TransactionFilter, page = 1, pageSize = 50): Observable<PaginatedResponse<any>> {
    let params = new HttpParams()
      .set('date_from', filter.date_from)
      .set('date_to', filter.date_to)
      .set('page', page.toString())
      .set('page_size', pageSize.toString());
    if (filter.template_id) params = params.set('template_id', filter.template_id);
    if (filter.branch_id) params = params.set('branch_id', filter.branch_id);
    if (filter.department_id) params = params.set('department_id', filter.department_id);
    if (filter.operator_id) params = params.set('operator_id', filter.operator_id);
    if (filter.status) params = params.set('status', filter.status);
    if (filter.customer_query) params = params.set('customer_query', filter.customer_query);
    return this.http.get<PaginatedResponse<any>>(`${this.apiUrl}/transactions`, { params });
  }

  exportTransactions(request: ExportRequest): Observable<ExportSuccess | ExportAsync> {
    return this.http.post<ExportSuccess | ExportAsync>(`${this.apiUrl}/transactions/export`, request);
  }

  getReconciliation(date: string, branchId?: string): Observable<any> {
    let params = new HttpParams().set('date', date);
    if (branchId) params = params.set('branch_id', branchId);
    return this.http.get(`${this.apiUrl}/reconciliation`, { params });
  }

  getPeriodSummary(period: string, groupBy: string, dateFrom?: string, compare = true): Observable<any> {
    let params = new HttpParams()
      .set('period', period)
      .set('group_by', groupBy)
      .set('compare', compare.toString());
    if (dateFrom) params = params.set('date_from', dateFrom);
    return this.http.get(`${this.apiUrl}/period-summary`, { params });
  }

  getJobStatus(jobId: string): Observable<ExportJobStatus> {
    return this.http.get<ExportJobStatus>(`${this.apiUrl}/jobs/${jobId}`);
  }

  getArchives(page = 1, pageSize = 50, reportType?: string): Observable<PaginatedResponse<ReportArchive>> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('page_size', pageSize.toString());
    if (reportType) params = params.set('report_type', reportType);
    return this.http.get<PaginatedResponse<ReportArchive>>(`${this.apiUrl}/archives`, { params });
  }

  getSchedules(page = 1, pageSize = 50, isActive?: boolean): Observable<PaginatedResponse<ReportSchedule>> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('page_size', pageSize.toString());
    if (isActive !== undefined) params = params.set('is_active', isActive.toString());
    return this.http.get<PaginatedResponse<ReportSchedule>>(`${this.apiUrl}/schedules`, { params });
  }

  createSchedule(schedule: Partial<ReportSchedule>): Observable<ReportSchedule> {
    return this.http.post<ReportSchedule>(`${this.apiUrl}/schedules`, schedule);
  }

  updateSchedule(id: string, schedule: Partial<ReportSchedule>): Observable<ReportSchedule> {
    return this.http.patch<ReportSchedule>(`${this.apiUrl}/schedules/${id}`, schedule);
  }

  deleteSchedule(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/schedules/${id}`);
  }

  runScheduleNow(id: string): Observable<{ job_id: string; message: string }> {
    return this.http.post<{ job_id: string; message: string }>(`${this.apiUrl}/schedules/${id}/run-now`, {});
  }

  getScheduleHistory(id: string, page = 1, pageSize = 50): Observable<PaginatedResponse<any>> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('page_size', pageSize.toString());
    return this.http.get<PaginatedResponse<any>>(`${this.apiUrl}/schedules/${id}/history`, { params });
  }

  previewCustomReport(request: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/custom/preview`, request);
  }

  saveCustomReport(request: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/custom/save`, request);
  }

  getBeneficiaryReport(dateFrom: string, dateTo: string, beneficiaryQuery?: string, templateId?: string): Observable<any> {
    let params = new HttpParams()
      .set('date_from', dateFrom)
      .set('date_to', dateTo);
    if (beneficiaryQuery) params = params.set('beneficiary_query', beneficiaryQuery);
    if (templateId) params = params.set('template_id', templateId);
    return this.http.get(`${this.apiUrl}/financial/beneficiary`, { params });
  }

  getVoidReprintReport(dateFrom: string, dateTo: string, branchId?: string, minReprintCount = 1): Observable<any> {
    let params = new HttpParams()
      .set('date_from', dateFrom)
      .set('date_to', dateTo)
      .set('min_reprint_count', minReprintCount.toString());
    if (branchId) params = params.set('branch_id', branchId);
    return this.http.get(`${this.apiUrl}/financial/void-reprint`, { params });
  }

  getSignatoryUsageReport(dateFrom: string, dateTo: string, signatoryId?: string): Observable<any> {
    let params = new HttpParams()
      .set('date_from', dateFrom)
      .set('date_to', dateTo);
    if (signatoryId) params = params.set('signatory_id', signatoryId);
    return this.http.get(`${this.apiUrl}/financial/signatory-usage`, { params });
  }
}

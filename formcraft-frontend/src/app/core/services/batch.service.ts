import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface BatchJob {
  id: string;
  name: string;
  status: string;
  template_id: string;
  template_version: number;
  data_source_type: string;
  column_mapping: Record<string, string>;
  row_count: number;
  success_count: number;
  fail_count: number;
  progress: number;
  duplicate_strategy: string;
  duplicate_count: number;
  download_format: string;
  printer_profile_id: string | null;
  scheduled_job_id: string | null;
  started_at: string | null;
  completed_at: string | null;
  cancelled_at: string | null;
  error_summary: string | null;
  created_at: string;
  updated_at: string;
}

export interface BatchJobSummary {
  id: string;
  name: string;
  status: string;
  template_name: string;
  row_count: number;
  success_count: number;
  fail_count: number;
  progress: number;
  created_at: string;
  updated_at: string;
}

export interface BatchValidationResult {
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  duplicate_rows: number;
  rows: Array<{
    row_number: number;
    status: 'valid' | 'invalid' | 'duplicate';
    field_errors: Record<string, string>;
  }>;
}

export interface BatchSchedule {
  id: string;
  name: string;
  enabled: boolean;
  template_id: string;
  template_name: string;
  cron_expression: string;
  next_run_at: string | null;
  last_run_status: string | null;
  last_run_at: string | null;
  last_run_job_id: string | null;
  failure_count: number;
  created_at: string;
  updated_at: string;
}

@Injectable({ providedIn: 'root' })
export class BatchService {
  private readonly baseUrl = '/api/batch-jobs';
  private readonly scheduleUrl = '/api/batch-schedules';

  constructor(private http: HttpClient) {}

  listJobs(status?: string, limit = 20, offset = 0): Observable<{ items: BatchJobSummary[]; total: number }> {
    let params = new HttpParams().set('limit', limit).set('offset', offset);
    if (status) params = params.set('status', status);
    return this.http.get<{ items: BatchJobSummary[]; total: number }>(this.baseUrl, { params });
  }

  getJob(id: string): Observable<BatchJob> {
    return this.http.get<BatchJob>(`${this.baseUrl}/${id}`);
  }

  createJob(formData: FormData): Observable<BatchJob> {
    return this.http.post<BatchJob>(this.baseUrl, formData);
  }

  validateJob(id: string, columnMapping: Record<string, string>, duplicateStrategy: string): Observable<BatchValidationResult> {
    return this.http.post<BatchValidationResult>(`${this.baseUrl}/${id}/validate`, {
      column_mapping: columnMapping,
      duplicate_strategy: duplicateStrategy,
    });
  }

  startJob(id: string): Observable<BatchJob> {
    return this.http.post<BatchJob>(`${this.baseUrl}/${id}/start`, {});
  }

  cancelJob(id: string): Observable<BatchJob> {
    return this.http.post<BatchJob>(`${this.baseUrl}/${id}/cancel`, {});
  }

  downloadResults(id: string, format: 'zip' | 'merged_pdf'): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/${id}/download?format=${format}`, { responseType: 'blob' });
  }

  downloadErrorReport(id: string): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/${id}/errors`, { responseType: 'blob' });
  }

  listSchedules(): Observable<BatchSchedule[]> {
    return this.http.get<BatchSchedule[]>(this.scheduleUrl);
  }

  getSchedule(id: string): Observable<BatchSchedule> {
    return this.http.get<BatchSchedule>(`${this.scheduleUrl}/${id}`);
  }

  createSchedule(payload: Partial<BatchSchedule>): Observable<BatchSchedule> {
    return this.http.post<BatchSchedule>(this.scheduleUrl, payload);
  }

  updateSchedule(id: string, payload: Partial<BatchSchedule>): Observable<BatchSchedule> {
    return this.http.put<BatchSchedule>(`${this.scheduleUrl}/${id}`, payload);
  }

  deleteSchedule(id: string): Observable<void> {
    return this.http.delete<void>(`${this.scheduleUrl}/${id}`);
  }
}

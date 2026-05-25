import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  ExportPreviewRequest,
  ExportPreviewResponse,
  ExportRequestRecord,
  ExportSchedule,
} from '../../shared/models/integration.models';

@Injectable({ providedIn: 'root' })
export class DataExportService {
  private baseUrl = `${environment.apiBaseUrl}/admin/export`;

  constructor(private http: HttpClient) {}

  preview(request: ExportPreviewRequest): Observable<ExportPreviewResponse> {
    return this.http.post<ExportPreviewResponse>(`${this.baseUrl}/preview`, request);
  }

  download(request: ExportPreviewRequest): Observable<Blob> {
    return this.http.post(`${this.baseUrl}/download`, request, { responseType: 'blob' });
  }

  listSchedules(): Observable<{ items: ExportSchedule[] }> {
    return this.http.get<{ items: ExportSchedule[] }>(`${this.baseUrl}/schedules`);
  }

  createSchedule(request: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/schedules`, request);
  }

  updateSchedule(scheduleId: string, updates: any): Observable<any> {
    return this.http.patch(`${this.baseUrl}/schedules/${scheduleId}`, updates);
  }

  runScheduleNow(scheduleId: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/schedules/${scheduleId}/run-now`, {});
  }

  listHistory(page = 1, pageSize = 25): Observable<{
    items: ExportRequestRecord[];
    total: number;
    page: number;
    page_size: number;
  }> {
    return this.http.get<{
      items: ExportRequestRecord[];
      total: number;
      page: number;
      page_size: number;
    }>(`${this.baseUrl}/history`, {
      params: { page, page_size: pageSize },
    });
  }
}

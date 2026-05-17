import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface PrinterProfile {
  id: string;
  name: string;
  description?: string;
  x_offset_mm: number;
  y_offset_mm: number;
  is_default: boolean;
  is_active: boolean;
  created_at: string;
}

@Injectable({ providedIn: 'root' })
export class PrinterProfileService {
  private baseUrl = `${environment.apiBaseUrl}/printer-profiles`;

  constructor(private http: HttpClient) {}

  list(): Observable<{ data: PrinterProfile[] }> {
    return this.http.get<{ data: PrinterProfile[] }>(this.baseUrl);
  }

  create(data: {
    name: string;
    description?: string;
    x_offset_mm?: number;
    y_offset_mm?: number;
    is_default?: boolean;
  }): Observable<PrinterProfile> {
    return this.http.post<PrinterProfile>(this.baseUrl, data);
  }

  update(id: string, data: {
    name?: string;
    description?: string;
    x_offset_mm?: number;
    y_offset_mm?: number;
  }): Observable<PrinterProfile> {
    return this.http.patch<PrinterProfile>(`${this.baseUrl}/${id}`, data);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }

  setDefault(id: string): Observable<PrinterProfile> {
    return this.http.post<PrinterProfile>(`${this.baseUrl}/${id}/set-default`, {});
  }

  downloadCalibrationPage(id: string): Observable<Blob> {
    return this.http.post(`${this.baseUrl}/${id}/calibration-page`, {}, {
      responseType: 'blob',
    });
  }
}

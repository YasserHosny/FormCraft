import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface PrintSettings {
  template_id: string;
  print_mode: 'full' | 'overlay' | 'both';
}

@Injectable({ providedIn: 'root' })
export class PrintSettingsService {
  private baseUrl = `${environment.apiBaseUrl}/templates`;

  constructor(private http: HttpClient) {}

  get(templateId: string): Observable<PrintSettings> {
    return this.http.get<PrintSettings>(`${this.baseUrl}/${templateId}/print-settings`);
  }

  update(templateId: string, printMode: string): Observable<PrintSettings> {
    return this.http.put<PrintSettings>(
      `${this.baseUrl}/${templateId}/print-settings`,
      { print_mode: printMode }
    );
  }
}

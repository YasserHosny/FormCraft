import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class TemplateVersionService {
  private baseUrl = `${environment.apiBaseUrl}/templates`;

  constructor(private http: HttpClient) {}

  transitionStatus(templateId: string, status: string, comment?: string): Observable<unknown> {
    return this.http.post(`${this.baseUrl}/${templateId}/transition`, { status, comment });
  }

  clone(templateId: string, name?: string): Observable<unknown> {
    return this.http.post(`${this.baseUrl}/${templateId}/clone`, { name });
  }

  getHistory(templateId: string): Observable<unknown> {
    return this.http.get(`${this.baseUrl}/${templateId}/history`);
  }

  getDiff(templateId: string, compareToId: string): Observable<unknown> {
    const params = new HttpParams().set('compare_to', compareToId);
    return this.http.get(`${this.baseUrl}/${templateId}/diff`, { params });
  }

  getReviews(templateId: string): Observable<unknown> {
    return this.http.get(`${this.baseUrl}/${templateId}/reviews`);
  }
}
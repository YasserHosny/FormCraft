import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class TemplateService {
  private baseUrl = `${environment.apiBaseUrl}/templates`;

  constructor(private http: HttpClient) {}

  list(params?: {
    page?: number;
    limit?: number;
    status?: string;
    category?: string;
    country?: string;
    search?: string;
  }): Observable<{ data: unknown[]; total: number; page: number; limit: number }> {
    let httpParams = new HttpParams();
    if (params?.page) httpParams = httpParams.set('page', params.page);
    if (params?.limit) httpParams = httpParams.set('limit', params.limit);
    if (params?.status) httpParams = httpParams.set('status', params.status);
    if (params?.category) httpParams = httpParams.set('category', params.category);
    if (params?.country) httpParams = httpParams.set('country', params.country);
    if (params?.search) httpParams = httpParams.set('search', params.search);
    return this.http.get<{ data: unknown[]; total: number; page: number; limit: number }>(
      this.baseUrl,
      { params: httpParams }
    );
  }

  get(id: string): Observable<unknown> {
    return this.http.get(`${this.baseUrl}/${id}`);
  }

  create(data: {
    name: string;
    description?: string;
    category?: string;
    thumbnail_asset?: string | null;
    language?: string;
    country?: string;
  }): Observable<unknown> {
    return this.http.post(this.baseUrl, data);
  }

  update(id: string, data: Record<string, unknown>): Observable<unknown> {
    return this.http.put(`${this.baseUrl}/${id}`, data);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }

  publish(id: string): Observable<unknown> {
    return this.http.post(`${this.baseUrl}/${id}/publish`, {});
  }

  addPage(templateId: string, data?: { width_mm?: number; height_mm?: number }): Observable<unknown> {
    return this.http.post(`${this.baseUrl}/${templateId}/pages`, data || {});
  }

  updatePage(pageId: string, data: Record<string, unknown>): Observable<unknown> {
    return this.http.put(`${this.baseUrl}/pages/${pageId}`, data);
  }

  deletePage(pageId: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/pages/${pageId}`);
  }

  addElement(pageId: string, data: Record<string, unknown>): Observable<unknown> {
    return this.http.post(`${this.baseUrl}/pages/${pageId}/elements`, data);
  }

  updateElement(elementId: string, data: Record<string, unknown>): Observable<unknown> {
    return this.http.put(`${this.baseUrl}/elements/${elementId}`, data);
  }

  deleteElement(elementId: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/elements/${elementId}`);
  }

  reorderPages(templateId: string, pageIds: string[]): Observable<void> {
    return this.http.put<void>(`${this.baseUrl}/${templateId}/pages/reorder`, { page_ids: pageIds });
  }

  reorderElements(pageId: string, elementIds: string[]): Observable<void> {
    return this.http.put<void>(`${this.baseUrl}/pages/${pageId}/elements/reorder`, { element_ids: elementIds });
  }

  createNewVersion(templateId: string): Observable<unknown> {
    return this.http.post(`${this.baseUrl}/${templateId}/version`, {});
  }

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

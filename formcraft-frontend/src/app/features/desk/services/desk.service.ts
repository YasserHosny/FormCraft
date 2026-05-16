import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';

export interface TemplateCard {
  id: string;
  name: string;
  description: string | null;
  category: string | null;
  status: string;
  version: number;
  language: string | null;
  country: string | null;
  updated_at: string;
  is_pinned: boolean;
}

export interface TemplatesPage {
  items: TemplateCard[];
  total: number;
  page: number;
  limit: number;
}

export interface RecentTemplate {
  template_id: string;
  template_name: string;
  category: string | null;
  version: number;
  last_used_at: string;
}

export interface PinnedTemplate {
  template_id: string;
  template_name: string;
  category: string | null;
  version: number;
  is_published: boolean;
  pinned_at: string;
}

export interface NotificationItem {
  id: string;
  template_id: string;
  template_name: string;
  old_version: number;
  new_version: number;
  updated_at: string;
}

export interface DashboardData {
  templates: TemplatesPage;
  recent: RecentTemplate[];
  pinned: PinnedTemplate[];
  drafts: any[];
  notifications: NotificationItem[];
}

export interface DashboardParams {
  search?: string;
  category?: string;
  country?: string;
  language?: string;
  page?: number;
  limit?: number;
}

@Injectable({ providedIn: 'root' })
export class DeskService {
  private readonly apiUrl = `${environment.apiBaseUrl}/desk`;

  constructor(private http: HttpClient) {}

  getDashboard(params: DashboardParams): Observable<DashboardData> {
    const queryParams: any = {};
    if (params.search) queryParams.search = params.search;
    if (params.category) queryParams.category = params.category;
    if (params.country) queryParams.country = params.country;
    if (params.language) queryParams.language = params.language;
    if (params.page) queryParams.page = params.page;
    if (params.limit) queryParams.limit = params.limit;

    return this.http.get<DashboardData>(`${this.apiUrl}/dashboard`, { params: queryParams });
  }

  pinTemplate(templateId: string): Observable<{ id: string; template_id: string; created_at: string }> {
    return this.http.post<{ id: string; template_id: string; created_at: string }>(`${this.apiUrl}/pins`, {
      template_id: templateId,
    });
  }

  unpinTemplate(templateId: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/pins/${templateId}`);
  }

  dismissNotification(notificationId: string): Observable<void> {
    return this.http.post<void>(`${this.apiUrl}/notifications/${notificationId}/dismiss`, {});
  }
}
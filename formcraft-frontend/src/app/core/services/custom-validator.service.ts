import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface CustomValidator {
  id: string;
  org_id?: string;
  name: string;
  description?: string | null;
  regex_pattern: string;
  error_message_ar: string;
  error_message_en: string;
  created_at?: string;
  updated_at?: string;
  created_by?: string;
  updated_by?: string;
}

export interface CustomValidatorListResponse {
  items: CustomValidator[];
  total: number;
  page: number;
  page_size: number;
}

export interface ValidatorTemplateUsage {
  template_id: string;
  template_name: string;
  template_status: string;
  last_submission_at: string | null;
}

export interface ValidatorTemplateUsageResponse {
  items: ValidatorTemplateUsage[];
  total: number;
  page: number;
  page_size: number;
}

export type CustomValidatorPayload = Pick<
  CustomValidator,
  'name' | 'description' | 'regex_pattern' | 'error_message_ar' | 'error_message_en'
>;

@Injectable({ providedIn: 'root' })
export class CustomValidatorService {
  private readonly adminUrl = `${environment.apiBaseUrl}/admin/validators`;
  private readonly designerUrl = `${environment.apiBaseUrl}/validators/org`;

  constructor(private http: HttpClient) {}

  list(params?: { page?: number; page_size?: number; search?: string }): Observable<CustomValidatorListResponse> {
    let httpParams = new HttpParams();
    if (params?.page) httpParams = httpParams.set('page', params.page);
    if (params?.page_size) httpParams = httpParams.set('page_size', params.page_size);
    if (params?.search) httpParams = httpParams.set('search', params.search);
    return this.http.get<CustomValidatorListResponse>(this.adminUrl, { params: httpParams });
  }

  listForDesigner(): Observable<CustomValidator[]> {
    return this.http.get<CustomValidator[]>(this.designerUrl);
  }

  create(payload: CustomValidatorPayload): Observable<CustomValidator> {
    return this.http.post<CustomValidator>(this.adminUrl, payload);
  }

  update(id: string, payload: Partial<CustomValidatorPayload>): Observable<CustomValidator> {
    return this.http.put<CustomValidator>(`${this.adminUrl}/${id}`, payload);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.adminUrl}/${id}`);
  }

  usage(id: string, page = 1, pageSize = 50): Observable<ValidatorTemplateUsageResponse> {
    const params = new HttpParams().set('page', page).set('page_size', pageSize);
    return this.http.get<ValidatorTemplateUsageResponse>(`${this.adminUrl}/${id}/templates`, { params });
  }
}

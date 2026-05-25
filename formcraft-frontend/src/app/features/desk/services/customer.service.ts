import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';
import {
  Customer,
  CustomerCreate,
  CustomerListResponse,
  CustomerSearchParams,
  CustomerUpdate,
} from './customer.models';

@Injectable({ providedIn: 'root' })
export class CustomerService {
  private baseUrl = `${environment.apiBaseUrl}/customers`;

  constructor(private http: HttpClient) {}

  list(params: CustomerSearchParams = {}): Observable<CustomerListResponse> {
    let httpParams = new HttpParams()
      .set('page', (params.page || 1).toString())
      .set('page_size', (params.page_size || 25).toString())
      .set('sort_by', params.sort_by || 'updated_at')
      .set('sort_order', params.sort_order || 'desc');

    if (params.search) httpParams = httpParams.set('search', params.search);
    if (params.is_active !== undefined) httpParams = httpParams.set('is_active', params.is_active.toString());

    return this.http.get<CustomerListResponse>(this.baseUrl, { params: httpParams });
  }

  getById(id: string): Observable<Customer> {
    return this.http.get<Customer>(`${this.baseUrl}/${id}`);
  }

  create(data: CustomerCreate): Observable<Customer> {
    return this.http.post<Customer>(this.baseUrl, data);
  }

  update(id: string, data: CustomerUpdate): Observable<Customer> {
    return this.http.patch<Customer>(`${this.baseUrl}/${id}`, data);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }

  deactivate(id: string): Observable<Customer> {
    return this.http.post<Customer>(`${this.baseUrl}/${id}/deactivate`, {});
  }

  reactivate(id: string): Observable<Customer> {
    return this.http.post<Customer>(`${this.baseUrl}/${id}/reactivate`, {});
  }

  search(query: string, page: number = 1, pageSize: number = 25): Observable<CustomerListResponse> {
    return this.list({ search: query, page, page_size: pageSize });
  }

  getRecent(limit: number = 5): Observable<Customer[]> {
    return this.http.get<Customer[]>(`${this.baseUrl}/recent`, {
      params: new HttpParams().set('limit', limit.toString()),
    });
  }

  getAutoPopulateData(customerId: string, templateId: string): Observable<{ mappings: any[] }> {
    return this.http.get<{ mappings: any[] }>(
      `${this.baseUrl}/${customerId}/auto-populate`,
      { params: new HttpParams().set('template_id', templateId) }
    );
  }

  getFieldMappings(templateId: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/field-mappings`, {
      params: new HttpParams().set('template_id', templateId),
    });
  }

  updateFieldMappings(templateId: string, mappings: any[]): Observable<any> {
    return this.http.put(`${this.baseUrl}/field-mappings`, { template_id: templateId, mappings });
  }

  getSubmissions(customerId: string, params: any = {}): Observable<any> {
    let httpParams = new HttpParams()
      .set('page', (params.page || 1).toString())
      .set('page_size', (params.page_size || 25).toString());
    if (params.template_id) httpParams = httpParams.set('template_id', params.template_id);
    if (params.date_from) httpParams = httpParams.set('date_from', params.date_from);
    if (params.date_to) httpParams = httpParams.set('date_to', params.date_to);

    return this.http.get(`${this.baseUrl}/${customerId}/submissions`, { params: httpParams });
  }
}

import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  OrganizationSummary,
  OrganizationCreate,
  OrganizationUpdate,
  OrganizationDetail,
  FirstAdminInvite,
  PlatformMetrics,
  PaginatedOrganizations,
} from '../../shared/models/platform.models';

@Injectable({ providedIn: 'root' })
export class PlatformService {
  private readonly baseUrl = `${environment.apiUrl}/platform`;

  constructor(private http: HttpClient) {}

  // Organizations

  listOrganizations(params: {
    page?: number;
    page_size?: number;
    search?: string;
    tier?: string;
    status?: string;
    country?: string;
    sort_by?: string;
    sort_order?: string;
  }): Observable<PaginatedOrganizations> {
    let httpParams = new HttpParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        httpParams = httpParams.set(key, String(value));
      }
    });
    return this.http.get<PaginatedOrganizations>(`${this.baseUrl}/organizations`, {
      params: httpParams,
    });
  }

  createOrganization(body: OrganizationCreate): Observable<OrganizationDetail> {
    return this.http.post<OrganizationDetail>(`${this.baseUrl}/organizations`, body);
  }

  getOrganization(orgId: string): Observable<OrganizationDetail> {
    return this.http.get<OrganizationDetail>(`${this.baseUrl}/organizations/${orgId}`);
  }

  updateOrganization(orgId: string, body: OrganizationUpdate): Observable<OrganizationDetail> {
    return this.http.patch<OrganizationDetail>(`${this.baseUrl}/organizations/${orgId}`, body);
  }

  deleteOrganization(orgId: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/organizations/${orgId}`);
  }

  suspendOrganization(orgId: string): Observable<OrganizationDetail> {
    return this.http.post<OrganizationDetail>(`${this.baseUrl}/organizations/${orgId}/suspend`, {});
  }

  reactivateOrganization(orgId: string): Observable<OrganizationDetail> {
    return this.http.post<OrganizationDetail>(`${this.baseUrl}/organizations/${orgId}/reactivate`, {});
  }

  inviteFirstAdmin(orgId: string, body: FirstAdminInvite): Observable<{ success: boolean; invite: unknown }> {
    return this.http.post<{ success: boolean; invite: unknown }>(
      `${this.baseUrl}/organizations/${orgId}/invite-first-admin`,
      body
    );
  }

  // Metrics

  getMetrics(): Observable<PlatformMetrics> {
    return this.http.get<PlatformMetrics>(`${this.baseUrl}/metrics`);
  }

  refreshMetrics(): Observable<{ status: string }> {
    return this.http.post<{ status: string }>(`${this.baseUrl}/metrics/refresh`, {});
  }

  // Domain uniqueness check

  checkDomainAvailable(domain: string): Observable<{ available: boolean }> {
    return this.http.get<{ available: boolean }>(`${this.baseUrl}/organizations/check-domain`, {
      params: { domain },
    });
  }
}

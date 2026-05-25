import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  PublicFormSession,
  OtpSendRequest,
  OtpSendResponse,
  OtpVerifyRequest,
  OtpVerifyResponse,
  PublicSubmissionRequest,
  PublicSubmissionResponse,
  PortalConfiguration,
  PortalTemplateListResponse,
  PortalAnalyticsResponse,
} from '../../shared/models/portal.models';

@Injectable({ providedIn: 'root' })
export class PortalService {
  private readonly baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // Public Portal

  loadPublicForm(orgSlug: string, publicSlug: string): Observable<PublicFormSession> {
    return this.http.get<PublicFormSession>(
      `${this.baseUrl}/public/forms/${orgSlug}/${publicSlug}`
    );
  }

  sendOtp(sessionToken: string, request: OtpSendRequest): Observable<OtpSendResponse> {
    return this.http.post<OtpSendResponse>(
      `${this.baseUrl}/public/forms/${sessionToken}/otp/send`,
      request
    );
  }

  verifyOtp(sessionToken: string, request: OtpVerifyRequest): Observable<OtpVerifyResponse> {
    return this.http.post<OtpVerifyResponse>(
      `${this.baseUrl}/public/forms/${sessionToken}/otp/verify`,
      request
    );
  }

  submitPublicForm(
    sessionToken: string,
    request: PublicSubmissionRequest
  ): Observable<PublicSubmissionResponse> {
    return this.http.post<PublicSubmissionResponse>(
      `${this.baseUrl}/public/forms/${sessionToken}/submit`,
      request
    );
  }

  downloadPdf(referenceNumber: string, token: string): Observable<Blob> {
    return this.http.get(
      `${this.baseUrl}/public/submissions/${referenceNumber}/pdf`,
      {
        params: { token },
        responseType: 'blob',
      }
    );
  }

  // Admin Portal

  listPortalTemplates(): Observable<PortalTemplateListResponse> {
    return this.http.get<PortalTemplateListResponse>(
      `${this.baseUrl}/admin/portal/templates`
    );
  }

  getPortalTemplate(templateId: string): Observable<PortalConfiguration> {
    return this.http.get<PortalConfiguration>(
      `${this.baseUrl}/admin/portal/templates/${templateId}`
    );
  }

  updatePortalTemplate(
    templateId: string,
    config: Partial<PortalConfiguration>
  ): Observable<PortalConfiguration> {
    return this.http.patch<PortalConfiguration>(
      `${this.baseUrl}/admin/portal/templates/${templateId}`,
      config
    );
  }

  getPortalAnalytics(
    templateId?: string,
    dateFrom?: string,
    dateTo?: string
  ): Observable<PortalAnalyticsResponse> {
    let params = new HttpParams();
    if (templateId) params = params.set('template_id', templateId);
    if (dateFrom) params = params.set('date_from', dateFrom);
    if (dateTo) params = params.set('date_to', dateTo);
    return this.http.get<PortalAnalyticsResponse>(
      `${this.baseUrl}/admin/portal/analytics`,
      { params }
    );
  }
}

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface SignatureWorkflow {
  id: string;
  name: string;
  is_ordered: boolean;
  expiration_days: number;
  decline_policy: string;
  require_all_signers: boolean;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface SignatureRequest {
  id: string;
  status: string;
  current_signer_index: number;
  expires_at: string;
  recipients: SignatureRecipient[];
  events?: SignatureEvent[];
}

export interface SignatureRecipient {
  id: string;
  signer_type: 'internal' | 'external';
  name: string;
  email?: string;
  status: string;
  signed_at?: string;
}

export interface SignatureEvent {
  event_type: string;
  created_at: string;
}

@Injectable({
  providedIn: 'root',
})
export class DigitalSignatureService {
  private readonly baseUrl = '/api/digital-signatures';

  constructor(private http: HttpClient) {}

  listWorkflows(params?: { template_id?: string; is_active?: boolean; page?: number; page_size?: number }): Observable<any> {
    return this.http.get(`${this.baseUrl}/workflows`, { params: params as any });
  }

  createWorkflow(payload: Partial<SignatureWorkflow>): Observable<any> {
    return this.http.post(`${this.baseUrl}/workflows`, payload);
  }

  updateWorkflow(id: string, payload: Partial<SignatureWorkflow>): Observable<any> {
    return this.http.patch(`${this.baseUrl}/workflows/${id}`, payload);
  }

  createRequest(payload: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/requests`, payload);
  }

  sendRequest(id: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/requests/${id}/send`, {});
  }

  listRequests(params?: { status?: string; submission_id?: string; page?: number; page_size?: number }): Observable<any> {
    return this.http.get(`${this.baseUrl}/requests`, { params: params as any });
  }

  getRequest(id: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/requests/${id}`);
  }

  cancelRequest(id: string, reason?: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/requests/${id}/cancel`, { reason });
  }

  resendInvitation(requestId: string, recipientId: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/requests/${requestId}/resend/${recipientId}`, {});
  }

  getEvidence(requestId: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/evidence/${requestId}`);
  }

  verifyEvidence(requestId: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/evidence/${requestId}/verify`, {});
  }
}

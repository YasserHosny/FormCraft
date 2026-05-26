import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  RetentionPolicy,
  RetentionJob,
  LegalHold,
  ArchiveManifest,
  PrivacyRequest,
  PreviewResult,
} from './models/retention.model';

@Injectable({ providedIn: 'root' })
export class RetentionService {
  private readonly base = '/api/retention';

  constructor(private http: HttpClient) {}

  // Policies
  listPolicies(dataClass?: string, action?: string, page = 1, pageSize = 20): Observable<any> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    if (dataClass) params = params.set('data_class', dataClass);
    if (action) params = params.set('action', action);
    return this.http.get(`${this.base}/policies`, { params });
  }

  createPolicy(body: Partial<RetentionPolicy>): Observable<RetentionPolicy> {
    return this.http.post<RetentionPolicy>(`${this.base}/policies`, body);
  }

  updatePolicy(id: string, body: Partial<RetentionPolicy>): Observable<RetentionPolicy> {
    return this.http.put<RetentionPolicy>(`${this.base}/policies/${id}`, body);
  }

  deletePolicy(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/policies/${id}`);
  }

  previewPolicy(id: string): Observable<PreviewResult> {
    return this.http.post<PreviewResult>(`${this.base}/policies/${id}/preview`, {});
  }

  // Jobs
  listJobs(policyId?: string, status?: string, page = 1, pageSize = 20): Observable<any> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    if (policyId) params = params.set('policy_id', policyId);
    if (status) params = params.set('status', status);
    return this.http.get(`${this.base}/jobs`, { params });
  }

  createJob(body: { policy_id: string; batch_size?: number }): Observable<RetentionJob> {
    return this.http.post<RetentionJob>(`${this.base}/jobs`, body);
  }

  pauseJob(id: string): Observable<RetentionJob> {
    return this.http.post<RetentionJob>(`${this.base}/jobs/${id}/pause`, {});
  }

  resumeJob(id: string): Observable<RetentionJob> {
    return this.http.post<RetentionJob>(`${this.base}/jobs/${id}/resume`, {});
  }

  // Holds
  listHolds(scopeType?: string, holdType?: string): Observable<LegalHold[]> {
    let params = new HttpParams();
    if (scopeType) params = params.set('scope_type', scopeType);
    if (holdType) params = params.set('hold_type', holdType);
    return this.http.get<LegalHold[]>(`${this.base}/holds`, { params });
  }

  createHold(body: Partial<LegalHold>): Observable<LegalHold> {
    return this.http.post<LegalHold>(`${this.base}/holds`, body);
  }

  releaseHold(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/holds/${id}`);
  }

  // Manifests
  listManifests(jobId?: string, integrityStatus?: string): Observable<ArchiveManifest[]> {
    let params = new HttpParams();
    if (jobId) params = params.set('job_id', jobId);
    if (integrityStatus) params = params.set('integrity_status', integrityStatus);
    return this.http.get<ArchiveManifest[]>(`${this.base}/manifests`, { params });
  }

  requestRestore(id: string, reason: string): Observable<any> {
    return this.http.post(`${this.base}/manifests/${id}/restore`, { reason });
  }

  // Privacy Requests
  listPrivacyRequests(status?: string, requestType?: string): Observable<PrivacyRequest[]> {
    let params = new HttpParams();
    if (status) params = params.set('status', status);
    if (requestType) params = params.set('request_type', requestType);
    return this.http.get<PrivacyRequest[]>(`${this.base}/privacy-requests`, { params });
  }

  createPrivacyRequest(body: Partial<PrivacyRequest>): Observable<PrivacyRequest> {
    return this.http.post<PrivacyRequest>(`${this.base}/privacy-requests`, body);
  }

  resolvePrivacyRequest(id: string, status: 'approved' | 'rejected', resolution?: any): Observable<PrivacyRequest> {
    return this.http.post<PrivacyRequest>(`${this.base}/privacy-requests/${id}/resolve`, { status, resolution });
  }
}

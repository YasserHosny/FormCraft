import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface OfflinePolicy {
  max_offline_age_hours: number;
  max_storage_mb: number;
  wipe_on_revocation: boolean;
}

export interface SyncPayload {
  device_id: string;
  idempotency_key: string;
  operation_type: 'draft' | 'submission' | 'attachment' | 'status_update';
  template_id: string;
  template_version: number;
  payload_digest: string;
  client_created_at: string;
  encrypted_payload: string;
}

export interface SyncConflict {
  id: string;
  conflict_type: string;
  blocking_reason: string;
  allowed_resolutions: string[];
}

export interface SyncResponse {
  operation_id: string;
  status: 'pending' | 'syncing' | 'submitted' | 'failed' | 'conflict';
  submitted_id?: string | null;
  conflicts: SyncConflict[];
}

@Injectable({ providedIn: 'root' })
export class OfflineDeskService {
  private readonly apiUrl = `${environment.apiBaseUrl}/offline-desk`;

  constructor(private http: HttpClient) {}

  registerDevice(payload: { device_fingerprint: string; display_name?: string | null; public_key: string }): Observable<{ id: string; status: string; policy: OfflinePolicy }> {
    return this.http.post<{ id: string; status: string; policy: OfflinePolicy }>(`${this.apiUrl}/devices`, payload);
  }

  getManifest(deviceId: string): Observable<{ device_id: string; expires_at: string; templates: unknown[]; policy: OfflinePolicy }> {
    return this.http.get<{ device_id: string; expires_at: string; templates: unknown[]; policy: OfflinePolicy }>(
      `${this.apiUrl}/packages/manifest`,
      { params: new HttpParams().set('device_id', deviceId) },
    );
  }

  sync(payload: SyncPayload): Observable<SyncResponse> {
    return this.http.post<SyncResponse>(`${this.apiUrl}/sync`, payload);
  }

  resolveConflict(conflictId: string, resolution: string): Observable<{ id: string; status: string; resolution: string }> {
    return this.http.post<{ id: string; status: string; resolution: string }>(`${this.apiUrl}/conflicts/${conflictId}/resolve`, { resolution });
  }
}

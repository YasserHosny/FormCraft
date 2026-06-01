import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';

export interface DraftResponse {
  id: string;
  template_id: string;
  template_version: number;
  operator_id: string;
  org_id: string;
  field_values: Record<string, any>;
  completion_percent: number;
  name: string | null;
  expires_at: string;
  created_at: string;
  updated_at: string;
}

export interface CreateDraftRequest {
  template_id: string;
  template_version: number;
  field_values: Record<string, any>;
  completion_percent?: number;
  name?: string;
}

export interface UpdateDraftRequest {
  field_values: Record<string, any>;
  completion_percent?: number;
}

@Injectable({ providedIn: 'root' })
export class DraftService {
  private readonly apiUrl = `${environment.apiBaseUrl}/desk/drafts`;

  constructor(private http: HttpClient) {}

  saveDraft(
    templateId: string,
    templateVersion: number,
    fieldValues: Record<string, any>,
    name?: string,
    completionPercent?: number,
  ): Observable<DraftResponse> {
    const body: CreateDraftRequest = {
      template_id: templateId,
      template_version: templateVersion,
      field_values: fieldValues,
    };
    if (name) {
      body.name = name;
    }
    if (completionPercent !== undefined) {
      body.completion_percent = completionPercent;
    }
    return this.http.post<DraftResponse>(this.apiUrl, body);
  }

  updateDraft(
    draftId: string,
    fieldValues: Record<string, any>,
    name?: string,
    completionPercent?: number,
  ): Observable<DraftResponse> {
    const body: UpdateDraftRequest = {
      field_values: fieldValues,
    };
    if (completionPercent !== undefined) {
      body.completion_percent = completionPercent;
    }
    return this.http.patch<DraftResponse>(`${this.apiUrl}/${draftId}`, body);
  }

  getDraft(draftId: string): Observable<DraftResponse> {
    return this.http.get<DraftResponse>(`${this.apiUrl}/${draftId}`);
  }

  listDrafts(): Observable<DraftResponse[]> {
    return this.http.get<DraftResponse[]>(this.apiUrl);
  }

  deleteDraft(draftId: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${draftId}`);
  }
}

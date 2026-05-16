import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';

export interface SubmissionResponse {
  id: string;
  reference_number: string;
  template_id: string;
  template_version: number;
  operator_id: string;
  created_at: string;
}

export interface CreateSubmissionRequest {
  template_id: string;
  template_version: number;
  field_values: Record<string, any>;
}

@Injectable({ providedIn: 'root' })
export class SubmissionService {
  private readonly apiUrl = `${environment.apiBaseUrl}/submissions`;

  constructor(private http: HttpClient) {}

  submit(templateId: string, templateVersion: number, fieldValues: Record<string, any>): Observable<SubmissionResponse> {
    const body: CreateSubmissionRequest = {
      template_id: templateId,
      template_version: templateVersion,
      field_values: fieldValues,
    };
    return this.http.post<SubmissionResponse>(this.apiUrl, body);
  }
}
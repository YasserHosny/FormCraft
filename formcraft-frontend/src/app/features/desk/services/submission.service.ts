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

export interface SignatureUploadResponse {
  type: 'storage';
  path: string;
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

  uploadSignature(submissionId: string, elementKey: string, dataUrl: string): Observable<SignatureUploadResponse> {
    const blob = this.dataUrlToBlob(dataUrl);
    const formData = new FormData();
    formData.append('file', blob, `${elementKey}.png`);
    formData.append('element_key', elementKey);
    return this.http.post<SignatureUploadResponse>(
      `${this.apiUrl}/${submissionId}/signature-upload`,
      formData
    );
  }

  getSignatureDataSize(dataUrl: string): number {
    const base64 = dataUrl.split(',')[1] || '';
    return Math.ceil(base64.length * 0.75);
  }

  private dataUrlToBlob(dataUrl: string): Blob {
    const parts = dataUrl.split(',');
    const mime = parts[0].match(/:(.*?);/)?.[1] || 'image/png';
    const byteString = atob(parts[1]);
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ab], { type: mime });
  }
}
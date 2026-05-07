import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';

export interface FeedbackSubmitRequest {
  page_url: string;
  text_content: string;
  image_url?: string | null;
  audio_url?: string | null;
}

export interface FeedbackSubmitResponse {
  id: string;
  submitted_at: string;
  status: string;
}

export interface FeedbackAdminItem {
  id: string;
  user_id: string;
  page_url: string;
  text_content: string;
  image_url: string | null;
  image_signed_url: string | null;
  audio_url: string | null;
  audio_signed_url: string | null;
  submitted_at: string;
  status: string;
  submitter_display_name: string | null;
}

export interface FeedbackAdminListResponse {
  data: FeedbackAdminItem[];
  total: number;
  page: number;
  limit: number;
}

@Injectable({ providedIn: 'root' })
export class FeedbackService {
  private baseUrl = `${environment.apiBaseUrl}/feedback`;

  constructor(private http: HttpClient) {}

  submitFeedback(payload: FeedbackSubmitRequest): Observable<FeedbackSubmitResponse> {
    return this.http.post<FeedbackSubmitResponse>(this.baseUrl, payload);
  }

  uploadImage(file: File): Observable<{ url: string }> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<{ url: string }>(`${this.baseUrl}/upload/image`, formData);
  }

  uploadAudio(file: File | Blob): Observable<{ url: string }> {
    const formData = new FormData();
    formData.append('file', file, 'audio.webm');
    return this.http.post<{ url: string }>(`${this.baseUrl}/upload/audio`, formData);
  }

  deleteUpload(url: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/upload`, { body: { url } });
  }

  listFeedback(params?: {
    page?: number;
    limit?: number;
    status?: string;
  }): Observable<FeedbackAdminListResponse> {
    let httpParams = new HttpParams();
    if (params?.page) httpParams = httpParams.set('page', params.page);
    if (params?.limit) httpParams = httpParams.set('limit', params.limit);
    if (params?.status) httpParams = httpParams.set('status', params.status);
    return this.http.get<FeedbackAdminListResponse>(`${environment.apiBaseUrl}/admin/feedback`, { params: httpParams });
  }

  updateStatus(id: string, newStatus: string): Observable<{ id: string; status: string }> {
    return this.http.patch<{ id: string; status: string }>(`${environment.apiBaseUrl}/admin/feedback/${id}`, { status: newStatus });
  }
}
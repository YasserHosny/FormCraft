import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';

export interface LabelResponse {
  id: string;
  name: string;
  colour: string | null;
  created_at: string;
}

export interface SubmitterItem {
  id: string;
  display_name: string;
}

export interface FeedbackImageSubmitItem {
  id: string;
  storage_path: string;
  display_order: number;
}

export interface FeedbackImageResponse {
  id: string;
  storage_url: string;
  display_order: number;
}

export interface FeedbackSubmitRequest {
  page_url: string;
  text_content: string;
  image_paths?: string[] | null;
  audio_url?: string | null;
  video_url?: string | null;
}

export interface FeedbackSubmitResponse {
  id: string;
  submitted_at: string;
  status: string;
  images: FeedbackImageSubmitItem[];
  audio_url: string | null;
  video_url: string | null;
}

export interface FeedbackAdminItem {
  id: string;
  user_id: string;
  page_url: string;
  text_content: string;
  images: FeedbackImageResponse[];
  audio_url: string | null;
  audio_signed_url: string | null;
  video_url: string | null;
  video_signed_url: string | null;
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

  uploadImage(file: File): Observable<{ storage_path: string }> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<{ storage_path: string }>(`${this.baseUrl}/upload/image`, formData);
  }

  uploadAudio(file: File | Blob): Observable<{ storage_path: string }> {
    const formData = new FormData();
    formData.append('file', file, 'audio.webm');
    return this.http.post<{ storage_path: string }>(`${this.baseUrl}/upload/audio`, formData);
  }

  uploadVideo(file: File | Blob): Observable<{ storage_path: string }> {
    const formData = new FormData();
    formData.append('file', file, 'video.webm');
    return this.http.post<{ storage_path: string }>(`${this.baseUrl}/upload/video`, formData);
  }

  deleteUpload(type: 'image' | 'video' | 'audio', storagePath: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/upload/${type}`, { body: { storage_path: storagePath } });
  }

  listFeedback(params?: {
    page?: number;
    limit?: number;
    status?: string;
    search?: string;
    labelIds?: string[];
  }): Observable<FeedbackAdminListResponse> {
    let httpParams = new HttpParams();
    if (params?.page) httpParams = httpParams.set('page', params.page);
    if (params?.limit) httpParams = httpParams.set('limit', params.limit);
    if (params?.status) httpParams = httpParams.set('status', params.status);
    if (params?.search) httpParams = httpParams.set('search', params.search);
    if (params?.labelIds && params.labelIds.length > 0) {
      httpParams = httpParams.set('label_ids', params.labelIds.join(','));
    }
    return this.http.get<FeedbackAdminListResponse>(`${environment.apiBaseUrl}/admin/feedback`, { params: httpParams });
  }

  updateStatus(id: string, newStatus: string): Observable<{ id: string; status: string }> {
    return this.http.patch<{ id: string; status: string }>(`${environment.apiBaseUrl}/admin/feedback/${id}`, { status: newStatus });
  }

  getLabels(): Observable<LabelResponse[]> {
    return this.http.get<LabelResponse[]>(`${environment.apiBaseUrl}/admin/labels`);
  }

  createLabel(name: string, colour: string | null): Observable<LabelResponse> {
    return this.http.post<LabelResponse>(`${environment.apiBaseUrl}/admin/labels`, { name, colour });
  }

  updateLabel(id: string, data: { name?: string; colour?: string }): Observable<LabelResponse> {
    return this.http.patch<LabelResponse>(`${environment.apiBaseUrl}/admin/labels/${id}`, data);
  }

  deleteLabel(id: string): Observable<void> {
    return this.http.delete<void>(`${environment.apiBaseUrl}/admin/labels/${id}`);
  }

  assignLabels(feedbackId: string, labelIds: string[]): Observable<void> {
    return this.http.put<void>(`${environment.apiBaseUrl}/admin/feedback/${feedbackId}/labels`, { label_ids: labelIds });
  }

  getSubmitters(): Observable<SubmitterItem[]> {
    return this.http.get<SubmitterItem[]>(`${environment.apiBaseUrl}/admin/feedback/submitters`);
  }
}
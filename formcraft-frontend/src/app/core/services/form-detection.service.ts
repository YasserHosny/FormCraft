import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { DetectionResponse } from '../../features/designer/models/detected-field.model';

@Injectable({ providedIn: 'root' })
export class FormDetectionService {
  private baseUrl = `${environment.apiBaseUrl}/forms`;

  constructor(private http: HttpClient) {}

  importForm(templateId: string, file: File, pageIndex = 0): Observable<DetectionResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('page_index', String(pageIndex));
    return this.http.post<DetectionResponse>(`${this.baseUrl}/import/${templateId}`, formData);
  }

  importFormFromPath(
    templateId: string,
    pageIndex = 0
  ): Observable<DetectionResponse> {
    return this.http.post<DetectionResponse>(`${this.baseUrl}/import/local/${templateId}`, {
      page_index: pageIndex,
    });
  }

  getLocalImportPreview(templateId: string): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/import/local/${templateId}/preview`, {
      responseType: 'blob',
    });
  }

  listDetections(templateId: string): Observable<DetectionResponse[]> {
    return this.http.get<DetectionResponse[]>(`${this.baseUrl}/${templateId}/detections`);
  }

  acceptDetections(
    templateId: string,
    detectionId: string,
    detectionIds: number[]
  ): Observable<{ message: string; created_elements: number }> {
    return this.http.post<{ message: string; created_elements: number }>(
      `${this.baseUrl}/${templateId}/detections/${detectionId}/accept`,
      { detection_ids: detectionIds }
    );
  }

  deleteDetection(detectionId: string): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.baseUrl}/detections/${detectionId}`);
  }
}

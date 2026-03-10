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
    detectionIds: number[],
    typeOverrides?: Record<number, string>
  ): Observable<{ message: string; created_elements: number }> {
    const body: { detection_ids: number[]; type_overrides?: Record<number, string> } = {
      detection_ids: detectionIds,
    };
    if (typeOverrides && Object.keys(typeOverrides).length > 0) {
      body.type_overrides = typeOverrides;
    }
    return this.http.post<{ message: string; created_elements: number }>(
      `${this.baseUrl}/${templateId}/detections/${detectionId}/accept`,
      body
    );
  }

  deleteDetection(detectionId: string): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${this.baseUrl}/detections/${detectionId}`);
  }
}

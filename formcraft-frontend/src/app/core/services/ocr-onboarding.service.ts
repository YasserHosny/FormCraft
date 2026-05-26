import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface OcrImportBatch {
  id: string;
  name: string;
  status: string;
  confidence_threshold: number;
  total_items: number;
  processed_items: number;
  accepted_items: number;
  failed_items: number;
  duplicate_items: number;
  created_at: string;
  updated_at: string;
}

export interface OcrImportItem {
  id: string;
  batch_id: string;
  file_name: string;
  status: string;
  mime_type: string;
  file_size_bytes: number;
  confidence: number | null;
  likely_type: string | null;
  category: string | null;
  language: string | null;
  page_count: number;
  retry_count: number;
  last_error: string | null;
  converted_template_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface OcrImportBatchDetail extends OcrImportBatch {
  items: OcrImportItem[];
}

@Injectable({ providedIn: 'root' })
export class OcrOnboardingService {
  private readonly baseUrl = '/api/ocr-onboarding/batches';

  constructor(private http: HttpClient) {}

  listBatches(status?: string, limit = 20, offset = 0): Observable<{ items: OcrImportBatch[]; total: number }> {
    let params = new HttpParams().set('limit', limit).set('offset', offset);
    if (status) params = params.set('status', status);
    return this.http.get<{ items: OcrImportBatch[]; total: number }>(this.baseUrl, { params });
  }

  getBatch(batchId: string): Observable<OcrImportBatchDetail> {
    return this.http.get<OcrImportBatchDetail>(`${this.baseUrl}/${batchId}`);
  }

  createBatch(name: string, confidenceThreshold: number, files: File[]): Observable<OcrImportBatch> {
    const formData = new FormData();
    formData.set('name', name);
    formData.set('confidence_threshold', String(confidenceThreshold));
    files.forEach(file => formData.append('files', file));
    return this.http.post<OcrImportBatch>(this.baseUrl, formData);
  }

  bulkAccept(batchId: string, itemIds: string[]): Observable<{ accepted_count: number; skipped: Array<{ item_id: string; reason: string }> }> {
    return this.http.post<{ accepted_count: number; skipped: Array<{ item_id: string; reason: string }> }>(
      `${this.baseUrl}/${batchId}/bulk-accept`,
      { item_ids: itemIds },
    );
  }

  decide(batchId: string, itemId: string, action: string, payload: Record<string, unknown> = {}): Observable<OcrImportItem> {
    return this.http.post<OcrImportItem>(`${this.baseUrl}/${batchId}/items/${itemId}/decision`, {
      action,
      payload,
    });
  }

  retry(batchId: string, itemId: string): Observable<OcrImportItem> {
    return this.http.post<OcrImportItem>(`${this.baseUrl}/${batchId}/items/${itemId}/retry`, {});
  }
}

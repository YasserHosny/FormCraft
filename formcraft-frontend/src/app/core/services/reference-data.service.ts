import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

export interface ColumnSchema {
  key: string;
  label_ar: string;
  label_en: string;
  type: 'text' | 'number' | 'date' | 'dropdown';
  required: boolean;
  unique_key: boolean;
  options?: string[];
}

export interface ReferenceList {
  id: string;
  name_ar: string;
  name_en: string;
  description?: string;
  columns: ColumnSchema[];
  column_count: number;
  entry_count: number;
  status: 'active' | 'archived';
  created_at: string;
  updated_at: string;
}

export interface ReferenceEntry {
  id: string;
  list_id: string;
  values: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ImportPreviewResult {
  token: string;
  valid_count: number;
  invalid_count: number;
  errors: { row: number; column: string; message: string }[];
  preview_rows: Record<string, any>[];
  csv_headers: string[];
}

@Injectable({ providedIn: 'root' })
export class ReferenceDataService {
  private baseUrl = `${environment.apiBaseUrl}/reference-lists`;

  constructor(private http: HttpClient) {}

  listLists(): Observable<ReferenceList[]> {
    return this.http.get<ReferenceList[]>(this.baseUrl);
  }

  getList(id: string): Observable<ReferenceList> {
    return this.http.get<ReferenceList>(`${this.baseUrl}/${id}`);
  }

  createList(data: Partial<ReferenceList>): Observable<ReferenceList> {
    return this.http.post<ReferenceList>(this.baseUrl, data);
  }

  updateList(id: string, data: Partial<ReferenceList>): Observable<ReferenceList> {
    return this.http.put<ReferenceList>(`${this.baseUrl}/${id}`, data);
  }

  archiveList(id: string): Observable<void> {
    return this.http.post<void>(`${this.baseUrl}/${id}/archive`, {});
  }

  unarchiveList(id: string): Observable<void> {
    return this.http.post<void>(`${this.baseUrl}/${id}/unarchive`, {});
  }

  deleteList(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }

  getEntries(listId: string, params?: { is_active?: boolean; page?: number; page_size?: number }): Observable<{ data: ReferenceEntry[]; total: number }> {
    let httpParams = new HttpParams();
    if (params) {
      if (params.is_active !== undefined) httpParams = httpParams.set('is_active', String(params.is_active));
      if (params.page !== undefined) httpParams = httpParams.set('page', String(params.page));
      if (params.page_size !== undefined) httpParams = httpParams.set('page_size', String(params.page_size));
    }
    return this.http.get<{ data: ReferenceEntry[]; total: number }>(`${this.baseUrl}/${listId}/entries`, { params: httpParams });
  }

  getEntry(listId: string, entryId: string): Observable<ReferenceEntry> {
    return this.http.get<ReferenceEntry>(`${this.baseUrl}/${listId}/entries/${entryId}`);
  }

  createEntry(listId: string, values: Record<string, any>): Observable<ReferenceEntry> {
    return this.http.post<ReferenceEntry>(`${this.baseUrl}/${listId}/entries`, { values });
  }

  updateEntry(listId: string, entryId: string, values: Record<string, any>): Observable<ReferenceEntry> {
    return this.http.put<ReferenceEntry>(`${this.baseUrl}/${listId}/entries/${entryId}`, { values });
  }

  deactivateEntry(listId: string, entryId: string): Observable<void> {
    return this.http.post<void>(`${this.baseUrl}/${listId}/entries/${entryId}/deactivate`, {});
  }

  activateEntry(listId: string, entryId: string): Observable<void> {
    return this.http.post<void>(`${this.baseUrl}/${listId}/entries/${entryId}/activate`, {});
  }

  getDropdownItems(listId: string, displayCol: string, valueCol: string, q?: string): Observable<{ display: string; value: any }[]> {
    let params = new HttpParams()
      .set('display_column', displayCol)
      .set('value_column', valueCol);
    if (q) params = params.set('q', q);
    return this.http.get<any>(`${this.baseUrl}/${listId}/entries/dropdown`, { params }).pipe(
      map((res: any) => res.items || [])
    );
  }

  importPreview(listId: string, file: File, mode: 'insert' | 'update'): Observable<ImportPreviewResult> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('mode', mode);
    return this.http.post<ImportPreviewResult>(`${this.baseUrl}/${listId}/import/preview`, formData);
  }

  importConfirm(listId: string, token: string, importValidOnly: boolean): Observable<{ imported: number; skipped: number }> {
    return this.http.post<{ imported: number; skipped: number }>(`${this.baseUrl}/${listId}/import/confirm`, { token, import_valid_only: importValidOnly });
  }
}

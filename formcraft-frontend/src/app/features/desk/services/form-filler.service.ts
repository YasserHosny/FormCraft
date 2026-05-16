import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environment';

export interface TemplateElement {
  id: string;
  key: string;
  type: string;
  label_ar: string;
  label_en: string;
  required: boolean;
  direction: string;
  sort_order: number;
  validation: any;
  formatting: any;
}

export interface TemplatePage {
  id: string;
  sort_order: number;
  width_mm: number;
  height_mm: number;
  elements: TemplateElement[];
}

export interface FillTemplate {
  id: string;
  name: string;
  version: number;
  language: string;
  country: string;
  pages: TemplatePage[];
}

@Injectable({ providedIn: 'root' })
export class FormFillerService {
  private readonly apiUrl = `${environment.apiBaseUrl}/desk`;

  constructor(private http: HttpClient) {}

  getTemplate(templateId: string): Observable<FillTemplate> {
    return this.http.get<FillTemplate>(`${this.apiUrl}/fill/${templateId}`);
  }

  getPdfUrl(templateId: string, fieldValues: Record<string, any>): Observable<Blob> {
    return this.http.post(`${environment.apiBaseUrl}/pdf/render/${templateId}`, { field_values: fieldValues }, {
      responseType: 'blob',
    });
  }
}
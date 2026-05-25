import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface MappedField {
  field_key: string;
  field_label: string;
  value: string;
  source_attribute: string;
  confidence: string;
}

export interface QuickFillMapResponse {
  customer_id: string;
  template_id: string;
  mapped_fields: MappedField[];
  unmapped_customer_attributes: string[];
  mapping_count: number;
}

export interface QuickFillCustomer {
  id: string;
  name_ar: string | null;
  name_en: string | null;
  identifier: string;
  contact_phone: string | null;
  recent_submissions_count: number;
  match_score: number;
}

export interface QuickFillCustomerSearchResponse {
  query: string;
  customers: QuickFillCustomer[];
}

@Injectable({ providedIn: 'root' })
export class QuickFillService {
  private baseUrl = `${environment.apiBaseUrl}/quickfill`;

  constructor(private http: HttpClient) {}

  searchCustomers(query: string, limit: number = 10): Observable<QuickFillCustomerSearchResponse> {
    const params = new HttpParams().set('q', query).set('limit', limit.toString());
    return this.http.get<QuickFillCustomerSearchResponse>(`${this.baseUrl}/customers`, { params });
  }

  mapCustomerToFields(customerId: string, templateId: string): Observable<QuickFillMapResponse> {
    return this.http.post<QuickFillMapResponse>(`${this.baseUrl}/map`, {
      customer_id: customerId,
      template_id: templateId,
    });
  }

  autoFill(
    formValues: Record<string, unknown>,
    mappedFields: MappedField[]
  ): Record<string, unknown> {
    const updated = { ...formValues };
    for (const field of mappedFields) {
      updated[field.field_key] = field.value;
    }
    return updated;
  }

  markAutoFilled(fields: { key: string }[]): string[] {
    return fields.map((f) => f.key);
  }

  saveToProfile(customerId: string, updates: Record<string, unknown>): Observable<unknown> {
    return this.http.patch(`${environment.apiBaseUrl}/customers/${customerId}`, updates);
  }
}

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '@environments/environment';

export interface TafqeetPreviewRequest {
  amount: number;
  currency_code: 'EGP' | 'SAR' | 'AED' | 'USD';
  language: 'ar' | 'en' | 'both';
  show_currency: boolean;
  prefix: 'none' | 'faqat';
  suffix: 'none' | 'la_ghair' | 'faqat_la_ghair' | 'only';
}

export interface TafqeetPreviewResponse {
  result: string | null;
}

@Injectable({ providedIn: 'root' })
export class TafqeetService {
  private readonly url = `${environment.apiUrl}/tafqeet/preview`;

  constructor(private http: HttpClient) {}

  preview(req: TafqeetPreviewRequest): Observable<TafqeetPreviewResponse> {
    return this.http.post<TafqeetPreviewResponse>(this.url, req);
  }
}

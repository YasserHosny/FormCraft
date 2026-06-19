import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  BillingOptionsResponse,
  BillingPurchase,
  BillingPurchaseCreateRequest,
  BillingPurchaseCreateResponse,
  BillingPurchaseListResponse,
  BillingPurchaseVerifyResponse,
  BillingPurpose,
  BillingRefundResponse,
} from '../../shared/models/billing.models';

@Injectable({ providedIn: 'root' })
export class BillingService {
  private readonly baseUrl = `${environment.apiBaseUrl}/billing`;
  private readonly platformBaseUrl = `${environment.apiBaseUrl}/platform/billing`;

  constructor(private http: HttpClient) {}

  getOptions(purpose?: BillingPurpose, listingId?: string): Observable<BillingOptionsResponse> {
    let params = new HttpParams();
    if (purpose) params = params.set('purpose', purpose);
    if (listingId) params = params.set('listing_id', listingId);
    return this.http.get<BillingOptionsResponse>(`${this.baseUrl}/options`, { params });
  }

  createPurchase(body: BillingPurchaseCreateRequest): Observable<BillingPurchaseCreateResponse> {
    return this.http.post<BillingPurchaseCreateResponse>(`${this.baseUrl}/purchases`, body);
  }

  verifyPurchase(purchaseId: string, providerPaymentId?: string): Observable<BillingPurchaseVerifyResponse> {
    return this.http.post<BillingPurchaseVerifyResponse>(`${this.baseUrl}/purchases/${purchaseId}/verify`, {
      provider_payment_id: providerPaymentId || null,
    });
  }

  getPurchase(purchaseId: string): Observable<BillingPurchase> {
    return this.http.get<BillingPurchase>(`${this.baseUrl}/purchases/${purchaseId}`);
  }

  listPurchases(filters?: {
    organization_id?: string;
    status?: string;
    purpose?: BillingPurpose;
    limit?: number;
  }): Observable<BillingPurchaseListResponse> {
    let params = new HttpParams();
    Object.entries(filters || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params = params.set(key, String(value));
      }
    });
    return this.http.get<BillingPurchaseListResponse>(`${this.baseUrl}/purchases`, { params });
  }

  refundPurchase(purchaseId: string, reason: string): Observable<BillingRefundResponse> {
    return this.http.post<BillingRefundResponse>(
      `${this.platformBaseUrl}/purchases/${purchaseId}/refund`,
      { reason }
    );
  }
}

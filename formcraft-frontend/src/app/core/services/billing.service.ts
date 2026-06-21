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
  CancelSubscriptionResponse,
  CreateSubscriptionRequest,
  CreateSubscriptionResponse,
  DowngradeScheduleResponse,
  PortalUrlResponse,
  ReactivateSubscriptionResponse,
  ScheduleDowngradeRequest,
  SubscriptionResponse,
  UpgradeSubscriptionRequest,
  UpgradeSubscriptionResponse,
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

  // F059 — Subscription methods
  private readonly subsUrl = `${environment.apiBaseUrl}/billing/subscriptions`;

  getCurrentSubscription(): Observable<SubscriptionResponse> {
    return this.http.get<SubscriptionResponse>(`${this.subsUrl}/current`);
  }

  createSubscription(req: CreateSubscriptionRequest): Observable<CreateSubscriptionResponse> {
    return this.http.post<CreateSubscriptionResponse>(this.subsUrl, req);
  }

  upgradeSubscription(req: UpgradeSubscriptionRequest): Observable<UpgradeSubscriptionResponse> {
    return this.http.post<UpgradeSubscriptionResponse>(`${this.subsUrl}/upgrade`, req);
  }

  scheduleDowngrade(req: ScheduleDowngradeRequest): Observable<DowngradeScheduleResponse> {
    return this.http.post<DowngradeScheduleResponse>(`${this.subsUrl}/downgrade-schedule`, req);
  }

  cancelDowngradeSchedule(): Observable<DowngradeScheduleResponse> {
    return this.http.delete<DowngradeScheduleResponse>(`${this.subsUrl}/downgrade-schedule`);
  }

  cancelSubscription(): Observable<CancelSubscriptionResponse> {
    return this.http.post<CancelSubscriptionResponse>(`${this.subsUrl}/cancel`, {});
  }

  reactivateSubscription(): Observable<ReactivateSubscriptionResponse> {
    return this.http.post<ReactivateSubscriptionResponse>(`${this.subsUrl}/reactivate`, {});
  }

  getPortalUrl(returnUrl: string): Observable<PortalUrlResponse> {
    return this.http.post<PortalUrlResponse>(`${this.subsUrl}/portal-url`, { return_url: returnUrl });
  }
}

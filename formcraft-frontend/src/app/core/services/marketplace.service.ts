import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  MarketplaceImportResponse,
  MarketplaceListResponse,
  MarketplaceListing,
  MarketplaceListingDetail,
  MarketplaceReview,
  MarketplaceTransactionResponse,
} from '../../shared/models/marketplace.models';

@Injectable({ providedIn: 'root' })
export class MarketplaceService {
  private baseUrl = `${environment.apiBaseUrl}/marketplace`;

  constructor(private http: HttpClient) {}

  list(params?: {
    search?: string;
    country?: string;
    category?: string;
    language?: string;
    compliance?: string;
    price_type?: string;
    sort_by?: string;
    sort_dir?: string;
    page?: number;
    page_size?: number;
  }): Observable<MarketplaceListResponse> {
    let httpParams = new HttpParams();
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        httpParams = httpParams.set(key, String(value));
      }
    });
    return this.http.get<MarketplaceListResponse>(`${this.baseUrl}/listings`, {
      params: httpParams,
    });
  }

  get(id: string): Observable<MarketplaceListingDetail> {
    return this.http.get<MarketplaceListingDetail>(`${this.baseUrl}/listings/${id}`);
  }

  publish(body: {
    template_id: string;
    description: string;
    tags: string[];
    preview_image_urls: string[];
    compliance_badges: string[];
    price_type: string;
    price_amount?: number | null;
    currency: string;
  }): Observable<MarketplaceListing> {
    return this.http.post<MarketplaceListing>(`${this.baseUrl}/listings`, body);
  }

  purchase(id: string): Observable<MarketplaceTransactionResponse> {
    return this.http.post<MarketplaceTransactionResponse>(
      `${this.baseUrl}/listings/${id}/purchase`,
      { provider: 'internal' }
    );
  }

  importListing(
    id: string,
    body: {
      draft_name?: string;
      reference_mappings?: Record<string, string>;
      accept_disabled_dependencies?: boolean;
    }
  ): Observable<MarketplaceImportResponse> {
    return this.http.post<MarketplaceImportResponse>(
      `${this.baseUrl}/listings/${id}/import`,
      body
    );
  }

  review(
    id: string,
    body: { import_id: string; rating: number; review_text: string }
  ): Observable<MarketplaceReview> {
    return this.http.post<MarketplaceReview>(`${this.baseUrl}/listings/${id}/reviews`, body);
  }

  listReviews(id: string): Observable<{ items: MarketplaceReview[]; total: number }> {
    return this.http.get<{ items: MarketplaceReview[]; total: number }>(
      `${this.baseUrl}/listings/${id}/reviews`
    );
  }
}

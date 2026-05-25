import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  IntegrationCredential,
  IntegrationCredentialCreated,
  WebhookDelivery,
  WebhookSubscription,
} from '../../shared/models/integration.models';

@Injectable({ providedIn: 'root' })
export class IntegrationService {
  private baseUrl = `${environment.apiBaseUrl}/admin/integrations`;

  constructor(private http: HttpClient) {}

  listCredentials(): Observable<{ items: IntegrationCredential[] }> {
    return this.http.get<{ items: IntegrationCredential[] }>(`${this.baseUrl}/credentials`);
  }

  createCredential(request: {
    name: string;
    scopes: string[];
    expires_at?: string | null;
  }): Observable<IntegrationCredentialCreated> {
    return this.http.post<IntegrationCredentialCreated>(`${this.baseUrl}/credentials`, request);
  }

  listWebhooks(): Observable<{ items: WebhookSubscription[] }> {
    return this.http.get<{ items: WebhookSubscription[] }>(`${this.baseUrl}/webhooks`);
  }

  revokeCredential(credentialId: string): Observable<any> {
    return this.http.patch(`${this.baseUrl}/credentials/${credentialId}/revoke`, {});
  }

  listWebhookDeliveries(webhookId: string): Observable<{ items: WebhookDelivery[] }> {
    return this.http.get<{ items: WebhookDelivery[] }>(
      `${this.baseUrl}/webhooks/${webhookId}/deliveries`,
    );
  }

  updateWebhook(webhookId: string, updates: any): Observable<any> {
    return this.http.patch(`${this.baseUrl}/webhooks/${webhookId}`, updates);
  }
}

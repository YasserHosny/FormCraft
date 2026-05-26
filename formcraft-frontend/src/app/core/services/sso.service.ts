import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface IdentityProvider {
  id: string;
  org_id: string;
  name: string;
  provider_type: 'saml' | 'oidc';
  domains: string[];
  is_active: boolean;
  last_validated_at?: string;
}

export interface IdentityProviderCreate {
  name: string;
  provider_type: 'saml' | 'oidc';
  domains: string[];
  metadata_url?: string;
  metadata_xml?: string;
  client_id?: string;
  client_secret?: string;
  signing_cert?: string;
}

@Injectable({ providedIn: 'root' })
export class SsoService {
  private readonly api = '/api/v1/sso';

  constructor(private http: HttpClient) {}

  getProviders(): Observable<{ items: IdentityProvider[] }> {
    return this.http.get<{ items: IdentityProvider[] }>(`${this.api}/providers`);
  }

  createProvider(payload: IdentityProviderCreate): Observable<IdentityProvider> {
    return this.http.post<IdentityProvider>(`${this.api}/providers`, payload);
  }

  deleteProvider(id: string): Observable<void> {
    return this.http.delete<void>(`${this.api}/providers/${id}`);
  }

  startSamlLogin(providerId: string): Observable<{ redirect_url: string }> {
    return this.http.get<{ redirect_url: string }>(`${this.api}/saml/login`, {
      params: { provider_id: providerId },
    });
  }

  startOidcLogin(providerId: string): Observable<{ redirect_url: string }> {
    return this.http.get<{ redirect_url: string }>(`${this.api}/oidc/login`, {
      params: { provider_id: providerId },
    });
  }
}

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface User {
  id: string;
  email: string;
  role: 'admin' | 'designer' | 'operator' | 'viewer' | 'branch_manager';
  language: 'ar' | 'en';
  display_name: string | null;
  org_id?: string;
  is_platform_admin?: boolean;
}

interface LoginResponse {
  access_token?: string;
  refresh_token?: string;
  token_type?: string;
  expires_in?: number;
  requires_org_selection?: boolean;
  organizations?: { id: string; name_en: string; name_ar: string; logo_url: string | null }[];
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  currentUser$ = this.currentUserSubject.asObservable();

  private isAuthenticatedSubject = new BehaviorSubject<boolean>(false);
  // Expose BehaviorSubject (not wrapped) so callers can read .value synchronously.
  // BehaviorSubject extends Observable, so .pipe()/.subscribe() still work everywhere.
  isAuthenticated$ = this.isAuthenticatedSubject;

  constructor(private http: HttpClient) {
    const token = this.getToken();
    if (token) {
      this.isAuthenticatedSubject.next(true);
      // Defer the HTTP call so the DI graph is fully resolved before HttpClient
      // tries to instantiate HTTP_INTERCEPTORS (which depend on AuthService).
      queueMicrotask(() => this.loadProfile());
    }
  }

  login(email: string, password: string): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(`${environment.apiBaseUrl}/auth/login`, {
        email,
        password,
      })
      .pipe(
        tap((response) => {
          if (response.requires_org_selection) {
            return;
          }
          if (response.access_token) {
            localStorage.setItem('access_token', response.access_token);
            localStorage.setItem('refresh_token', response.refresh_token || '');
            this.isAuthenticatedSubject.next(true);
            this.loadProfile();
          }
        })
      );
  }

  selectOrg(orgId: string): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(`${environment.apiBaseUrl}/auth/login/select-org`, { org_id: orgId })
      .pipe(
        tap((response) => {
          if (response.access_token) {
            localStorage.setItem('access_token', response.access_token);
            localStorage.setItem('refresh_token', response.refresh_token || '');
            this.isAuthenticatedSubject.next(true);
            this.loadProfile();
          }
        })
      );
  }

  logout(): void {
    this.http.post(`${environment.apiBaseUrl}/auth/logout`, {}).subscribe({
      complete: () => this.clearSession(),
      error: () => this.clearSession(),
    });
  }

  refresh(): Observable<LoginResponse> {
    const refreshToken = localStorage.getItem('refresh_token') || '';
    return this.http
      .post<LoginResponse>(`${environment.apiBaseUrl}/auth/refresh`, {
        refresh_token: refreshToken,
      })
      .pipe(
        tap((response) => {
          if (response.access_token) {
            localStorage.setItem('access_token', response.access_token);
          }
          if (response.refresh_token) {
            localStorage.setItem('refresh_token', response.refresh_token);
          }
        })
      );
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  private loadProfile(): void {
    this.http
      .get<User>(`${environment.apiBaseUrl}/users/me`)
      .subscribe({
        next: (user) => this.currentUserSubject.next(user),
        error: () => this.clearSession(),
      });
  }

  /**
   * Immediately clears the local session without making an HTTP call.
   * Used by the auth interceptor when the server returns 401 so we don't
   * trigger another HTTP request (which would also 401 and loop).
   */
  forceLogout(): void {
    this.clearSession();
  }

  private clearSession(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.currentUserSubject.next(null);
    this.isAuthenticatedSubject.next(false);
  }
}

import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ModeConfig, MODES, ROLE_DEFAULT_MODE } from './mode.config';

@Injectable({ providedIn: 'root' })
export class ModeService {
  private activeModeSubject = new BehaviorSubject<string | null>(null);
  activeMode$ = this.activeModeSubject.asObservable();

  constructor(private router: Router, private http: HttpClient) {}

  getPermittedModes(role: string): ModeConfig[] {
    return MODES.filter((mode) => mode.permittedRoles.includes(role));
  }

  getActiveMode(url: string): ModeConfig | null {
    const matching = MODES.find((mode) => url.startsWith(mode.routePrefix));
    return matching || null;
  }

  getDefaultMode(role: string, preferredMode: string | null): ModeConfig {
    if (preferredMode) {
      const preferred = MODES.find((m) => m.id === preferredMode);
      if (preferred && preferred.permittedRoles.includes(role)) {
        return preferred;
      }
    }
    const defaultId = ROLE_DEFAULT_MODE[role] || 'desk';
    return MODES.find((m) => m.id === defaultId)!;
  }

  savePreference(mode: string): void {
    this.http
      .put(`${environment.apiBaseUrl}/users/me`, { preferred_mode: mode })
      .subscribe({
        next: () => this.activeModeSubject.next(mode),
        error: () => {},
      });
  }

  setActiveMode(modeId: string): void {
    this.activeModeSubject.next(modeId);
  }
}
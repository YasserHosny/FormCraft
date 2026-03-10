import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Subject, of } from 'rxjs';
import { catchError, debounceTime, distinctUntilChanged, switchMap } from 'rxjs/operators';
import { environment } from '../../../../environments/environment';

export interface SuggestionRequest {
  label: string;
  language: 'ar' | 'en';
  country: 'EG' | 'SA' | 'AE';
  context?: string;
}

export interface SuggestionResponse {
  control_type: string;
  confidence: number;
  validation: Record<string, unknown>;
  formatting: Record<string, unknown>;
  direction: string;
  source: 'deterministic' | 'llm' | 'fallback';
}

@Injectable({ providedIn: 'root' })
export class AiSuggestionService {
  private labelSubject = new Subject<SuggestionRequest>();
  suggestion$: Observable<SuggestionResponse | null>;

  constructor(private http: HttpClient) {
    this.suggestion$ = this.labelSubject.pipe(
      debounceTime(300),
      distinctUntilChanged((prev, curr) => prev.label === curr.label),
      switchMap((request) => this.fetchSuggestion(request)),
    );
  }

  requestSuggestion(request: SuggestionRequest): void {
    if (request.label.trim().length > 0) {
      this.labelSubject.next(request);
    }
  }

  private fetchSuggestion(request: SuggestionRequest): Observable<SuggestionResponse | null> {
    return this.http
      .post<SuggestionResponse>(`${environment.apiBaseUrl}/ai/suggest-control`, request)
      .pipe(
        catchError(() => of(null)),
      );
  }
}

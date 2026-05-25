import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { debounceTime, distinctUntilChanged, switchMap, catchError } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

export interface SearchResult {
  type: 'template' | 'submission' | 'customer';
  id: string;
  title: string;
  subtitle: string;
  metadata: Record<string, unknown>;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
}

export interface ReferenceSearchResponse {
  found: boolean;
  submission: {
    id: string;
    reference_number: string;
    template_name: string;
    customer_name: string;
    status: string;
    created_at: string;
  } | null;
}

@Injectable({ providedIn: 'root' })
export class SearchService {
  private baseUrl = `${environment.apiBaseUrl}/search`;

  constructor(private http: HttpClient) {}

  search(query: string, types?: string[], limit: number = 5): Observable<SearchResponse> {
    let params = new HttpParams().set('q', query).set('limit', limit.toString());
    if (types && types.length) {
      params = params.set('types', types.join(','));
    }
    return this.http.get<SearchResponse>(this.baseUrl, { params });
  }

  searchByReference(ref: string): Observable<ReferenceSearchResponse> {
    const params = new HttpParams().set('ref', ref);
    return this.http.get<ReferenceSearchResponse>(`${this.baseUrl}/reference`, { params });
  }

  createSearchObservable$(query$: Observable<string>, debounceMs: number = 200): Observable<SearchResponse> {
    return query$.pipe(
      debounceTime(debounceMs),
      distinctUntilChanged(),
      switchMap((q) => {
        if (!q || q.length < 2) {
          return of({ query: q, results: [] });
        }
        return this.search(q).pipe(
          catchError(() => of({ query: q, results: [] }))
        );
      })
    );
  }

  getRecentSearches(): string[] {
    try {
      const raw = localStorage.getItem('fc_recent_searches');
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  }

  addRecentSearch(query: string): void {
    if (!query || query.length < 2) return;
    const recent = this.getRecentSearches();
    const updated = [query, ...recent.filter((q) => q !== query)].slice(0, 10);
    localStorage.setItem('fc_recent_searches', JSON.stringify(updated));
  }
}

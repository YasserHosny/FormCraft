import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { debounceTime, switchMap, catchError, map } from 'rxjs/operators';
import { TafqeetService, TafqeetPreviewRequest, TafqeetPreviewResponse } from '../../designer/services/tafqeet.service';

export interface TafqeetSourceMapping {
  tafqeetKey: string;
  sourceKey: string;
  formatting: {
    currency_code: 'EGP' | 'SAR' | 'AED' | 'USD';
    language: 'ar' | 'en' | 'both';
    show_currency: boolean;
    prefix: 'none' | 'faqat';
    suffix: 'none' | 'la_ghair' | 'faqat_la_ghair' | 'only';
  };
}

@Injectable({ providedIn: 'root' })
export class FillerTafqeetService {
  private debounceMs = 200;

  constructor(private tafqeetService: TafqeetService) {}

  compute(amount: number, formatting: TafqeetSourceMapping['formatting']): Observable<string | null> {
    if (amount === null || amount === undefined || isNaN(amount)) {
      return of(null);
    }

    const req: TafqeetPreviewRequest = {
      amount,
      currency_code: formatting.currency_code || 'SAR',
      language: formatting.language || 'ar',
      show_currency: formatting.show_currency !== undefined ? formatting.show_currency : true,
      prefix: formatting.prefix || 'none',
      suffix: formatting.suffix || 'la_ghair',
    };

    return this.tafqeetService.preview(req).pipe(
      map((res: TafqeetPreviewResponse) => res.result),
      catchError(() => of(null)),
    );
  }
}
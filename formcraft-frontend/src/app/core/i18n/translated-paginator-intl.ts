import { Injectable, OnDestroy } from '@angular/core';
import { MatPaginatorIntl } from '@angular/material/paginator';
import { TranslateService } from '@ngx-translate/core';
import { Subject, takeUntil } from 'rxjs';

@Injectable()
export class TranslatedPaginatorIntl extends MatPaginatorIntl implements OnDestroy {
  private readonly destroy$ = new Subject<void>();

  constructor(private translate: TranslateService) {
    super();
    this.getRangeLabel = (page: number, pageSize: number, length: number) => {
      if (length === 0 || pageSize === 0) {
        return this.translate.instant('paginator.range_empty', { length });
      }

      const startIndex = page * pageSize;
      const endIndex = Math.min(startIndex + pageSize, length);
      return this.translate.instant('paginator.range', {
        start: startIndex + 1,
        end: endIndex,
        length,
      });
    };

    this.updateLabels();
    this.translate.onLangChange
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => this.updateLabels());
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private updateLabels(): void {
    this.translate.get([
      'paginator.items_per_page',
      'paginator.next_page',
      'paginator.previous_page',
      'paginator.first_page',
      'paginator.last_page',
    ]).subscribe((labels) => {
      this.itemsPerPageLabel = labels['paginator.items_per_page'];
      this.nextPageLabel = labels['paginator.next_page'];
      this.previousPageLabel = labels['paginator.previous_page'];
      this.firstPageLabel = labels['paginator.first_page'];
      this.lastPageLabel = labels['paginator.last_page'];
      this.changes.next();
    });
  }
}

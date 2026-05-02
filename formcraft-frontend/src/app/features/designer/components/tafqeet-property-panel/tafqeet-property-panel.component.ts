import { Component, Input, OnChanges, OnDestroy, SimpleChanges } from '@angular/core';
import { Subject, Subscription } from 'rxjs';
import { debounceTime, switchMap, catchError } from 'rxjs/operators';
import { of } from 'rxjs';
import { CanvasElement, CanvasService } from '../../services/canvas.service';
import { TafqeetService, TafqeetPreviewRequest } from '../../services/tafqeet.service';

const PX_PER_MM = 96 / 25.4; // 96 DPI

@Component({
  selector: 'fc-tafqeet-property-panel',
  standalone: false,
  templateUrl: './tafqeet-property-panel.component.html',
  styleUrls: ['./tafqeet-property-panel.component.scss'],
})
export class TafqeetPropertyPanelComponent implements OnChanges, OnDestroy {
  @Input() element!: CanvasElement;
  @Input() pageElements: Record<string, unknown>[] = [];

  overflowWarning = false;
  negativeWarning = false;
  validationError: string | null = null;

  private previewSubject$ = new Subject<TafqeetPreviewRequest | null>();
  private subs: Subscription[] = [];

  constructor(
    private canvasService: CanvasService,
    private tafqeetService: TafqeetService,
  ) {
    // Debounced preview pipeline (300ms debounce, <200ms API = <500ms total)
    this.subs.push(
      this.previewSubject$.pipe(
        debounceTime(300),
        switchMap((req) => {
          if (!req) return of({ result: null });
          return this.tafqeetService.preview(req).pipe(
            catchError(() => of({ result: null }))
          );
        }),
      ).subscribe((response) => {
        if (!this.element) return;
        this.canvasService.updateTafqeetPreview(this.element.id, response.result);
        this.checkOverflow(response.result);
      })
    );
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['element'] && this.element) {
      // Trigger a preview refresh when element selection changes (if previewValue is set)
      const previewValue = this.fmt['previewValue'] as number | null;
      if (previewValue != null && !isNaN(previewValue)) {
        this.triggerPreview(previewValue);
      }
    }
  }

  ngOnDestroy(): void {
    this.subs.forEach((s) => s.unsubscribe());
  }

  // ---------------------------------------------------------------------------
  // Formatting accessors
  // ---------------------------------------------------------------------------

  get fmt(): Record<string, unknown> {
    return (this.element?.data['formatting'] as Record<string, unknown>) || {};
  }

  get sourceElementKey(): string | null {
    return (this.fmt['sourceElementKey'] as string) || null;
  }

  get currencyCode(): 'EGP' | 'SAR' | 'AED' | 'USD' {
    return (this.fmt['currencyCode'] as 'EGP' | 'SAR' | 'AED' | 'USD') || 'EGP';
  }

  get outputLanguage(): 'ar' | 'en' | 'both' {
    return (this.fmt['outputLanguage'] as 'ar' | 'en' | 'both') || 'ar';
  }

  get showCurrency(): boolean {
    return this.fmt['showCurrency'] !== false;
  }

  get prefix(): 'none' | 'faqat' {
    return (this.fmt['prefix'] as 'none' | 'faqat') || 'none';
  }

  get suffix(): 'none' | 'la_ghair' | 'faqat_la_ghair' | 'only' {
    return (this.fmt['suffix'] as 'none' | 'la_ghair' | 'faqat_la_ghair' | 'only') || 'none';
  }

  get previewValue(): number | null {
    const v = this.fmt['previewValue'];
    return v != null ? Number(v) : null;
  }

  // ---------------------------------------------------------------------------
  // Source element picker — filtered to number/currency elements
  // ---------------------------------------------------------------------------

  get sourceElements(): Record<string, unknown>[] {
    return this.pageElements
      .filter((el) => (el['type'] === 'number' || el['type'] === 'currency') && el['id'] !== this.element?.id)
      .sort((a, b) => String(a['label_ar'] || a['key']).localeCompare(String(b['label_ar'] || b['key'])));
  }

  onSourceElementChange(key: string | null): void {
    const sourceEl = this.pageElements.find((el) => el['key'] === key);
    const newCurrencyCode = sourceEl?.['type'] === 'currency'
      ? ((sourceEl['formatting'] as Record<string, unknown>)?.['currencyCode'] as string || 'EGP')
      : this.currencyCode;

    this.updateFormatting({ sourceElementKey: key, currencyCode: newCurrencyCode });
    this.triggerPreviewIfReady();
  }

  // ---------------------------------------------------------------------------
  // Preview value input
  // ---------------------------------------------------------------------------

  onPreviewValueChange(value: string): void {
    const num = parseFloat(value);
    if (value === '' || value == null) {
      this.updateFormatting({ previewValue: null });
      this.canvasService.updateTafqeetPreview(this.element.id, null);
      this.negativeWarning = false;
      this.overflowWarning = false;
      return;
    }
    if (isNaN(num)) return;

    // Negative values: show warning, skip API call (FR-007 / US7)
    if (num < 0) {
      this.negativeWarning = true;
      this.overflowWarning = false;
      this.canvasService.updateTafqeetPreview(this.element.id, null);
      return;
    }
    this.negativeWarning = false;
    this.updateFormatting({ previewValue: num });
    this.triggerPreview(num);
  }

  // ---------------------------------------------------------------------------
  // Language / currency controls
  // ---------------------------------------------------------------------------

  onOutputLanguageChange(lang: 'ar' | 'en' | 'both'): void {
    this.updateFormatting({ outputLanguage: lang });
    // Guard: suffix "only" is invalid for ar/both — reset to none
    if (lang !== 'en' && this.suffix === 'only') {
      this.updateFormatting({ suffix: 'none' });
    }
    this.triggerPreviewIfReady();
  }

  onShowCurrencyChange(checked: boolean): void {
    this.updateFormatting({ showCurrency: checked });
    this.triggerPreviewIfReady();
  }

  onPrefixChange(value: 'none' | 'faqat'): void {
    this.updateFormatting({ prefix: value });
    this.triggerPreviewIfReady();
  }

  onSuffixChange(value: 'none' | 'la_ghair' | 'faqat_la_ghair' | 'only'): void {
    this.updateFormatting({ suffix: value });
    this.triggerPreviewIfReady();
  }

  /** Whether suffix "Only" should be disabled (only valid for English output) */
  isSuffixOnlyDisabled(): boolean {
    return this.outputLanguage === 'ar';
  }

  // ---------------------------------------------------------------------------
  // Internal helpers
  // ---------------------------------------------------------------------------

  private updateFormatting(patch: Record<string, unknown>): void {
    this.canvasService.updateElementFormatting(this.element.id, patch);
  }

  private triggerPreviewIfReady(): void {
    const v = this.previewValue;
    if (v != null && !isNaN(v) && v >= 0) {
      this.triggerPreview(v);
    }
  }

  private triggerPreview(amount: number): void {
    this.previewSubject$.next({
      amount,
      currency_code: this.currencyCode,
      language: this.outputLanguage,
      show_currency: this.showCurrency,
      prefix: this.prefix,
      suffix: this.suffix,
    });
  }

  private checkOverflow(previewText: string | null): void {
    if (!previewText || !this.element) {
      this.overflowWarning = false;
      return;
    }
    const heightMm = this.element.data['height_mm'] as number;
    const heightPx = heightMm * PX_PER_MM;
    // Estimate text height: ~14px per line at 12pt
    const lineCount = previewText.split('\n').length;
    const estimatedHeightPx = lineCount * 16;
    this.overflowWarning = estimatedHeightPx > heightPx;
  }
}

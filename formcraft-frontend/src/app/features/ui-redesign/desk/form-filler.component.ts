import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { debounceTime, retry, Subject, takeUntil, timer } from 'rxjs';
import { AvatarComponent } from '../shared/components/avatar.component';
import { StatusChipComponent } from '../shared/components/status-chip.component';
import { FormFillerService, FillTemplate, TemplateElement } from '../../../features/desk/services/form-filler.service';
import { ConditionEngineService, ConditionalElement } from '../../../features/desk/services/condition-engine.service';
import { AutoFillService } from '../../../features/desk/services/auto-fill.service';
import { CustomerService } from '../../../features/desk/services/customer.service';
import { FillerTafqeetService } from '../../../features/desk/services/filler-tafqeet.service';
import { ValidationService } from '../../../features/desk/services/validation.service';
import { SubmissionService } from '../../../features/desk/services/submission.service';
import { DraftService } from '../../../features/desk/services/draft.service';
import { VersionWarningComponent, VersionWarningData } from '../../../features/desk/components/version-warning/version-warning.component';
import { LanguageService } from '../../../core/i18n/language.service';

@Component({
  selector: 'fc-form-filler',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatSnackBarModule, MatDialogModule, TranslateModule, AvatarComponent, StatusChipComponent, ReactiveFormsModule],
  templateUrl: './form-filler.component.html',
  styleUrl: './form-filler.component.scss',
})
export class FormFillerComponent implements OnInit, OnDestroy {
  showCustomerPicker = false;
  templateId = '';
  templateName = '';
  templateCode = '';
  loading = true;
  error: string | null = null;
  template: FillTemplate | null = null;
  formGroup: FormGroup;
  draftId: string | null = null;
  draftUpdatedAt: string | null = null;
  submitting = false;
  savingDraft = false;
  retryCount = 0;
  submissionError: string | null = null;
  showRetryBanner = false;
  tafqeetValues: Record<string, string> = {};
  currentLanguage = 'ar';
  visibleFields = new Set<string>();
  requiredFields = new Set<string>();
  hasSubmitted = false;
  hasUnsavedChanges = false;
  sections: any[] = [];
  sideSections: any[] = [];
  shortcuts = [
    { labelKey: 'DESK.FILL.SHORTCUT_SAVE', key: 'Ctrl+S' },
    { labelKey: 'DESK.FILL.SHORTCUT_SUBMIT', key: 'Ctrl+Enter' },
  ];
  recentCustomers: string[] = [];
  customerResults: any[] = [];
  selectedCustomer: any = null;
  private destroy$ = new Subject<void>();

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private snackBar: MatSnackBar,
    private formFillerService: FormFillerService,
    private conditionEngineService: ConditionEngineService,
    private autoFillService: AutoFillService,
    private customerService: CustomerService,
    private tafqeetService: FillerTafqeetService,
    private validationService: ValidationService,
    private submissionService: SubmissionService,
    private draftService: DraftService,
    private languageService: LanguageService,
    private translate: TranslateService,
    private dialog: MatDialog,
    private fb: FormBuilder,
  ) {
    this.formGroup = this.fb.group({});
  }

  ngOnInit(): void {
    this.templateId = this.route.snapshot.paramMap.get('templateId') || '';
    this.draftId = this.route.snapshot.queryParamMap.get('draftId');
    this.currentLanguage = this.languageService.getLanguage() === 'ar' ? 'ar' : 'en';

    if (!this.templateId) {
      this.loading = false;
      this.error = this.translate.instant('DESK.FILL.NO_TEMPLATE_ID');
      return;
    }

    this.formFillerService.getTemplate(this.templateId).pipe(takeUntil(this.destroy$)).subscribe({
      next: (template) => {
        this.template = template;
        this.templateName = template.name;
        this.templateCode = `v${template.version}`;
        this.buildFormFromTemplate(template);
        this.draftId ? this.loadDraft(this.draftId) : this.loading = false;
        this.error = null;
      },
      error: (err) => {
        console.error('Failed to load template:', err);
        this.loading = false;
        this.error = this.translate.instant('DESK.FILL.TEMPLATE_LOAD_FAILED');
      },
    });
  }

  ngOnDestroy(): void {
    if (this.hasUnsavedChanges && this.templateId) this.saveDraft();
    this.destroy$.next();
    this.destroy$.complete();
    this.conditionEngineService.destroy();
  }

  private buildFormFromTemplate(template: FillTemplate): void {
    const controls: Record<string, any> = {};
    const allElements = template.pages.flatMap((page) => page.elements);
    this.sections = [];
    this.sideSections = [];

    template.pages.forEach((page, pageIndex) => {
      const sectionNumber = String(pageIndex + 1);
      const pageLabel = this.translate.instant('DESK.FILL.PAGE_LABEL', { number: sectionNumber });
      page.elements.forEach((element) => {
        const validators = [];
        if (element.required) validators.push(Validators.required);
        if (element.validation) validators.push(...this.validationService.getValidatorFn(element));
        controls[element.key] = ['', validators];
      });
      this.sections.push({
        number: sectionNumber,
        title: pageLabel,
        complete: false,
        fields: page.elements.map((element: TemplateElement) => ({
          key: element.key,
          type: element.type,
          label: this.currentLanguage === 'ar' ? element.label_ar : element.label_en,
          placeholder: (element as any).placeholder_text?.[this.currentLanguage] || '',
          required: element.required,
          options: (element as any).options || [],
          span: (element as any).span,
          suffix: (element as any).suffix,
          tafqeetEnabled: !!(element.formatting as any)?.tafqeet_enabled,
        })),
        columns: 2,
      });
      this.sideSections.push({ number: sectionNumber, label: pageLabel, state: pageIndex === 0 ? 'active' : 'pending', count: `0/${page.elements.length}` });
    });

    this.formGroup = this.fb.group(controls);
    this.visibleFields = new Set(allElements.map((element) => element.key));
    this.requiredFields = new Set(allElements.filter((element) => element.required).map((element) => element.key));
    this.initializeConditionEngine(allElements);
    this.wireTafqeetSubscriptions(allElements);
    this.formGroup.valueChanges.pipe(takeUntil(this.destroy$)).subscribe(() => this.hasUnsavedChanges = true);
  }

  private initializeConditionEngine(elements: TemplateElement[]): void {
    const conditionalElements: ConditionalElement[] = elements.map((element) => ({
      key: element.key,
      required: element.required,
      visible_when: (element as any).visible_when || null,
      required_when: (element as any).required_when || null,
      computed_value: (element as any).computed_value || null,
      default_value: (element as any).default_value || null,
      placeholder_text: (element as any).placeholder_text || null,
    }));
    const defaults = this.conditionEngineService.resolveDefaults(conditionalElements, this.currentLanguage);
    Object.entries(defaults).forEach(([key, value]) => {
      const control = this.formGroup.get(key);
      if (control && !control.value) control.setValue(value, { emitEvent: false });
    });
    this.conditionEngineService.initialize(conditionalElements, this.formGroup);
    this.conditionEngineService.visibilityChanged$.pipe(takeUntil(this.destroy$)).subscribe((visibleKeys) => {
      this.visibleFields = visibleKeys;
      this.syncHiddenControls(visibleKeys);
    });
    this.conditionEngineService.requiredChanged$.pipe(takeUntil(this.destroy$)).subscribe((requiredKeys) => this.requiredFields = requiredKeys);
  }

  private wireTafqeetSubscriptions(elements: TemplateElement[]): void {
    elements.filter((element) => !!(element.formatting as any)?.tafqeet_enabled).forEach((element) => {
      const control = this.formGroup.get(element.key);
      if (!control) return;
      control.valueChanges.pipe(debounceTime(100), takeUntil(this.destroy$)).subscribe((value) => {
        const amount = value !== null && value !== undefined && value !== '' ? Number(value) : NaN;
        if (isNaN(amount)) {
          this.tafqeetValues[element.key] = '';
          return;
        }
        const formatting = {
          currency_code: (element.formatting as any)?.currency_code || 'SAR',
          language: (element.formatting as any)?.language || 'ar',
          show_currency: (element.formatting as any)?.show_currency !== false,
          prefix: (element.formatting as any)?.prefix || 'none',
          suffix: (element.formatting as any)?.suffix || 'la_ghair',
        };
        this.tafqeetService.compute(amount, formatting as any).pipe(takeUntil(this.destroy$)).subscribe((result) => this.tafqeetValues[element.key] = result || '');
      });
    });
  }

  private syncHiddenControls(visibleKeys: Set<string>): void {
    Object.keys(this.formGroup.controls).forEach((key) => {
      const control = this.formGroup.get(key);
      if (!control) return;
      visibleKeys.has(key) ? control.enable({ emitEvent: false }) : control.disable({ emitEvent: false });
    });
  }

  private isFormValid(): boolean {
    return Array.from(this.visibleFields).every((key) => !this.formGroup.get(key)?.invalid);
  }

  private loadDraft(draftId: string): void {
    this.draftService.getDraft(draftId).pipe(takeUntil(this.destroy$)).subscribe({
      next: (draft: any) => {
        if (draft.expires_at && new Date(draft.expires_at) < new Date()) {
          this.snackBar.open(this.translate.instant('DESK.FILL.DRAFT_EXPIRED'), '', { duration: 3000 });
          this.router.navigate(['/ui/desk']);
          this.loading = false;
          return;
        }
        if (this.template && draft.template_version !== this.template.version) {
          const dialogRef = this.dialog.open(VersionWarningComponent, { data: { oldVersion: draft.template_version, newVersion: this.template.version } as VersionWarningData });
          dialogRef.afterClosed().pipe(takeUntil(this.destroy$)).subscribe((result) => {
            if (result === 'start_fresh') this.formGroup.reset();
            else if (draft.field_values) this.formGroup.patchValue(draft.field_values);
          });
        }
        this.draftUpdatedAt = draft.updated_at;
        if (draft.field_values) this.formGroup.patchValue(draft.field_values);
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load draft:', err);
        this.snackBar.open(this.translate.instant('DESK.FILL.DRAFT_LOAD_FAILED'), '', { duration: 3000 });
        this.loading = false;
      },
    });
  }

  goBack(): void {
    this.router.navigate(['/ui/desk']);
  }

  saveDraft(): void {
    if (!this.templateId || this.savingDraft) return;
    this.savingDraft = true;
    const templateVersion = this.template?.version || 1;
    const completionPercent = this.calculateCompletion();
    const request$ = this.draftId
      ? this.draftService.updateDraft(this.draftId, this.formGroup.value, undefined, completionPercent)
      : this.draftService.saveDraft(this.templateId, templateVersion, this.formGroup.value, undefined, completionPercent);
    request$.pipe(takeUntil(this.destroy$)).subscribe({
      next: (response: any) => {
        this.savingDraft = false;
        this.hasUnsavedChanges = false;
        if (this.draftId && this.draftUpdatedAt && response.updated_at && new Date(response.updated_at) > new Date(this.draftUpdatedAt)) {
          this.snackBar.open(this.translate.instant('DESK.FILL.DRAFT_CONCURRENT_MODIFIED'), '', { duration: 4000 });
        }
        this.draftId = this.draftId || response.id;
        this.draftUpdatedAt = response.updated_at || this.draftUpdatedAt;
        this.snackBar.open(this.translate.instant('DESK.FILL.DRAFT_SAVED'), '', { duration: 3000 });
      },
      error: (err) => {
        console.error('Failed to save draft:', err);
        this.savingDraft = false;
        this.snackBar.open(this.translate.instant('DESK.FILL.DRAFT_SAVE_FAILED'), '', { duration: 3000 });
      },
    });
  }

  submitForm(): void {
    this.hasSubmitted = true;
    if (!this.templateId || !this.isFormValid()) {
      this.snackBar.open(this.translate.instant('DESK.FILL.REQUIRED_FIELDS_MISSING'), '', { duration: 3000 });
      this.formGroup.markAllAsTouched();
      this.scrollFirstInvalidFieldIntoView();
      return;
    }
    if (this.submitting) return;
    this.submitting = true;
    this.dismissBanner();
    this.submissionService.submit(this.templateId, this.template?.version || 1, this.formGroup.value).pipe(
      retry({ count: 3, delay: (_error, retryIndex) => { this.retryCount = retryIndex; return timer(Math.pow(2, retryIndex - 1) * 1000); } }),
      takeUntil(this.destroy$),
    ).subscribe({
      next: (response: any) => {
        this.submitting = false;
        this.retryCount = 0;
        this.hasUnsavedChanges = false;
        this.snackBar.open(this.translate.instant('DESK.FILL.SUBMIT_SUCCESS', { ref: response.reference_number }), '', { duration: 3000 });
        setTimeout(() => this.router.navigate(['/ui/desk']), 2000);
      },
      error: (err) => {
        console.error('Failed to submit form:', err);
        this.submitting = false;
        this.showRetryBanner = true;
        this.submissionError = this.translate.instant('DESK.FILL.SUBMIT_RETRY_EXHAUSTED');
        this.snackBar.open(this.translate.instant('DESK.FILL.SUBMIT_FAILED'), '', { duration: 3000 });
      },
    });
  }

  retrySubmit(): void { this.submitForm(); }
  dismissBanner(): void { this.showRetryBanner = false; this.submissionError = null; }

  private scrollFirstInvalidFieldIntoView(): void {
    setTimeout(() => document.querySelector('.form-field')?.scrollIntoView({ behavior: 'smooth', block: 'center' }));
  }

  printPdf(): void {
    this.templateId
      ? this.router.navigate(['/desk/fill', this.templateId], { queryParams: { print: true } })
      : this.snackBar.open(this.translate.instant('DESK.FILL.PRINT_OPEN_FROM_DESK'), '', { duration: 3000 });
  }

  openCustomerPicker(): void { this.showCustomerPicker = true; }
  closeCustomerPicker(): void { this.showCustomerPicker = false; }
  createNewCustomer(): void { this.closeCustomerPicker(); this.router.navigate(['/desk/customers/new']); }

  searchCustomers(query: string): void {
    this.customerService.search(query).pipe(takeUntil(this.destroy$)).subscribe((response: any) => this.customerResults = response.items || response.customers || response.results || []);
  }

  selectCustomer(customerId: string, customer?: any): void {
    if (!this.templateId) return;
    this.selectedCustomer = customer || this.customerResults.find((c) => c.id === customerId) || null;
    this.customerService.getAutoPopulateData(customerId, this.templateId).pipe(takeUntil(this.destroy$)).subscribe((response: any) => {
      this.autoFillService.executeAutoFill(response.mappings || [], response.values || response.entry_values || response.customer || {}, this.formGroup, this.visibleFields);
      this.closeCustomerPicker();
    });
  }

  calculateCompletion(): number {
    const requiredVisibleKeys = Array.from(this.requiredFields).filter((key) => this.visibleFields.has(key));
    if (requiredVisibleKeys.length === 0) return 100;
    const filledFields = requiredVisibleKeys.filter((key) => {
      const value = this.formGroup.get(key)?.value;
      return value !== null && value !== undefined && value !== '';
    }).length;
    return Math.round((filledFields / requiredVisibleKeys.length) * 100);
  }
}

import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';

import { FormFillerService, FillTemplate, TemplateElement } from '../../../features/desk/services/form-filler.service';
import { ConditionEngineService, ConditionalElement } from '../../../features/desk/services/condition-engine.service';
import { AutoFillService } from '../../../features/desk/services/auto-fill.service';
import { FillerTafqeetService, TafqeetSourceMapping } from '../../../features/desk/services/filler-tafqeet.service';
import { ValidationService } from '../../../features/desk/services/validation.service';
import { SubmissionService } from '../../../features/desk/services/submission.service';
import { DraftService } from '../../../features/desk/services/draft.service';
import { LanguageService } from '../../../core/i18n/language.service';
import { TranslateService } from '@ngx-translate/core';
import { TranslateModule } from '@ngx-translate/core';
import { AuthService } from '../../../core/auth/auth.service';
import { CustomerService } from '../../../features/desk/services/customer.service';
import { VersionWarningComponent } from '../../../features/desk/components/version-warning/version-warning.component';
import { SignaturePadComponent } from '../../../features/desk/components/signature-pad/signature-pad.component';
import { PrintDialogComponent } from '../../../features/desk/components/print-dialog/print-dialog.component';
import { Customer } from '../../../features/desk/customers/customer.models';
import { CustomerPickerDialogComponent } from '../../../features/desk/components/customer-picker/customer-picker-dialog.component';
import { Subject, takeUntil, debounceTime } from 'rxjs';

@Component({
  selector: 'fc-form-filler',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, MatIconModule, MatSnackBarModule, TranslateModule, SignaturePadComponent],
  templateUrl: './form-filler.component.html',
  styleUrl: './form-filler.component.scss',
})
export class FormFillerComponent implements OnInit, OnDestroy {
  templateId = '';
  templateName = '';
  templateCode = '';
  retryLabel = 'Retry';

  loading = true;
  error: string | null = null;
  submitError: string | null = null;
  submitted = false;
  submitting = false;
  isReadOnly = false;

  template: FillTemplate | null = null;
  formGroup: FormGroup;
  draftId: string | null = null;
  currentLanguage: 'ar' | 'en' = 'ar';

  sections: Array<{ number: string; title: string; complete: boolean; fields: Array<{ key: string; type: string; label: string; placeholder: string; required: boolean; validation: any; options: Array<{value: string; label: string}>; element: TemplateElement }>; columns: number }> = [];
  sideSections: Array<{ number: string; label: string; state: string; count: string }> = [];

  visibleKeys = new Set<string>();
  requiredKeys = new Set<string>();
  tafqeetValues = new Map<string, string>();

  private destroy$ = new Subject<void>();

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private snackBar: MatSnackBar,
    private dialog: MatDialog,
    private formFillerService: FormFillerService,
    private conditionEngineService: ConditionEngineService,
    private autoFillService: AutoFillService,
    private tafqeetService: FillerTafqeetService,
    private validationService: ValidationService,
    private submissionService: SubmissionService,
    private draftService: DraftService,
    private customerService: CustomerService,
    private authService: AuthService,
    private languageService: LanguageService,
    private translate: TranslateService,
    private fb: FormBuilder,
  ) {
    this.formGroup = this.fb.group({});
  }

  ngOnInit(): void {
    this.templateId = this.route.snapshot.paramMap.get('templateId') || '';
    this.draftId = this.route.snapshot.queryParamMap.get('draftId');
    this.currentLanguage = this.languageService.getLanguage() === 'ar' ? 'ar' : 'en';
    this.retryLabel = this.translate.instant('desk.retry');
    this.isReadOnly = this.authService.getCurrentUser()?.role === 'designer';

    this.conditionEngineService.visibilityChanged$.pipe(takeUntil(this.destroy$)).subscribe((keys) => {
      this.visibleKeys = keys;
    });

    this.conditionEngineService.requiredChanged$.pipe(takeUntil(this.destroy$)).subscribe((keys) => {
      this.requiredKeys = keys;
      this.updateRequiredValidators();
    });

    // React to language switching — update field labels, section titles, side panel
    this.translate.onLangChange.pipe(takeUntil(this.destroy$)).subscribe((event) => {
      this.currentLanguage = event.lang === 'ar' ? 'ar' : 'en';
      this.retryLabel = this.translate.instant('desk.retry');
      this.refreshLabels();
    });

    if (!this.templateId) {
      this.loading = false;
      this.error = this.translate.instant('desk.template_load_error');
      return;
    }

    this.loadTemplate();
  }

  ngOnDestroy(): void {
    if (this.formGroup.dirty && !this.submitted && this.templateId) {
      localStorage.setItem(`fc_draft_${this.templateId}`, JSON.stringify(this.formGroup.value));
    }
    this.conditionEngineService.destroy();
    this.destroy$.next();
    this.destroy$.complete();
  }

  private loadTemplate(): void {
    this.loading = true;
    this.formFillerService.getTemplate(this.templateId).subscribe({
      next: (template) => {
        this.template = template;
        this.templateName = template.name;
        this.templateCode = `v${template.version}`;

        this.buildFormFromTemplate(template);
        this.flushLocalDraftIfExists();

        if (this.draftId) {
          this.loadDraft(this.draftId);
        } else {
          this.loading = false;
        }
        this.error = null;
      },
      error: () => {
        this.loading = false;
        this.error = this.translate.instant('desk.template_load_error');
      },
    });
  }

  private flushLocalDraftIfExists(): void {
    const key = `fc_draft_${this.templateId}`;
    const raw = localStorage.getItem(key);
    if (!raw || !this.template) return;

    try {
      const fieldValues = JSON.parse(raw) as Record<string, any>;
      this.draftService.saveDraft(this.templateId, this.template.version, fieldValues).subscribe({
        next: (draft) => {
          this.draftId = draft.id;
          localStorage.removeItem(key);
        },
      });
    } catch {
      localStorage.removeItem(key);
    }
  }

  private buildFormFromTemplate(template: FillTemplate): void {
    const controls: Record<string, FormControl> = {};

    this.sections = [];
    this.sideSections = [];

    template.pages.forEach((page, pageIndex) => {
      const pageTitle = this.translate.instant('desk.page_number', { n: pageIndex + 1 });

      page.elements.forEach((element: TemplateElement) => {
        const validatorFns = this.validationService.getValidatorFn(element, template.country, this.currentLanguage);
        controls[element.key] = new FormControl('', validatorFns);
      });

      this.sections.push({
        number: String(pageIndex + 1),
        title: pageTitle,
        complete: false,
        fields: page.elements.map((el: TemplateElement) => ({
          key: el.key,
          type: el.type,
          label: this.currentLanguage === 'ar' ? el.label_ar : el.label_en,
          placeholder: '',
          required: !!el.required,
          validation: el.validation,
          options: (el.options || []).map((opt) => ({
            value: opt.value,
            label: this.currentLanguage === 'ar' ? opt.label_ar : opt.label_en,
          })),
          element: el,
        })),
        columns: 2,
      });

      this.sideSections.push({
        number: String(pageIndex + 1),
        label: pageTitle,
        state: pageIndex === 0 ? 'active' : 'pending',
        count: `0/${page.elements.length}`,
      });
    });

    this.formGroup = this.fb.group(controls);

    const flatElements = template.pages.flatMap((p) => p.elements);
    const conditionalElements: ConditionalElement[] = flatElements.map((el) => ({
      key: el.key,
      required: el.required,
      visible_when: el.visible_when || null,
      required_when: el.required_when || null,
    }));

    this.conditionEngineService.initialize(conditionalElements, this.formGroup);

    this.formGroup.valueChanges.pipe(takeUntil(this.destroy$)).subscribe(() => {
      this.submitError = null;
    });

    // Wire tafqeet auto-population: source number field → tafqeet target field
    const tafqeetElements = flatElements.filter((e) => e.type === 'tafqeet');
    for (const tafqeetElem of tafqeetElements) {
      // Designer stores camelCase: sourceElementKey, currencyCode, outputLanguage, etc.
      const fmt = tafqeetElem.formatting || {};
      const sourceKey = fmt.sourceElementKey || fmt.source_element || tafqeetElem.validation?.source_element;
      if (!sourceKey) continue;

      const sourceControl = this.formGroup.get(sourceKey);
      const tafqeetControl = this.formGroup.get(tafqeetElem.key);
      if (!sourceControl || !tafqeetControl) continue;

      const formatting: TafqeetSourceMapping['formatting'] = {
        currency_code: fmt.currencyCode || fmt.currency_code || 'SAR',
        language: fmt.outputLanguage || fmt.language || 'ar',
        show_currency: fmt.showCurrency !== undefined ? fmt.showCurrency : (fmt.show_currency !== false),
        prefix: fmt.prefix || 'none',
        suffix: fmt.suffix || 'la_ghair',
      };

      sourceControl.valueChanges.pipe(
        debounceTime(200),
        takeUntil(this.destroy$),
      ).subscribe((val: any) => {
        const num = val !== null && val !== undefined && val !== '' ? Number(val) : NaN;
        if (isNaN(num)) {
          tafqeetControl.setValue('', { emitEvent: false });
          return;
        }
        this.tafqeetService.compute(num, formatting).pipe(takeUntil(this.destroy$)).subscribe({
          next: (result) => tafqeetControl.setValue(result || '', { emitEvent: false }),
          error: () => tafqeetControl.setValue('', { emitEvent: false }),
        });
      });
    }

    // Wire inline tafqeet text below number fields with tafqeet_enabled
    for (const element of flatElements) {
      if (!element.tafqeet_enabled) continue;
      const control = this.formGroup.get(element.key);
      if (!control) continue;

      control.valueChanges.pipe(takeUntil(this.destroy$)).subscribe((value) => {
        if (value === null || value === undefined || value === '') {
          this.tafqeetValues.delete(element.key);
          return;
        }

        const amount = Number(value);
        if (Number.isNaN(amount)) {
          this.tafqeetValues.delete(element.key);
          return;
        }

        const formatting: TafqeetSourceMapping['formatting'] = {
          currency_code: 'SAR',
          language: 'ar',
          show_currency: true,
          prefix: 'none',
          suffix: 'la_ghair',
        };

        this.tafqeetService.compute(amount, formatting).subscribe((result) => {
          if (result) {
            this.tafqeetValues.set(element.key, result);
          } else {
            this.tafqeetValues.delete(element.key);
          }
        });
      });
    }
  }

  private updateRequiredValidators(): void {
    if (!this.template) return;

    const allElements = this.template.pages.flatMap((p) => p.elements);
    for (const element of allElements) {
      const control = this.formGroup.get(element.key);
      if (!control) continue;

      const baseValidators = this.validationService.getValidatorFn(element, this.template.country, this.currentLanguage)
        .filter((fn) => fn !== Validators.required);

      if (this.requiredKeys.has(element.key) || element.required) {
        baseValidators.unshift(Validators.required);
      }

      control.setValidators(baseValidators);
      control.updateValueAndValidity({ emitEvent: false });
    }
  }

  /** Re-derive field labels, section titles, and side-panel labels from the current language */
  private refreshLabels(): void {
    if (!this.template) return;

    this.templateName = this.template.name;

    this.template.pages.forEach((page, pageIndex) => {
      const pageTitle = this.translate.instant('desk.page_number', { n: pageIndex + 1 });
      const section = this.sections[pageIndex];
      if (section) {
        section.title = pageTitle;
        for (const field of section.fields) {
          const el = field.element;
          field.label = this.currentLanguage === 'ar' ? el.label_ar : el.label_en;
          field.options = (el.options || []).map((opt) => ({
            value: opt.value,
            label: this.currentLanguage === 'ar' ? opt.label_ar : opt.label_en,
          }));
        }
      }

      const sideSection = this.sideSections[pageIndex];
      if (sideSection) {
        sideSection.label = pageTitle;
      }
    });
  }

  private loadDraft(draftId: string): void {
    this.draftService.getDraft(draftId).subscribe({
      next: (draft) => {
        if (draft.field_values) {
          this.formGroup.patchValue(draft.field_values);
        }

        if (this.template && draft.template_version !== this.template.version) {
          this.dialog.open(VersionWarningComponent, {
            data: {
              oldVersion: draft.template_version,
              newVersion: this.template.version,
            },
          });
          this.snackBar.open(this.translate.instant('desk.form_filler.draft_version_mismatch'), '', { duration: 4000 });
        }

        this.loading = false;
      },
      error: () => {
        this.loading = false;
      },
    });
  }

  goBack(): void {
    this.router.navigate(['/ui/desk/templates']);
  }

  saveDraft(): void {
    if (!this.templateId || !this.template) return;

    if (this.draftId) {
      this.draftService.updateDraft(this.draftId, this.formGroup.value).subscribe({
        next: () => {
          this.formGroup.markAsPristine();
          this.snackBar.open(this.translate.instant('desk.form_filler.draft_saved'), '', { duration: 3000 });
        },
        error: () => {
          this.snackBar.open(this.translate.instant('desk.form_filler.draft_save_failed'), '', { duration: 3000 });
        },
      });
      return;
    }

    this.draftService.saveDraft(this.templateId, this.template.version, this.formGroup.value).subscribe({
      next: (response) => {
        this.draftId = response.id;
        this.formGroup.markAsPristine();
        this.snackBar.open(this.translate.instant('desk.form_filler.draft_saved'), '', { duration: 3000 });
      },
      error: () => {
        this.snackBar.open(this.translate.instant('desk.form_filler.draft_save_failed'), '', { duration: 3000 });
      },
    });
  }

  submitForm(): void {
    this.submitted = true;
    this.submitError = null;

    if (this.isReadOnly || !this.templateId || !this.template) {
      return;
    }

    if (!this.formGroup.valid) {
      this.snackBar.open(this.translate.instant('desk.form_filler.submit_blocked'), '', { duration: 3000 });
      return;
    }

    this.submitting = true;

    const payload = Object.fromEntries(
      Object.entries(this.formGroup.value).filter(([key]) => this.visibleKeys.size === 0 || this.visibleKeys.has(key)),
    );

    this.submissionService.submit(this.templateId, this.template.version, payload).subscribe({
      next: (response) => {
        this.submitting = false;
        this.submitted = true;
        this.formGroup.markAsPristine();
        this.router.navigate(['/ui/desk/submission-confirmed'], {
          state: {
            referenceNumber: response.reference_number,
            templateName: this.template?.name || '',
            submittedAt: new Date().toISOString(),
          },
        });
      },
      error: () => {
        this.submitting = false;
        this.submitError = this.translate.instant('desk.form_filler.submit_failed');
      },
    });
  }

  retrySubmit(): void {
    this.submitForm();
  }

  printPdf(): void {
    if (!this.template || !this.templateId) return;
    if (!this.formGroup.valid) {
      this.snackBar.open(this.translate.instant('desk.form_filler.submit_blocked'), '', { duration: 3000 });
      return;
    }

    this.submitting = true;
    const payload = Object.fromEntries(
      Object.entries(this.formGroup.value).filter(([key]) => this.visibleKeys.size === 0 || this.visibleKeys.has(key)),
    );

    this.submissionService.submit(this.templateId, this.template.version, payload).subscribe({
      next: (response) => {
        this.submitting = false;
        this.submitted = true;
        this.formGroup.markAsPristine();
        this.snackBar.open(
          this.translate.instant('filler.reference_number', { ref: response.reference_number }),
          '',
          { duration: 4000 },
        );
        this.dialog.open(PrintDialogComponent, {
          width: '520px',
          data: {
            templateId: this.templateId,
            templateName: this.template?.name || '',
            fieldValues: payload,
          },
        });
      },
      error: () => {
        this.submitting = false;
        this.snackBar.open(this.translate.instant('desk.form_filler.submit_failed'), '', { duration: 3000 });
      },
    });
  }

  openCustomerPicker(): void {
    const dialogRef = this.dialog.open(CustomerPickerDialogComponent, { width: '560px' });
    dialogRef.afterClosed().subscribe((customer: Customer | undefined) => {
      if (!customer || !this.templateId) return;

      this.customerService.getAutoPopulateData(customer.id, this.templateId).subscribe({
        next: (response) => {
          const visible = this.visibleKeys.size === 0
            ? new Set(Object.keys(this.formGroup.controls))
            : this.visibleKeys;
          this.autoFillService.executeAutoFill(response.mappings || [], customer as unknown as Record<string, any>, this.formGroup, visible);
        },
      });
    });
  }

  onSignatureConfirmed(key: string, base64Value: string | null): void {
    const control = this.formGroup.get(key);
    if (control) {
      control.setValue(base64Value);
      control.markAsTouched();
    }
  }

  getErrorMessage(fieldKey: string): string {
    const control = this.formGroup.get(fieldKey);
    if (!control?.errors) {
      return '';
    }
    if (control.hasError('required')) {
      return this.translate.instant('desk.form_filler.field_required');
    }
    return this.translate.instant('desk.form_filler.field_invalid');
  }

  getInvalidVisibleFields(): Array<{ label: string; message: string }> {
    const items: Array<{ label: string; message: string }> = [];
    for (const section of this.sections) {
      for (const field of section.fields) {
        const control = this.formGroup.get(field.key);
        const isVisible = this.visibleKeys.size === 0 || this.visibleKeys.has(field.key);
        if (isVisible && control?.invalid) {
          items.push({ label: field.label, message: this.getErrorMessage(field.key) });
        }
      }
    }
    return items;
  }
}

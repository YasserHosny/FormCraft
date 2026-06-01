import { Component, OnInit, OnDestroy, ViewChild, HostListener } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { Subject, takeUntil, debounceTime, forkJoin, of, switchMap } from 'rxjs';
import { map } from 'rxjs/operators';
import { FormFillerService, FillTemplate, TemplateElement } from '../services/form-filler.service';
import { ValidationService } from '../services/validation.service';
import { FillerTafqeetService } from '../services/filler-tafqeet.service';
import { ConditionEngineService } from '../services/condition-engine.service';
import { TranslateService } from '@ngx-translate/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatDialog } from '@angular/material/dialog';
import { VersionWarningComponent, VersionWarningData } from '../components/version-warning/version-warning.component';
import { TemplateFeedbackDialogComponent } from '../components/template-feedback-dialog/template-feedback-dialog.component';
import { PrintDialogComponent } from '../components/print-dialog/print-dialog.component';
import { DraftService } from '../services/draft.service';
import { SubmissionService } from '../services/submission.service';
import { HistoryService } from '../services/history.service';
import { AutoFillService } from '../services/auto-fill.service';
import { OfflineSyncService } from '../offline/offline-sync.service';

@Component({
  selector: 'fc-fill',
  standalone: false,
  templateUrl: './fill.component.html',
  styleUrls: ['./fill.component.scss'],
})
export class FillComponent implements OnInit, OnDestroy {
  template: FillTemplate | null = null;
  isDeprecated = false;
  form!: FormGroup;
  loading = true;
  error = false;
  isDirty = false;
  formValid = false;
  draftId: string | null = null;
  templateVersion = 0;
  submitting = false;
  savingDraft = false;
  savingOffline = false;
  completionPercent = 0;
  cloneInfo: { id: string; ref: string } | null = null;
  visibleKeys = new Set<string>();
  requiredKeys = new Set<string>();

  private destroy$ = new Subject<void>();
  private autoSaveInterval: ReturnType<typeof setInterval> | null = null;
  private lastSavedValues: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private fillService: FormFillerService,
    private validationService: ValidationService,
    private tafqeetService: FillerTafqeetService,
    private translate: TranslateService,
    private snackBar: MatSnackBar,
    private dialog: MatDialog,
    private draftService: DraftService,
    private submissionService: SubmissionService,
    private historyService: HistoryService,
    private conditionEngine: ConditionEngineService,
    private autoFillService: AutoFillService,
    private offlineSync: OfflineSyncService,
  ) {}

  ngOnInit(): void {
    const templateId = this.route.snapshot.paramMap.get('templateId');
    if (!templateId) {
      this.error = true;
      this.loading = false;
      return;
    }

    this.draftId = this.route.snapshot.queryParamMap.get('draft');
    const cloneSubmissionId = this.route.snapshot.queryParamMap.get('clone');
    this.cloneInfo = cloneSubmissionId ? { id: cloneSubmissionId, ref: '' } : null;

    this.fillService.getTemplate(templateId).pipe(takeUntil(this.destroy$)).subscribe({
      next: (tmpl) => {
        this.template = tmpl;
        this.templateVersion = tmpl.version;
        this.isDeprecated = tmpl.is_deprecated || false;

        forkJoin([
          this.validationService.loadValidators(tmpl.country),
          this.validationService.loadCustomValidators(),
        ]).pipe(takeUntil(this.destroy$)).subscribe(() => {
          this.buildForm(tmpl);
          this.form.markAllAsTouched();
          this.formValid = this.form.valid;
          this.updateCompletionPercent();
          this.loading = false;
          this.startAutoSave();

          if (this.cloneInfo) {
            this.loadCloneData(this.cloneInfo.id);
          } else if (this.draftId) {
            this.loadDraft(this.draftId, tmpl.version);
          }
        });
      },
      error: () => {
        this.error = true;
        this.loading = false;
      },
    });
  }

  buildForm(template: FillTemplate): void {
    const controls: Record<string, FormControl> = {};
    const allElements = template.pages.flatMap((p) => p.elements);

    for (const elem of allElements) {
      const initialValue = this.getInitialValue(elem);
      const validators = this.validationService.getValidatorFn(
        elem,
        template.country,
        this.translate.currentLang || template.language,
      );
      controls[elem.key] = new FormControl(initialValue, validators);
    }

    this.form = new FormGroup(controls);

    this.initConditionEngine(allElements);
    this.wireTafqeetSubscriptions(allElements);

    this.form.valueChanges.pipe(
      debounceTime(100),
      takeUntil(this.destroy$),
    ).subscribe(() => {
      this.isDirty = true;
      this.formValid = this.form.valid;
      this.updateCompletionPercent();
    });
  }

  private initConditionEngine(elements: TemplateElement[]): void {
    const conditionalElements = elements.map((e) => ({
      key: e.key,
      required: e.required,
      visible_when: (e as any).visible_when || null,
      required_when: (e as any).required_when || null,
      computed_value: (e as any).computed_value || null,
      default_value: (e as any).default_value || null,
      placeholder_text: (e as any).placeholder_text || null,
    }));

    const defaults = this.conditionEngine.resolveDefaults(conditionalElements, this.translate.currentLang);
    for (const [key, val] of Object.entries(defaults)) {
      const control = this.form.get(key);
      if (control && !control.value) {
        control.setValue(val, { emitEvent: false });
      }
    }

    this.conditionEngine.initialize(conditionalElements, this.form);

    this.conditionEngine.visibilityChanged$.pipe(takeUntil(this.destroy$)).subscribe((keys) => {
      this.visibleKeys = keys;
    });

    this.conditionEngine.requiredChanged$.pipe(takeUntil(this.destroy$)).subscribe((keys) => {
      this.requiredKeys = keys;
    });
  }

  isElementVisible(key: string): boolean {
    if (this.visibleKeys.size === 0) return true;
    return this.visibleKeys.has(key);
  }

  isElementRequired(key: string): boolean {
    return this.requiredKeys.has(key);
  }

  wireTafqeetSubscriptions(elements: TemplateElement[]): void {
    const tafqeetElements = elements.filter((e) => e.type === 'tafqeet');
    for (const tafqeetElem of tafqeetElements) {
      const sourceKey = tafqeetElem.formatting?.source_element || tafqeetElem.validation?.source_element;
      if (!sourceKey) continue;

      const sourceControl = this.form.get(sourceKey);
      const tafqeetControl = this.form.get(tafqeetElem.key);
      if (!sourceControl || !tafqeetControl) continue;

      const formatting = {
        currency_code: tafqeetElem.formatting?.currency_code || 'SAR',
        language: tafqeetElem.formatting?.language || 'ar',
        show_currency: tafqeetElem.formatting?.show_currency !== false,
        prefix: tafqeetElem.formatting?.prefix || 'none',
        suffix: tafqeetElem.formatting?.suffix || 'la_ghair',
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
  }

  getInitialValue(elem: TemplateElement): any {
    switch (elem.type) {
      case 'checkbox':
        return false;
      case 'number':
      case 'currency':
        return null;
      case 'tafqeet':
      case 'image':
      case 'qr':
      case 'barcode':
        return '';
      default:
        return '';
    }
  }

  loadDraft(draftId: string, currentVersion: number): void {
    this.draftService.getDraft(draftId).pipe(takeUntil(this.destroy$)).subscribe({
      next: (draft) => {
        if (draft.template_version < currentVersion) {
          this.showVersionWarning(draft.template_version, currentVersion, draft.field_values);
        } else {
          this.populateForm(draft.field_values);
        }
      },
      error: () => {
        this.snackBar.open(this.translate.instant('filler.draft_expired'), undefined, { duration: 3000 });
        this.draftId = null;
      },
    });
  }

  showVersionWarning(oldVersion: number, newVersion: number, savedValues: Record<string, any>): void {
    const dialogRef = this.dialog.open(VersionWarningComponent, {
      data: { oldVersion, newVersion } as VersionWarningData,
      disableClose: true,
    });

    dialogRef.afterClosed().pipe(takeUntil(this.destroy$)).subscribe((result) => {
      if (result === 'start_fresh') {
        this.form.reset();
        this.isDirty = false;
      } else {
        this.populateForm(savedValues);
      }
    });
  }

  populateForm(fieldValues: Record<string, any>): void {
    if (!fieldValues) return;
    for (const key of Object.keys(fieldValues)) {
      const control = this.form.get(key);
      if (control) {
        control.setValue(fieldValues[key]);
      }
    }
    this.isDirty = false;
  }

  loadCloneData(submissionId: string): void {
    this.historyService.getSubmission(submissionId).pipe(takeUntil(this.destroy$)).subscribe({
      next: (data) => {
        this.cloneInfo = { id: submissionId, ref: data.reference_number };
        this.populateForm(data.field_values);
        this.isDirty = true;
      },
      error: () => {
        this.snackBar.open(this.translate.instant('errors.generic'), undefined, { duration: 3000 });
      },
    });
  }

  getLabel(elem: TemplateElement): string {
    const lang = this.translate.currentLang || 'ar';
    return lang === 'en' && elem.label_en ? elem.label_en : elem.label_ar;
  }

  getElementsForPage(pageIndex: number): TemplateElement[] {
    if (!this.template) return [];
    const page = this.template.pages[pageIndex];
    if (!page) return [];
    return [...page.elements].sort((a, b) => a.sort_order - b.sort_order);
  }

  getAllElements(): TemplateElement[] {
    if (!this.template) return [];
    return this.template.pages.flatMap((p) => p.elements);
  }

  getControl(key: string): FormControl {
    return this.form.get(key) as FormControl;
  }

  updateCompletionPercent(): void {
    if (!this.template) return;
    const allElements = this.template.pages.flatMap((p) => p.elements);
    const requiredElements = allElements.filter((e) => e.required);
    if (requiredElements.length === 0) {
      this.completionPercent = 100;
      return;
    }
    let filled = 0;
    for (const elem of requiredElements) {
      const control = this.form.get(elem.key);
      if (control && control.value !== null && control.value !== undefined && control.value !== '') {
        filled++;
      }
    }
    this.completionPercent = Math.round((filled / requiredElements.length) * 100);
  }

  onCancel(): void {
    if (this.isDirty) {
      const msg = this.translate.instant('filler.unsaved_changes');
      if (!confirm(msg)) return;
    }
    this.router.navigate(['/desk']);
  }

  onClearAll(): void {
    this.form.reset();
    this.isDirty = false;
  }

  retryLoad(): void {
    this.error = false;
    this.loading = true;
    this.ngOnInit();
  }

  openFeedbackDialog(): void {
    const templateId = this.template?.id;
    if (!templateId) return;
    this.dialog.open(TemplateFeedbackDialogComponent, {
      width: '480px',
      data: {
        templateId,
        templateName: this.template?.name,
        templateVersion: this.template?.version,
      },
    });
  }

  onEntrySelected(event: { entry_id: string; values: Record<string, any>; elementKey: string }): void {
    if (!this.template) return;

    const boundElement = this.template.pages
      .flatMap(p => p.elements)
      .find(e => e.key === event.elementKey);
    if (!boundElement) return;

    const formatting = boundElement.formatting as Record<string, unknown> | undefined;
    const refBinding = formatting?.['ref_binding'] as Record<string, any> | undefined;
    if (!refBinding || !refBinding['auto_fill']) return;

    const visibleKeys = new Set<string>(
      this.template.pages.flatMap(p => p.elements).map(e => e.key)
    );

    this.autoFillService.executeAutoFill(
      refBinding['auto_fill'],
      event.values,
      this.form,
      visibleKeys,
      refBinding['clear_on_deselect'] ?? false,
    );
  }

  onPrint(): void {
    if (!this.formValid || this.submitting) {
      this.form?.markAllAsTouched();
      this.scrollFirstInvalidFieldIntoView();
      return;
    }
    this.submitting = true;

    const fieldValues = this.form.value;
    this.validationService.refreshCustomValidators().pipe(
      switchMap(() => {
        this.rebuildValidators();
        if (this.form.invalid) {
          this.submitting = false;
          this.form.markAllAsTouched();
          return of(null);
        }
        return this.submissionService.submit(
          this.template!.id,
          this.template!.version,
          fieldValues,
        );
      }),
      switchMap((response) => response ? this.resolveSignatureUploads(response.id, fieldValues).pipe(map(() => response)) : of(null)),
      takeUntil(this.destroy$),
    ).subscribe({
      next: (response) => {
        if (!response) return;
        this.submitting = false;
        this.deleteDraftIfLoaded();
        this.snackBar.open(
          this.translate.instant('filler.success_submit') + ' ' +
          this.translate.instant('filler.reference_number', { ref: response.reference_number }),
          undefined,
          { duration: 5000 },
        );
        this.isDirty = false;
        this.openPrintDialog(fieldValues);
      },
      error: () => {
        this.submitting = false;
        this.snackBar.open(this.translate.instant('errors.generic'), undefined, { duration: 3000 });
      },
    });
  }

  private rebuildValidators(): void {
    if (!this.template || !this.form) return;
    const allElements = this.template.pages.flatMap((p) => p.elements);
    for (const elem of allElements) {
      const control = this.form.get(elem.key);
      if (!control) continue;
      control.setValidators(this.validationService.getValidatorFn(
        elem,
        this.template.country,
        this.translate.currentLang || this.template.language,
      ));
      control.updateValueAndValidity({ emitEvent: false });
    }
    this.formValid = this.form.valid;
  }

  onPrintAndNext(): void {
    if (!this.formValid || this.submitting) {
      this.form?.markAllAsTouched();
      this.scrollFirstInvalidFieldIntoView();
      return;
    }
    this.submitting = true;

    const fieldValues = this.form.value;
    this.validationService.refreshCustomValidators().pipe(
      switchMap(() => {
        this.rebuildValidators();
        if (this.form.invalid) {
          this.submitting = false;
          this.form.markAllAsTouched();
          return of(null);
        }
        return this.submissionService.submit(
          this.template!.id,
          this.template!.version,
          fieldValues,
        );
      }),
      switchMap((response) => response ? this.resolveSignatureUploads(response.id, fieldValues).pipe(map(() => response)) : of(null)),
      takeUntil(this.destroy$),
    ).subscribe({
      next: (response) => {
        if (!response) return;
        this.submitting = false;
        this.deleteDraftIfLoaded();
        this.snackBar.open(
          this.translate.instant('filler.success_submit') + ' ' +
          this.translate.instant('filler.reference_number', { ref: response.reference_number }),
          undefined,
          { duration: 5000 },
        );
        this.openPrintDialog(fieldValues);
        this.form.reset();
        this.isDirty = false;
      },
      error: () => {
        this.submitting = false;
        this.snackBar.open(this.translate.instant('errors.generic'), undefined, { duration: 3000 });
      },
    });
  }

  onSaveDraft(): void {
    if (!navigator.onLine) {
      this.onSaveOfflineDraft();
      return;
    }
    if (this.savingDraft) return;
    this.savingDraft = true;

    const fieldValues = this.form.value;

    if (this.draftId) {
      this.draftService.updateDraft(this.draftId, fieldValues).pipe(takeUntil(this.destroy$)).subscribe({
        next: () => {
          this.savingDraft = false;
          this.isDirty = false;
          this.snackBar.open(this.translate.instant('filler.draft_saved'), undefined, { duration: 2000 });
        },
        error: () => {
          this.savingDraft = false;
          this.snackBar.open(this.translate.instant('filler.draft_save_error'), undefined, { duration: 3000 });
        },
      });
    } else {
      this.draftService.saveDraft(
        this.template!.id,
        this.template!.version,
        fieldValues,
        undefined,
      ).pipe(takeUntil(this.destroy$)).subscribe({
        next: (draft) => {
          this.savingDraft = false;
          this.draftId = draft.id;
          this.isDirty = false;
          this.snackBar.open(this.translate.instant('filler.draft_saved'), undefined, { duration: 2000 });
        },
        error: () => {
          this.savingDraft = false;
          this.snackBar.open(this.translate.instant('filler.draft_save_error'), undefined, { duration: 3000 });
        },
      });
    }
  }

  onSaveOfflineDraft(): void {
    if (!this.template || this.savingOffline) return;
    this.savingOffline = true;
    this.offlineSync.saveDraft(this.template.id, this.template.version, this.form.value)
      .then(() => {
        this.savingOffline = false;
        this.isDirty = false;
        this.snackBar.open(this.translate.instant('offline.draft_saved'), undefined, { duration: 2500 });
      })
      .catch(() => {
        this.savingOffline = false;
        this.snackBar.open(this.translate.instant('offline.save_failed'), undefined, { duration: 3000 });
      });
  }

  onQueueOfflineSubmission(): void {
    if (!this.template || !this.formValid || this.submitting) {
      this.form?.markAllAsTouched();
      this.scrollFirstInvalidFieldIntoView();
      return;
    }
    this.submitting = true;
    this.offlineSync.queueSubmission(this.template.id, this.template.version, this.form.value)
      .then(() => {
        this.submitting = false;
        this.isDirty = false;
        this.deleteDraftIfLoaded();
        this.snackBar.open(this.translate.instant('offline.submission_queued'), undefined, { duration: 3000 });
      })
      .catch(() => {
        this.submitting = false;
        this.snackBar.open(this.translate.instant('offline.queue_failed'), undefined, { duration: 3000 });
      });
  }

  private resolveSignatureUploads(submissionId: string, fieldValues: Record<string, any>) {
    const uploads: Record<string, ReturnType<typeof this.submissionService.uploadSignature>> = {};
    for (const [key, val] of Object.entries(fieldValues)) {
      if (typeof val === 'string' && val.startsWith('data:image/png;base64,')) {
        const base64 = val.split(',')[1] || '';
        const sizeBytes = Math.ceil(base64.length * 0.75);
        if (sizeBytes > 100 * 1024) {
          uploads[key] = this.submissionService.uploadSignature(submissionId, key, val);
        }
      }
    }
    const keys = Object.keys(uploads);
    if (keys.length === 0) return of(null);
    return forkJoin(Object.values(uploads)).pipe(
      map((results) => {
        results.forEach((res, i) => {
          fieldValues[keys[i]] = { type: res.type, path: res.path };
        });
        return null;
      }),
    );
  }

  private scrollFirstInvalidFieldIntoView(): void {
    setTimeout(() => {
      const firstInvalidKey = Object.keys(this.form.controls).find((key) => this.form.get(key)?.invalid);
      if (!firstInvalidKey) return;

      const target = document.querySelector(
        `[formcontrolname="${firstInvalidKey}"], [name="${firstInvalidKey}"], .ng-invalid`,
      );
      target?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
  }

  openPrintDialog(fieldValues: Record<string, any>): void {
    const isPhone = window.matchMedia('(max-width: 599px)').matches;
    this.dialog.open(PrintDialogComponent, {
      width: isPhone ? '100vw' : '520px',
      maxWidth: isPhone ? '100vw' : undefined,
      height: isPhone ? '100vh' : undefined,
      maxHeight: isPhone ? '100vh' : undefined,
      data: {
        templateId: this.template!.id,
        templateName: this.template!.name,
        fieldValues,
      },
    });
  }

  @HostListener('window:beforeunload', ['$event'])
  onBeforeUnload(event: BeforeUnloadEvent): void {
    if (this.isDirty) {
      event.preventDefault();
      event.returnValue = true;
    }
  }

  @HostListener('window:keydown', ['$event'])
  onKeyDown(event: KeyboardEvent): void {
    if (event.ctrlKey || event.metaKey) {
      if (event.key === 's' || event.key === 'S') {
        event.preventDefault();
        this.onSaveDraft();
      } else if (event.key === 'p' || event.key === 'P') {
        event.preventDefault();
        if (this.formValid) {
          this.onPrint();
        }
      }
    }
    if (event.ctrlKey && event.key === 'Enter') {
      event.preventDefault();
      if (this.formValid) {
        this.onPrintAndNext();
      }
    }
  }

  startAutoSave(): void {
    if (this.autoSaveInterval) return;
    this.autoSaveInterval = setInterval(() => {
      if (!this.isDirty || this.submitting) return;
      const currentValues = JSON.stringify(this.form.value);
      if (currentValues === this.lastSavedValues) return;

      if (this.draftId) {
        this.draftService.updateDraft(this.draftId, this.form.value).pipe(takeUntil(this.destroy$)).subscribe({
          next: () => {
            this.lastSavedValues = currentValues;
            this.isDirty = false;
            this.snackBar.open(this.translate.instant('filler.auto_saved'), undefined, { duration: 1500 });
          },
          error: () => {
            this.snackBar.open(this.translate.instant('filler.draft_save_error'), undefined, { duration: 3000 });
          },
        });
      } else {
        this.draftService.saveDraft(
          this.template!.id,
          this.template!.version,
          this.form.value,
          undefined,
        ).pipe(takeUntil(this.destroy$)).subscribe({
          next: (draft) => {
            this.draftId = draft.id;
            this.lastSavedValues = currentValues;
            this.isDirty = false;
            this.snackBar.open(this.translate.instant('filler.auto_saved'), undefined, { duration: 1500 });
          },
          error: () => {},
        });
      }
    }, 60000);
  }

  stopAutoSave(): void {
    if (this.autoSaveInterval) {
      clearInterval(this.autoSaveInterval);
      this.autoSaveInterval = null;
    }
  }

  deleteDraftIfLoaded(): void {
    if (this.draftId) {
      this.draftService.deleteDraft(this.draftId).pipe(takeUntil(this.destroy$)).subscribe();
      this.draftId = null;
    }
  }

  ngOnDestroy(): void {
    this.stopAutoSave();
    this.conditionEngine.destroy();
    this.destroy$.next();
    this.destroy$.complete();
  }
}

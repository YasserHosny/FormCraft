import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AvatarComponent } from '../shared/components/avatar.component';
import { StatusChipComponent } from '../shared/components/status-chip.component';
import { FormFillerService, FillTemplate, TemplateElement } from '../../../features/desk/services/form-filler.service';
import { ConditionEngineService, ConditionalElement } from '../../../features/desk/services/condition-engine.service';
import { AutoFillService } from '../../../features/desk/services/auto-fill.service';
import { FillerTafqeetService } from '../../../features/desk/services/filler-tafqeet.service';
import { ValidationService } from '../../../features/desk/services/validation.service';
import { SubmissionService } from '../../../features/desk/services/submission.service';
import { DraftService } from '../../../features/desk/services/draft.service';
import { LanguageService } from '../../../core/i18n/language.service';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: 'fc-form-filler',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatSnackBarModule, AvatarComponent, StatusChipComponent, ReactiveFormsModule],
  templateUrl: './form-filler.component.html',
  styleUrl: './form-filler.component.scss',
})
export class FormFillerComponent implements OnInit, OnDestroy {
  showCustomerPicker = false;
  templateId = '';
  templateName = 'طلب فتح حساب جاري للأفراد';
  templateCode = 'AC-001 · v4.2';
  loading = true;
  error: string | null = null;

  template: FillTemplate | null = null;
  formGroup: FormGroup;
  draftId: string | null = null;
  currentLanguage = 'ar';

  sections: any[] = [];
  sideSections: any[] = [];
  recentCustomers: string[] = [];
  customerResults: any[] = [];
  visibleFields = new Set<string>();
  requiredFields = new Set<string>();
  hasUnsavedChanges = false;

  private destroy$ = new Subject<void>();

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private snackBar: MatSnackBar,
    private formFillerService: FormFillerService,
    private conditionEngineService: ConditionEngineService,
    private autoFillService: AutoFillService,
    private tafqeetService: FillerTafqeetService,
    private validationService: ValidationService,
    private submissionService: SubmissionService,
    private draftService: DraftService,
    private languageService: LanguageService,
    private fb: FormBuilder,
  ) {
    this.formGroup = this.fb.group({});
  }

  ngOnInit(): void {
    this.templateId = this.route.snapshot.paramMap.get('templateId') || '';
    this.draftId = this.route.snapshot.queryParamMap.get('draftId');
    const lang = this.languageService.getLanguage();
    this.currentLanguage = lang === 'ar' ? 'ar' : 'en';

    if (this.templateId) {
      this.loading = true;
      this.formFillerService.getTemplate(this.templateId).subscribe({
        next: (template: FillTemplate) => {
          this.template = template;
          this.templateName = template.name;
          this.templateCode = `v${template.version}`;

          this.buildFormFromTemplate(template);

          if (this.draftId) {
            this.loadDraft(this.draftId);
          } else {
            this.loading = false;
          }

          this.error = null;
        },
        error: (err) => {
          console.error('Failed to load template:', err);
          this.loading = false;
          this.error = 'Failed to load template';
        },
      });
    } else {
      this.loading = false;
      this.error = 'No template ID provided';
    }
  }

  ngOnDestroy(): void {
    if (this.hasUnsavedChanges && this.templateId) {
      this.saveDraft();
    }
    this.destroy$.next();
    this.destroy$.complete();
  }

  private buildFormFromTemplate(template: FillTemplate): void {
    const controls: Record<string, any> = {};

    this.sections = [];
    this.sideSections = [];

    template.pages.forEach((page, pageIndex) => {
      const sectionNumber = String(pageIndex + 1);

      page.elements.forEach((element: TemplateElement) => {
        const validators = [];

        if (element.required) {
          validators.push(Validators.required);
        }

        if (element.validation) {
          const customValidators = this.validationService.getValidatorFn(element);
          validators.push(...customValidators);
        }

        controls[element.key] = ['', validators];
      });

      this.sections.push({
        number: sectionNumber,
        title: `صفحة ${sectionNumber}`,
        complete: false,
        fields: page.elements.map((el: TemplateElement) => ({
          key: el.key,
          type: el.type,
          label: this.currentLanguage === 'ar' ? el.label_ar : el.label_en,
          placeholder: '',
          required: el.required,
          validation: el.validation,
          options: (el as any).options || [],
          element: el,
        })),
        columns: 2,
      });

      this.sideSections.push({
        number: sectionNumber,
        label: `صفحة ${sectionNumber}`,
        state: pageIndex === 0 ? 'active' : 'pending',
        count: `0/${page.elements.length}`,
      });
    });

    this.formGroup = this.fb.group(controls);

    const conditionalElements: ConditionalElement[] = [];
    const allElements = template.pages.flatMap(p => p.elements);
    allElements.forEach(el => {
      conditionalElements.push({
        key: el.key,
        required: el.required,
        visible_when: (el as any).visible_when,
        required_when: (el as any).required_when,
      });
    });

    this.conditionEngineService.initialize(conditionalElements, this.formGroup);

    this.conditionEngineService.visibilityChanged$
      .pipe(takeUntil(this.destroy$))
      .subscribe(visibleKeys => {
        this.visibleFields = visibleKeys;
      });

    this.conditionEngineService.requiredChanged$
      .pipe(takeUntil(this.destroy$))
      .subscribe(requiredKeys => {
        this.requiredFields = requiredKeys;
        requiredKeys.forEach(key => {
          const control = this.formGroup.get(key);
          if (control) {
            const validators = control.validator ? [control.validator] : [];
            validators.push(Validators.required);
            control.setValidators(validators);
            control.updateValueAndValidity({ emitEvent: false });
          }
        });
      });

    this.formGroup.valueChanges
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.hasUnsavedChanges = true;
      });
  }

  private loadDraft(draftId: string): void {
    this.draftService.getDraft(draftId).subscribe({
      next: (draft: any) => {
        if (draft.field_values) {
          this.formGroup.patchValue(draft.field_values);
        }

        if (this.template && draft.template_version && draft.template_version !== this.template.version) {
          this.snackBar.open(
            `تحذير: تم تحديث النموذج منذ حفظ هذه المسودة. الإصدار المحفوظ: v${draft.template_version}، الإصدار الحالي: v${this.template.version}`,
            'تحديث',
            { duration: 7000 }
          );
        }

        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load draft:', err);
        this.loading = false;
      },
    });
  }

  goBack(): void {
    this.router.navigate(['/ui/desk']);
  }

  saveDraft(): void {
    if (!this.templateId) {
      return;
    }

    const templateVersion = this.template?.version || 1;

    if (this.draftId) {
      this.draftService.updateDraft(this.draftId, this.formGroup.value).subscribe({
        next: () => {
          this.hasUnsavedChanges = false;
          this.snackBar.open('تم حفظ المسودة بنجاح', '', { duration: 3000 });
        },
        error: (err) => {
          console.error('Failed to save draft:', err);
          this.snackBar.open('فشل حفظ المسودة', '', { duration: 3000 });
        },
      });
    } else {
      this.draftService.saveDraft(this.templateId, templateVersion, this.formGroup.value).subscribe({
        next: (response: any) => {
          this.draftId = response.id;
          this.hasUnsavedChanges = false;
          this.snackBar.open('تم حفظ المسودة بنجاح', '', { duration: 3000 });
        },
        error: (err) => {
          console.error('Failed to save draft:', err);
          this.snackBar.open('فشل حفظ المسودة', '', { duration: 3000 });
        },
      });
    }
  }

  submitForm(): void {
    if (!this.templateId || !this.formGroup.valid) {
      this.snackBar.open('يرجى ملء جميع الحقول المطلوبة', '', { duration: 3000 });
      return;
    }

    const templateVersion = this.template?.version || 1;

    this.submissionService.submit(this.templateId, templateVersion, this.formGroup.value).subscribe({
      next: (response: any) => {
        this.snackBar.open('تم إرسال النموذج بنجاح', '', { duration: 3000 });
        setTimeout(() => {
          this.router.navigate(['/ui/desk']);
        }, 2000);
      },
      error: (err) => {
        console.error('Failed to submit form:', err);
        this.snackBar.open('فشل إرسال النموذج', '', { duration: 3000 });
      },
    });
  }

  printPdf(): void {
    if (this.templateId) {
      this.router.navigate(['/desk/fill', this.templateId], { queryParams: { print: true } });
    } else {
      this.snackBar.open('افتح النموذج من مكتب النماذج للطباعة', '', { duration: 3000 });
    }
  }

  openCustomerPicker(): void {
    this.showCustomerPicker = true;
  }

  closeCustomerPicker(): void {
    this.showCustomerPicker = false;
  }

  createNewCustomer(): void {
    this.closeCustomerPicker();
    this.router.navigate(['/desk/customers/new']);
  }

  private calculateCompletion(): number {
    const totalFields = Object.keys(this.formGroup.controls).length;
    if (totalFields === 0) return 0;

    const filledFields = Object.keys(this.formGroup.controls).filter(
      (key) => this.formGroup.get(key)?.value
    ).length;

    return Math.round((filledFields / totalFields) * 100);
  }
}

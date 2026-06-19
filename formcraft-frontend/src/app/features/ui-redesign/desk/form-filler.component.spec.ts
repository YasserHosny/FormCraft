import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormBuilder } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { TranslateService } from '@ngx-translate/core';
import { Observable, Subject, of, throwError } from 'rxjs';
import { AutoFillService } from '../../../features/desk/services/auto-fill.service';
import { ConditionEngineService } from '../../../features/desk/services/condition-engine.service';
import { CustomerService } from '../../../features/desk/services/customer.service';
import { DraftService } from '../../../features/desk/services/draft.service';
import { FillTemplate, FormFillerService } from '../../../features/desk/services/form-filler.service';
import { FillerTafqeetService } from '../../../features/desk/services/filler-tafqeet.service';
import { SubmissionService } from '../../../features/desk/services/submission.service';
import { ValidationService } from '../../../features/desk/services/validation.service';
import { AuthService } from '../../../core/auth/auth.service';
import { LanguageService } from '../../../core/i18n/language.service';
import { FormFillerComponent } from './form-filler.component';

describe('FormFillerComponent', () => {
  let component: FormFillerComponent;
  let fixture: ComponentFixture<FormFillerComponent>;
  let visibility$: Subject<Set<string>>;
  let required$: Subject<Set<string>>;
  let formFillerService: jasmine.SpyObj<FormFillerService>;
  let draftService: jasmine.SpyObj<DraftService>;
  let submissionService: jasmine.SpyObj<SubmissionService>;
  let tafqeetService: jasmine.SpyObj<FillerTafqeetService>;
  let customerService: jasmine.SpyObj<CustomerService>;
  let autoFillService: jasmine.SpyObj<AutoFillService>;
  let conditionEngine: jasmine.SpyObj<ConditionEngineService>;
  let dialog: jasmine.SpyObj<MatDialog>;
  let translate: jasmine.SpyObj<TranslateService>;
  let router: jasmine.SpyObj<Router>;

  const template: FillTemplate = {
    id: 'tpl-001',
    name: 'Real Account Form',
    version: 7,
    language: 'ar',
    country: 'AE',
    is_deprecated: false,
    pages: [{
      id: 'page-1',
      sort_order: 1,
      width_mm: 210,
      height_mm: 297,
      elements: [
        { id: 'name-id', key: 'name', type: 'text', label_ar: 'الاسم', label_en: 'Name', required: true, direction: 'auto', sort_order: 1, validation: null, formatting: {} },
        { id: 'hidden-id', key: 'hidden_required', type: 'text', label_ar: 'مخفي', label_en: 'Hidden', required: true, direction: 'auto', sort_order: 2, validation: null, formatting: {} },
        { id: 'amount-id', key: 'amount', type: 'number', label_ar: 'المبلغ', label_en: 'Amount', required: false, direction: 'auto', sort_order: 3, validation: null, formatting: { currency_code: 'AED' }, tafqeet_enabled: true },
      ],
    }],
  };

  beforeEach(async () => {
    visibility$ = new Subject<Set<string>>();
    required$ = new Subject<Set<string>>();
    formFillerService = jasmine.createSpyObj<FormFillerService>('FormFillerService', ['getTemplate']);
    conditionEngine = jasmine.createSpyObj('ConditionEngineService', ['initialize', 'destroy', 'resolveDefaults']);
    conditionEngine.visibilityChanged$ = visibility$.asObservable();
    conditionEngine.requiredChanged$ = required$.asObservable();
    conditionEngine.resolveDefaults.and.returnValue({});
    autoFillService = jasmine.createSpyObj<AutoFillService>('AutoFillService', ['executeAutoFill']);
    tafqeetService = jasmine.createSpyObj<FillerTafqeetService>('FillerTafqeetService', ['compute']);
    const validationService = jasmine.createSpyObj<ValidationService>('ValidationService', ['getValidatorFn']);
    submissionService = jasmine.createSpyObj<SubmissionService>('SubmissionService', ['submit']);
    draftService = jasmine.createSpyObj<DraftService>('DraftService', ['getDraft', 'saveDraft', 'updateDraft']);
    customerService = jasmine.createSpyObj<CustomerService>('CustomerService', ['search', 'getAutoPopulateData']);
    dialog = jasmine.createSpyObj<MatDialog>('MatDialog', ['open']);
    translate = jasmine.createSpyObj<TranslateService>('TranslateService', ['instant']);
    (translate as any).onLangChange = new Subject();
    router = jasmine.createSpyObj<Router>('Router', ['navigate']);

    formFillerService.getTemplate.and.returnValue(of(template));
    draftService.saveDraft.and.returnValue(of({ id: 'draft-1', updated_at: '2026-06-01T00:00:00Z' } as any));
    draftService.updateDraft.and.returnValue(of({ id: 'draft-1', updated_at: '2026-06-01T00:00:00Z' } as any));
    validationService.getValidatorFn.and.returnValue([]);
    tafqeetService.compute.and.returnValue(of('one thousand'));
    translate.instant.and.callFake((key: string, params?: any) => {
      if (key === 'desk.page_number') return `Page ${params.n}`;
      return key;
    });

    await TestBed.configureTestingModule({
      imports: [FormFillerComponent],
      providers: [
        { provide: ActivatedRoute, useValue: { snapshot: { paramMap: { get: () => 'tpl-001' }, queryParamMap: { get: () => null } } } },
        { provide: Router, useValue: router },
        { provide: MatSnackBar, useValue: jasmine.createSpyObj<MatSnackBar>('MatSnackBar', ['open']) },
        { provide: MatDialog, useValue: dialog },
        { provide: FormFillerService, useValue: formFillerService },
        { provide: ConditionEngineService, useValue: conditionEngine },
        { provide: AutoFillService, useValue: autoFillService },
        { provide: CustomerService, useValue: customerService },
        { provide: FillerTafqeetService, useValue: tafqeetService },
        { provide: ValidationService, useValue: validationService },
        { provide: SubmissionService, useValue: submissionService },
        { provide: DraftService, useValue: draftService },
        { provide: AuthService, useValue: { getCurrentUser: () => ({ role: 'operator' }) } },
        { provide: LanguageService, useValue: { getLanguage: () => 'en' } },
        { provide: TranslateService, useValue: translate },
        FormBuilder,
      ],
    }).compileComponents();

    localStorage.clear();
    fixture = TestBed.createComponent(FormFillerComponent);
    component = fixture.componentInstance;
  });

  it('loads real template metadata and translated section labels', () => {
    component.ngOnInit();

    expect(component.templateName).toBe('Real Account Form');
    expect(component.templateCode).toBe('v7');
    expect(component.sections[0].title).toBe('Page 1');
  });

  it('tears down the condition engine and stops syncing visibility on destroy', () => {
    component.ngOnInit();
    component.ngOnDestroy();

    expect(conditionEngine.destroy).toHaveBeenCalled();

    // After destroy, emissions on the (now-unsubscribed) stream are ignored.
    visibility$.next(new Set(['name']));
    expect(component.visibleKeys.has('name')).toBeFalse();
  });

  it('excludes hidden controls from the submission payload', () => {
    component.ngOnInit();
    component.formGroup.patchValue({ name: 'Alice', hidden_required: 'secret' });
    visibility$.next(new Set(['name']));
    submissionService.submit.and.returnValue(of({ reference_number: 'REF-1' } as any));

    component.submitForm();

    expect(submissionService.submit).toHaveBeenCalledWith('tpl-001', 7, { name: 'Alice' });
    expect(router.navigate).toHaveBeenCalledWith(
      ['/ui/desk/submission-confirmed'],
      jasmine.objectContaining({ state: jasmine.objectContaining({ referenceNumber: 'REF-1' }) }),
    );
  });

  it('creates a draft, then updates it once a draft id exists', () => {
    component.ngOnInit();
    component.formGroup.get('name')?.setValue('Alice');

    component.saveDraft();
    expect(draftService.saveDraft).toHaveBeenCalledWith('tpl-001', 7, jasmine.any(Object));

    // saveDraft response sets draftId; the next save should update.
    component.formGroup.get('hidden_required')?.setValue('Done');
    component.saveDraft();
    expect(draftService.updateDraft).toHaveBeenCalledWith('draft-1', jasmine.any(Object));
  });

  it('surfaces a submit error when submission fails', () => {
    component.ngOnInit();
    component.formGroup.get('name')?.setValue('Alice');
    visibility$.next(new Set(['name']));
    submissionService.submit.and.returnValue(throwError(() => new Error('network')));

    component.submitForm();

    expect(component.submitting).toBeFalse();
    expect(component.submitError).toBe('desk.form_filler.submit_failed');
  });

  it('auto-fills the form from the customer picker selection', () => {
    component.ngOnInit();
    dialog.open.and.returnValue({ afterClosed: () => of({ id: 'customer-1', name: 'Fatima' }) } as any);
    customerService.getAutoPopulateData.and.returnValue(
      of({ mappings: [{ target_element_key: 'name', source_column: 'name' }], values: { name: 'Fatima' } } as any),
    );

    component.openCustomerPicker();

    expect(customerService.getAutoPopulateData).toHaveBeenCalledWith('customer-1', 'tpl-001');
    expect(autoFillService.executeAutoFill).toHaveBeenCalled();
  });

  it('computes inline tafqeet text when a tafqeet-enabled amount changes', () => {
    component.ngOnInit();

    component.formGroup.get('amount')?.setValue(1000);

    expect(tafqeetService.compute).toHaveBeenCalledWith(1000, jasmine.objectContaining({ currency_code: 'SAR' }));
    expect(component.tafqeetValues.get('amount')).toBe('one thousand');
  });

  it('cleans up the template subscription stream on destroy', () => {
    let active = 0;
    formFillerService.getTemplate.and.returnValue(new Observable<FillTemplate>(() => {
      active += 1;
      return () => { active -= 1; };
    }));

    component.ngOnInit();
    expect(active).toBe(1);
    component.ngOnDestroy();
  });
});

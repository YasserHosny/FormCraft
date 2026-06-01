import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
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
        { id: 'amount-id', key: 'amount', type: 'number', label_ar: 'المبلغ', label_en: 'Amount', required: false, direction: 'auto', sort_order: 3, validation: null, formatting: { tafqeet_enabled: true, currency_code: 'AED' } },
      ],
    }],
  };

  beforeEach(async () => {
    visibility$ = new Subject<Set<string>>();
    required$ = new Subject<Set<string>>();
    formFillerService = jasmine.createSpyObj<FormFillerService>('FormFillerService', ['getTemplate']);
    const conditionEngine = jasmine.createSpyObj('ConditionEngineService', ['initialize', 'destroy', 'resolveDefaults']);
    conditionEngine.visibilityChanged$ = visibility$.asObservable();
    conditionEngine.requiredChanged$ = required$.asObservable();
    conditionEngine.resolveDefaults.and.returnValue({});
    autoFillService = jasmine.createSpyObj<AutoFillService>('AutoFillService', ['executeAutoFill']);
    tafqeetService = jasmine.createSpyObj<FillerTafqeetService>('FillerTafqeetService', ['compute']);
    const validationService = jasmine.createSpyObj<ValidationService>('ValidationService', ['getValidatorFn']);
    submissionService = jasmine.createSpyObj<SubmissionService>('SubmissionService', ['submit']);
    draftService = jasmine.createSpyObj<DraftService>('DraftService', ['getDraft', 'saveDraft', 'updateDraft']);
    customerService = jasmine.createSpyObj<CustomerService>('CustomerService', ['search', 'getAutoPopulateData']);
    translate = jasmine.createSpyObj<TranslateService>('TranslateService', ['instant']);
    router = jasmine.createSpyObj<Router>('Router', ['navigate']);

    formFillerService.getTemplate.and.returnValue(of(template));
    draftService.saveDraft.and.returnValue(of({ id: 'draft-1', updated_at: '2026-06-01T00:00:00Z' } as any));
    draftService.updateDraft.and.returnValue(of({ id: 'draft-1', updated_at: '2026-06-01T00:00:00Z' } as any));
    validationService.getValidatorFn.and.returnValue([]);
    tafqeetService.compute.and.returnValue(of('one thousand'));
    translate.instant.and.callFake((key: string, params?: any) => {
      if (key === 'DESK.FILL.PAGE_LABEL') return `Page ${params.number}`;
      if (key === 'DESK.FILL.SUBMIT_SUCCESS') return `Submitted ${params.ref}`;
      return key;
    });

    await TestBed.configureTestingModule({
      imports: [FormFillerComponent],
      providers: [
        { provide: ActivatedRoute, useValue: { snapshot: { paramMap: { get: () => 'tpl-001' }, queryParamMap: { get: () => null } } } },
        { provide: Router, useValue: router },
        { provide: MatSnackBar, useValue: jasmine.createSpyObj<MatSnackBar>('MatSnackBar', ['open']) },
        { provide: FormFillerService, useValue: formFillerService },
        { provide: ConditionEngineService, useValue: conditionEngine },
        { provide: AutoFillService, useValue: autoFillService },
        { provide: CustomerService, useValue: customerService },
        { provide: FillerTafqeetService, useValue: tafqeetService },
        { provide: ValidationService, useValue: validationService },
        { provide: SubmissionService, useValue: submissionService },
        { provide: DraftService, useValue: draftService },
        { provide: LanguageService, useValue: { getLanguage: () => 'en' } },
        { provide: TranslateService, useValue: translate },
        { provide: MatDialog, useValue: jasmine.createSpyObj<MatDialog>('MatDialog', ['open']) },
        FormBuilder,
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(FormFillerComponent);
    component = fixture.componentInstance;
  });

  it('loads real template metadata and translated section labels', () => {
    component.ngOnInit();

    expect(component.templateName).toBe('Real Account Form');
    expect(component.templateCode).toBe('v7');
    expect(component.sections[0].title).toBe('Page 1');
  });

  it('cleans up the template subscription on destroy', () => {
    let activeSubscriptions = 0;
    formFillerService.getTemplate.and.returnValue(new Observable<FillTemplate>(() => {
      activeSubscriptions += 1;
      return () => { activeSubscriptions -= 1; };
    }));

    component.ngOnInit();
    component.ngOnDestroy();

    expect(activeSubscriptions).toBe(0);
  });

  it('validates only visible controls and excludes hidden controls from submission payload', () => {
    component.ngOnInit();
    component.formGroup.patchValue({ name: 'Alice', hidden_required: 'secret' });
    visibility$.next(new Set(['name']));
    submissionService.submit.and.returnValue(of({ reference_number: 'REF-1' } as any));

    component.submitForm();

    expect(component.formGroup.get('hidden_required')?.disabled).toBeTrue();
    expect(submissionService.submit).toHaveBeenCalledWith('tpl-001', 7, { name: 'Alice' });
  });

  it('persists completion percent when creating and updating drafts', () => {
    component.ngOnInit();
    visibility$.next(new Set(['name', 'hidden_required']));
    required$.next(new Set(['name', 'hidden_required']));
    component.formGroup.get('name')?.setValue('Alice');

    component.saveDraft();

    expect(draftService.saveDraft).toHaveBeenCalledWith('tpl-001', 7, jasmine.any(Object), undefined, 50);

    component.savingDraft = false;
    component.draftId = 'draft-1';
    component.formGroup.get('hidden_required')?.setValue('Done');
    component.saveDraft();

    expect(draftService.updateDraft).toHaveBeenCalledWith('draft-1', jasmine.any(Object), undefined, 100);
  });

  it('shows retry banner after submission retry exhaustion', fakeAsync(() => {
    component.ngOnInit();
    component.formGroup.get('name')?.setValue('Alice');
    visibility$.next(new Set(['name']));
    submissionService.submit.and.returnValue(throwError(() => new Error('network')));
    spyOn(console, 'error');

    component.submitForm();
    tick(7000);

    expect(component.submitting).toBeFalse();
    expect(component.showRetryBanner).toBeTrue();
    expect(component.submissionError).toBe('DESK.FILL.SUBMIT_RETRY_EXHAUSTED');
  }));

  it('supports customer auto-fill selection', () => {
    component.ngOnInit();
    customerService.getAutoPopulateData.and.returnValue(of({ mappings: [{ target_element_key: 'name', source_column: 'name' }], values: { name: 'Fatima' } } as any));

    component.openCustomerPicker();
    component.selectCustomer('customer-1');

    expect(autoFillService.executeAutoFill).toHaveBeenCalled();
    expect(component.showCustomerPicker).toBeFalse();
  });

  it('computes tafqeet values after a 100ms debounce', fakeAsync(() => {
    component.ngOnInit();

    component.formGroup.get('amount')?.setValue(1000);
    tick(99);
    expect(tafqeetService.compute).not.toHaveBeenCalled();

    tick(1);
    expect(tafqeetService.compute).toHaveBeenCalledWith(1000, jasmine.objectContaining({ currency_code: 'AED' }));
    expect(component.tafqeetValues['amount']).toBe('one thousand');
  }));

  it('keeps visibility sync and validation inside the performance smoke budget', () => {
    component.ngOnInit();
    const start = performance.now();

    visibility$.next(new Set(['name']));
    component.submitForm();

    expect(performance.now() - start).toBeLessThan(200);
    expect(component.hasSubmitted).toBeTrue();
    expect(component.formGroup.get('name')?.invalid).toBeTrue();
  });
});

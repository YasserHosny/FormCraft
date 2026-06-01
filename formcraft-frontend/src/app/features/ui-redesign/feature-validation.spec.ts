import { Directionality } from '@angular/cdk/bidi';
import { EventEmitter } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { TestBed } from '@angular/core/testing';
import { Router, Routes } from '@angular/router';
import { BehaviorSubject, NEVER, of, throwError } from 'rxjs';

import { AppRoutingModule } from '../../app-routing.module';
import { RoleGuard } from '../../core/auth/role.guard';
import { AuthService, User } from '../../core/auth/auth.service';
import { DirectionService } from '../../core/i18n/direction.service';
import { LanguageService } from '../../core/i18n/language.service';
import { ThemePreferenceService } from '../../core/services/theme-preference.service';
import { TemplateService } from '../../core/services/template.service';
import { AdminModule } from '../admin/admin.module';
import { DeskModule } from '../desk/desk.module';
import { DesignerModule } from '../designer/designer.module';
import { PlatformModule } from '../platform/platform.module';
import { TemplatesModule } from '../templates/templates.module';
import { StepStartingPointComponent } from '../templates/template-wizard/steps/step-starting-point/step-starting-point.component';
import { TemplateWizardComponent } from '../templates/template-wizard/template-wizard.component';
import { UI_REDESIGN_ROUTES } from './ui-redesign.routes';
import { ClassicRedirectComponent } from './shared/classic-redirect.component';
import { TemplateListComponent } from './studio/template-list.component';
import { DesignerComponent } from './studio/designer.component';
import { DashboardComponent } from './desk/dashboard.component';
import { FormFillerComponent } from './desk/form-filler.component';
import { CustomersComponent } from './desk/customers.component';
import { AnalyticsComponent } from './admin/analytics.component';

describe('FormCraft feature validation automation', () => {
  const flattenRoutes = (routes: Routes, prefix = ''): string[] =>
    routes.flatMap((route) => {
      const path = [prefix, route.path].filter(Boolean).join('/');
      const own = path ? [path] : [];
      return own.concat(route.children ? flattenRoutes(route.children, path) : []);
    });

  beforeEach(() => {
    localStorage.clear();
  });

  describe('new theme route matrix', () => {
    it('registers every implemented and redirected /ui route with the expected component type', () => {
      const paths = flattenRoutes(UI_REDESIGN_ROUTES);

      expect(paths).toContain('studio/templates');
      expect(paths).toContain('studio/designer/:pageId');
      expect(paths).toContain('desk');
      expect(paths).toContain('desk/fill/:templateId');
      expect(paths).toContain('desk/customers');
      expect(paths).toContain('desk/customers/:id');
      expect(paths).toContain('desk/history');
      expect(paths).toContain('desk/queue');
      expect(paths).toContain('admin/analytics');
      expect(paths).toContain('admin/reviews');
      expect(paths).toContain('admin/governance');
      expect(paths).toContain('admin/settings');
      expect(paths).toContain('admin/users');
      expect(paths).toContain('admin/departments');

      const children = UI_REDESIGN_ROUTES[0].children || [];
      const redirected = children
        .filter((route) => route.component === ClassicRedirectComponent)
        .map((route) => route.path);

      expect(redirected).toEqual([
        'desk/customers/:id',
        'desk/history',
        'desk/queue',
        'admin/reviews',
        'admin/governance',
        'admin/settings',
        'admin/users',
        'admin/departments',
      ]);
    });
  });

  describe('classic route matrix', () => {
    let router: Router;

    beforeEach(() => {
      TestBed.resetTestingModule();
      TestBed.configureTestingModule({
        imports: [AppRoutingModule],
      });
      router = TestBed.inject(Router);
    });

    it('mounts standalone classic features from the checklist', () => {
      const topLevel = router.config.map((route) => route.path);

      expect(topLevel).toContain('templates');
      expect(topLevel).toContain('designer');
      expect(topLevel).toContain('desk');
      expect(topLevel).toContain('admin/analytics');
      expect(topLevel).toContain('platform');
      expect(topLevel).toContain('admin/ocr-onboarding');
    });

    it('keeps specific admin classic routes before the broad /admin module route', () => {
      const paths = router.config.map((route) => route.path);

      expect(paths.indexOf('admin/analytics')).toBeLessThan(paths.indexOf('admin'));
      expect(paths.indexOf('admin/ocr-onboarding')).toBeLessThan(paths.indexOf('admin'));
    });

    it('mounts nested classic feature modules used by redirects and standalone pages', () => {
      const scenarios = [
        {
          imports: [TemplatesModule],
          paths: ['', 'new'],
        },
        {
          imports: [DesignerModule],
          paths: [':templateId'],
        },
        {
          imports: [DeskModule],
          paths: ['', 'fill', 'history', 'customers', 'customers/new', 'customers/:id', 'queue'],
        },
        {
          imports: [AdminModule],
          paths: [
            '',
            'reviews',
            'governance',
            'settings',
            'departments',
            'users',
            'export',
            'integrations',
            'reports',
            'portal',
          ],
        },
        {
          imports: [PlatformModule],
          paths: [''],
        },
      ];

      scenarios.forEach((scenario) => {
        TestBed.resetTestingModule();
        TestBed.configureTestingModule({ imports: scenario.imports });
        const paths = TestBed.inject(Router).config.map((route) => route.path);

        scenario.paths.forEach((path) => expect(paths).toContain(path));
      });
    });
  });

  describe('theme and language switching', () => {
    it('maps bidirectionally between production-ready classic and new routes', () => {
      const service = TestBed.inject(ThemePreferenceService);

      expect(service.mapRouteToTheme('/templates', 'new', 'admin')).toBe('/ui/studio/templates');
      expect(service.mapRouteToTheme('/ui/studio/templates', 'classic', 'admin')).toBe('/templates');
      expect(service.mapRouteToTheme('/ui/desk/customers/123', 'classic', 'operator')).toBe('/desk/customers/123');
      expect(service.getDefaultRoute('new', 'operator')).toBe('/ui/desk');
      expect(service.getDefaultRoute('classic', 'operator')).toBe('/desk');
    });

    it('switches Arabic and English language direction on the document', () => {
      const translate = jasmine.createSpyObj('TranslateService', ['setDefaultLang', 'use']);
      const directionality = {
        value: 'rtl',
        change: new EventEmitter<'rtl' | 'ltr'>(),
      } as unknown as Directionality;
      const direction = new DirectionService(directionality);
      const service = new LanguageService(translate, direction);

      service.setLanguage('en');
      expect(document.documentElement.lang).toBe('en');
      expect(document.documentElement.dir).toBe('ltr');
      expect(document.body.dir).toBe('ltr');

      service.setLanguage('ar');
      expect(document.documentElement.lang).toBe('ar');
      expect(document.documentElement.dir).toBe('rtl');
      expect(document.body.dir).toBe('rtl');
    });
  });

  describe('role-based access', () => {
    let users$: BehaviorSubject<User | null>;
    let navigations: unknown[][];
    let guard: RoleGuard;

    beforeEach(() => {
      users$ = new BehaviorSubject<User | null>(null);
      navigations = [];
      TestBed.configureTestingModule({
        providers: [
          RoleGuard,
          ThemePreferenceService,
          {
            provide: AuthService,
            useValue: { currentUser$: users$.asObservable() },
          },
          {
            provide: Router,
            useValue: { navigate: (args: unknown[]) => navigations.push(args) },
          },
        ],
      });
      guard = TestBed.inject(RoleGuard);
    });

    it('allows each listed role only through routes that include that role', (done) => {
      users$.next({
        id: 'designer-1',
        email: 'designer@example.com',
        role: 'designer',
        language: 'ar',
        display_name: 'Designer',
      });

      guard.canActivate({ data: { roles: ['admin', 'designer'] } } as any).subscribe((allowed) => {
        expect(allowed).toBeTrue();
        expect(navigations).toEqual([]);
        done();
      });
    });

    it('redirects disallowed roles to their role/theme default route', (done) => {
      localStorage.setItem('fc_theme_preference', 'new');
      users$.next({
        id: 'operator-1',
        email: 'operator@example.com',
        role: 'operator',
        language: 'ar',
        display_name: 'Operator',
      });

      guard.canActivate({ data: { roles: ['admin'] } } as any).subscribe((allowed) => {
        expect(allowed).toBeFalse();
        expect(navigations).toEqual([['/ui/desk']]);
        done();
      });
    });
  });

  describe('implemented new-theme page behavior', () => {
    it('validates template cards, filtering, clone/delete/publish actions', () => {
      const component = new TemplateListComponent(
        jasmine.createSpyObj<TemplateService>('TemplateService', {
          list: of({ data: [], total: 0, page: 1, limit: 100 }),
          delete: of(undefined),
          publish: of({}),
          createNewVersion: of({ id: 'tpl-2', version: 2 }),
        }),
        jasmine.createSpyObj<Router>('Router', ['navigate']),
        jasmine.createSpyObj('MatDialog', { open: { afterClosed: () => of(true) } }),
        jasmine.createSpyObj('MatSnackBar', ['open']),
      );
      const template = {
        id: 'tpl-1',
        name: 'Account Opening',
        code: 'ACC-001',
        status: 'draft',
        version: 'v1',
        dept: 'الحسابات',
        updated: 'اليوم',
        by: 'النظام',
        color: 'c1',
        submissions: 0,
        pages: 1,
        fields: 3,
      };
      component.templates = [template];

      component.search = 'account';
      expect(component.filteredTemplates.length).toBe(1);

      const event = jasmine.createSpyObj<Event>('Event', ['stopPropagation']);
      spyOn(window, 'confirm').and.returnValue(true);
      component.cloneTemplate(event, template);
      component.publishTemplate(event, template);
      component.deleteTemplate(event, template);

      expect(event.stopPropagation).toHaveBeenCalled();
    });

    it('validates designer canvas, palette, properties panel, and actions', () => {
      const router = jasmine.createSpyObj<Router>('Router', ['navigate']);
      const snackBar = jasmine.createSpyObj('MatSnackBar', ['open']);
      const component = new DesignerComponent(
        { snapshot: { paramMap: new Map([['pageId', 'tpl-1']]) } } as any,
        router,
        snackBar,
        jasmine.createSpyObj<TemplateService>('TemplateService', {
          get: of({ id: 'tpl-1', name: 'Template', version: 3 }),
          publish: of({}),
        }),
      );

      component.ngOnInit();
      expect(component.paletteGroups.length).toBeGreaterThan(0);
      expect(component.canvasFields.some((field) => field.selected)).toBeTrue();
      expect(component.propTabs.map((tab) => tab.key)).toEqual(['props', 'validation', 'logic']);

      component.preview();
      component.submitForReview();

      expect(router.navigate).toHaveBeenCalledWith(['/designer', 'tpl-1']);
      expect(snackBar.open).toHaveBeenCalledWith('تم إرسال النموذج للمراجعة', '', { duration: 3000 });
    });

    it('validates desk dashboard stats, pinned templates, and recent transaction actions', () => {
      const router = jasmine.createSpyObj<Router>('Router', ['navigate']);
      const component = new DashboardComponent(
        router,
        jasmine.createSpyObj<TemplateService>('TemplateService', {
          list: of({ data: [{ id: 'tpl-1', name: 'Published', status: 'published' }], total: 1, page: 1, limit: 50 }),
        }),
        jasmine.createSpyObj('DeskService', {
          getDashboard: of({ drafts: [], templates: { total: 5 }, pinned: [] }),
        }),
        jasmine.createSpyObj('HistoryService', {
          getSubmissions: of({ total: 2, items: [{ id: '1', template_name: 'Test', status: 'submitted', reference_number: 'REF-001', created_at: new Date(), key_summary: ['Customer'] }] }),
        }),
        {
          currentUser$: of({ display_name: 'Operator', email: 'operator@example.com' }),
        } as any,
      );

      component.ngOnInit();
      component.viewAllCustomers();
      component.viewAllTransactions();

      expect(component.pinnedTemplates).toBeDefined();
      expect(component.activities.length).toBeGreaterThan(-1);
      expect(router.navigate).toHaveBeenCalledWith(['/ui/desk/customers']);
      expect(router.navigate).toHaveBeenCalledWith(['/desk/history']);
    });

    it('validates form filler groups, save, print, submit, and customer picker actions', () => {
      const router = jasmine.createSpyObj<Router>('Router', ['navigate']);
      const snackBar = jasmine.createSpyObj('MatSnackBar', ['open']);
      const visibility$ = new BehaviorSubject<Set<string>>(new Set(['name']));
      const required$ = new BehaviorSubject<Set<string>>(new Set());
      const formFillerService = jasmine.createSpyObj('FormFillerService', {
        getTemplate: of({
          id: 'tpl-1',
          name: 'Fill Template',
          version: 4,
          language: 'ar',
          country: 'AE',
          is_deprecated: false,
          pages: [{
            id: 'p1',
            sort_order: 1,
            width_mm: 210,
            height_mm: 297,
            elements: [{
              id: 'e1',
              key: 'name',
              type: 'text',
              label_ar: 'الاسم',
              label_en: 'Name',
              required: false,
              direction: 'auto',
              sort_order: 1,
              validation: null,
              formatting: {},
            }],
          }],
        }),
      });
      const conditionEngine = jasmine.createSpyObj('ConditionEngineService', ['initialize', 'destroy', 'resolveDefaults']);
      conditionEngine.visibilityChanged$ = visibility$.asObservable();
      conditionEngine.requiredChanged$ = required$.asObservable();
      conditionEngine.resolveDefaults.and.returnValue({});
      const translate = jasmine.createSpyObj('TranslateService', ['instant']);
      translate.instant.and.callFake((key: string, params?: any) => key === 'DESK.FILL.PAGE_LABEL' ? `Page ${params.number}` : key);
      const draftService = jasmine.createSpyObj('DraftService', {
        saveDraft: of({ id: 'draft-1', updated_at: '2026-06-01T00:00:00Z' }),
        updateDraft: of({ id: 'draft-1', updated_at: '2026-06-01T00:00:00Z' }),
      });
      const submissionService = jasmine.createSpyObj('SubmissionService', {
        submit: of({ reference_number: 'REF-1' }),
      });
      const component = new FormFillerComponent(
        {
          snapshot: {
            paramMap: new Map([['templateId', 'tpl-1']]),
            queryParamMap: new Map(),
          },
        } as any,
        router,
        snackBar,
        formFillerService as any,
        conditionEngine,
        jasmine.createSpyObj('AutoFillService', ['executeAutoFill']),
        jasmine.createSpyObj('CustomerService', ['search', 'getAutoPopulateData']),
        jasmine.createSpyObj('FillerTafqeetService', { compute: of('') }),
        jasmine.createSpyObj('ValidationService', { getValidatorFn: [] }),
        submissionService,
        draftService,
        { getLanguage: () => 'ar' } as any,
        translate,
        jasmine.createSpyObj('MatDialog', ['open']),
        new FormBuilder(),
      );

      component.ngOnInit();
      component.saveDraft();
      component.printPdf();
      component.submitForm();
      component.openCustomerPicker();
      component.createNewCustomer();

      expect(component.sections.length).toBeGreaterThan(0);
      expect(snackBar.open).toHaveBeenCalledWith('DESK.FILL.DRAFT_SAVED', '', { duration: 3000 });
      expect(snackBar.open).toHaveBeenCalledWith('DESK.FILL.SUBMIT_SUCCESS', '', { duration: 3000 });
      expect(router.navigate).toHaveBeenCalledWith(['/desk/fill', 'tpl-1'], { queryParams: { print: true } });
      expect(router.navigate).toHaveBeenCalledWith(['/desk/customers/new']);
    });

    it('validates customer table add/view/fill actions', () => {
      const router = jasmine.createSpyObj<Router>('Router', ['navigate']);
      const customerService = jasmine.createSpyObj('CustomerService', {
        list: of({ items: [{ id: 'cust-1', name: 'Customer' }], total: 1 }),
      });
      const component = new CustomersComponent(router, customerService);

      component.ngOnInit();
      component.addCustomer();
      component.viewCustomer('cust-1');
      component.fillFormForCustomer();

      expect(component.customers.length).toBeGreaterThan(0);
      expect(router.navigate).toHaveBeenCalledWith(['/desk/customers/new']);
      expect(router.navigate).toHaveBeenCalledWith(['/desk/customers', 'cust-1']);
      expect(router.navigate).toHaveBeenCalledWith(['/desk']);
    });

    it('validates analytics KPIs, charts, and export action', () => {
      const router = jasmine.createSpyObj<Router>('Router', ['navigate']);
      const component = new AnalyticsComponent(router);

      expect(component.lineData.length).toBe(30);
      expect(component.donutData.length).toBeGreaterThan(0);
      expect(component.getBarWidth(component.barMax)).toBe(100);

      component.exportPdf();
      expect(router.navigate).toHaveBeenCalledWith(['/admin/analytics'], { queryParams: { export: 'pdf' } });
    });

    it('validates the classic create-template wizard starting-point choices', () => {
      const component = new StepStartingPointComponent();
      component.form = new FormBuilder().group({ type: ['blank'], cloneTemplateId: [null], packageFile: [null] });
      const createSpy = jasmine.createSpy('create');
      component.create.subscribe(createSpy);

      expect(component.options.map((option) => option.value)).toEqual(['blank', 'clone', 'ocr', 'package']);
      component.form.patchValue({ type: 'clone', cloneTemplateId: 'tpl-source' });
      component.onCreate();

      expect(component.form.value).toEqual(jasmine.objectContaining({ type: 'clone', cloneTemplateId: 'tpl-source' }));
      expect(createSpy).toHaveBeenCalled();
    });

    it('validates blank template creation through the classic wizard', () => {
      const fb = new FormBuilder();
      const wizardService = jasmine.createSpyObj('TemplateWizardService', [
        'buildBasicInfoForm',
        'buildLocaleForm',
        'buildPageSetupForm',
        'buildStartingPointForm',
        'getState',
        'setState',
        'resetState',
        'listOrgCategories',
        'createTemplate',
      ]);
      wizardService.buildBasicInfoForm.and.returnValue(fb.group({
        name: ['New Account Template'],
        description: ['Used by branch operators'],
        category: ['accounts'],
        tags: [['retail']],
      }));
      wizardService.buildLocaleForm.and.returnValue(fb.group({
        language: ['ar'],
        country: ['AE'],
        currency: ['AED'],
      }));
      wizardService.buildPageSetupForm.and.returnValue(fb.group({
        pageSize: ['A4'],
        customWidthMm: [null],
        customHeightMm: [null],
        orientation: ['portrait'],
        margins: fb.group({ top: [10], bottom: [10], left: [10], right: [10] }),
      }));
      wizardService.buildStartingPointForm.and.returnValue(fb.group({
        type: ['blank'],
        cloneTemplateId: [null],
        packageFile: [null],
      }));
      wizardService.getState.and.returnValue({
        stepIndex: 0,
        basicInfo: { name: '', description: '', category: '', tags: [] },
        locale: { language: 'ar', country: 'AE', currency: 'AED' },
        pageSetup: { pageSize: 'A4', orientation: 'portrait', margins: { top: 10, bottom: 10, left: 10, right: 10 } },
        startingPoint: { type: 'blank' },
        createdAt: new Date().toISOString(),
      });
      wizardService.listOrgCategories.and.returnValue(of({ items: [] }));
      wizardService.createTemplate.and.returnValue(of({ id: 'created-template' }));

      const router = jasmine.createSpyObj<Router>('Router', ['navigate']);
      const component = new TemplateWizardComponent(wizardService, router);

      component.onCreate();

      expect(wizardService.createTemplate).toHaveBeenCalledWith(jasmine.objectContaining({
        name: 'New Account Template',
        description: 'Used by branch operators',
        category: 'accounts',
        language: 'ar',
        country: 'AE',
        currency: 'AED',
        tags: ['retail'],
        starting_point: jasmine.objectContaining({ type: 'blank' }),
        page_setup: jasmine.objectContaining({ page_size: 'A4', orientation: 'portrait' }),
      }));
      expect(wizardService.resetState).toHaveBeenCalled();
      expect(router.navigate).toHaveBeenCalledWith(['/designer', 'created-template']);
    });

    it('keeps create-template wizard unblocked when organization categories are empty', () => {
      const fb = new FormBuilder();
      const wizardService = jasmine.createSpyObj('TemplateWizardService', [
        'buildBasicInfoForm',
        'buildLocaleForm',
        'buildPageSetupForm',
        'buildStartingPointForm',
        'getState',
        'listOrgCategories',
      ]);
      wizardService.buildBasicInfoForm.and.returnValue(fb.group({
        name: ['test'],
        description: [''],
        category: [''],
        tags: [[]],
      }));
      wizardService.buildLocaleForm.and.returnValue(fb.group({ language: ['ar'], country: ['EG'], currency: ['EGP'] }));
      wizardService.buildPageSetupForm.and.returnValue(fb.group({
        pageSize: ['A4'],
        orientation: ['portrait'],
        margins: fb.group({ top: [10], bottom: [10], left: [10], right: [10] }),
      }));
      wizardService.buildStartingPointForm.and.returnValue(fb.group({ type: ['blank'] }));
      wizardService.getState.and.returnValue({
        stepIndex: 0,
        basicInfo: { name: '', description: '', category: '', tags: [] },
        locale: { language: 'ar', country: 'EG', currency: 'EGP' },
        pageSetup: { pageSize: 'A4', orientation: 'portrait', margins: { top: 10, bottom: 10, left: 10, right: 10 } },
        startingPoint: { type: 'blank' },
        createdAt: new Date().toISOString(),
      });
      wizardService.listOrgCategories.and.returnValue(of({ items: [] }));

      const component = new TemplateWizardComponent(wizardService, jasmine.createSpyObj<Router>('Router', ['navigate']));
      component.ngOnInit();

      expect(component.categories.length).toBeGreaterThan(0);
      expect(component.basicInfoForm.get('category')?.value).toBe('الحسابات');
      expect(component.basicInfoForm.valid).toBeTrue();
    });

    it('shows fallback categories immediately before organization categories load', () => {
      const fb = new FormBuilder();
      const wizardService = jasmine.createSpyObj('TemplateWizardService', [
        'buildBasicInfoForm',
        'buildLocaleForm',
        'buildPageSetupForm',
        'buildStartingPointForm',
        'getState',
        'listOrgCategories',
      ]);
      wizardService.buildBasicInfoForm.and.returnValue(fb.group({
        name: ['test'],
        description: [''],
        category: [''],
        tags: [[]],
      }));
      wizardService.buildLocaleForm.and.returnValue(fb.group({ language: ['ar'], country: ['EG'], currency: ['EGP'] }));
      wizardService.buildPageSetupForm.and.returnValue(fb.group({
        pageSize: ['A4'],
        orientation: ['portrait'],
        margins: fb.group({ top: [10], bottom: [10], left: [10], right: [10] }),
      }));
      wizardService.buildStartingPointForm.and.returnValue(fb.group({ type: ['blank'] }));
      wizardService.getState.and.returnValue({
        stepIndex: 0,
        basicInfo: { name: '', description: '', category: '', tags: [] },
        locale: { language: 'ar', country: 'EG', currency: 'EGP' },
        pageSetup: { pageSize: 'A4', orientation: 'portrait', margins: { top: 10, bottom: 10, left: 10, right: 10 } },
        startingPoint: { type: 'blank' },
        createdAt: new Date().toISOString(),
      });
      wizardService.listOrgCategories.and.returnValue(NEVER);

      const component = new TemplateWizardComponent(wizardService, jasmine.createSpyObj<Router>('Router', ['navigate']));
      component.ngOnInit();

      expect(component.categories.map((category) => category.name)).toEqual(['الحسابات', 'الالتزام', 'التمويل', 'عام']);
      expect(component.basicInfoForm.get('category')?.value).toBe('الحسابات');
      expect(component.basicInfoForm.valid).toBeTrue();
    });

    it('normalizes backend category labels so dropdown options are not blank', () => {
      const fb = new FormBuilder();
      const wizardService = jasmine.createSpyObj('TemplateWizardService', [
        'buildBasicInfoForm',
        'buildLocaleForm',
        'buildPageSetupForm',
        'buildStartingPointForm',
        'getState',
        'listOrgCategories',
      ]);
      wizardService.buildBasicInfoForm.and.returnValue(fb.group({
        name: ['test'],
        description: [''],
        category: [''],
        tags: [[]],
      }));
      wizardService.buildLocaleForm.and.returnValue(fb.group({ language: ['ar'], country: ['EG'], currency: ['EGP'] }));
      wizardService.buildPageSetupForm.and.returnValue(fb.group({
        pageSize: ['A4'],
        orientation: ['portrait'],
        margins: fb.group({ top: [10], bottom: [10], left: [10], right: [10] }),
      }));
      wizardService.buildStartingPointForm.and.returnValue(fb.group({ type: ['blank'] }));
      wizardService.getState.and.returnValue({
        stepIndex: 0,
        basicInfo: { name: '', description: '', category: '', tags: [] },
        locale: { language: 'ar', country: 'EG', currency: 'EGP' },
        pageSetup: { pageSize: 'A4', orientation: 'portrait', margins: { top: 10, bottom: 10, left: 10, right: 10 } },
        startingPoint: { type: 'blank' },
        createdAt: new Date().toISOString(),
      });
      wizardService.listOrgCategories.and.returnValue(of({
        items: [
          { id: 'ops', name_ar: 'العمليات' },
          { id: 'risk', name_en: 'Risk' },
        ],
      } as any));

      const component = new TemplateWizardComponent(wizardService, jasmine.createSpyObj<Router>('Router', ['navigate']));
      component.ngOnInit();

      expect(component.categories.map((category) => category.name)).toEqual(['العمليات', 'Risk']);
      expect(component.basicInfoForm.get('category')?.value).toBe('العمليات');
    });


    it('keeps create-template wizard unblocked when category loading fails', () => {
      const fb = new FormBuilder();
      const wizardService = jasmine.createSpyObj('TemplateWizardService', [
        'buildBasicInfoForm',
        'buildLocaleForm',
        'buildPageSetupForm',
        'buildStartingPointForm',
        'getState',
        'listOrgCategories',
      ]);
      wizardService.buildBasicInfoForm.and.returnValue(fb.group({
        name: ['test'],
        description: [''],
        category: [''],
        tags: [[]],
      }));
      wizardService.buildLocaleForm.and.returnValue(fb.group({ language: ['ar'], country: ['EG'], currency: ['EGP'] }));
      wizardService.buildPageSetupForm.and.returnValue(fb.group({
        pageSize: ['A4'],
        orientation: ['portrait'],
        margins: fb.group({ top: [10], bottom: [10], left: [10], right: [10] }),
      }));
      wizardService.buildStartingPointForm.and.returnValue(fb.group({ type: ['blank'] }));
      wizardService.getState.and.returnValue({
        stepIndex: 0,
        basicInfo: { name: '', description: '', category: '', tags: [] },
        locale: { language: 'ar', country: 'EG', currency: 'EGP' },
        pageSetup: { pageSize: 'A4', orientation: 'portrait', margins: { top: 10, bottom: 10, left: 10, right: 10 } },
        startingPoint: { type: 'blank' },
        createdAt: new Date().toISOString(),
      });
      wizardService.listOrgCategories.and.returnValue(throwError(() => new Error('category load failed')));

      const component = new TemplateWizardComponent(wizardService, jasmine.createSpyObj<Router>('Router', ['navigate']));
      component.ngOnInit();

      expect(component.categories.map((category) => category.name)).toContain('الحسابات');
      expect(component.basicInfoForm.get('category')?.value).toBe('الحسابات');
      expect(component.basicInfoForm.valid).toBeTrue();
    });
  });
});

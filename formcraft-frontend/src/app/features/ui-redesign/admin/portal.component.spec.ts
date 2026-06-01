import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { TranslateFakeLoader, TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { of, throwError } from 'rxjs';

import { PortalComponent } from './portal.component';
import { PortalService } from '../../../core/services/portal.service';

class MockPortalService {
  listPortalTemplates = jasmine.createSpy('listPortalTemplates').and.returnValue(of({
    items: [
      {
        template_id: 't1',
        public_slug: 'invoice-form',
        public_url: 'https://example.com/p/invoice-form',
        public_qr_svg: null,
        enabled: true,
        verification_required: true,
        allowed_otp_modes: ['sms', 'email'],
        captcha_enabled: false,
        captcha_provider: null,
        allow_pdf_download: true,
        send_email_confirmation: true,
        rate_limit_max: 100,
        rate_limit_window_minutes: 60,
      },
    ],
  }));
  getPortalAnalytics = jasmine.createSpy('getPortalAnalytics').and.returnValue(of({
    submission_count: 42,
    otp_sent_count: 10,
    otp_failure_count: 1,
    rate_limited_count: 0,
    email_confirmation_failure_count: 2,
  }));
  updatePortalTemplate = jasmine.createSpy('updatePortalTemplate').and.returnValue(of({
    template_id: 't1',
    public_slug: 'invoice-form',
    public_url: 'https://example.com/p/invoice-form',
    public_qr_svg: null,
    enabled: true,
    verification_required: true,
    allowed_otp_modes: ['sms', 'email'],
    captcha_enabled: false,
    captcha_provider: null,
    allow_pdf_download: true,
    send_email_confirmation: true,
    rate_limit_max: 100,
    rate_limit_window_minutes: 60,
  }));
}

describe('PortalComponent', () => {
  let component: PortalComponent;
  let fixture: ComponentFixture<PortalComponent>;
  let mockService: MockPortalService;

  beforeEach(async () => {
    mockService = new MockPortalService();

    await TestBed.configureTestingModule({
      imports: [
        PortalComponent,
        BrowserAnimationsModule,
        TranslateModule.forRoot({ loader: { provide: TranslateLoader, useClass: TranslateFakeLoader } }),
      ],
      providers: [
        { provide: PortalService, useValue: mockService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(PortalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('loads templates on init', () => {
    expect(mockService.listPortalTemplates).toHaveBeenCalled();
    expect(component.templates.length).toBe(1);
  });

  it('selects a template and loads analytics', () => {
    const tpl = component.templates[0];
    component.selectTemplate(tpl);
    fixture.detectChanges();
    expect(component.selectedTemplate?.template_id).toBe('t1');
    expect(mockService.getPortalAnalytics).toHaveBeenCalledWith('t1');
  });

  it('saves successfully', () => {
    component.selectedTemplate = { ...component.templates[0] };
    component.save();
    fixture.detectChanges();
    expect(component.success).toBeTrue();
  });

  it('shows error on save failure', () => {
    mockService.updatePortalTemplate.and.returnValue(throwError(() => ({ error: { detail: 'Slug taken' } })));
    component.selectedTemplate = { ...component.templates[0] };
    component.save();
    fixture.detectChanges();
    expect(component.error).toContain('Slug taken');
  });

  it('preserves edited form state on save failure', () => {
    mockService.updatePortalTemplate.and.returnValue(throwError(() => ({ error: { detail: 'fail' } })));
    component.selectedTemplate = { ...component.templates[0], public_slug: 'edited-slug' };
    component.save();
    fixture.detectChanges();
    expect(component.selectedTemplate?.public_slug).toBe('edited-slug');
  });
});

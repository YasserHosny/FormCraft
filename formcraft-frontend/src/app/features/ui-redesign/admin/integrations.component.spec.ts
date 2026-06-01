import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { TranslateFakeLoader, TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { of, throwError } from 'rxjs';

import { IntegrationsComponent } from './integrations.component';
import { IntegrationService } from '../../../core/services/integration.service';

class MockIntegrationService {
  listCredentials = jasmine.createSpy('listCredentials').and.returnValue(of({
    items: [
      { id: 'c1', name: 'Production Key', key_prefix: 'prod_****', scopes: ['read', 'write'], status: 'active', expires_at: null, created_at: '2026-01-01T00:00:00Z' },
      { id: 'c2', name: 'Old Key', key_prefix: 'old_****', scopes: ['read'], status: 'revoked', expires_at: null, created_at: '2026-01-01T00:00:00Z' },
    ],
  }));
  listWebhooks = jasmine.createSpy('listWebhooks').and.returnValue(of({
    items: [
      { id: 'w1', name: 'Submission Hook', event_type: 'form_submitted', target_url: 'https://example.com/hook', status: 'active', created_at: '2026-01-01T00:00:00Z' },
      { id: 'w2', name: 'Paused Hook', event_type: 'form_printed', target_url: 'https://example.com/hook2', status: 'paused', created_at: '2026-01-01T00:00:00Z' },
      { id: 'w3', name: 'Disabled Hook', event_type: 'template_published', target_url: 'https://example.com/hook3', status: 'disabled', created_at: '2026-01-01T00:00:00Z' },
    ],
  }));
  revokeCredential = jasmine.createSpy('revokeCredential').and.returnValue(of({}));
  updateWebhook = jasmine.createSpy('updateWebhook').and.returnValue(of({}));
}

describe('IntegrationsComponent', () => {
  let component: IntegrationsComponent;
  let fixture: ComponentFixture<IntegrationsComponent>;
  let mockService: MockIntegrationService;

  beforeEach(async () => {
    mockService = new MockIntegrationService();

    await TestBed.configureTestingModule({
      imports: [
        IntegrationsComponent,
        BrowserAnimationsModule,
        TranslateModule.forRoot({ loader: { provide: TranslateLoader, useClass: TranslateFakeLoader } }),
      ],
      providers: [
        { provide: IntegrationService, useValue: mockService },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(IntegrationsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('loads credentials and webhooks on init', () => {
    expect(mockService.listCredentials).toHaveBeenCalled();
    expect(mockService.listWebhooks).toHaveBeenCalled();
    expect(component.credentials.length).toBe(2);
    expect(component.webhooks.length).toBe(3);
  });

  it('revokes active credentials only', () => {
    const activeCredential = component.credentials[0];
    expect(component.canRevoke(activeCredential)).toBeTrue();
    component.revokeCredential(activeCredential.id);
    expect(mockService.revokeCredential).toHaveBeenCalledWith('c1');
  });

  it('does not enable revoke for revoked credentials', () => {
    const revokedCredential = component.credentials[1];
    expect(component.canRevoke(revokedCredential)).toBeFalse();
  });

  it('toggles active and paused webhooks', () => {
    const activeWebhook = component.webhooks[0];
    expect(component.canToggle(activeWebhook)).toBeTrue();
    component.toggleWebhook(activeWebhook);
    expect(mockService.updateWebhook).toHaveBeenCalledWith('w1', { status: 'paused' });
  });

  it('does not toggle disabled webhooks', () => {
    const disabledWebhook = component.webhooks[2];
    expect(component.canToggle(disabledWebhook)).toBeFalse();
  });

  it('does not expose create-credential controls', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).not.toContain('Create Credential');
    expect(compiled.textContent).not.toContain('Create Webhook');
  });
});

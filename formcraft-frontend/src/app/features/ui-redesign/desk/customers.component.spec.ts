import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CustomersComponent } from './customers.component';
import { RouterTestingModule } from '@angular/router/testing';
import { MatIconModule } from '@angular/material/icon';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { TranslateFakeLoader, TranslateLoader, TranslateModule, TranslateService } from '@ngx-translate/core';
import { of } from 'rxjs';
import { CustomerService } from '../../../features/desk/services/customer.service';

describe('CustomersComponent - User Story 6: Real Customer Data', () => {
  let component: CustomersComponent;
  let fixture: ComponentFixture<CustomersComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        CustomersComponent,
        RouterTestingModule,
        MatIconModule,
        NoopAnimationsModule,
        TranslateModule.forRoot({
          loader: { provide: TranslateLoader, useClass: TranslateFakeLoader },
        }),
      ],
      providers: [
        {
          provide: CustomerService,
          useValue: { list: jasmine.createSpy('list').and.returnValue(of({ items: [], total: 0 })) },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(CustomersComponent);
    component = fixture.componentInstance;
    TestBed.inject(TranslateService).use('ar');
  });

  describe('Customer List Display', () => {
    it('should display loading state while fetching', () => {
      component.loading = true;
      fixture.detectChanges();

      const loadingState = fixture.nativeElement.querySelector('.loading-state');
      expect(loadingState).toBeTruthy();
    });

    it('should display error state when fetch fails', () => {
      component.loading = false;
      component.error = 'Failed to load customers';
      fixture.detectChanges();

      const errorState = fixture.nativeElement.querySelector('.error-state');
      expect(errorState).toBeTruthy();
      expect(errorState.textContent).toContain('حدث خطأ');
    });

    it('should render customer table when data loaded', () => {
      component.loading = false;
      component.error = null;
      component.customers = [
        {
          id: '1',
          org_id: 'org-1',
          name_ar: 'فاطمة',
          name_en: 'Fatima',
          identifier_type: 'national_id',
          identifier: '123',
          contact_phone: '+971',
          contact_email: 'f@example.com',
          address: null,
          custom_fields: null,
          is_active: true,
          created_by: null,
          created_at: '2026-06-01T00:00:00Z',
          updated_at: '2026-06-01T00:00:00Z',
          color: 'c1',
        },
      ];
      fixture.detectChanges();

      const table = fixture.nativeElement.querySelector('.fc-table');
      expect(table).toBeTruthy();
    });

    it('should display Arabic name when English name is missing', () => {
      component.loading = false;
      component.error = null;
      component.customers = [
        {
          id: '1',
          name_ar: 'قاسم',
          name_en: null,
          identifier: '5566',
          identifier_type: 'national_id',
          org_id: 'org-1',
          contact_phone: null,
          contact_email: null,
          address: null,
          custom_fields: null,
          is_active: true,
          created_by: null,
          created_at: '2026-06-01T00:00:00Z',
          updated_at: '2026-06-01T00:00:00Z',
        },
      ];
      fixture.detectChanges();

      const customerCell = fixture.nativeElement.querySelector('.customer-cell');
      expect(customerCell.textContent).toContain('قاسم');
    });

    it('should display empty state when no customers', () => {
      component.loading = false;
      component.error = null;
      component.customers = [];
      fixture.detectChanges();

      const emptyState = fixture.nativeElement.querySelector('.empty-state');
      expect(emptyState).toBeTruthy();
    });

    it('should open row overflow menu with secondary actions', () => {
      component.loading = false;
      component.error = null;
      component.customers = [
        {
          id: '1',
          name_ar: 'قاسم',
          name_en: null,
          identifier: '5566',
          identifier_type: 'national_id',
          org_id: 'org-1',
          contact_phone: null,
          contact_email: null,
          address: null,
          custom_fields: null,
          is_active: true,
          created_by: null,
          created_at: '2026-06-01T00:00:00Z',
          updated_at: '2026-06-01T00:00:00Z',
        },
      ];
      fixture.detectChanges();

      const overflowButton = fixture.nativeElement.querySelector('button[aria-label="customers.action_more"]');
      expect(overflowButton).toBeTruthy();

      overflowButton.click();
      fixture.detectChanges();

      expect(document.body.textContent).toContain('customers.action_view');
      expect(document.body.textContent).toContain('customers.action_fill');
    });
  });

  describe('Search Functionality', () => {
    it('should have search input available', () => {
      component.loading = false;
      fixture.detectChanges();

      const searchInput = fixture.nativeElement.querySelector('.fc-search-box input');
      expect(searchInput).toBeTruthy();
    });
  });

  describe('Pagination', () => {
    it('should display pagination controls', () => {
      component.loading = false;
      component.error = null;
      component.customers = Array(50).fill(null).map((_, i) => ({
        id: `${i}`,
        org_id: 'org-1',
        name_ar: `عميل ${i}`,
        name_en: `Customer ${i}`,
        identifier_type: 'national_id',
        identifier: `${i}`,
        contact_phone: '+971',
        contact_email: `c${i}@example.com`,
        address: null,
        custom_fields: null,
        is_active: true,
        created_by: null,
        created_at: '2026-06-01T00:00:00Z',
        updated_at: '2026-06-01T00:00:00Z',
      }));
      fixture.detectChanges();

      const pagination = fixture.nativeElement.querySelector('.pagination');
      expect(pagination).toBeTruthy();
    });
  });
});

import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { TranslateFakeLoader, TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { of } from 'rxjs';
import { CustomerService } from '../services/customer.service';
import { CustomerListComponent } from './customer-list.component';
import { CustomerListResponse } from './customer.models';

describe('CustomerListComponent', () => {
  let fixture: ComponentFixture<CustomerListComponent>;

  const response: CustomerListResponse = {
    items: [
      {
        id: 'customer-1',
        org_id: 'org-1',
        name_ar: 'قاسم',
        name_en: 'Qasem',
        identifier_type: 'national_id',
        identifier: '5566',
        contact_phone: '',
        contact_email: '',
        address: '',
        custom_fields: {},
        is_active: true,
        created_by: 'user-1',
        created_at: '2026-06-01T00:00:00Z',
        updated_at: '2026-06-01T00:00:00Z',
      },
    ],
    total: 1,
    page: 1,
    page_size: 25,
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        CustomerListComponent,
        NoopAnimationsModule,
        TranslateModule.forRoot({
          loader: { provide: TranslateLoader, useClass: TranslateFakeLoader },
        }),
      ],
      providers: [
        {
          provide: CustomerService,
          useValue: { list: jasmine.createSpy('list').and.returnValue(of(response)) },
        },
        { provide: Router, useValue: { navigate: jasmine.createSpy('navigate') } },
        { provide: MatSnackBar, useValue: { open: jasmine.createSpy('open') } },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(CustomerListComponent);
    fixture.detectChanges();
  });

  it('renders Classic customer page chrome with translation keys', () => {
    const text = fixture.nativeElement.textContent;
    const viewButton: HTMLButtonElement = fixture.nativeElement.querySelector('button[mat-icon-button]');
    const searchInput: HTMLInputElement = fixture.nativeElement.querySelector('input[matInput]');

    expect(text).toContain('customers.title');
    expect(text).toContain('customers.add_customer');
    expect(text).toContain('customers.col_customer');
    expect(text).toContain('customers.col_id_num');
    expect(text).toContain('customers.col_contact');
    expect(text).toContain('customers.col_status');
    expect(text).toContain('customers.status_active');
    expect(searchInput.placeholder).toBe('customers.search_placeholder');
    expect(viewButton.getAttribute('ng-reflect-message')).toBe('customers.action_view');
    expect(viewButton.getAttribute('aria-label')).toBe('customers.action_view');
  });
});

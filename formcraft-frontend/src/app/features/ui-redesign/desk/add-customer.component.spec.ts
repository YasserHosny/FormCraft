import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { RouterTestingModule } from '@angular/router/testing';
import { Router } from '@angular/router';
import { of, throwError } from 'rxjs';
import { AddCustomerComponent } from './add-customer.component';
import { CustomerService } from '../../desk/services/customer.service';
import { TranslateModule } from '@ngx-translate/core';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

describe('AddCustomerComponent', () => {
  let component: AddCustomerComponent;
  let fixture: ComponentFixture<AddCustomerComponent>;
  let router: Router;
  let customerServiceSpy: jasmine.SpyObj<CustomerService>;

  beforeEach(async () => {
    customerServiceSpy = jasmine.createSpyObj('CustomerService', ['create']);

    await TestBed.configureTestingModule({
      imports: [
        AddCustomerComponent,
        ReactiveFormsModule,
        RouterTestingModule,
        TranslateModule.forRoot(),
        NoopAnimationsModule,
      ],
      providers: [{ provide: CustomerService, useValue: customerServiceSpy }],
    }).compileComponents();

    fixture = TestBed.createComponent(AddCustomerComponent);
    component = fixture.componentInstance;
    router = TestBed.inject(Router);
    fixture.detectChanges();
  });

  // ── US1: Render ─────────────────────────────────────────────────────────────

  it('T008 — renders a <form> element (no placeholder)', () => {
    const form = fixture.nativeElement.querySelector('form');
    expect(form).toBeTruthy();
  });

  // ── US1: Required-field validation ──────────────────────────────────────────

  it('T009 — clicking Save with empty form marks name_ar as required error', () => {
    const saveBtn: HTMLButtonElement = fixture.nativeElement.querySelector('[data-testid="save-btn"]');
    saveBtn.click();
    fixture.detectChanges();
    expect(component.form.get('name_ar')!.hasError('required')).toBeTrue();
    expect(customerServiceSpy.create).not.toHaveBeenCalled();
  });

  // ── US1: Cancel navigation ───────────────────────────────────────────────────

  it('T010 — Cancel navigates to /ui/desk/customers', () => {
    const navigateSpy = spyOn(router, 'navigate');
    component.cancel();
    expect(navigateSpy).toHaveBeenCalledWith(['/ui/desk/customers']);
  });

  // ── US1: Successful save redirect ───────────────────────────────────────────

  it('T011 — successful save navigates to Classic customer detail page', () => {
    const navigateSpy = spyOn(router, 'navigate');
    customerServiceSpy.create.and.returnValue(of({ id: 'abc-123' } as any));

    component.form.patchValue({
      name_ar: 'محمد علي',
      identifier_type: 'national_id',
      identifier: '1234567890',
    });
    component.save();
    fixture.detectChanges();

    expect(navigateSpy).toHaveBeenCalledWith(['/desk/customers', 'abc-123']);
  });

  // ── US2: Duplicate detection ─────────────────────────────────────────────────

  it('T019 — HTTP 409 sets duplicate error on identifier control and keeps form open', () => {
    const navigateSpy = spyOn(router, 'navigate');
    customerServiceSpy.create.and.returnValue(
      throwError(() => ({ status: 409, error: { customer: {} } })),
    );

    component.form.patchValue({
      name_ar: 'محمد',
      identifier_type: 'national_id',
      identifier: '1234567890',
    });
    component.save();
    fixture.detectChanges();

    expect(component.form.get('identifier')!.hasError('duplicate')).toBeTrue();
    expect(navigateSpy).not.toHaveBeenCalled();
  });

  // ── US3: buildPayload strips empty optional fields ──────────────────────────

  it('T023 — buildPayload returns only required fields + custom_fields when optionals are empty', () => {
    component.form.patchValue({
      name_ar: 'أحمد',
      identifier_type: 'national_id',
      identifier: '9876543210',
      name_en: '',
      contact_phone: '',
      contact_email: '',
      address: '',
    });
    const payload = component.buildPayload();
    expect(payload.name_ar).toBe('أحمد');
    expect(payload.identifier_type).toBe('national_id');
    expect(payload.identifier).toBe('9876543210');
    expect(payload.name_en).toBeUndefined();
    expect(payload.contact_phone).toBeUndefined();
    expect(payload.contact_email).toBeUndefined();
    expect(payload.address).toBeUndefined();
    expect(payload.custom_fields).toEqual({});
  });
});

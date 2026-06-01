import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { of } from 'rxjs';
import { MatDialogRef } from '@angular/material/dialog';

import { CustomerPickerDialogComponent } from './customer-picker-dialog.component';
import { CustomerService } from '../../services/customer.service';

describe('CustomerPickerDialogComponent', () => {
  let component: CustomerPickerDialogComponent;
  let fixture: ComponentFixture<CustomerPickerDialogComponent>;
  let customerService: jasmine.SpyObj<CustomerService>;
  let dialogRef: jasmine.SpyObj<MatDialogRef<CustomerPickerDialogComponent>>;

  beforeEach(async () => {
    customerService = jasmine.createSpyObj<CustomerService>('CustomerService', ['search']);
    dialogRef = jasmine.createSpyObj<MatDialogRef<CustomerPickerDialogComponent>>('MatDialogRef', ['close']);
    customerService.search.and.returnValue(of({ items: [{ id: '1', name_ar: 'Ahmed', identifier: '123' }] } as any));

    await TestBed.configureTestingModule({
      imports: [CustomerPickerDialogComponent],
      providers: [
        { provide: CustomerService, useValue: customerService },
        { provide: MatDialogRef, useValue: dialogRef },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(CustomerPickerDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('debounces search by 300ms before calling CustomerService.search', fakeAsync(() => {
    component.searchControl.setValue('Ahmed');
    tick(299);
    expect(customerService.search).not.toHaveBeenCalled();
    tick(1);
    expect(customerService.search).toHaveBeenCalledWith('Ahmed');
  }));

  it('renders customer names and closes dialog on selection', fakeAsync(() => {
    component.searchControl.setValue('Ahmed');
    tick(300);
    fixture.detectChanges();

    expect(component.results.length).toBe(1);
    expect(component.results[0].name_ar).toBe('Ahmed');

    component.select(component.results[0] as any);
    expect(dialogRef.close).toHaveBeenCalled();
  }));

  it('shows empty state when no results', fakeAsync(() => {
    customerService.search.and.returnValue(of({ items: [] } as any));
    component.searchControl.setValue('none');
    tick(300);
    fixture.detectChanges();

    expect(component.results.length).toBe(0);
  }));
});

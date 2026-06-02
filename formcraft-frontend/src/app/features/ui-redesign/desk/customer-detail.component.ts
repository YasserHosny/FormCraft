import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { CustomerService } from '../../desk/services/customer.service';
import { Customer, CustomerUpdate } from '../../desk/customers/customer.models';

@Component({
  selector: 'fc-spark-customer-detail',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatIconModule,
    TranslateModule,
  ],
  templateUrl: './customer-detail.component.html',
  styleUrl: './customer-detail.component.scss',
})
export class CustomerDetailComponent implements OnInit {
  form!: FormGroup;
  customer: Customer | null = null;
  loading = true;
  saving = false;
  editing = false;
  customerId = '';

  identifierTypes = [
    { value: 'national_id', labelKey: 'add_customer.id_type_national_id' },
    { value: 'iqama', labelKey: 'add_customer.id_type_iqama' },
    { value: 'commercial_register', labelKey: 'add_customer.id_type_commercial_register' },
    { value: 'passport', labelKey: 'add_customer.id_type_passport' },
    { value: 'other', labelKey: 'add_customer.id_type_other' },
  ];

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private customerService: CustomerService,
    private snackBar: MatSnackBar,
    private translate: TranslateService,
  ) {}

  ngOnInit(): void {
    this.customerId = this.route.snapshot.paramMap.get('id') || '';
    this.form = this.fb.group({
      name_ar: ['', Validators.required],
      name_en: [''],
      identifier_type: ['national_id', Validators.required],
      identifier: ['', Validators.required],
      contact_phone: [''],
      contact_email: ['', Validators.email],
      address: [''],
    });
    this.form.disable();
    this.loadCustomer();
  }

  private loadCustomer(): void {
    this.loading = true;
    this.customerService.getById(this.customerId).subscribe({
      next: (customer) => {
        this.customer = customer;
        this.form.patchValue({
          name_ar: customer.name_ar || '',
          name_en: customer.name_en || '',
          identifier_type: customer.identifier_type || 'national_id',
          identifier: customer.identifier || '',
          contact_phone: customer.contact_phone || '',
          contact_email: customer.contact_email || '',
          address: customer.address || '',
        });
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.snackBar.open(
          this.translate.instant('customer_detail.error_load'),
          '',
          { duration: 4000 },
        );
        this.router.navigate(['/ui/desk/customers']);
      },
    });
  }

  toggleEdit(): void {
    this.editing = !this.editing;
    if (this.editing) {
      this.form.enable();
    } else {
      this.form.disable();
      if (this.customer) {
        this.form.patchValue({
          name_ar: this.customer.name_ar || '',
          name_en: this.customer.name_en || '',
          identifier_type: this.customer.identifier_type || 'national_id',
          identifier: this.customer.identifier || '',
          contact_phone: this.customer.contact_phone || '',
          contact_email: this.customer.contact_email || '',
          address: this.customer.address || '',
        });
      }
    }
  }

  save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    if (!this.customer) return;

    const v = this.form.value;
    const update: CustomerUpdate = {};
    if (v.name_ar !== this.customer.name_ar) update.name_ar = v.name_ar;
    if (v.name_en !== (this.customer.name_en || '')) update.name_en = v.name_en;
    if (v.identifier_type !== this.customer.identifier_type) update.identifier_type = v.identifier_type;
    if (v.identifier !== this.customer.identifier) update.identifier = v.identifier;
    if (v.contact_phone !== (this.customer.contact_phone || '')) update.contact_phone = v.contact_phone;
    if (v.contact_email !== (this.customer.contact_email || '')) update.contact_email = v.contact_email;
    if (v.address !== (this.customer.address || '')) update.address = v.address;

    if (Object.keys(update).length === 0) {
      this.editing = false;
      this.form.disable();
      return;
    }

    this.saving = true;
    this.customerService.update(this.customer.id, update).subscribe({
      next: (updated) => {
        this.customer = updated;
        this.saving = false;
        this.editing = false;
        this.form.disable();
        this.snackBar.open(
          this.translate.instant('customer_detail.save_success'),
          '',
          { duration: 3000 },
        );
      },
      error: (err) => {
        this.saving = false;
        const msg = err.error?.detail ?? this.translate.instant('customer_detail.error_save');
        this.snackBar.open(msg, '', { duration: 4000 });
      },
    });
  }

  back(): void {
    this.router.navigate(['/ui/desk/customers']);
  }
}

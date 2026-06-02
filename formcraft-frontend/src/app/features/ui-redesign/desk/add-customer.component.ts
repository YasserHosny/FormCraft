import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
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
import { CustomerCreate } from '../../desk/customers/customer.models';
import { notWhitespace } from '../../../shared/validators/not-whitespace.validator';

@Component({
  selector: 'fc-spark-add-customer',
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
  templateUrl: './add-customer.component.html',
  styleUrl: './add-customer.component.scss',
})
export class AddCustomerComponent implements OnInit {
  form!: FormGroup;
  saving = false;

  identifierTypes = [
    { value: 'national_id', labelKey: 'add_customer.id_type_national_id' },
    { value: 'iqama', labelKey: 'add_customer.id_type_iqama' },
    { value: 'commercial_register', labelKey: 'add_customer.id_type_commercial_register' },
    { value: 'passport', labelKey: 'add_customer.id_type_passport' },
    { value: 'other', labelKey: 'add_customer.id_type_other' },
  ];

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private customerService: CustomerService,
    private snackBar: MatSnackBar,
    private translate: TranslateService,
  ) {}

  ngOnInit(): void {
    this.form = this.fb.group({
      name_ar: ['', [Validators.required, notWhitespace()]],
      name_en: [''],
      identifier_type: ['national_id', Validators.required],
      identifier: ['', Validators.required],
      contact_phone: [''],
      contact_email: ['', Validators.email],
      address: [''],
    });

    // Clear the duplicate error the moment the operator edits the identifier
    this.form.get('identifier')!.valueChanges.subscribe(() => {
      const ctrl = this.form.get('identifier')!;
      if (ctrl.hasError('duplicate')) {
        const errors = { ...ctrl.errors };
        delete errors['duplicate'];
        ctrl.setErrors(Object.keys(errors).length ? errors : null);
      }
    });
  }

  buildPayload(): CustomerCreate {
    const v = this.form.value;
    const payload: CustomerCreate = {
      name_ar: v.name_ar,
      identifier_type: v.identifier_type,
      identifier: v.identifier,
      custom_fields: {},
    };
    if (v.name_en) payload.name_en = v.name_en;
    if (v.contact_phone) payload.contact_phone = v.contact_phone;
    if (v.contact_email) payload.contact_email = v.contact_email;
    if (v.address) payload.address = v.address;
    return payload;
  }

  save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.saving = true;
    this.customerService.create(this.buildPayload()).subscribe({
      next: (customer) => {
        this.saving = false;
        this.router.navigate(['/desk/customers', customer.id]);
      },
      error: (err) => {
        this.saving = false;
        if (err.status === 409) {
          this.form.get('identifier')!.setErrors({ duplicate: true });
        } else {
          const msg =
            err.error?.detail ?? this.translate.instant('add_customer.error_generic');
          this.snackBar.open(msg, '', { duration: 4000 });
        }
      },
    });
  }

  cancel(): void {
    this.router.navigate(['/ui/desk/customers']);
  }
}

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { FormsModule } from '@angular/forms';
import { CustomerService } from '../services/customer.service';
import { Customer, CustomerCreate, CustomerUpdate } from './customer.models';

@Component({
  selector: 'fc-customer-detail',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatCardModule,
    MatChipsModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './customer-detail.component.html',
  styleUrls: ['./customer-detail.component.scss'],
})
export class CustomerDetailComponent implements OnInit {
  customer: Customer | null = null;
  isNew = false;
  loading = true;
  saving = false;

  identifierTypes = [
    { value: 'national_id', label: 'National ID' },
    { value: 'iqama', label: 'Iqama' },
    { value: 'commercial_register', label: 'Commercial Register' },
    { value: 'passport', label: 'Passport' },
    { value: 'other', label: 'Other' },
  ];

  formData: Partial<CustomerCreate> = {
    name_ar: '',
    name_en: '',
    identifier_type: 'national_id',
    identifier: '',
    contact_phone: '',
    contact_email: '',
    address: '',
    custom_fields: {},
  };

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private customerService: CustomerService,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id === 'new') {
      this.isNew = true;
      this.loading = false;
    } else if (id) {
      this.loadCustomer(id);
    }
  }

  loadCustomer(id: string): void {
    this.loading = true;
    this.customerService.getById(id).subscribe({
      next: (customer: Customer) => {
        this.customer = customer;
        this.formData = {
          name_ar: customer.name_ar,
          name_en: customer.name_en || '',
          identifier_type: customer.identifier_type,
          identifier: customer.identifier,
          contact_phone: customer.contact_phone || '',
          contact_email: customer.contact_email || '',
          address: customer.address || '',
          custom_fields: customer.custom_fields || {},
        };
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.snackBar.open('Failed to load customer', '', { duration: 3000 });
        this.router.navigate(['/desk/customers']);
      },
    });
  }

  save(): void {
    if (!this.formData.name_ar || !this.formData.identifier) {
      this.snackBar.open('Name and identifier are required', '', { duration: 3000 });
      return;
    }

    this.saving = true;

    if (this.isNew) {
      this.customerService.create(this.formData as CustomerCreate).subscribe({
        next: (customer: Customer) => {
          this.snackBar.open('Customer created successfully', '', { duration: 3000 });
          this.router.navigate(['/desk/customers', customer.id]);
        },
        error: (err: any) => {
          this.saving = false;
          if (err.status === 409 && err.error?.customer) {
            this.snackBar.open('Customer already exists', '', { duration: 5000 });
          } else {
            this.snackBar.open(err.error?.detail || 'Failed to create customer', '', { duration: 3000 });
          }
        },
      });
    } else if (this.customer) {
      const update: CustomerUpdate = {};
      if (this.formData.name_ar !== this.customer.name_ar) update.name_ar = this.formData.name_ar;
      if (this.formData.name_en !== this.customer.name_en) update.name_en = this.formData.name_en;
      if (this.formData.identifier_type !== this.customer.identifier_type) update.identifier_type = this.formData.identifier_type;
      if (this.formData.identifier !== this.customer.identifier) update.identifier = this.formData.identifier;
      if (this.formData.contact_phone !== this.customer.contact_phone) update.contact_phone = this.formData.contact_phone;
      if (this.formData.contact_email !== this.customer.contact_email) update.contact_email = this.formData.contact_email;
      if (this.formData.address !== this.customer.address) update.address = this.formData.address;

      this.customerService.update(this.customer.id, update).subscribe({
        next: () => {
          this.snackBar.open('Customer updated successfully', '', { duration: 3000 });
          this.saving = false;
        },
        error: (err: any) => {
          this.saving = false;
          this.snackBar.open(err.error?.detail || 'Failed to update customer', '', { duration: 3000 });
        },
      });
    }
  }

  cancel(): void {
    this.router.navigate(['/desk/customers']);
  }
}

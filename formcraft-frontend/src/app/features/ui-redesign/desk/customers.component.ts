import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { Customer } from '../../../features/desk/customers/customer.models';
import { PageHeaderComponent } from '../shared/components/page-header.component';
import { StatusChipComponent } from '../shared/components/status-chip.component';
import { AvatarComponent } from '../shared/components/avatar.component';
import { CustomerService } from '../../../features/desk/services/customer.service';
import { FormsModule } from '@angular/forms';

type CustomerGridItem = Customer & {
  branch?: string;
  color?: string;
  is_premium?: boolean;
  submission_count?: number;
};

@Component({
  selector: 'fc-customers',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatMenuModule, TranslateModule, PageHeaderComponent, StatusChipComponent, AvatarComponent, FormsModule],
  templateUrl: './customers.component.html',
  styleUrl: './customers.component.scss',
})
export class CustomersComponent implements OnInit {
  customers: CustomerGridItem[] = [];
  loading = true;
  error: string | null = null;
  searchQuery = '';
  currentPage = 1;
  pageSize = 50;
  totalCustomers = 0;
  Math = Math;

  // Stats are dynamic once data loads; shown as placeholders until then
  totalStat = 0;
  activeStat = 0;
  inactiveStat = 0;
  duplicatesStat = 0;

  constructor(
    private router: Router,
    private customerService: CustomerService,
    private translate: TranslateService,
  ) {}

  ngOnInit(): void {
    this.loadCustomers();
  }

  private loadCustomers(): void {
    this.loading = true;
    this.customerService.list({ page: this.currentPage, page_size: this.pageSize }).subscribe({
      next: (response) => {
        this.customers = response.items || [];
        this.totalCustomers = response.total || 0;
        this.totalStat = this.totalCustomers;
        this.loading = false;
        this.error = null;
      },
      error: (err) => {
        console.error('Failed to load customers:', err);
        this.loading = false;
        this.error = this.translate.instant('customers.error_load');
        this.customers = [];
      },
    });
  }

  addCustomer(): void {
    this.router.navigate(['/ui/desk/customers/new']);
  }

  viewCustomer(customerId: string): void {
    this.router.navigate(['/ui/desk/customers', customerId]);
  }

  fillFormForCustomer(): void {
    this.router.navigate(['/ui/desk']);
  }

  onSearch(query: string): void {
    this.searchQuery = query;
    this.currentPage = 1;
    if (query.length > 0) {
      this.loading = true;
      this.customerService.list({ page: this.currentPage, page_size: this.pageSize, search: query }).subscribe({
        next: (response) => {
          this.customers = response.items || [];
          this.totalCustomers = response.total || 0;
          this.loading = false;
        },
        error: (err) => {
          console.error('Search failed:', err);
          this.error = this.translate.instant('customers.error_search');
          this.loading = false;
        },
      });
    } else {
      this.loadCustomers();
    }
  }

  onPageChange(newPage: number): void {
    if (newPage > 0 && newPage <= Math.ceil(this.totalCustomers / this.pageSize)) {
      this.currentPage = newPage;
      this.loadCustomers();
    }
  }

  onPageSizeChange(size: number): void {
    this.pageSize = size;
    this.currentPage = 1;
    this.loadCustomers();
  }

  getCustomerName(customer: CustomerGridItem): string {
    const nameAr = customer.name_ar?.trim() || '';
    const nameEn = customer.name_en?.trim() || '';

    if (this.translate.currentLang === 'ar') {
      return nameAr || nameEn || '-';
    }

    return nameEn || nameAr || '-';
  }

  getCustomerSecondaryName(customer: CustomerGridItem): string | null {
    const primaryName = this.getCustomerName(customer);
    const fallbackName = this.translate.currentLang === 'ar'
      ? customer.name_en?.trim()
      : customer.name_ar?.trim();

    return fallbackName && fallbackName !== primaryName ? fallbackName : null;
  }

  getIdentifierType(customer: CustomerGridItem): string {
    return customer.identifier_type || this.translate.instant('customers.id_type_national');
  }

  getIdentifier(customer: CustomerGridItem): string {
    return customer.identifier || customer.id?.slice(0, 12) || '-';
  }

  getPhone(customer: CustomerGridItem): string {
    return customer.contact_phone || '-';
  }
}

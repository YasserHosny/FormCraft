import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { PageHeaderComponent } from '../shared/components/page-header.component';
import { StatusChipComponent } from '../shared/components/status-chip.component';
import { AvatarComponent } from '../shared/components/avatar.component';
import { CustomerService } from '../../../features/desk/services/customer.service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'fc-customers',
  standalone: true,
  imports: [CommonModule, MatIconModule, TranslateModule, PageHeaderComponent, StatusChipComponent, AvatarComponent, FormsModule],
  templateUrl: './customers.component.html',
  styleUrl: './customers.component.scss',
})
export class CustomersComponent implements OnInit {
  customers: any[] = [];
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
    this.router.navigate(['/desk/customers/new']);
  }

  viewCustomer(customerId: string): void {
    this.router.navigate(['/desk/customers', customerId]);
  }

  fillFormForCustomer(): void {
    this.router.navigate(['/desk']);
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
}

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { PageHeaderComponent } from '../shared/components/page-header.component';
import { StatusChipComponent } from '../shared/components/status-chip.component';
import { AvatarComponent } from '../shared/components/avatar.component';
import { CustomerService } from '../../../features/desk/services/customer.service';
import { FormsModule } from '@angular/forms';

interface Stat {
  label: string;
  value: string;
  sub?: string;
  delta?: string;
  up?: boolean;
  warn?: boolean;
}

@Component({
  selector: 'fc-customers',
  standalone: true,
  imports: [CommonModule, MatIconModule, PageHeaderComponent, StatusChipComponent, AvatarComponent, FormsModule],
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

  constructor(private router: Router, private customerService: CustomerService) {}

  ngOnInit(): void {
    this.loadCustomers();
  }

  private loadCustomers(): void {
    this.loading = true;
    this.customerService.list({ page: this.currentPage, page_size: this.pageSize }).subscribe({
      next: (response) => {
        this.customers = response.items || [];
        this.totalCustomers = response.total || 0;
        this.loading = false;
        this.error = null;
      },
      error: (err) => {
        console.error('Failed to load customers:', err);
        this.loading = false;
        this.error = 'Failed to load customer list';
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
          this.error = 'Failed to search customers';
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

  stats: Stat[] = [
    { label: 'إجمالي العملاء', value: '٢٨٤١', delta: '+47 هذا الأسبوع', up: true },
    { label: 'عملاء نشطون', value: '٢٧٩٢', sub: '٩٨٫٣%' },
    { label: 'إضافات اليوم', value: '٧', sub: 'من ٣ فروع' },
    { label: 'تكرارات محتملة', value: '٤', sub: 'تحتاج مراجعة', warn: true },
    { label: 'متوسط النماذج/عميل', value: '٧٫٢', sub: '+0.8 عن الربع السابق' },
  ];
}

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatChipsModule } from '@angular/material/chips';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { CustomerService } from '../services/customer.service';
import { Customer, CustomerListResponse } from './customer.models';

@Component({
  selector: 'fc-customer-list',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule,
    MatTableModule,
    MatPaginatorModule,
    MatButtonModule,
    MatIconModule,
    MatInputModule,
    MatFormFieldModule,
    MatChipsModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
    TranslateModule,
  ],
  templateUrl: './customer-list.component.html',
  styleUrls: ['./customer-list.component.scss'],
})
export class CustomerListComponent implements OnInit {
  customers: Customer[] = [];
  displayedColumns = ['name', 'identifier', 'contact', 'status', 'actions'];
  loading = true;
  total = 0;
  page = 1;
  pageSize = 25;
  searchQuery = '';
  private searchSubject = new Subject<string>();

  constructor(
    private customerService: CustomerService,
    private router: Router,
    private snackBar: MatSnackBar,
    private translate: TranslateService,
  ) {}

  ngOnInit(): void {
    this.searchSubject.pipe(
      debounceTime(300),
      distinctUntilChanged(),
    ).subscribe((query) => {
      this.page = 1;
      this.loadCustomers(query);
    });

    this.loadCustomers();
  }

  loadCustomers(search: string = ''): void {
    this.loading = true;
    this.customerService.list({
      page: this.page,
      page_size: this.pageSize,
      search: search || undefined,
    }).subscribe({
      next: (response: CustomerListResponse) => {
        this.customers = response.items;
        this.total = response.total;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.snackBar.open(this.translate.instant('customers.error_load'), '', { duration: 3000 });
      },
    });
  }

  onSearchChange(value: string): void {
    this.searchSubject.next(value);
  }

  onPageChange(event: PageEvent): void {
    this.page = event.pageIndex + 1;
    this.pageSize = event.pageSize;
    this.loadCustomers(this.searchQuery);
  }

  viewCustomer(customer: Customer): void {
    this.router.navigate(['/desk/customers', customer.id]);
  }

  addCustomer(): void {
    this.router.navigate(['/desk/customers/new']);
  }

  getStatusColor(isActive: boolean): string {
    return isActive ? 'primary' : 'warn';
  }
}

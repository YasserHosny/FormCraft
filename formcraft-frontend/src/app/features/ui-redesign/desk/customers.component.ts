import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { PageHeaderComponent } from '../shared/components/page-header.component';
import { StatusChipComponent } from '../shared/components/status-chip.component';
import { AvatarComponent } from '../shared/components/avatar.component';

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
  imports: [CommonModule, MatIconModule, PageHeaderComponent, StatusChipComponent, AvatarComponent],
  templateUrl: './customers.component.html',
  styleUrl: './customers.component.scss',
})
export class CustomersComponent {
  customers: any[] = [];
  loading = true;
  error: string | null = null;

  constructor(private router: Router) {}

  addCustomer(): void {
    this.router.navigate(['/desk/customers/new']);
  }

  viewCustomer(customerId: string): void {
    this.router.navigate(['/desk/customers', customerId]);
  }

  fillFormForCustomer(): void {
    this.router.navigate(['/desk']);
  }

  stats: Stat[] = [
    { label: 'إجمالي العملاء', value: '٢٨٤١', delta: '+47 هذا الأسبوع', up: true },
    { label: 'عملاء نشطون', value: '٢٧٩٢', sub: '٩٨٫٣%' },
    { label: 'إضافات اليوم', value: '٧', sub: 'من ٣ فروع' },
    { label: 'تكرارات محتملة', value: '٤', sub: 'تحتاج مراجعة', warn: true },
    { label: 'متوسط النماذج/عميل', value: '٧٫٢', sub: '+0.8 عن الربع السابق' },
  ];
}

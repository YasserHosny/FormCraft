import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { PageHeaderComponent } from '../shared/components/page-header.component';
import { StatusChipComponent } from '../shared/components/status-chip.component';
import { AvatarComponent } from '../shared/components/avatar.component';
import { CUSTOMERS } from '../shared/mock-data';

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
  customers = CUSTOMERS;

  stats: Stat[] = [
    { label: 'إجمالي العملاء', value: '٢٨٤١', delta: '+47 هذا الأسبوع', up: true },
    { label: 'عملاء نشطون', value: '٢٧٩٢', sub: '٩٨٫٣%' },
    { label: 'إضافات اليوم', value: '٧', sub: 'من ٣ فروع' },
    { label: 'تكرارات محتملة', value: '٤', sub: 'تحتاج مراجعة', warn: true },
    { label: 'متوسط النماذج/عميل', value: '٧٫٢', sub: '+0.8 عن الربع السابق' },
  ];
}

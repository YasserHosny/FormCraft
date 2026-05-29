import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { PageHeaderComponent } from '../shared/components/page-header.component';
import { KpiCardComponent } from '../shared/components/kpi-card.component';
import { AvatarComponent } from '../shared/components/avatar.component';

interface BarItem {
  label: string;
  value: number;
  code: string;
}

interface DonutSegment {
  label: string;
  value: number;
  color: string;
}

interface Operator {
  name: string;
  branch: string;
  forms: number;
  time: string;
  accuracy: number;
  color: string;
}

@Component({
  selector: 'fc-analytics',
  standalone: true,
  imports: [CommonModule, MatIconModule, PageHeaderComponent, KpiCardComponent, AvatarComponent],
  templateUrl: './analytics.component.html',
  styleUrl: './analytics.component.scss',
})
export class AnalyticsComponent {
  constructor(private router: Router) {}

  exportPdf(): void {
    this.router.navigate(['/admin/analytics'], { queryParams: { export: 'pdf' } });
  }

  openClassicAnalytics(): void {
    this.router.navigate(['/admin/analytics']);
  }

  // Line chart data
  lineData = [42, 58, 51, 47, 63, 70, 38, 41, 55, 68, 72, 81, 76, 65, 78, 92, 88, 73, 81, 95, 102, 87, 79, 94, 108, 115, 98, 92, 105, 124];
  lineMax = 130;

  // Donut data
  donutData: DonutSegment[] = [
    { label: 'الحسابات الجارية', value: 38, color: '#3F51B5' },
    { label: 'القروض الشخصية', value: 22, color: '#5C6BC0' },
    { label: 'الخدمات الإلكترونية', value: 16, color: '#7986CB' },
    { label: 'الحوالات', value: 12, color: '#FFA000' },
    { label: 'الالتزام (KYC)', value: 8, color: '#00897B' },
    { label: 'أخرى', value: 4, color: '#BDBDBD' },
  ];

  // Bar chart data
  barData: BarItem[] = [
    { label: 'طلب فتح حساب جاري', value: 1837, code: 'AC-001' },
    { label: 'تحديث بيانات KYC', value: 1284, code: 'KYC-018' },
    { label: 'تحويل خارجي', value: 942, code: 'TR-022' },
    { label: 'إصدار بطاقة الصراف', value: 712, code: 'CRD-007' },
    { label: 'طلب قرض شخصي', value: 612, code: 'LN-002' },
    { label: 'إصدار خطاب ضمان', value: 287, code: 'LG-011' },
    { label: 'دفتر شيكات', value: 184, code: 'CHQ-009' },
  ];

  // Operators performance
  operators: Operator[] = [
    { name: 'سلمان الغامدي', branch: 'أبوظبي', forms: 184, time: '3:12', accuracy: 99.4, color: 'c6' },
    { name: 'أحمد العتيبي', branch: 'أبوظبي', forms: 167, time: '3:28', accuracy: 98.1, color: 'c1' },
    { name: 'هدى الحربي', branch: 'دبي', forms: 142, time: '3:51', accuracy: 97.8, color: 'c3' },
    { name: 'منى السعيد', branch: 'الشارقة', forms: 128, time: '4:02', accuracy: 96.5, color: 'c5' },
    { name: 'عبدالله المالكي', branch: 'العين', forms: 119, time: '3:44', accuracy: 98.7, color: 'c2' },
  ];

  get barMax(): number {
    return this.barData[0]?.value || 1;
  }

  formatValue(n: number): string {
    return n.toLocaleString('ar-EG');
  }

  getBarWidth(value: number): number {
    return (value / this.barMax) * 100;
  }
}

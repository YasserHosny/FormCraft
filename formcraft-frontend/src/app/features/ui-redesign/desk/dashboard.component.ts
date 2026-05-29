import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { PageHeaderComponent } from '../shared/components/page-header.component';
import { StatusChipComponent } from '../shared/components/status-chip.component';
import { AvatarComponent } from '../shared/components/avatar.component';
import { KpiCardComponent } from '../shared/components/kpi-card.component';
import { TemplateService } from '../../../core/services/template.service';

interface PinnedForm {
  icon: string;
  color: string;
  name: string;
  code: string;
  lastUsed: string;
  count?: string;
  accent?: boolean;
}

interface ActivityItem {
  time: string;
  customer: string;
  form: string;
  status: string;
  ref: string;
  color: string;
}

interface DraftItem {
  form: string;
  customer: string;
  progress: number;
  time: string;
  warn?: boolean;
}

@Component({
  selector: 'fc-desk-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, MatIconModule, PageHeaderComponent, StatusChipComponent, AvatarComponent, KpiCardComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class DashboardComponent implements OnInit {
  publishedTemplates: { id: string; name: string; code: string }[] = [];

  constructor(private router: Router, private templateService: TemplateService) {}

  ngOnInit(): void {
    this.templateService.list({ limit: 50 }).subscribe({
      next: (response) => {
        this.publishedTemplates = (response.data || [])
          .filter((t: any) => t.status === 'published')
          .map((t: any) => ({ id: t.id, name: t.name, code: t.id.slice(0, 8) }));
      },
    });
  }

  fillNewForm(): void {
    this.router.navigate(['/desk']);
  }

  viewAllTransactions(): void {
    this.router.navigate(['/desk/history']);
  }

  viewAllCustomers(): void {
    this.router.navigate(['/ui/desk/customers']);
  }

  pinnedForms: PinnedForm[] = [
    { icon: 'account_balance', color: '#3F51B5', name: 'طلب فتح حساب جاري', code: 'AC-001 · v4.2', lastUsed: 'قبل ١٢ دقيقة', count: '٨', accent: true },
    { icon: 'credit_card', color: '#1565C0', name: 'إصدار بطاقة الصراف', code: 'CRD-007 · v1.5', lastUsed: 'قبل ٢٤ دقيقة', count: '٥', accent: true },
    { icon: 'verified_user', color: '#6A1B9A', name: 'تحديث بيانات KYC', code: 'KYC-018 · v2.0', lastUsed: 'قبل ساعة' },
    { icon: 'send', color: '#00897B', name: 'تحويل خارجي', code: 'TR-022 · v2.3', lastUsed: 'قبل ساعتين', count: '٣', accent: true },
    { icon: 'receipt_long', color: '#E65100', name: 'طلب دفتر شيكات', code: 'CHQ-009 · v1.0', lastUsed: 'أمس' },
  ];

  activities: ActivityItem[] = [
    { time: '١٠:٤٢', customer: 'فاطمة بنت عبدالله القحطاني', form: 'طلب فتح حساب جاري', status: 'published', ref: 'REF-2026-3841', color: 'c2' },
    { time: '١٠:٢٨', customer: 'خالد بن سعد الدوسري', form: 'إصدار بطاقة الصراف', status: 'published', ref: 'REF-2026-3840', color: 'c1' },
    { time: '١٠:١٥', customer: 'نورة بنت إبراهيم الزهراني', form: 'تحويل خارجي', status: 'in-review', ref: 'REF-2026-3839', color: 'c3' },
    { time: '٠٩:٥٨', customer: 'محمد بن علي الشمري', form: 'تحديث بيانات KYC', status: 'published', ref: 'REF-2026-3838', color: 'c4' },
    { time: '٠٩:٤٢', customer: 'ريم بنت فهد العنزي', form: 'طلب قرض شخصي', status: 'draft', ref: 'REF-2026-3837', color: 'c5' },
    { time: '٠٩:٢٠', customer: 'سلمان بن أحمد الغامدي', form: 'طلب فتح حساب جاري', status: 'published', ref: 'REF-2026-3836', color: 'c6' },
    { time: '٠٩:٠٥', customer: 'هدى بنت محمد الحربي', form: 'إصدار خطاب ضمان', status: 'rejected', ref: 'REF-2026-3835', color: 'c2' },
  ];

  drafts: DraftItem[] = [
    { form: 'طلب قرض شخصي', customer: 'ريم بنت فهد العنزي', progress: 78, time: 'قبل ٤٥ دقيقة', warn: true },
    { form: 'تحديث بيانات KYC', customer: 'عبدالعزيز بن خالد', progress: 62, time: 'قبل ساعة' },
    { form: 'فتح وديعة استثمارية', customer: 'لمياء بنت سعود', progress: 45, time: 'قبل ٣ ساعات', warn: true },
    { form: 'طلب إصدار خطاب ضمان', customer: 'شركة الفجر للمقاولات', progress: 31, time: 'أمس' },
  ];
}

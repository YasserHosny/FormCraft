import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { LanguageService } from '../../../core/i18n/language.service';

interface SidebarItem {
  icon: string;
  label: string;
  route: string;
}

interface SidebarGroup {
  label: string;
  items: SidebarItem[];
}

const NAV_CONFIG: Record<string, SidebarGroup[]> = {
  studio: [
    { label: 'استوديو التصميم', items: [
      { icon: 'description', label: 'النماذج', route: '/ui/studio/templates' },
      { icon: 'history', label: 'سجل الإصدارات', route: '' },
      { icon: 'folder_special', label: 'القوالب الجاهزة', route: '' },
      { icon: 'palette', label: 'مكوّنات قابلة للاستخدام', route: '' },
    ]},
    { label: 'الذكاء الاصطناعي', items: [
      { icon: 'auto_awesome', label: 'اقتراحات الحقول', route: '' },
      { icon: 'fact_check', label: 'فحص جودة النموذج', route: '' },
    ]},
  ],
  desk: [
    { label: 'مكتب النماذج', items: [
      { icon: 'home', label: 'الرئيسية', route: '/ui/desk' },
      { icon: 'edit_document', label: 'تعبئة نموذج جديد', route: '' },
      { icon: 'inbox', label: 'الواردات', route: '' },
      { icon: 'pending_actions', label: 'المسوّدات', route: '' },
      { icon: 'history', label: 'سجل المعاملات', route: '' },
    ]},
    { label: 'العملاء', items: [
      { icon: 'groups', label: 'دليل العملاء', route: '/ui/desk/customers' },
      { icon: 'person_add', label: 'إضافة عميل', route: '' },
      { icon: 'merge_type', label: 'دمج التكرارات', route: '' },
    ]},
  ],
  admin: [
    { label: 'لوحة الإدارة', items: [
      { icon: 'analytics', label: 'التحليلات والتقارير', route: '/ui/admin/analytics' },
      { icon: 'rule', label: 'قائمة المراجعة', route: '' },
      { icon: 'history_edu', label: 'سجل النشاط', route: '' },
    ]},
    { label: 'المؤسسة', items: [
      { icon: 'people', label: 'المستخدمون', route: '' },
      { icon: 'account_tree', label: 'الإدارات والفروع', route: '' },
      { icon: 'business', label: 'إعدادات المؤسسة', route: '' },
      { icon: 'list_alt', label: 'البيانات المرجعية', route: '' },
      { icon: 'print', label: 'ملفات تعريف الطابعات', route: '' },
    ]},
  ],
};

@Component({
  selector: 'fc-redesign-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule, MatIconModule, MatTooltipModule],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.scss',
})
export class SidebarComponent {
  @Input() mode: 'studio' | 'desk' | 'admin' = 'studio';

  constructor(private languageService: LanguageService) {}

  get groups(): SidebarGroup[] {
    return NAV_CONFIG[this.mode] || [];
  }

  get currentLang(): string {
    return this.languageService.getLanguage();
  }

  toggleLanguage(): void {
    this.languageService.toggleLanguage();
  }
}

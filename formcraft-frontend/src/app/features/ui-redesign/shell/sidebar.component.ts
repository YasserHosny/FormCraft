import { Component, EventEmitter, HostListener, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { TranslateModule } from '@ngx-translate/core';
import { LanguageService } from '../../../core/i18n/language.service';

interface SidebarItem {
  icon: string;
  labelKey: string;
  route: string;
}

interface SidebarGroup {
  labelKey: string;
  items: SidebarItem[];
}

const NAV_CONFIG: Record<string, SidebarGroup[]> = {
  studio: [
    { labelKey: 'sidebar.studio.group_design', items: [
      { icon: 'description',    labelKey: 'sidebar.studio.templates',           route: '/ui/studio/templates' },
      { icon: 'history',        labelKey: 'sidebar.studio.version_history',     route: '' },
      { icon: 'folder_special', labelKey: 'sidebar.studio.starter_templates',   route: '' },
      { icon: 'palette',        labelKey: 'sidebar.studio.reusable_components', route: '' },
    ]},
    { labelKey: 'sidebar.studio.group_ai', items: [
      { icon: 'auto_awesome', labelKey: 'sidebar.studio.ai_suggestions', route: '' },
      { icon: 'fact_check',   labelKey: 'sidebar.studio.ai_quality',     route: '' },
    ]},
  ],
  desk: [
    { labelKey: 'sidebar.desk.group_desk', items: [
      { icon: 'home',            labelKey: 'sidebar.desk.home',      route: '/ui/desk' },
      { icon: 'edit_document',   labelKey: 'sidebar.desk.fill_new',  route: '/ui/desk/templates' },
      { icon: 'inbox',           labelKey: 'sidebar.desk.inbound',   route: '' },
      { icon: 'pending_actions', labelKey: 'sidebar.desk.drafts',    route: '/ui/desk' },
      { icon: 'history',         labelKey: 'sidebar.desk.history',   route: '/ui/desk/history' },
    ]},
    { labelKey: 'sidebar.desk.group_customers', items: [
      { icon: 'groups',      labelKey: 'sidebar.desk.customers',        route: '/ui/desk/customers' },
      { icon: 'person_add',  labelKey: 'sidebar.desk.add_customer',     route: '' },
      { icon: 'merge_type',  labelKey: 'sidebar.desk.merge_duplicates', route: '' },
    ]},
  ],
  admin: [
    { labelKey: 'sidebar.admin.group_admin', items: [
      { icon: 'analytics',    labelKey: 'sidebar.admin.analytics',    route: '/ui/admin/analytics' },
      { icon: 'rule',         labelKey: 'sidebar.admin.review_queue', route: '' },
      { icon: 'history_edu',  labelKey: 'sidebar.admin.activity_log', route: '' },
    ]},
    { labelKey: 'sidebar.admin.group_org', items: [
      { icon: 'people',       labelKey: 'sidebar.admin.users',            route: '' },
      { icon: 'account_tree', labelKey: 'sidebar.admin.departments',      route: '' },
      { icon: 'business',     labelKey: 'sidebar.admin.org_settings',     route: '' },
      { icon: 'list_alt',     labelKey: 'sidebar.admin.ref_data',         route: '' },
      { icon: 'print',        labelKey: 'sidebar.admin.printer_profiles', route: '' },
    ]},
  ],
};

@Component({
  selector: 'fc-redesign-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule, MatIconModule, MatTooltipModule, TranslateModule],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.scss',
})
export class SidebarComponent {
  @Input() mode: 'studio' | 'desk' | 'admin' = 'studio';
  @Input() open = false;
  @Output() closed = new EventEmitter<void>();

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

  close(): void {
    this.closed.emit();
  }

  @HostListener('document:keydown.escape')
  onEscape(): void {
    if (this.open) {
      this.close();
    }
  }
}

import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { PageHeaderComponent } from '../shared/components/page-header.component';
import { StatusChipComponent } from '../shared/components/status-chip.component';
import { AvatarComponent } from '../shared/components/avatar.component';
import { TEMPLATES } from '../shared/mock-data';

@Component({
  selector: 'fc-template-list',
  standalone: true,
  imports: [CommonModule, MatIconModule, PageHeaderComponent, StatusChipComponent, AvatarComponent],
  templateUrl: './template-list.component.html',
  styleUrl: './template-list.component.scss',
})
export class TemplateListComponent {
  templates = TEMPLATES;
  activeTab = 'all';

  statusTabs = [
    { key: 'all', label: 'الكل', count: 47 },
    { key: 'published', label: 'منشور', count: 12 },
    { key: 'in-review', label: 'قيد المراجعة', count: 6 },
    { key: 'approved', label: 'معتمد', count: 8 },
    { key: 'draft', label: 'مسوّدة', count: 18 },
    { key: 'archived', label: 'مؤرشف', count: 3 },
  ];

  get filteredTemplates() {
    if (this.activeTab === 'all') return this.templates;
    return this.templates.filter(t => t.status === this.activeTab);
  }

  formatSubmissions(n: number): string {
    return n.toLocaleString('ar-EG');
  }
}

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { PageHeaderComponent } from '../shared/components/page-header.component';
import { StatusChipComponent } from '../shared/components/status-chip.component';
import { AvatarComponent } from '../shared/components/avatar.component';
import { TemplateService } from '../../../core/services/template.service';
import { RedesignCloneDialogComponent } from './clone-dialog.component';

interface RedesignTemplate {
  id: string;
  name: string;
  code: string;
  status: string;
  version: string;
  dept: string;
  updated: string;
  by: string;
  color: string;
  submissions: number;
  pages: number;
  fields: number;
}

interface TemplateRow {
  id?: string;
  name?: string;
  status?: string;
  version?: number | string;
  category?: string;
  updated_at?: string;
  created_at?: string;
  created_by?: string;
  pages?: Array<{ elements?: unknown[] }>;
}

@Component({
  selector: 'fc-template-list',
  standalone: true,
  imports: [CommonModule, FormsModule, MatIconModule, MatMenuModule, MatTooltipModule, MatDialogModule, MatSnackBarModule, PageHeaderComponent, StatusChipComponent, AvatarComponent],
  templateUrl: './template-list.component.html',
  styleUrl: './template-list.component.scss',
})
export class TemplateListComponent implements OnInit {
  templates: RedesignTemplate[] = [];
  activeTab = 'all';
  search = '';
  category = 'all';
  viewMode: 'grid' | 'list' = 'grid';
  loading = true;
  error = '';

  statusTabs = [
    { key: 'all', label: 'الكل', count: 0 },
    { key: 'published', label: 'منشور', count: 0 },
    { key: 'in-review', label: 'قيد المراجعة', count: 0 },
    { key: 'approved', label: 'معتمد', count: 0 },
    { key: 'draft', label: 'مسوّدة', count: 0 },
    { key: 'archived', label: 'مؤرشف', count: 0 },
  ];

  categories = [
    { key: 'all', label: 'جميع الإدارات' },
    { key: 'accounts', label: 'الحسابات' },
    { key: 'compliance', label: 'الالتزام' },
    { key: 'finance', label: 'التمويل' },
    { key: 'general', label: 'عام' },
  ];

  constructor(
    private templateService: TemplateService,
    private router: Router,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit(): void {
    this.loadTemplates();
  }

  get filteredTemplates() {
    const normalizedSearch = this.search.trim().toLowerCase();
    return this.templates.filter((template) => {
      const matchesTab = this.activeTab === 'all' || template.status === this.activeTab;
      const matchesCategory = this.category === 'all' || template.dept === this.categoryLabel(this.category);
      const matchesSearch =
        !normalizedSearch ||
        `${template.name} ${template.code} ${template.dept}`.toLowerCase().includes(normalizedSearch);
      return matchesTab && matchesCategory && matchesSearch;
    });
  }

  get headerSubtitle(): string {
    const published = this.statusTabs.find((tab) => tab.key === 'published')?.count ?? 0;
    const review = this.statusTabs.find((tab) => tab.key === 'in-review')?.count ?? 0;
    return `إدارة قوالب النماذج المؤسسية وإصداراتها · ${this.templates.length} قالباً · ${published} منشوراً · ${review} قيد المراجعة`;
  }

  loadTemplates(): void {
    this.loading = true;
    this.error = '';
    this.templateService.list({ limit: 100 }).subscribe({
      next: (response) => {
        this.templates = (response.data as TemplateRow[]).map((row, index) => this.mapTemplate(row, index));
        this.updateStatusCounts();
        this.loading = false;
      },
      error: () => {
        this.error = 'تعذر تحميل النماذج من قاعدة البيانات.';
        this.loading = false;
      },
    });
  }

  createTemplate(): void {
    this.router.navigate(['/ui/studio/wizard']);
  }

  importPdf(): void {
    this.router.navigate(['/ui/studio/wizard'], { queryParams: { source: 'pdf' } });
  }

  openTemplate(template: RedesignTemplate): void {
    this.router.navigate(['/ui/studio/designer', template.id]);
  }

  exportTemplates(): void {
    const payload = JSON.stringify(this.filteredTemplates, null, 2);
    const blob = new Blob([payload], { type: 'application/json;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'formcraft-templates.json';
    link.click();
    URL.revokeObjectURL(url);
  }

  cloneTemplate(event: Event, template: RedesignTemplate): void {
    event.stopPropagation();
    const dialogRef = this.dialog.open(RedesignCloneDialogComponent, {
      width: '480px',
      disableClose: true,
      data: { templateId: template.id, templateName: template.name },
    });
    dialogRef.afterClosed().subscribe((result: any) => {
      if (result) {
        this.snackBar.open('تم استنساخ النموذج بنجاح', '', { duration: 3000 });
        this.loadTemplates();
      }
    });
  }

  deleteTemplate(event: Event, template: RedesignTemplate): void {
    event.stopPropagation();
    if (!confirm(`هل أنت متأكد من حذف "${template.name}"؟`)) return;
    this.templateService.delete(template.id).subscribe({
      next: () => {
        this.snackBar.open('تم حذف النموذج', '', { duration: 3000 });
        this.loadTemplates();
      },
      error: () => {
        this.snackBar.open('فشل حذف النموذج', '', { duration: 3000 });
      },
    });
  }

  publishTemplate(event: Event, template: RedesignTemplate): void {
    event.stopPropagation();
    this.templateService.publish(template.id).subscribe({
      next: () => {
        this.snackBar.open('تم نشر النموذج بنجاح', '', { duration: 3000 });
        this.loadTemplates();
      },
      error: () => {
        this.snackBar.open('فشل نشر النموذج', '', { duration: 3000 });
      },
    });
  }

  createNewVersion(event: Event, template: RedesignTemplate): void {
    event.stopPropagation();
    this.templateService.createNewVersion(template.id).subscribe({
      next: (newTemplate: any) => {
        this.snackBar.open(`تم إنشاء الإصدار ${newTemplate.version}`, '', { duration: 3000 });
        this.router.navigate(['/ui/studio/designer', newTemplate.id]);
      },
      error: () => {
        this.snackBar.open('فشل إنشاء إصدار جديد', '', { duration: 3000 });
      },
    });
  }

  onCardAction(event: Event): void {
    event.stopPropagation();
  }

  formatSubmissions(n: number): string {
    return n.toLocaleString('ar-EG');
  }

  private mapTemplate(row: TemplateRow, index: number): RedesignTemplate {
    const pages = row.pages?.length || 1;
    const fields = row.pages?.reduce((count, page) => count + (page.elements?.length || 0), 0) || 0;
    const category = row.category || 'general';
    return {
      id: row.id || '',
      name: row.name || 'نموذج بدون اسم',
      code: this.codeFrom(row, index),
      status: this.mapStatus(row.status),
      version: `v${row.version || 1}`,
      dept: this.categoryLabel(category),
      updated: this.relativeDate(row.updated_at || row.created_at),
      by: 'النظام',
      color: `c${(index % 6) + 1}`,
      submissions: 0,
      pages,
      fields,
    };
  }

  private updateStatusCounts(): void {
    this.statusTabs = this.statusTabs.map((tab) => ({
      ...tab,
      count: tab.key === 'all'
        ? this.templates.length
        : this.templates.filter((template) => template.status === tab.key).length,
    }));
  }

  private mapStatus(status = 'draft'): string {
    if (status === 'submitted_for_review') return 'in-review';
    return status;
  }

  private categoryLabel(category: string): string {
    const labels: Record<string, string> = {
      accounts: 'الحسابات',
      compliance: 'الالتزام',
      finance: 'التمويل',
      general: 'عام',
    };
    return labels[category] || category;
  }

  private codeFrom(row: TemplateRow, index: number): string {
    const prefix = (row.category || 'TMP').slice(0, 3).toUpperCase();
    return `${prefix}-${String(index + 1).padStart(3, '0')}`;
  }

  private relativeDate(value?: string): string {
    if (!value) return 'غير معروف';
    const timestamp = new Date(value).getTime();
    if (Number.isNaN(timestamp)) return 'غير معروف';
    const minutes = Math.max(1, Math.floor((Date.now() - timestamp) / 60000));
    if (minutes < 60) return `قبل ${minutes.toLocaleString('ar-EG')} دقيقة`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `قبل ${hours.toLocaleString('ar-EG')} ساعة`;
    const days = Math.floor(hours / 24);
    return `قبل ${days.toLocaleString('ar-EG')} يوم`;
  }
}

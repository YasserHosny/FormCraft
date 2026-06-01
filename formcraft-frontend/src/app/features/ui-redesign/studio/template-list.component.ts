import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { Subject, takeUntil } from 'rxjs';
import { PageHeaderComponent } from '../shared/components/page-header.component';
import { StatusChipComponent } from '../shared/components/status-chip.component';
import { AvatarComponent } from '../shared/components/avatar.component';
import { TemplateService } from '../../../core/services/template.service';
import { RedesignCloneDialogComponent } from './clone-dialog.component';
import { environment } from '../../../../environments/environment';

interface PreviewElement {
  x_mm: number;
  y_mm: number;
  width_mm: number;
  height_mm: number;
  type: string;
}

interface RedesignTemplate {
  id: string;
  name: string;
  code: string;
  thumbnailAsset?: string | null;
  status: string;
  version: string;
  dept: string;       // stores i18n key, displayed with | translate
  updated: string;
  by: string;
  color: string;
  submissions: number;
  pages: number;
  fields: number;
  previewElements?: PreviewElement[];
}

interface TemplateRow {
  id?: string;
  name?: string;
  status?: string;
  thumbnail_asset?: string | null;
  version?: number | string;
  category?: string;
  updated_at?: string;
  created_at?: string;
  created_by?: string;
  pages?: Array<{ elements?: Array<Partial<PreviewElement> & Record<string, unknown>> }>;
}

@Component({
  selector: 'fc-template-list',
  standalone: true,
  imports: [
    CommonModule, FormsModule, MatIconModule, MatMenuModule, MatTooltipModule,
    MatDialogModule, MatSnackBarModule, TranslateModule,
    PageHeaderComponent, StatusChipComponent, AvatarComponent,
  ],
  templateUrl: './template-list.component.html',
  styleUrl: './template-list.component.scss',
})
export class TemplateListComponent implements OnInit, OnDestroy {
  templates: RedesignTemplate[] = [];
  activeTab = 'all';
  search = '';
  category = 'all';
  viewMode: 'grid' | 'list' = 'grid';
  loading = true;
  error = '';

  statusTabs = [
    { key: 'all',       labelKey: 'templates.tab_all',                      count: 0 },
    { key: 'published', labelKey: 'templates.statuses.published',            count: 0 },
    { key: 'in-review', labelKey: 'templates.statuses.submitted_for_review', count: 0 },
    { key: 'approved',  labelKey: 'templates.statuses.approved',             count: 0 },
    { key: 'draft',     labelKey: 'templates.statuses.draft',                count: 0 },
    { key: 'archived',  labelKey: 'templates.statuses.archived',             count: 0 },
  ];

  categories = [
    { key: 'all',        labelKey: 'templates.dept_all' },
    { key: 'accounts',   labelKey: 'templates.dept_accounts' },
    { key: 'compliance', labelKey: 'templates.dept_compliance' },
    { key: 'finance',    labelKey: 'templates.dept_finance' },
    { key: 'general',    labelKey: 'templates.dept_general' },
  ];

  private rawTemplates: TemplateRow[] = [];
  private destroy$ = new Subject<void>();

  constructor(
    private templateService: TemplateService,
    private router: Router,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
    private translate: TranslateService,
  ) {}

  ngOnInit(): void {
    this.loadTemplates();

    // Re-map computed string fields when language switches
    this.translate.onLangChange
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => this.remapTemplates());
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  get filteredTemplates() {
    const normalizedSearch = this.search.trim().toLowerCase();
    return this.templates.filter((template) => {
      const matchesTab = this.activeTab === 'all' || template.status === this.activeTab;
      const matchesCategory = this.category === 'all' || template.dept === this.categoryKey(this.category);
      const matchesSearch =
        !normalizedSearch ||
        `${template.name} ${template.code} ${this.translate.instant(template.dept)}`
          .toLowerCase()
          .includes(normalizedSearch);
      return matchesTab && matchesCategory && matchesSearch;
    });
  }

  get headerSubtitle(): string {
    const published = this.statusTabs.find((tab) => tab.key === 'published')?.count ?? 0;
    const review = this.statusTabs.find((tab) => tab.key === 'in-review')?.count ?? 0;
    return this.translate.instant('templates.subtitle', {
      total: this.templates.length,
      published,
      review,
    });
  }

  loadTemplates(): void {
    this.loading = true;
    this.error = '';
    this.templateService.list({ limit: 100 }).subscribe({
      next: (response) => {
        this.rawTemplates = response.data as TemplateRow[];
        this.remapTemplates();
        this.loading = false;
      },
      error: () => {
        this.error = this.translate.instant('templates.load_error');
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
        this.snackBar.open(this.translate.instant('templates.clone_success'), '', { duration: 3000 });
        this.loadTemplates();
      }
    });
  }

  deleteTemplate(event: Event, template: RedesignTemplate): void {
    event.stopPropagation();
    if (!confirm(this.translate.instant('templates.delete_confirm', { name: template.name }))) return;
    this.templateService.delete(template.id).subscribe({
      next: () => {
        this.snackBar.open(this.translate.instant('templates.delete_success'), '', { duration: 3000 });
        this.loadTemplates();
      },
      error: () => {
        this.snackBar.open(this.translate.instant('templates.delete_error'), '', { duration: 3000 });
      },
    });
  }

  publishTemplate(event: Event, template: RedesignTemplate): void {
    event.stopPropagation();
    this.templateService.publish(template.id).subscribe({
      next: () => {
        this.snackBar.open(this.translate.instant('templates.publish_success'), '', { duration: 3000 });
        this.loadTemplates();
      },
      error: () => {
        this.snackBar.open(this.translate.instant('templates.publish_error'), '', { duration: 3000 });
      },
    });
  }

  createNewVersion(event: Event, template: RedesignTemplate): void {
    event.stopPropagation();
    this.templateService.createNewVersion(template.id).subscribe({
      next: (newTemplate: any) => {
        this.snackBar.open(
          this.translate.instant('templates.new_version_success', { version: newTemplate.version }),
          '',
          { duration: 3000 },
        );
        this.router.navigate(['/ui/studio/designer', newTemplate.id]);
      },
      error: () => {
        this.snackBar.open(this.translate.instant('templates.new_version_error'), '', { duration: 3000 });
      },
    });
  }

  onCardAction(event: Event): void {
    event.stopPropagation();
  }

  formatSubmissions(n: number): string {
    const locale = this.translate.currentLang === 'ar' ? 'ar-EG' : 'en-US';
    return n.toLocaleString(locale);
  }

  // ── Private helpers ─────────────────────────────────────────────────────────

  private remapTemplates(): void {
    this.templates = this.rawTemplates.map((row, index) => this.mapTemplate(row, index));
    this.updateStatusCounts();
  }

  /** Color fill for each element type in the SVG mini-canvas. */
  elementFill(type: string): string {
    const fills: Record<string, string> = {
      text:        '#C7D2FE',   // light indigo — labels / headings
      text_block:  '#A5B4FC',   // indigo — rich text blocks
      field:       '#BBF7D0',   // green — input fields
      input:       '#BBF7D0',
      checkbox:    '#FDE68A',   // yellow — checkboxes / radio
      radio:       '#FDE68A',
      signature:   '#FBCFE8',   // pink — signature boxes
      image:       '#BAE6FD',   // sky — images / logos
      table:       '#DDD6FE',   // purple — tables / grids
      separator:   '#E2E8F0',   // slate — dividers
      barcode:     '#FEF08A',   // lime — barcodes / QR
      qr:          '#FEF08A',
    };
    return fills[type] ?? '#E2E8F0';
  }

  private mapTemplate(row: TemplateRow, index: number): RedesignTemplate {
    const pages = row.pages?.length || 1;
    const rawElements = row.pages?.[0]?.elements ?? [];
    const fields = row.pages?.reduce((count, page) => count + (page.elements?.length || 0), 0) || 0;
    const category = row.category || 'general';

    // Extract position data for the SVG mini-canvas (first page only, clipped to viewBox)
    const previewElements: PreviewElement[] = rawElements
      .filter((el) => el.x_mm != null && el.y_mm != null && el.width_mm != null && el.height_mm != null)
      .map((el) => ({
        x_mm:      el.x_mm as number,
        y_mm:      el.y_mm as number,
        width_mm:  el.width_mm as number,
        height_mm: el.height_mm as number,
        type:      (el.type as string) || 'field',
      }))
      // Only keep elements visible within the 210×130 mm viewBox
      .filter((el) => el.x_mm < 210 && el.y_mm < 130);

    return {
      id: row.id || '',
      name: row.name || this.translate.instant('templates.untitled'),
      code: this.codeFrom(row, index),
      thumbnailAsset: this.resolveThumbnailAsset(row.thumbnail_asset),
      status: this.mapStatus(row.status),
      version: `v${row.version || 1}`,
      dept: this.categoryKey(category),   // i18n key — displayed via | translate
      updated: this.relativeDate(row.updated_at || row.created_at),
      by: this.translate.instant('templates.system'),
      color: `c${(index % 6) + 1}`,
      submissions: 0,
      pages,
      fields,
      previewElements,
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

  /** Returns the i18n key for a category slug. */
  private categoryKey(category: string): string {
    const keys: Record<string, string> = {
      accounts:   'templates.dept_accounts',
      compliance: 'templates.dept_compliance',
      finance:    'templates.dept_finance',
      general:    'templates.dept_general',
    };
    return keys[category] || category;
  }

  private codeFrom(row: TemplateRow, index: number): string {
    const prefix = (row.category || 'TMP').slice(0, 3).toUpperCase();
    return `${prefix}-${String(index + 1).padStart(3, '0')}`;
  }

  private resolveThumbnailAsset(asset?: string | null): string | null {
    if (!asset) return null;
    if (/^(https?:|data:|blob:|\/)/.test(asset)) return asset;
    const baseUrl = environment.supabaseUrl.replace(/\/$/, '');
    return baseUrl
      ? `${baseUrl}/storage/v1/object/public/assets/${asset.replace(/^\/+/, '')}`
      : asset;
  }

  private relativeDate(value?: string): string {
    if (!value) return this.translate.instant('templates.unknown_date');
    const timestamp = new Date(value).getTime();
    if (Number.isNaN(timestamp)) return this.translate.instant('templates.unknown_date');
    const locale = this.translate.currentLang === 'ar' ? 'ar-EG' : 'en-US';
    const minutes = Math.max(1, Math.floor((Date.now() - timestamp) / 60000));
    if (minutes < 60) {
      return this.translate.instant('templates.time_minutes_ago', { n: minutes.toLocaleString(locale) });
    }
    const hours = Math.floor(minutes / 60);
    if (hours < 24) {
      return this.translate.instant('templates.time_hours_ago', { n: hours.toLocaleString(locale) });
    }
    const days = Math.floor(hours / 24);
    return this.translate.instant('templates.time_days_ago', { n: days.toLocaleString(locale) });
  }
}

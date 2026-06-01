import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { TranslateModule } from '@ngx-translate/core';
import { catchError, forkJoin, of, Subject, takeUntil } from 'rxjs';
import {
  DashboardFilter,
  DashboardSummaryResponse,
  DepartmentDistributionResponse,
  OperatorAnalyticsItem,
  SubmissionsOverTimeResponse,
  TopTemplatesResponse,
} from '../../analytics/models/analytics.model';
import { AnalyticsService } from '../../analytics/services/analytics.service';
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

interface OperatorRow {
  name: string;
  branch: string;
  forms: number;
  time: string;
  accuracy: number;
  color: string;
}

const PALETTE = [
  '#3F51B5',
  '#5C6BC0',
  '#7986CB',
  '#FFA000',
  '#00897B',
  '#BDBDBD',
];

@Component({
  selector: 'fc-analytics',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatMenuModule, TranslateModule, PageHeaderComponent, KpiCardComponent, AvatarComponent],
  templateUrl: './analytics.component.html',
  styleUrl: './analytics.component.scss',
})
export class AnalyticsComponent implements OnInit {
  private router = inject(Router);
  private analyticsService = inject(AnalyticsService);
  private destroy$ = new Subject<void>();

  filter: DashboardFilter = { period: '30d' };
  activePeriod: '7d' | '30d' | '90d' | 'yearly' = '30d';

  summary: DashboardSummaryResponse | null = null;
  timeSeries: SubmissionsOverTimeResponse | null = null;
  distribution: DepartmentDistributionResponse | null = null;
  topTemplates: TopTemplatesResponse | null = null;
  operators: OperatorAnalyticsItem[] = [];

  departments: { id: string; name: string }[] = [];
  branches: { id: string; name: string }[] = [];

  loadingStates = { summary: false, timeSeries: false, distribution: false, topTemplates: false, operators: false };
  errorStates = { summary: false, timeSeries: false, distribution: false, topTemplates: false, operators: false };
  private initialLoad = true;

  get selectedDeptLabel(): string {
    const dept = this.departments.find(d => d.id === this.filter.departmentId);
    return dept?.name || 'جميع الإدارات';
  }

  get selectedBranchLabel(): string {
    const branch = this.branches.find(b => b.id === this.filter.branchId);
    return branch?.name || 'جميع الفروع';
  }

  // Line chart getters
  get lineData(): number[] {
    return this.timeSeries?.points.map(p => p.count) ?? [];
  }

  get lineMax(): number {
    return this.timeSeries?.peakCount || 1;
  }

  get peakLabel(): string {
    if (!this.timeSeries?.peakCount || !this.timeSeries.peakDate) return '';
    const dateStr = new Date(this.timeSeries.peakDate).toLocaleDateString('ar-EG', { month: 'long', day: 'numeric' });
    return `${this.formatValue(this.timeSeries.peakCount)} — ${dateStr}`;
  }

  // Donut getters
  get donutData(): DonutSegment[] {
    return this.distribution?.departments.map((d, i) => ({
      label: d.departmentName,
      value: d.percentage,
      color: PALETTE[i % PALETTE.length],
    })) ?? [];
  }

  get donutTotal(): number {
    return this.distribution?.total ?? 0;
  }

  // Bar chart getters
  get barData(): BarItem[] {
    return this.topTemplates?.templates.map(t => ({
      label: t.templateName,
      value: t.count,
      code: t.templateCode,
    })) ?? [];
  }

  get barMax(): number {
    return this.barData[0]?.value || 1;
  }

  // Operator table getter
  get operatorRows(): OperatorRow[] {
    return this.operators.slice(0, 5).map((o, i) => ({
      name: o.operatorName,
      branch: '',
      forms: o.formsFilled,
      time: this.formatMsToTime(o.avgFillTimeMs),
      accuracy: +(100 - o.errorRate * 100).toFixed(1),
      color: `c${(i % 6) + 1}`,
    }));
  }

  ngOnInit(): void {
    this.loadAllWidgets();
    this.loadFilterLists();
  }

  private loadFilterLists(): void {
    // TODO: wire to actual org services when available
    this.departments = [];
    this.branches = [];
  }

  loadAllWidgets(): void {
    const filter = this.filter;
    const deptFilter = { ...filter };
    delete (deptFilter as any).departmentId;

    if (this.initialLoad) {
      this.loadingStates = { summary: true, timeSeries: true, distribution: true, topTemplates: true, operators: true };
      this.initialLoad = false;
    }
    this.errorStates = { summary: false, timeSeries: false, distribution: false, topTemplates: false, operators: false };

    forkJoin({
      summary: this.analyticsService.getDashboardSummary(filter).pipe(catchError(() => { this.errorStates.summary = true; return of(null); })),
      timeSeries: this.analyticsService.getSubmissionsOverTime(filter).pipe(catchError(() => { this.errorStates.timeSeries = true; return of(null); })),
      distribution: this.analyticsService.getDepartmentDistribution(deptFilter).pipe(catchError(() => { this.errorStates.distribution = true; return of(null); })),
      topTemplates: this.analyticsService.getTopTemplates(filter).pipe(catchError(() => { this.errorStates.topTemplates = true; return of(null); })),
      operators: this.analyticsService.getOperatorAnalytics('week', undefined, undefined, filter.branchId).pipe(catchError(() => { this.errorStates.operators = true; return of(null); })),
    }).pipe(takeUntil(this.destroy$)).subscribe({
      next: (results) => {
        if (results.summary) { this.summary = results.summary; this.loadingStates.summary = false; }
        if (results.timeSeries) { this.timeSeries = results.timeSeries; this.loadingStates.timeSeries = false; }
        if (results.distribution) { this.distribution = results.distribution; this.loadingStates.distribution = false; }
        if (results.topTemplates) { this.topTemplates = results.topTemplates; this.loadingStates.topTemplates = false; }
        if (results.operators) { this.operators = results.operators.operators; this.loadingStates.operators = false; }
      },
      error: () => {
        this.loadingStates = { summary: false, timeSeries: false, distribution: false, topTemplates: false, operators: false };
      },
    });
  }

  setPeriod(p: DashboardFilter['period']): void {
    this.filter = { ...this.filter, period: p };
    this.activePeriod = p;
    this.loadAllWidgets();
  }

  setDepartment(id: string | undefined): void {
    this.filter = { ...this.filter, departmentId: id };
    this.loadAllWidgets();
  }

  setBranch(id: string | undefined): void {
    this.filter = { ...this.filter, branchId: id };
    this.loadAllWidgets();
  }

  retryWidget(widget: string): void {
    (this.errorStates as any)[widget] = false;
    this.loadAllWidgets();
  }

  exportPdf(): void {
    this.router.navigate(['/admin/analytics'], { queryParams: { export: 'pdf' } });
  }

  openClassicAnalytics(): void {
    this.router.navigate(['/admin/analytics']);
  }

  formatValue(n: number | null | undefined): string {
    if (n == null) return '–';
    return n.toLocaleString('ar-EG');
  }

  formatMsToTime(ms: number | null | undefined): string {
    if (ms == null) return '–';
    const totalSeconds = Math.round(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }

  getBarWidth(value: number): number {
    return (value / this.barMax) * 100;
  }
}

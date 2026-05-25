import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ReportsService, TransactionFilter, ExportJobStatus } from '../../services/reports.service';
import { ReportFilterPanelComponent } from '../shared/report-filter-panel.component';
import { ReportExportButtonComponent } from '../shared/report-export-button.component';

@Component({
  selector: 'app-transaction-register',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatProgressSpinnerModule,
    ReportFilterPanelComponent,
    ReportExportButtonComponent,
  ],
  template: `
    <mat-card>
      <mat-card-header>
        <mat-card-title>{{ 'reports.transaction_register' | translate }}</mat-card-title>
      </mat-card-header>
      <mat-card-content>
        <app-report-filter-panel
          [config]="filterConfig"
          [filters]="filters"
          (filtersChange)="onFilterChange($event)">
        </app-report-filter-panel>
        <div class="actions">
          <button mat-raised-button color="primary" (click)="loadData()" [disabled]="loading">
            <mat-icon>search</mat-icon>
            {{ 'common.search' | translate }}
          </button>
          <app-report-export-button [loading]="exportLoading" (export)="onExport($event)"></app-report-export-button>
        </div>
        <div *ngIf="loading" class="spinner-container">
          <mat-spinner diameter="40"></mat-spinner>
        </div>
        <table mat-table [dataSource]="dataSource" class="mat-elevation-z1" *ngIf="!loading">
          <ng-container matColumnDef="reference_number">
            <th mat-header-cell *matHeaderCellDef>{{ 'reports.reference_number' | translate }}</th>
            <td mat-cell *matCellDef="let row">{{ row.reference_number }}</td>
          </ng-container>
          <ng-container matColumnDef="template_name">
            <th mat-header-cell *matHeaderCellDef>{{ 'reports.template' | translate }}</th>
            <td mat-cell *matCellDef="let row">{{ row.template_name }}</td>
          </ng-container>
          <ng-container matColumnDef="operator_name">
            <th mat-header-cell *matHeaderCellDef>{{ 'reports.operator' | translate }}</th>
            <td mat-cell *matCellDef="let row">{{ row.operator_name }}</td>
          </ng-container>
          <ng-container matColumnDef="customer_name">
            <th mat-header-cell *matHeaderCellDef>{{ 'reports.customer' | translate }}</th>
            <td mat-cell *matCellDef="let row">{{ row.customer_name || '-' }}</td>
          </ng-container>
          <ng-container matColumnDef="created_at">
            <th mat-header-cell *matHeaderCellDef>{{ 'reports.date' | translate }}</th>
            <td mat-cell *matCellDef="let row">{{ row.created_at | date:'short' }}</td>
          </ng-container>
          <ng-container matColumnDef="status">
            <th mat-header-cell *matHeaderCellDef>{{ 'reports.status' | translate }}</th>
            <td mat-cell *matCellDef="let row">{{ row.status }}</td>
          </ng-container>

          <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
          <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
        </table>
        <mat-paginator [length]="totalCount"
                       [pageSize]="pageSize"
                       [pageSizeOptions]="[25, 50, 100, 200]"
                       (page)="onPageChange($event)">
        </mat-paginator>
      </mat-card-content>
    </mat-card>
  `,
  styles: [`
    .actions { display: flex; gap: 12px; margin: 16px 0; }
    .spinner-container { display: flex; justify-content: center; padding: 24px; }
    table { width: 100%; margin-top: 16px; }
  `]
})
export class TransactionRegisterComponent implements OnInit {
  loading = false;
  exportLoading = false;
  displayedColumns = ['reference_number', 'template_name', 'operator_name', 'customer_name', 'created_at', 'status'];
  dataSource: any[] = [];
  totalCount = 0;
  page = 1;
  pageSize = 50;

  filters: any = {
    dateFrom: new Date(new Date().setDate(new Date().getDate() - 7)),
    dateTo: new Date(),
  };

  filterConfig = {
    showDateRange: true,
    showTemplate: true,
    showBranch: true,
    showDepartment: false,
    showOperator: false,
    showStatus: true,
    showCustomerQuery: false,
  };

  constructor(private reportsService: ReportsService) {}

  ngOnInit(): void {
    this.loadData();
  }

  onFilterChange(updated: any): void {
    this.filters = updated;
  }

  loadData(): void {
    this.loading = true;
    const filter: TransactionFilter = {
      date_from: this.filters.dateFrom.toISOString().split('T')[0],
      date_to: this.filters.dateTo.toISOString().split('T')[0],
      template_id: this.filters.templateId,
      branch_id: this.filters.branchId,
      status: this.filters.status,
    };
    this.reportsService.getTransactions(filter, this.page, this.pageSize).subscribe({
      next: (res) => {
        this.dataSource = res.data;
        this.totalCount = res.pagination.total_count;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      },
    });
  }

  onPageChange(event: PageEvent): void {
    this.page = event.pageIndex + 1;
    this.pageSize = event.pageSize;
    this.loadData();
  }

  onExport(format: 'xlsx' | 'csv' | 'pdf'): void {
    this.exportLoading = true;
    const request = {
      filters: {
        date_from: this.filters.dateFrom.toISOString().split('T')[0],
        date_to: this.filters.dateTo.toISOString().split('T')[0],
        template_id: this.filters.templateId,
        branch_id: this.filters.branchId,
        status: this.filters.status,
      },
      format,
    };
    this.reportsService.exportTransactions(request).subscribe({
      next: (res: any) => {
        this.exportLoading = false;
        if (res.job_id) {
          this.pollJob(res.job_id);
        } else if (res.download_url) {
          window.open(res.download_url, '_blank');
        }
      },
      error: () => {
        this.exportLoading = false;
      },
    });
  }

  pollJob(jobId: string): void {
    const interval = setInterval(() => {
      this.reportsService.getJobStatus(jobId).subscribe({
        next: (status: ExportJobStatus) => {
          if (status.status === 'completed' && status.download_url) {
            clearInterval(interval);
            window.open(status.download_url, '_blank');
          } else if (status.status === 'failed') {
            clearInterval(interval);
          }
        },
      });
    }, 3000);
  }
}

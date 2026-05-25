import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { FormsModule } from '@angular/forms';
import { TranslateModule } from '@ngx-translate/core';
import { TemplateGovernanceService } from '../../../core/services/template-governance.service';
import { GovernanceTemplate, GovernanceTemplateListResponse } from '../../../shared/models/governance.models';

@Component({
  selector: 'fc-template-governance',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatPaginatorModule,
    MatButtonModule,
    MatIconModule,
    MatInputModule,
    MatFormFieldModule,
    MatSelectModule,
    MatChipsModule,
    MatCheckboxModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
    TranslateModule,
  ],
  templateUrl: './template-governance.component.html',
  styleUrls: ['./template-governance.component.scss'],
})
export class TemplateGovernanceComponent implements OnInit {
  templates: GovernanceTemplate[] = [];
  displayedColumns = ['select', 'name', 'status', 'designer', 'category', 'version', 'updatedAt', 'actions'];
  loading = true;
  total = 0;
  page = 1;
  pageSize = 25;
  searchQuery = '';
  statusFilter = '';
  selectedIds = new Set<string>();

  constructor(
    private governanceService: TemplateGovernanceService,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit(): void {
    this.loadTemplates();
  }

  loadTemplates(): void {
    this.loading = true;
    this.governanceService.list({
      page: this.page,
      page_size: this.pageSize,
      search: this.searchQuery || undefined,
      status: this.statusFilter || undefined,
    }).subscribe({
      next: (response: GovernanceTemplateListResponse) => {
        this.templates = response.items;
        this.total = response.total;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.snackBar.open('Failed to load templates', '', { duration: 3000 });
      },
    });
  }

  onPageChange(event: PageEvent): void {
    this.page = event.pageIndex + 1;
    this.pageSize = event.pageSize;
    this.loadTemplates();
  }

  onSearch(): void {
    this.page = 1;
    this.loadTemplates();
  }

  onStatusChange(): void {
    this.page = 1;
    this.loadTemplates();
  }

  toggleSelection(id: string): void {
    if (this.selectedIds.has(id)) {
      this.selectedIds.delete(id);
    } else {
      this.selectedIds.add(id);
    }
  }

  isSelected(id: string): boolean {
    return this.selectedIds.has(id);
  }

  hasSelection(): boolean {
    return this.selectedIds.size > 0;
  }

  async bulkArchive(): Promise<void> {
    if (!this.hasSelection()) return;
    const confirmed = confirm(`Archive ${this.selectedIds.size} templates?`);
    if (!confirmed) return;

    this.governanceService.bulkAction({
      action: 'archive',
      template_ids: Array.from(this.selectedIds),
      dry_run: false,
    }).subscribe({
      next: () => {
        this.snackBar.open('Templates archived', '', { duration: 3000 });
        this.selectedIds.clear();
        this.loadTemplates();
      },
      error: (err: any) => {
        this.snackBar.open(err.error?.detail || 'Archive failed', '', { duration: 3000 });
      },
    });
  }

  getStatusColor(status: string): string {
    switch (status) {
      case 'draft': return '';
      case 'submitted_for_review': return 'primary';
      case 'approved': return 'accent';
      case 'rejected': return 'warn';
      case 'published': return 'primary';
      case 'archived': return '';
      default: return '';
    }
  }
}

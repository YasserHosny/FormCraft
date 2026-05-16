import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { TranslateModule } from '@ngx-translate/core';
import { TemplateService } from '../../../core/services/template.service';
import { StatusBadgeComponent } from '../../designer/components/status-badge/status-badge.component';

@Component({
  selector: 'fc-review-queue',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatDialogModule,
    MatSnackBarModule,
    TranslateModule,
    StatusBadgeComponent,
  ],
  templateUrl: './review-queue.component.html',
  styleUrls: ['./review-queue.component.scss'],
})
export class ReviewQueueComponent implements OnInit {
  templates: any[] = [];
  displayedColumns = ['name', 'version', 'created_by', 'created_at', 'status', 'actions'];
  loading = true;

  constructor(
    private templateService: TemplateService,
    private snackBar: MatSnackBar,
    private dialog: MatDialog,
  ) {}

  ngOnInit(): void {
    this.loadPending();
  }

  loadPending(): void {
    this.loading = true;
    this.templateService.list({ status: 'submitted_for_review', limit: 100 }).subscribe({
      next: (response: any) => {
        this.templates = response.data || [];
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      },
    });
  }

  approve(template: any): void {
    this.templateService.transitionStatus(template.id, 'approved').subscribe({
      next: () => {
        this.snackBar.open(this.translate('versioning.transitionSuccess', { status: 'approved' }), '', { duration: 3000 });
        this.loadPending();
      },
      error: (err: any) => {
        this.snackBar.open(err.error?.detail || this.translate('versioning.transitionError'), '', { duration: 3000 });
      },
    });
  }

  reject(template: any): void {
    const comment = prompt(this.translate('review.rejectComment'));
    if (!comment) return;
    this.templateService.transitionStatus(template.id, 'rejected', comment).subscribe({
      next: () => {
        this.snackBar.open(this.translate('versioning.transitionSuccess', { status: 'rejected' }), '', { duration: 3000 });
        this.loadPending();
      },
      error: (err: any) => {
        this.snackBar.open(err.error?.detail || this.translate('versioning.transitionError'), '', { duration: 3000 });
      },
    });
  }

  private translate(key: string, params?: any): string {
    return key;
  }
}
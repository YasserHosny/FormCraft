import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Router, RouterModule } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { TemplateFeedbackService, TemplateFeedbackAdminOverviewItem } from '../../desk/services/template-feedback.service';

@Component({
  selector: 'fc-template-feedback-overview',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatPaginatorModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatIconModule,
    MatButtonModule,
    MatTooltipModule,
    RouterModule,
    TranslateModule,
  ],
  template: `
    <div class="overview-container">
      <h2>{{ 'template_feedback.admin.title' | translate }}</h2>

      <div *ngIf="loading" class="loading-state">
        <mat-spinner diameter="40"></mat-spinner>
      </div>

      <table mat-table *ngIf="!loading" [dataSource]="items" class="overview-table">
        <ng-container matColumnDef="template">
          <th mat-header-cell *matHeaderCellDef>{{ 'template_feedback.admin.template' | translate }}</th>
          <td mat-cell *matCellDef="let item">{{ item.template_name }}</td>
        </ng-container>

        <ng-container matColumnDef="total">
          <th mat-header-cell *matHeaderCellDef>Total</th>
          <td mat-cell *matCellDef="let item">{{ item.total_feedback }}</td>
        </ng-container>

        <ng-container matColumnDef="new">
          <th mat-header-cell *matHeaderCellDef>{{ 'template_feedback.panel.statusNew' | translate }}</th>
          <td mat-cell *matCellDef="let item">
            <span class="status-chip new" *ngIf="item.new_count > 0">{{ item.new_count }}</span>
            <span *ngIf="item.new_count === 0">0</span>
          </td>
        </ng-container>

        <ng-container matColumnDef="acknowledged">
          <th mat-header-cell *matHeaderCellDef>{{ 'template_feedback.panel.statusAcknowledged' | translate }}</th>
          <td mat-cell *matCellDef="let item">
            <span class="status-chip acknowledged" *ngIf="item.acknowledged_count > 0">{{ item.acknowledged_count }}</span>
            <span *ngIf="item.acknowledged_count === 0">0</span>
          </td>
        </ng-container>

        <ng-container matColumnDef="resolved">
          <th mat-header-cell *matHeaderCellDef>{{ 'template_feedback.panel.statusResolved' | translate }}</th>
          <td mat-cell *matCellDef="let item">
            <span class="status-chip resolved" *ngIf="item.resolved_count > 0">{{ item.resolved_count }}</span>
            <span *ngIf="item.resolved_count === 0">0</span>
          </td>
        </ng-container>

        <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
        <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
      </table>

      <div *ngIf="!loading && items.length === 0" class="empty-state">
        <mat-icon>feedback</mat-icon>
        <p>{{ 'template_feedback.panel.emptyState' | translate }}</p>
      </div>
    </div>
  `,
  styles: [`
    .overview-container { padding: 24px; }
    .loading-state, .empty-state {
      display: flex; flex-direction: column; align-items: center;
      justify-content: center; padding: 48px; color: #999;
    }
    .overview-table { width: 100%; }
    .status-chip {
      display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px;
    }
    .status-chip.new { background: #e3f2fd; color: #1565c0; }
    .status-chip.acknowledged { background: #fff3e0; color: #e65100; }
    .status-chip.resolved { background: #e8f5e9; color: #2e7d32; }
    :host-context([dir='rtl']) .overview-container { text-align: right; }
  `],
})
export class TemplateFeedbackOverviewComponent implements OnInit {
  items: TemplateFeedbackAdminOverviewItem[] = [];
  loading = true;
  displayedColumns = ['template', 'total', 'new', 'acknowledged', 'resolved'];

  constructor(private feedbackService: TemplateFeedbackService) {}

  ngOnInit(): void {
    this.feedbackService.getAdminOverview().subscribe({
      next: (response) => {
        this.items = response.items || [];
        this.loading = false;
      },
      error: () => { this.loading = false; },
    });
  }
}
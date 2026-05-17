import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { TranslateModule } from '@ngx-translate/core';
import { TemplateFeedbackItem } from '../../desk/services/template-feedback.service';

@Component({
  selector: 'fc-feedback-panel',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatListModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
    TranslateModule,
  ],
  template: `
    <div class="feedback-panel">
      <div class="panel-header">
        <h3>{{ 'template_feedback.panel.title' | translate }}</h3>
        <button mat-icon-button (click)="close.emit()">
          <mat-icon>close</mat-icon>
        </button>
      </div>

      <div *ngIf="loading" class="loading-state">
        <mat-spinner diameter="32"></mat-spinner>
      </div>

      <div *ngIf="!loading && feedbackItems.length === 0" class="empty-state">
        <mat-icon>feedback</mat-icon>
        <p>{{ 'template_feedback.panel.emptyState' | translate }}</p>
      </div>

      <mat-list *ngIf="!loading && feedbackItems.length > 0" class="feedback-list">
        <mat-list-item *ngFor="let item of feedbackItems" class="feedback-item">
          <div class="item-content">
            <div class="item-header">
              <span class="item-category">{{ item.category }}</span>
              <span class="item-status" [ngClass]="item.status">
                {{ getStatusLabel(item.status) | translate }}
              </span>
            </div>
            <p class="item-comment">{{ item.comment }}</p>
            <div class="item-meta">
              <span *ngIf="item.element_key" class="item-element">
                #{{ item.element_key }}
              </span>
              <span *ngIf="item.element_key" class="show-on-canvas">
                <button mat-icon-button size="small"
                  (click)="showOnCanvas.emit(item.element_key!)"
                  [matTooltip]="'template_feedback.panel.showOnCanvas' | translate">
                  <mat-icon>location_searching</mat-icon>
                </button>
              </span>
              <span *ngIf="!item.element_key" class="general-feedback">
                {{ 'template_feedback.panel.noElement' | translate }}
              </span>
              <span class="item-date">{{ item.created_at | date:'shortDate' }}</span>
            </div>
            <div *ngIf="item.created_by_name" class="item-author">{{ item.created_by_name }}</div>
            <div class="item-actions" *ngIf="item.status !== 'resolved'">
              <button mat-stroked-button size="small"
                *ngIf="item.status === 'new'"
                (click)="acknowledge.emit(item.id)">
                {{ 'template_feedback.panel.markAcknowledged' | translate }}
              </button>
              <button mat-stroked-button size="small" color="primary"
                (click)="resolve.emit(item.id)">
                {{ 'template_feedback.panel.markResolved' | translate }}
              </button>
            </div>
          </div>
        </mat-list-item>
      </mat-list>
    </div>
  `,
  styles: [`
    .feedback-panel {
      width: 360px;
      height: 100%;
      overflow-y: auto;
      padding: 16px;
    }
    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
    }
    .panel-header h3 {
      margin: 0;
      font-size: 18px;
    }
    .loading-state, .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 48px 16px;
      color: #999;
    }
    .empty-state mat-icon {
      font-size: 48px;
      width: 48px;
      height: 48px;
      margin-bottom: 8px;
    }
    .feedback-item {
      margin-bottom: 8px;
    }
    .item-content {
      width: 100%;
    }
    .item-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 4px;
    }
    .item-category {
      font-weight: 500;
      text-transform: capitalize;
    }
    .item-status {
      font-size: 12px;
      padding: 2px 8px;
      border-radius: 12px;
    }
    .item-status.new { background: #e3f2fd; color: #1565c0; }
    .item-status.acknowledged { background: #fff3e0; color: #e65100; }
    .item-status.resolved { background: #e8f5e9; color: #2e7d32; }
    .item-comment {
      margin: 4px 0;
      font-size: 14px;
    }
    .item-meta {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      color: #666;
    }
    .item-element {
      font-family: monospace;
      background: #f5f5f5;
      padding: 2px 6px;
      border-radius: 4px;
    }
    .item-author {
      font-size: 12px;
      color: #999;
      margin-top: 2px;
    }
    .item-actions {
      margin-top: 8px;
      display: flex;
      gap: 8px;
    }
    :host-context([dir='rtl']) .feedback-panel {
      text-align: right;
    }
  `],
})
export class FeedbackPanelComponent {
  @Input() templateId: string | null = null;
  @Input() feedbackItems: TemplateFeedbackItem[] = [];
  @Input() loading = false;
  @Output() close = new EventEmitter<void>();
  @Output() showOnCanvas = new EventEmitter<string>();
  @Output() acknowledge = new EventEmitter<string>();
  @Output() resolve = new EventEmitter<string>();

  getStatusLabel(status: string): string {
    switch (status) {
      case 'new': return 'template_feedback.panel.statusNew';
      case 'acknowledged': return 'template_feedback.panel.statusAcknowledged';
      case 'resolved': return 'template_feedback.panel.statusResolved';
      default: return status;
    }
  }
}
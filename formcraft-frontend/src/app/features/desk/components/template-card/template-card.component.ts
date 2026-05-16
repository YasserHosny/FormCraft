import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { TranslateModule } from '@ngx-translate/core';
import { TemplateCard } from '../../services/desk.service';

@Component({
  selector: 'fc-template-card',
  standalone: true,
  imports: [CommonModule, RouterModule, MatCardModule, MatIconModule, MatTooltipModule, TranslateModule],
  template: `
    <mat-card class="template-card" [class.template-card--unavailable]="!isPublished"
      (click)="onCardClick()" [attr.tabindex]="0" role="button">
      <mat-card-header>
        <mat-card-title class="template-card__title">
          {{ template?.name }}
        </mat-card-title>
        <span class="template-card__version">{{ 'desk.version' | translate:{ version: template?.version } }}</span>
        <button mat-icon-button class="template-card__pin-btn"
          [matTooltip]="template?.is_pinned ? ('desk.unpin' | translate) : ('desk.pin' | translate)"
          (click)="onPinToggle($event)">
          <mat-icon [color]="template?.is_pinned ? 'warn' : undefined">
            {{ template?.is_pinned ? 'star' : 'star_border' }}
          </mat-icon>
        </button>
      </mat-card-header>
      <mat-card-content>
        <div class="deprecated-warning" *ngIf="template?.is_deprecated">
          <mat-icon color="warn">warning</mat-icon>
          <span>A newer version is available</span>
        </div>
        <p class="template-card__description" *ngIf="template?.description">
          {{ template?.description }}
        </p>
        <div class="template-card__meta">
          <span *ngIf="template?.category" class="template-card__chip">{{ template?.category }}</span>
          <span *ngIf="template?.country" class="template-card__chip">{{ template?.country }}</span>
          <span *ngIf="template?.language" class="template-card__chip">{{ template?.language }}</span>
        </div>
      </mat-card-content>
    </mat-card>
  `,
  styles: [`
    .template-card {
      cursor: pointer;
      transition: box-shadow 0.2s, opacity 0.2s;
    }
    .template-card:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    .template-card--unavailable {
      opacity: 0.5;
      pointer-events: none;
    }
    .template-card__title {
      flex: 1;
      margin: 0;
      font-size: 15px;
    }
    .template-card__version {
      font-size: 12px;
      margin-left: 8px;
      color: rgba(0, 0, 0, 0.54);
    }
    .template-card__pin-btn {
      margin-left: auto;
    }
    .template-card__description {
      margin: 4px 0;
      font-size: 13px;
      color: rgba(0, 0, 0, 0.6);
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    .template-card__meta {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
      margin-top: 8px;
    }
    .template-card__chip {
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 12px;
      background: rgba(0, 0, 0, 0.06);
    }
    .deprecated-warning {
      display: flex;
      align-items: center;
      gap: 4px;
      padding: 6px 10px;
      margin-bottom: 6px;
      background: #fff3e0;
      border-radius: 4px;
      font-size: 12px;
      color: #e65100;
    }
    :host-context([dir='rtl']) .template-card__version {
      margin-left: 0;
      margin-right: 8px;
    }
  `],
})
export class TemplateCardComponent {
  @Input() template: TemplateCard | null = null;
  @Input() isPublished = true;
  @Input() lastUsedAt: string | null = null;
  @Output() pinToggle = new EventEmitter<TemplateCard>();
  @Output() cardClick = new EventEmitter<TemplateCard>();

  onPinToggle(event: Event): void {
    event.stopPropagation();
    if (this.template) {
      this.pinToggle.emit(this.template);
    }
  }

  onCardClick(): void {
    if (this.template && this.isPublished) {
      this.cardClick.emit(this.template);
    }
  }
}
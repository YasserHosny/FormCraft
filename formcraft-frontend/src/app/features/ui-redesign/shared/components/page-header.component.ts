import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'fc-page-header',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="fc-page-header">
      <div class="header-text">
        <h1 class="fc-page-title">{{ title }}</h1>
        <div class="fc-page-sub" *ngIf="subtitle">{{ subtitle }}</div>
      </div>
      <div class="header-actions">
        <ng-content select="[actions]"></ng-content>
      </div>
    </div>
  `,
  styles: [`
    .fc-page-header {
      background: var(--fc-surface);
      border-bottom: 1px solid var(--fc-border);
      padding: 14px 24px;
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .header-text { flex: 1; }
    .fc-page-title {
      font-size: 18px;
      font-weight: 700;
      margin: 0;
      color: var(--fc-text);
    }
    .fc-page-sub {
      font-size: 12px;
      color: var(--fc-text-3);
      margin-top: 2px;
    }
    .header-actions {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  `],
})
export class PageHeaderComponent {
  @Input() title = '';
  @Input() subtitle = '';
}

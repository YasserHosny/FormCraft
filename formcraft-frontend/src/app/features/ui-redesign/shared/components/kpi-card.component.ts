import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'fc-kpi-card',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  template: `
    <div class="fc-kpi">
      <div class="fc-kpi-label">{{ label }}</div>
      <div class="fc-kpi-value">{{ value }}</div>
      <div class="fc-kpi-delta" [class.up]="deltaDir === 'up'" [class.down]="deltaDir === 'down'" *ngIf="delta">
        <mat-icon>{{ deltaDir === 'up' ? 'trending_up' : 'trending_down' }}</mat-icon>
        {{ delta }}
      </div>
      <div class="fc-kpi-icon" *ngIf="icon">
        <mat-icon>{{ icon }}</mat-icon>
      </div>
    </div>
  `,
  styleUrl: './kpi-card.component.scss',
})
export class KpiCardComponent {
  @Input() label = '';
  @Input() value = '';
  @Input() delta = '';
  @Input() deltaDir: 'up' | 'down' = 'up';
  @Input() icon = '';
}

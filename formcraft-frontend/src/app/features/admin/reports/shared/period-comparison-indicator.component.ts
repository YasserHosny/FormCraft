import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-period-comparison-indicator',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  template: `
    <span class="indicator" [class.positive]="value > 0" [class.negative]="value < 0" [class.neutral]="value === 0">
      <mat-icon>{{ value > 0 ? 'trending_up' : value < 0 ? 'trending_down' : 'trending_flat' }}</mat-icon>
      {{ value | number:'1.2-2' }}%
    </span>
  `,
  styles: [`
    .indicator { display: inline-flex; align-items: center; gap: 4px; font-weight: 500; }
    .positive { color: #2e7d32; }
    .negative { color: #c62828; }
    .neutral { color: #757575; }
  `]
})
export class PeriodComparisonIndicatorComponent {
  @Input() value = 0;
}

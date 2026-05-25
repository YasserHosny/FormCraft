import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { STATUS_LABELS } from '../mock-data';

@Component({
  selector: 'fc-status-chip',
  standalone: true,
  imports: [CommonModule],
  template: `
    <span class="fc-chip" [ngClass]="status">
      <span class="dot"></span>
      {{ statusLabel }}
    </span>
  `,
  styleUrl: './status-chip.component.scss',
})
export class StatusChipComponent {
  @Input() status = 'draft';

  get statusLabel(): string {
    return STATUS_LABELS[this.status] || this.status;
  }
}

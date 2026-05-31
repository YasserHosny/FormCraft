import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

const STATUS_LABELS: Record<string, string> = {
  draft: 'مسوّدة',
  'in-review': 'قيد المراجعة',
  approved: 'معتمد',
  published: 'منشور',
  archived: 'مؤرشف',
  rejected: 'مرفوض',
  active: 'نشط',
  inactive: 'موقوف',
};

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

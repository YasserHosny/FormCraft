import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'fc-status-chip',
  standalone: true,
  imports: [CommonModule, TranslateModule],
  template: `
    <span class="fc-chip" [ngClass]="status">
      <span class="dot"></span>
      {{ 'status.' + statusKey | translate }}
    </span>
  `,
  styleUrl: './status-chip.component.scss',
})
export class StatusChipComponent {
  @Input() status = 'draft';

  get statusKey(): string {
    // Normalise backend status strings → i18n key (e.g. "in-review" → "in_review")
    return this.status.replace(/-/g, '_').replace(/\s+/g, '_').toLowerCase();
  }
}

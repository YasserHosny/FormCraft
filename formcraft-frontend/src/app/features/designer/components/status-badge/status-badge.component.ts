import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatChipsModule } from '@angular/material/chips';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'fc-status-badge',
  standalone: true,
  imports: [CommonModule, MatChipsModule, TranslateModule],
  template: `
    <mat-chip [ngClass]="statusClass" [disabled]="false">
      {{ 'versioning.statusBadge.' + status | translate }}
    </mat-chip>
  `,
  styles: [`
    :host { display: inline-block; }
    .status-draft { background: #9e9e9e !important; color: white !important; }
    .status-submitted_for_review { background: #1976d2 !important; color: white !important; }
    .status-approved { background: #388e3c !important; color: white !important; }
    .status-rejected { background: #d32f2f !important; color: white !important; }
    .status-published { background: #00897b !important; color: white !important; }
    .status-archived { background: #f57c00 !important; color: white !important; }
    .status-deprecated { background: #c62828 !important; color: white !important; }
  `],
})
export class StatusBadgeComponent {
  @Input() status: string = 'draft';

  get statusClass(): string {
    return 'status-' + (this.status || 'draft');
  }
}
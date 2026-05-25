import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'fc-avatar',
  standalone: true,
  imports: [CommonModule],
  template: `<span class="fc-avatar" [ngClass]="[size, color]">{{ initials }}</span>`,
  styles: [`
    .fc-avatar {
      display: inline-grid;
      place-items: center;
      border-radius: 50%;
      font-weight: 700;
      font-family: 'Noto Sans', sans-serif;
      flex-shrink: 0;
      &.sm { width: 24px; height: 24px; font-size: 10px; }
      &.md { width: 28px; height: 28px; font-size: 11px; }
      &.lg { width: 32px; height: 32px; font-size: 12px; }
      &.c1 { background: #E8EAF6; color: #303F9F; }
      &.c2 { background: #FFF3E0; color: #B85C00; }
      &.c3 { background: #E0F2F1; color: #00695C; }
      &.c4 { background: #F3E5F5; color: #6A1B9A; }
      &.c5 { background: #FCE4EC; color: #AD1457; }
      &.c6 { background: #E3F2FD; color: #1565C0; }
    }
  `],
})
export class AvatarComponent {
  @Input() name = '';
  @Input() size: 'sm' | 'md' | 'lg' = 'sm';
  @Input() color = 'c1';

  get initials(): string {
    const parts = this.name.trim().split(/\s+/);
    if (parts.length === 1) return parts[0].slice(0, 2);
    return parts[0][0] + parts[parts.length - 1][0];
  }
}

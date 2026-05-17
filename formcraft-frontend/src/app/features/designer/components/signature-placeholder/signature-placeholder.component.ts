import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'fc-signature-placeholder',
  standalone: true,
  imports: [CommonModule, TranslateModule],
  template: `
    <div class="signature-placeholder" [style.width.px]="widthPx" [style.height.px]="heightPx">
      <div class="signature-border">
        <mat-icon class="signature-icon">draw</mat-icon>
        <span class="signature-label">{{ label }}</span>
      </div>
    </div>
  `,
  styles: [`
    .signature-placeholder {
      display: flex;
      align-items: center;
      justify-content: center;
      border: 2px dashed #999;
      border-radius: 4px;
      background: rgba(0,0,0,0.02);
      cursor: default;
      overflow: hidden;
    }
    .signature-border {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 4px;
      color: #999;
    }
    .signature-icon {
      font-size: 24px;
      width: 24px;
      height: 24px;
    }
    .signature-label {
      font-size: 12px;
    }
    :host-context([dir='rtl']) .signature-label {
      direction: rtl;
    }
  `],
})
export class SignaturePlaceholderComponent {
  @Input() widthPx = 200;
  @Input() heightPx = 80;
  @Input() label = 'Signature';
}
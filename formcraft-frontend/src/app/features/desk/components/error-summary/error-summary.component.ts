import { Component, Input } from '@angular/core';
import { FormGroup, AbstractControl } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatBadgeModule } from '@angular/material/badge';

@Component({
  selector: 'fc-error-summary',
  standalone: true,
  imports: [
    CommonModule,
    TranslateModule,
    MatButtonModule,
    MatIconModule,
    MatBadgeModule,
  ],
  template: `
    <div class="error-summary-banner" *ngIf="errorCount > 0" (click)="scrollToFirstError()">
      <mat-icon class="error-icon">error_outline</mat-icon>
      <span class="error-text">{{ 'filler.error_summary' | translate:{count: errorCount} }}</span>
      <button mat-icon-button class="error-scroll-btn" [matTooltip]="'Scroll to first error'">
        <mat-icon>keyboard_arrow_down</mat-icon>
      </button>
    </div>
  `,
  styles: [`
    .error-summary-banner {
      position: sticky;
      top: 64px;
      z-index: 99;
      display: flex;
      align-items: center;
      padding: 8px 16px;
      background-color: #f44336;
      color: white;
      border-radius: 4px;
      margin-bottom: 16px;
      cursor: pointer;
    }
    .error-icon {
      margin-right: 8px;
    }
    .error-text {
      flex: 1;
      font-weight: 500;
    }
    .error-scroll-btn {
      color: white;
    }
    :host-context([dir='rtl']) .error-icon {
      margin-right: 0;
      margin-left: 8px;
    }
  `],
})
export class ErrorSummaryComponent {
  @Input() form: FormGroup | null = null;

  constructor(private translate: TranslateService) {}

  get errorCount(): number {
    if (!this.form) return 0;
    let count = 0;
    const controls = this.form.controls;
    for (const key in controls) {
      if (controls.hasOwnProperty(key)) {
        const control = controls[key];
        if (control.invalid && control.touched) {
          count++;
        }
      }
    }
    return count;
  }

  scrollToFirstError(): void {
    const controls = this.form?.controls;
    if (!controls) return;
    for (const key in controls) {
      if (controls.hasOwnProperty(key)) {
        const control = controls[key];
        if (control.invalid && control.touched) {
          const el = document.querySelector(`[formcontrolname="${key}"]`);
          if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            (el as HTMLElement).focus();
          }
          return;
        }
      }
    }
  }
}
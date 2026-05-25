import { Component, EventEmitter, Input, Output } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { PortalService } from '../../../core/services/portal.service';

@Component({
  selector: 'fc-otp-gate',
  standalone: false,
  templateUrl: './otp-gate.component.html',
  styleUrls: ['./otp-gate.component.scss'],
})
export class OtpGateComponent {
  Math = Math;
  @Input() sessionToken = '';
  @Input() allowedModes: string[] = [];
  @Output() verified = new EventEmitter<void>();

  contactMode: 'sms' | 'email' | null = null;
  contactValue = '';
  code = '';
  isSending = false;
  isVerifying = false;
  sent = false;
  error: string | null = null;
  lockoutTimer = 0;
  lockoutInterval: any = null;

  constructor(
    private portalService: PortalService,
    private translate: TranslateService,
  ) {}

  sendCode(): void {
    if (!this.contactMode || !this.contactValue || this.isSending) return;
    this.isSending = true;
    this.error = null;

    this.portalService
      .sendOtp(this.sessionToken, {
        contact_mode: this.contactMode,
        contact_value: this.contactValue,
      })
      .subscribe({
        next: () => {
          this.isSending = false;
          this.sent = true;
        },
        error: (err) => {
          this.isSending = false;
          this.handleError(err);
        },
      });
  }

  verifyCode(): void {
    if (!this.code || this.isVerifying) return;
    this.isVerifying = true;
    this.error = null;

    this.portalService
      .verifyOtp(this.sessionToken, { code: this.code })
      .subscribe({
        next: () => {
          this.isVerifying = false;
          this.verified.emit();
        },
        error: (err) => {
          this.isVerifying = false;
          this.handleError(err);
        },
      });
  }

  private handleError(err: any): void {
    const status = err?.status;
    if (status === 423) {
      this.error = this.translate.instant('otpGate.locked');
      this.startLockoutTimer(15);
    } else if (status === 503) {
      this.error = this.translate.instant('otpGate.providerError');
    } else {
      this.error = this.translate.instant('otpGate.invalidCode');
    }
  }

  private startLockoutTimer(minutes: number): void {
    this.lockoutTimer = minutes * 60;
    if (this.lockoutInterval) clearInterval(this.lockoutInterval);
    this.lockoutInterval = setInterval(() => {
      this.lockoutTimer--;
      if (this.lockoutTimer <= 0) {
        clearInterval(this.lockoutInterval);
      }
    }, 1000);
  }
}

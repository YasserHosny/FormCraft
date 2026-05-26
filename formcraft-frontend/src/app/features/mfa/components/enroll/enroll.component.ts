import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MfaService } from '../../../core/services/mfa.service';

@Component({
  selector: 'app-enroll',
  template: `
    <mat-card>
      <mat-card-title>{{ 'mfa.enroll.title' | translate }}</mat-card-title>
      <mat-card-content>
        <form [formGroup]="form" (ngSubmit)="onSubmit()">
          <mat-form-field appearance="fill" class="full-width">
            <mat-label>{{ 'mfa.enroll.methodType' | translate }}</mat-label>
            <mat-select formControlName="method_type">
              <mat-option value="totp">{{ 'mfa.enroll.totp' | translate }}</mat-option>
              <mat-option value="sms">{{ 'mfa.enroll.sms' | translate }}</mat-option>
              <mat-option value="email">{{ 'mfa.enroll.email' | translate }}</mat-option>
            </mat-select>
          </mat-form-field>

          <mat-form-field appearance="fill" class="full-width" *ngIf="form.value.method_type !== 'totp'">
            <mat-label>{{ 'mfa.enroll.phoneNumber' | translate }}</mat-label>
            <input matInput formControlName="phone_number" />
          </mat-form-field>

          <div *ngIf="qrUri">
            <img [src]="qrUri" alt="QR Code" />
            <p>{{ 'mfa.enroll.scanQr' | translate }}</p>
          </div>

          <button mat-raised-button color="primary" type="submit" [disabled]="form.invalid">
            {{ 'common.next' | translate }}
          </button>
        </form>
      </mat-card-content>
    </mat-card>
  `,
  styles: [`
    .full-width { width: 100%; margin-bottom: 1rem; }
    img { max-width: 200px; display: block; margin: 1rem 0; }
  `],
})
export class EnrollComponent {
  form: FormGroup;
  qrUri: string | null = null;

  constructor(private fb: FormBuilder, private mfa: MfaService) {
    this.form = this.fb.group({
      method_type: ['totp', Validators.required],
      phone_number: [''],
    });
  }

  onSubmit(): void {
    if (this.form.invalid) return;
    const { method_type, phone_number } = this.form.value;
    this.mfa.enroll(method_type, phone_number).subscribe((res) => {
      this.qrUri = res.qr_code_uri || null;
      // If QR shown, next step would be verify enrollment
    });
  }
}

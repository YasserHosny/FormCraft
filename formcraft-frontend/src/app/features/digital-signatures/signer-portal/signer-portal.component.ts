import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-signer-portal',
  template: `
    <div class="container" *ngIf="metadata">
      <h2>{{ metadata.template_name }}</h2>
      <p>{{ metadata.organization_name }}</p>
      <p>{{ 'SIGNATURE.SIGNER_NAME' | translate }}: {{ metadata.signer_name }}</p>
      <p>{{ 'SIGNATURE.STATUS' | translate }}: {{ metadata.status }}</p>

      <div *ngIf="metadata.requires_otp && !verified">
        <button mat-raised-button (click)="sendOtp()">{{ 'SIGNATURE.SEND_OTP' | translate }}</button>
        <mat-form-field appearance="fill">
          <mat-label>{{ 'SIGNATURE.OTP_CODE' | translate }}</mat-label>
          <input matInput [(ngModel)]="otp" />
        </mat-form-field>
        <button mat-raised-button color="primary" (click)="verifyOtp()">{{ 'SIGNATURE.VERIFY' | translate }}</button>
      </div>

      <div *ngIf="!metadata.requires_otp && !verified">
        <mat-form-field appearance="fill">
          <mat-label>{{ 'SIGNATURE.PASSWORD' | translate }}</mat-label>
          <input matInput type="password" [(ngModel)]="password" />
        </mat-form-field>
        <button mat-raised-button color="primary" (click)="authenticate()">{{ 'SIGNATURE.AUTHENTICATE' | translate }}</button>
      </div>

      <div *ngIf="verified">
        <button mat-raised-button color="primary" (click)="sign()">{{ 'SIGNATURE.SIGN' | translate }}</button>
        <button mat-raised-button (click)="decline()">{{ 'SIGNATURE.DECLINE' | translate }}</button>
      </div>
    </div>
  `,
  standalone: false,
})
export class SignerPortalComponent implements OnInit {
  token: string = '';
  metadata: any;
  otp: string = '';
  password: string = '';
  verified = false;

  constructor(private route: ActivatedRoute, private http: HttpClient) {}

  ngOnInit(): void {
    this.token = this.route.snapshot.paramMap.get('token') || '';
    this.http.get(`/api/sign/${this.token}`).subscribe((res: any) => {
      this.metadata = res;
    });
  }

  sendOtp(): void {
    this.http.post(`/api/sign/${this.token}/otp/send`, {}).subscribe();
  }

  verifyOtp(): void {
    this.http.post(`/api/sign/${this.token}/otp/verify`, { otp: this.otp }).subscribe(() => {
      this.verified = true;
    });
  }

  authenticate(): void {
    this.http.post(`/api/sign/${this.token}/authenticate`, { password: this.password }).subscribe(() => {
      this.verified = true;
    });
  }

  sign(): void {
    this.http.post(`/api/sign/${this.token}/sign`, { consent: true }).subscribe();
  }

  decline(): void {
    this.http.post(`/api/sign/${this.token}/decline`, {}).subscribe();
  }
}

import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-domain-verify',
  template: `
    <mat-card>
      <mat-card-title>{{ 'sso.domainVerify.title' | translate }}</mat-card-title>
      <mat-card-content>
        <form [formGroup]="form" (ngSubmit)="onSubmit()">
          <mat-form-field appearance="fill" class="full-width">
            <mat-label>{{ 'sso.domainVerify.domain' | translate }}</mat-label>
            <input matInput formControlName="domain" />
          </mat-form-field>
          <button mat-raised-button color="primary" type="submit" [disabled]="form.invalid">
            {{ 'common.verify' | translate }}
          </button>
        </form>
      </mat-card-content>
    </mat-card>
  `,
  styles: [`
    .full-width { width: 100%; margin-bottom: 1rem; }
  `],
})
export class DomainVerifyComponent {
  form: FormGroup;

  constructor(private fb: FormBuilder) {
    this.form = this.fb.group({
      domain: ['', [Validators.required]],
    });
  }

  onSubmit(): void {
    if (this.form.invalid) return;
    // Call verification API
  }
}

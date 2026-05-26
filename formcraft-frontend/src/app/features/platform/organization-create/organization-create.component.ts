import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { PlatformService } from '../../../core/services/platform.service';

@Component({
  selector: 'app-organization-create',
  template: `
    <div class="create-container">
      <h1>{{ 'PLATFORM.CREATE_ORG_TITLE' | translate }}</h1>
      <form [formGroup]="form" (ngSubmit)="submit()">
        <mat-form-field appearance="outline">
          <mat-label>{{ 'PLATFORM.ORG_NAME_AR' | translate }}</mat-label>
          <input matInput formControlName="name_ar" required />
          <mat-error *ngIf="form.get('name_ar')?.hasError('required')">
            {{ 'PLATFORM.REQUIRED' | translate }}
          </mat-error>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>{{ 'PLATFORM.ORG_NAME_EN' | translate }}</mat-label>
          <input matInput formControlName="name_en" />
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>{{ 'PLATFORM.DEFAULT_LANGUAGE' | translate }}</mat-label>
          <mat-select formControlName="default_language">
            <mat-option value="ar">{{ 'LANG.ARABIC' | translate }}</mat-option>
            <mat-option value="en">{{ 'LANG.ENGLISH' | translate }}</mat-option>
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>{{ 'PLATFORM.DEFAULT_COUNTRY' | translate }}</mat-label>
          <input matInput formControlName="default_country" />
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>{{ 'PLATFORM.DEFAULT_CURRENCY' | translate }}</mat-label>
          <input matInput formControlName="default_currency" />
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>{{ 'PLATFORM.SUBSCRIPTION_TIER' | translate }}</mat-label>
          <mat-select formControlName="subscription_tier">
            <mat-option value="starter">Starter</mat-option>
            <mat-option value="professional">Professional</mat-option>
            <mat-option value="enterprise">Enterprise</mat-option>
            <mat-option value="platform">Platform</mat-option>
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>{{ 'PLATFORM.CUSTOM_DOMAIN' | translate }}</mat-label>
          <input matInput formControlName="domain" />
          <mat-error *ngIf="form.get('domain')?.hasError('domainTaken')">
            {{ 'PLATFORM.DOMAIN_TAKEN' | translate }}
          </mat-error>
        </mat-form-field>

        <div class="actions">
          <button mat-raised-button color="primary" type="submit" [disabled]="form.invalid || submitting">
            {{ 'PLATFORM.SUBMIT' | translate }}
          </button>
          <button mat-button type="button" (click)="cancel()">
            {{ 'PLATFORM.CANCEL' | translate }}
          </button>
        </div>
      </form>
    </div>
  `,
  styles: [
    `.create-container { padding: 16px; max-width: 600px; }`,
    `mat-form-field { display: block; margin-bottom: 16px; }`,
    `.actions { display: flex; gap: 16px; }`,
  ],
})
export class OrganizationCreateComponent {
  form: FormGroup;
  submitting = false;

  constructor(
    private fb: FormBuilder,
    private platformService: PlatformService,
    private router: Router
  ) {
    this.form = this.fb.group({
      name_ar: ['', Validators.required],
      name_en: [''],
      default_language: ['ar'],
      default_country: ['SA'],
      default_currency: ['SAR'],
      subscription_tier: ['starter'],
      domain: [''],
    });
  }

  submit(): void {
    if (this.form.invalid) return;
    this.submitting = true;
    this.platformService.createOrganization(this.form.value).subscribe({
      next: (org) => {
        this.router.navigate(['/platform/organizations', org.id]);
      },
      error: (err) => {
        this.submitting = false;
        if (err.status === 409) {
          this.form.get('domain')?.setErrors({ domainTaken: true });
        }
      },
    });
  }

  cancel(): void {
    this.router.navigate(['/platform/organizations']);
  }
}

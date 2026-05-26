import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { SsoService, IdentityProviderCreate } from '../../../core/services/sso.service';

@Component({
  selector: 'app-idp-config',
  template: `
    <mat-card>
      <mat-card-title>{{ 'sso.idpConfig.title' | translate }}</mat-card-title>
      <mat-card-content>
        <form [formGroup]="form" (ngSubmit)="onSubmit()">
          <mat-form-field appearance="fill" class="full-width">
            <mat-label>{{ 'sso.idpConfig.name' | translate }}</mat-label>
            <input matInput formControlName="name" />
          </mat-form-field>

          <mat-form-field appearance="fill" class="full-width">
            <mat-label>{{ 'sso.idpConfig.type' | translate }}</mat-label>
            <mat-select formControlName="provider_type">
              <mat-option value="saml">SAML 2.0</mat-option>
              <mat-option value="oidc">OpenID Connect</mat-option>
            </mat-select>
          </mat-form-field>

          <mat-form-field appearance="fill" class="full-width">
            <mat-label>{{ 'sso.idpConfig.domains' | translate }}</mat-label>
            <input matInput formControlName="domains" placeholder="example.com" />
          </mat-form-field>

          <mat-form-field appearance="fill" class="full-width">
            <mat-label>{{ 'sso.idpConfig.metadataUrl' | translate }}</mat-label>
            <input matInput formControlName="metadata_url" />
          </mat-form-field>

          <button mat-raised-button color="primary" type="submit" [disabled]="form.invalid">
            {{ 'common.save' | translate }}
          </button>
        </form>
      </mat-card-content>
    </mat-card>
  `,
  styles: [`
    .full-width { width: 100%; margin-bottom: 1rem; }
  `],
})
export class IdpConfigComponent {
  form: FormGroup;

  constructor(private fb: FormBuilder, private sso: SsoService) {
    this.form = this.fb.group({
      name: ['', Validators.required],
      provider_type: ['saml', Validators.required],
      domains: ['', Validators.required],
      metadata_url: [''],
    });
  }

  onSubmit(): void {
    if (this.form.invalid) return;
    const payload: IdentityProviderCreate = {
      ...this.form.value,
      domains: this.form.value.domains.split(',').map((d: string) => d.trim()),
    };
    this.sso.createProvider(payload).subscribe(() => {
      // Handle success (toast, navigation)
    });
  }
}

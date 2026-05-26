import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-mapping-config',
  template: `
    <mat-card>
      <mat-card-title>{{ 'sso.mappingConfig.title' | translate }}</mat-card-title>
      <mat-card-content>
        <form [formGroup]="form" (ngSubmit)="onSubmit()">
          <mat-form-field appearance="fill" class="full-width">
            <mat-label>{{ 'sso.mappingConfig.claimType' | translate }}</mat-label>
            <input matInput formControlName="claim_type" />
          </mat-form-field>
          <mat-form-field appearance="fill" class="full-width">
            <mat-label>{{ 'sso.mappingConfig.claimValue' | translate }}</mat-label>
            <input matInput formControlName="claim_value" />
          </mat-form-field>
          <mat-form-field appearance="fill" class="full-width">
            <mat-label>{{ 'sso.mappingConfig.assignedRole' | translate }}</mat-label>
            <input matInput formControlName="assigned_role" />
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
export class MappingConfigComponent {
  form: FormGroup;

  constructor(private fb: FormBuilder) {
    this.form = this.fb.group({
      claim_type: ['', Validators.required],
      claim_value: ['', Validators.required],
      assigned_role: [''],
    });
  }

  onSubmit(): void {
    if (this.form.invalid) return;
    // Save mapping
  }
}

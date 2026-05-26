import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { DigitalSignatureService } from '../../../core/services/digital-signature.service';

@Component({
  selector: 'app-workflow-config',
  template: `
    <div class="container">
      <h2>{{ 'SIGNATURE.WORKFLOW_CONFIG' | translate }}</h2>
      <form [formGroup]="form" (ngSubmit)="save()">
        <mat-form-field appearance="fill">
          <mat-label>{{ 'SIGNATURE.WORKFLOW_NAME' | translate }}</mat-label>
          <input matInput formControlName="name" />
        </mat-form-field>

        <mat-slide-toggle formControlName="is_ordered">
          {{ 'SIGNATURE.ORDERED_SIGNING' | translate }}
        </mat-slide-toggle>

        <mat-form-field appearance="fill">
          <mat-label>{{ 'SIGNATURE.EXPIRATION_DAYS' | translate }}</mat-label>
          <input matInput type="number" formControlName="expiration_days" min="1" max="30" />
        </mat-form-field>

        <mat-form-field appearance="fill">
          <mat-label>{{ 'SIGNATURE.DECLINE_POLICY' | translate }}</mat-label>
          <mat-select formControlName="decline_policy">
            <mat-option value="stop">{{ 'SIGNATURE.POLICY_STOP' | translate }}</mat-option>
            <mat-option value="continue_next">{{ 'SIGNATURE.POLICY_CONTINUE' | translate }}</mat-option>
            <mat-option value="route_to_admin">{{ 'SIGNATURE.POLICY_ROUTE_ADMIN' | translate }}</mat-option>
          </mat-select>
        </mat-form-field>

        <mat-slide-toggle formControlName="require_all_signers">
          {{ 'SIGNATURE.REQUIRE_ALL' | translate }}
        </mat-slide-toggle>

        <button mat-raised-button color="primary" type="submit" [disabled]="form.invalid">
          {{ 'COMMON.SAVE' | translate }}
        </button>
      </form>
    </div>
  `,
  standalone: false,
})
export class WorkflowConfigComponent implements OnInit {
  form: FormGroup;

  constructor(private fb: FormBuilder, private service: DigitalSignatureService) {
    this.form = this.fb.group({
      name: ['', Validators.required],
      is_ordered: [false],
      expiration_days: [7, [Validators.min(1), Validators.max(30)]],
      decline_policy: ['stop'],
      require_all_signers: [true],
    });
  }

  ngOnInit(): void {}

  save(): void {
    if (this.form.invalid) return;
    this.service.createWorkflow(this.form.value).subscribe(() => {
      // handle success
    });
  }
}

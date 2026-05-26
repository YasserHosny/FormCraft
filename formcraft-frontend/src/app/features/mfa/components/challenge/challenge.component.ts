import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MfaService } from '../../../core/services/mfa.service';

@Component({
  selector: 'app-challenge',
  template: `
    <mat-card>
      <mat-card-title>{{ 'mfa.challenge.title' | translate }}</mat-card-title>
      <mat-card-content>
        <form [formGroup]="form" (ngSubmit)="onSubmit()">
          <mat-form-field appearance="fill" class="full-width">
            <mat-label>{{ 'mfa.challenge.code' | translate }}</mat-label>
            <input matInput formControlName="code" maxlength="6" />
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
export class ChallengeComponent {
  form: FormGroup;

  constructor(private fb: FormBuilder, private mfa: MfaService, private router: Router) {
    this.form = this.fb.group({
      code: ['', [Validators.required, Validators.minLength(6), Validators.maxLength(6)]],
    });
  }

  onSubmit(): void {
    if (this.form.invalid) return;
    // In real app we would track challenge_id from the challenge response
    const challengeId = 'placeholder';
    this.mfa.verifyChallenge(challengeId, this.form.value.code).subscribe(() => {
      this.router.navigate(['/templates']);
    });
  }
}

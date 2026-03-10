import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { HttpClient } from '@angular/common/http';
import { TranslateService } from '@ngx-translate/core';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'fc-register',
  standalone: false,
  template: `
    <div class="register-container">
      <mat-card class="register-card">
        <mat-card-header>
          <mat-card-title>{{ 'auth.register' | translate }}</mat-card-title>
        </mat-card-header>
        <mat-card-content>
          <form [formGroup]="registerForm" (ngSubmit)="onSubmit()">
            <mat-form-field appearance="outline" class="full-width">
              <mat-label>{{ 'auth.email' | translate }}</mat-label>
              <input matInput type="email" formControlName="email" />
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>{{ 'auth.password' | translate }}</mat-label>
              <input matInput type="password" formControlName="password" />
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Display Name</mat-label>
              <input matInput formControlName="display_name" fcAutoDir />
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>{{ 'auth.role' | translate }}</mat-label>
              <mat-select formControlName="role">
                <mat-option value="admin">{{ 'roles.admin' | translate }}</mat-option>
                <mat-option value="designer">{{ 'roles.designer' | translate }}</mat-option>
                <mat-option value="operator">{{ 'roles.operator' | translate }}</mat-option>
                <mat-option value="viewer">{{ 'roles.viewer' | translate }}</mat-option>
              </mat-select>
            </mat-form-field>

            <div *ngIf="errorMessage" class="error-message">{{ errorMessage }}</div>

            <button
              mat-raised-button
              color="primary"
              type="submit"
              class="full-width"
              [disabled]="registerForm.invalid || loading"
            >
              <mat-spinner *ngIf="loading" diameter="20"></mat-spinner>
              <span *ngIf="!loading">{{ 'auth.register' | translate }}</span>
            </button>
          </form>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .register-container {
      display: flex;
      justify-content: center;
      padding: 48px 24px;
    }
    .register-card {
      width: 480px;
      padding: 24px;
    }
    .full-width {
      width: 100%;
    }
    mat-form-field {
      margin-bottom: 16px;
    }
    .error-message {
      color: #f44336;
      margin-bottom: 16px;
      font-size: 14px;
    }
  `],
})
export class RegisterComponent {
  registerForm: FormGroup;
  loading = false;
  errorMessage = '';

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private router: Router,
    private snackBar: MatSnackBar,
    private translate: TranslateService
  ) {
    this.registerForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      display_name: [''],
      role: ['viewer', Validators.required],
    });
  }

  onSubmit(): void {
    if (this.registerForm.invalid) return;
    this.loading = true;
    this.errorMessage = '';

    this.http
      .post(`${environment.apiBaseUrl}/auth/register`, this.registerForm.value)
      .subscribe({
        next: () => {
          this.loading = false;
          this.snackBar.open('User registered successfully', '', {
            duration: 3000,
          });
          this.router.navigate(['/templates']);
        },
        error: (err) => {
          this.loading = false;
          this.errorMessage =
            err.error?.detail || 'Failed to register user';
        },
      });
  }
}

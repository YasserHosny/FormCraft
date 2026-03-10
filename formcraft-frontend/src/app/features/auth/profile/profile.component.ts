import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { TranslateService } from '@ngx-translate/core';
import { AuthService, User } from '../../../core/auth/auth.service';
import { LanguageService } from '../../../core/i18n/language.service';
import { environment } from '../../../../environments/environment';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'fc-profile',
  standalone: false,
  template: `
    <div class="profile-container">
      <mat-card class="profile-card">
        <mat-card-header>
          <mat-card-title>{{ 'auth.profile' | translate }}</mat-card-title>
        </mat-card-header>
        <mat-card-content>
          <form [formGroup]="profileForm" (ngSubmit)="onSave()">
            <mat-form-field appearance="outline" class="full-width">
              <mat-label>{{ 'auth.email' | translate }}</mat-label>
              <input matInput formControlName="email" readonly />
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>{{ 'auth.role' | translate }}</mat-label>
              <input matInput [value]="roleName" readonly />
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Display Name</mat-label>
              <input matInput formControlName="display_name" fcAutoDir />
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>{{ 'auth.language' | translate }}</mat-label>
              <mat-select formControlName="language">
                <mat-option value="ar">العربية</mat-option>
                <mat-option value="en">English</mat-option>
              </mat-select>
            </mat-form-field>

            <button
              mat-raised-button
              color="primary"
              type="submit"
              class="full-width"
              [disabled]="profileForm.pristine || saving"
            >
              {{ 'common.save' | translate }}
            </button>
          </form>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .profile-container {
      display: flex;
      justify-content: center;
      padding: 48px 24px;
    }
    .profile-card {
      width: 480px;
      padding: 24px;
    }
    .full-width {
      width: 100%;
    }
    mat-form-field {
      margin-bottom: 16px;
    }
  `],
})
export class ProfileComponent implements OnInit {
  profileForm!: FormGroup;
  saving = false;
  roleName = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private languageService: LanguageService,
    private translate: TranslateService,
    private snackBar: MatSnackBar,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    this.profileForm = this.fb.group({
      email: [{ value: '', disabled: true }],
      display_name: [''],
      language: ['ar'],
    });

    this.authService.currentUser$.subscribe((user) => {
      if (user) {
        this.profileForm.patchValue({
          email: user.email,
          display_name: user.display_name || '',
          language: user.language,
        });
        this.translate.get(`roles.${user.role}`).subscribe((name) => {
          this.roleName = name;
        });
        this.profileForm.markAsPristine();
      }
    });
  }

  onSave(): void {
    if (this.profileForm.pristine) return;
    this.saving = true;

    const { display_name, language } = this.profileForm.getRawValue();
    this.http
      .put(`${environment.apiBaseUrl}/users/me`, { display_name, language })
      .subscribe({
        next: () => {
          this.saving = false;
          this.languageService.setLanguage(language);
          this.profileForm.markAsPristine();
          this.snackBar.open(
            this.translate.instant('common.save') + ' ✓',
            '',
            { duration: 2000 }
          );
        },
        error: () => {
          this.saving = false;
          this.snackBar.open('Error saving profile', 'Dismiss', {
            duration: 3000,
          });
        },
      });
  }
}

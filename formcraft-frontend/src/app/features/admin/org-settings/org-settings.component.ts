import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { TranslateModule } from '@ngx-translate/core';
import {
  OrgAdminService,
  OrgSettings,
  OrgFeatureSettings,
} from '../../../core/services/org-admin.service';

@Component({
  selector: 'fc-org-settings',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    MatSlideToggleModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
    TranslateModule,
  ],
  template: `
    <div class="org-settings-container" *ngIf="settings; else loading">
      <h2>{{ 'org.title' | translate }}</h2>

      <!-- Identity -->
      <mat-card class="section-card">
        <mat-card-header>
          <mat-card-title>{{ 'org.branding' | translate }}</mat-card-title>
        </mat-card-header>
        <mat-card-content>
          <div class="form-row">
            <mat-form-field appearance="outline">
              <mat-label>{{ 'org.name_ar' | translate }}</mat-label>
              <input matInput [(ngModel)]="settings.name_ar" dir="rtl" />
            </mat-form-field>
            <mat-form-field appearance="outline">
              <mat-label>{{ 'org.name_en' | translate }}</mat-label>
              <input matInput [(ngModel)]="settings.name_en" />
            </mat-form-field>
          </div>

          <div class="logo-section">
            <label class="field-label">{{ 'org.logo' | translate }}</label>
            <div class="logo-row">
              <img
                *ngIf="settings.logo_url"
                [src]="settings.logo_url"
                alt="Organization logo"
                class="logo-preview"
              />
              <button mat-stroked-button (click)="logoInput.click()">
                <mat-icon>upload</mat-icon>
                {{ 'org.upload_logo' | translate }}
              </button>
              <input
                #logoInput
                type="file"
                accept="image/*"
                hidden
                (change)="onLogoSelected($event)"
              />
            </div>
          </div>

          <div class="form-row">
            <mat-form-field appearance="outline">
              <mat-label>{{ 'org.primary_color' | translate }}</mat-label>
              <input matInput type="color" [(ngModel)]="settings.primary_color" />
            </mat-form-field>
            <mat-form-field appearance="outline">
              <mat-label>{{ 'org.custom_domain' | translate }}</mat-label>
              <input matInput [(ngModel)]="settings.custom_domain" />
            </mat-form-field>
          </div>
        </mat-card-content>
      </mat-card>

      <!-- Defaults -->
      <mat-card class="section-card">
        <mat-card-header>
          <mat-card-title>{{ 'org.settings' | translate }}</mat-card-title>
        </mat-card-header>
        <mat-card-content>
          <div class="form-row">
            <mat-form-field appearance="outline">
              <mat-label>{{ 'org.default_language' | translate }}</mat-label>
              <mat-select [(ngModel)]="settings.default_language">
                <mat-option value="ar">العربية</mat-option>
                <mat-option value="en">English</mat-option>
              </mat-select>
            </mat-form-field>
            <mat-form-field appearance="outline">
              <mat-label>{{ 'org.default_country' | translate }}</mat-label>
              <mat-select [(ngModel)]="settings.default_country">
                <mat-option value="EG">{{ 'countries.EG' | translate }}</mat-option>
                <mat-option value="SA">{{ 'countries.SA' | translate }}</mat-option>
                <mat-option value="AE">{{ 'countries.AE' | translate }}</mat-option>
              </mat-select>
            </mat-form-field>
            <mat-form-field appearance="outline">
              <mat-label>{{ 'org.default_currency' | translate }}</mat-label>
              <mat-select [(ngModel)]="settings.default_currency">
                <mat-option value="EGP">EGP</mat-option>
                <mat-option value="SAR">SAR</mat-option>
                <mat-option value="AED">AED</mat-option>
                <mat-option value="USD">USD</mat-option>
              </mat-select>
            </mat-form-field>
          </div>

          <div class="toggles-section">
            <mat-slide-toggle [(ngModel)]="settings.settings.approval_workflow">
              {{ 'org.approval_workflow' | translate }}
            </mat-slide-toggle>
            <mat-slide-toggle [(ngModel)]="settings.settings.hijri_date_support">
              Hijri Date Support
            </mat-slide-toggle>
          </div>

          <div class="form-row">
            <mat-form-field appearance="outline">
              <mat-label>{{ 'org.draft_expiry' | translate }}</mat-label>
              <input matInput type="number" [(ngModel)]="settings.settings.draft_expiry_days" />
            </mat-form-field>
            <mat-form-field appearance="outline">
              <mat-label>{{ 'org.data_retention' | translate }}</mat-label>
              <input matInput type="number" [(ngModel)]="settings.settings.data_retention_months" />
            </mat-form-field>
            <mat-form-field appearance="outline">
              <mat-label>{{ 'org.max_batch_size' | translate }}</mat-label>
              <input matInput type="number" [(ngModel)]="settings.settings.max_batch_size" />
            </mat-form-field>
          </div>
        </mat-card-content>
      </mat-card>

      <div class="actions-row">
        <button mat-raised-button color="primary" (click)="save()" [disabled]="saving">
          <mat-spinner *ngIf="saving" diameter="18"></mat-spinner>
          <span *ngIf="!saving">{{ 'common.save' | translate }}</span>
        </button>
      </div>
    </div>

    <ng-template #loading>
      <div class="center-spinner">
        <mat-spinner diameter="48"></mat-spinner>
      </div>
    </ng-template>
  `,
  styles: [`
    .org-settings-container {
      max-width: 900px;
      margin: 24px auto;
      padding: 0 16px;
    }
    .section-card {
      margin-bottom: 24px;
    }
    .form-row {
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
    }
    .form-row mat-form-field {
      flex: 1;
      min-width: 200px;
    }
    .logo-section {
      margin: 16px 0;
    }
    .field-label {
      display: block;
      margin-bottom: 8px;
      font-weight: 500;
      color: rgba(0, 0, 0, 0.6);
    }
    .logo-row {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .logo-preview {
      max-height: 64px;
      max-width: 200px;
      border: 1px solid #ddd;
      border-radius: 4px;
      object-fit: contain;
    }
    .toggles-section {
      display: flex;
      flex-direction: column;
      gap: 16px;
      margin: 16px 0;
    }
    .actions-row {
      display: flex;
      justify-content: flex-end;
      margin-top: 16px;
    }
    .center-spinner {
      display: flex;
      justify-content: center;
      padding: 48px;
    }
  `],
})
export class OrgSettingsComponent implements OnInit {
  settings: OrgSettings | null = null;
  saving = false;

  constructor(
    private orgAdmin: OrgAdminService,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit(): void {
    this.orgAdmin.getOrgSettings().subscribe({
      next: (s) => (this.settings = s),
      error: () => this.snackBar.open('Failed to load settings', '', { duration: 3000 }),
    });
  }

  onLogoSelected(event: Event): void {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (!file) return;
    this.orgAdmin.uploadLogo(file).subscribe({
      next: (res) => {
        if (this.settings) this.settings.logo_url = res.logo_url;
        this.snackBar.open('Logo uploaded', '', { duration: 2000 });
      },
      error: () => this.snackBar.open('Logo upload failed', '', { duration: 3000 }),
    });
  }

  save(): void {
    if (!this.settings) return;
    this.saving = true;
    this.orgAdmin.updateOrgSettings(this.settings).subscribe({
      next: (s) => {
        this.settings = s;
        this.saving = false;
        this.snackBar.open('Settings saved', '', { duration: 2000 });
      },
      error: () => {
        this.saving = false;
        this.snackBar.open('Failed to save settings', '', { duration: 3000 });
      },
    });
  }
}

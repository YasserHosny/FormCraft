import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { TranslateModule } from '@ngx-translate/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../../environments/environment';
import {
  PrinterProfile,
  PrinterProfileService,
} from '../../../../core/services/printer-profile.service';
import { PrintSettingsService } from '../../../../core/services/print-settings.service';

export interface PrintDialogData {
  templateId: string;
  templateName: string;
}

@Component({
  selector: 'app-print-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatSelectModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    TranslateModule,
  ],
  template: `
    <h2 mat-dialog-title>{{ 'overlay.print_dialog_title' | translate }}</h2>
    <mat-dialog-content>
      <mat-form-field appearance="outline" class="full-width">
        <mat-label>{{ 'print_settings.mode' | translate }}</mat-label>
        <mat-select [(ngModel)]="printMode">
          <mat-option value="full">{{ 'print_settings.mode_full' | translate }}</mat-option>
          <mat-option value="overlay">{{ 'print_settings.mode_overlay' | translate }}</mat-option>
          <mat-option value="both">{{ 'print_settings.mode_both' | translate }}</mat-option>
        </mat-select>
      </mat-form-field>

      <mat-form-field appearance="outline" class="full-width" *ngIf="profiles.length > 0">
        <mat-label>{{ 'printer_profiles.title' | translate }}</mat-label>
        <mat-select [(ngModel)]="selectedProfileId">
          <mat-option [value]="null">{{ 'common.none' | translate }}</mat-option>
          <mat-option *ngFor="let p of profiles" [value]="p.id">
            {{ p.name }} <span *ngIf="p.is_default">(default)</span>
          </mat-option>
        </mat-select>
      </mat-form-field>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>{{ 'common.cancel' | translate }}</button>
      <button mat-raised-button color="primary" (click)="print()" [disabled]="loading">
        <mat-spinner *ngIf="loading" diameter="20"></mat-spinner>
        <span *ngIf="!loading">{{ 'overlay.generate_pdf' | translate }}</span>
      </button>
    </mat-dialog-actions>
  `,
  styles: [`
    .full-width { width: 100%; margin-bottom: 8px; }
  `],
})
export class PrintDialogComponent implements OnInit {
  profiles: PrinterProfile[] = [];
  printMode = 'full';
  selectedProfileId: string | null = null;
  loading = false;

  constructor(
    private dialogRef: MatDialogRef<PrintDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: PrintDialogData,
    private http: HttpClient,
    private profileService: PrinterProfileService,
    private settingsService: PrintSettingsService
  ) {}

  ngOnInit(): void {
    this.profileService.list().subscribe((res) => {
      this.profiles = res.data;
      const def = this.profiles.find((p) => p.is_default);
      if (def) this.selectedProfileId = def.id;
    });

    this.settingsService.get(this.data.templateId).subscribe((s) => {
      this.printMode = s.print_mode || 'full';
    });
  }

  print(): void {
    this.loading = true;
    const body: Record<string, unknown> = {
      print_mode_override: this.printMode,
    };
    if (this.selectedProfileId) {
      body['printer_profile_id'] = this.selectedProfileId;
    }

    const url = `${environment.apiBaseUrl}/pdf/render/${this.data.templateId}`;
    this.http.post(url, body, { responseType: 'blob' }).subscribe({
      next: (blob) => {
        this.loading = false;
        const fileUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = fileUrl;
        const ext = this.printMode === 'both' ? 'zip' : 'pdf';
        a.download = `${this.data.templateName}.${ext}`;
        a.click();
        URL.revokeObjectURL(fileUrl);
        this.dialogRef.close(true);
      },
      error: () => {
        this.loading = false;
      },
    });
  }
}

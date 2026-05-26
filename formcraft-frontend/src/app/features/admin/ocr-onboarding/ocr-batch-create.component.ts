import { Component } from '@angular/core';
import { Router } from '@angular/router';

import { OcrOnboardingService } from '../../../core/services/ocr-onboarding.service';
import { SharedModule } from '../../../shared/shared.module';

@Component({
  selector: 'app-ocr-batch-create',
  standalone: true,
  imports: [SharedModule],
  template: `
    <section class="ocr-page">
      <header class="toolbar">
        <button mat-icon-button routerLink="../" [matTooltip]="'common.back' | translate">
          <mat-icon>arrow_back</mat-icon>
        </button>
        <h1>{{ 'ocrOnboarding.createTitle' | translate }}</h1>
      </header>

      <form class="create-form" (ngSubmit)="submit()">
        <mat-form-field appearance="outline">
          <mat-label>{{ 'ocrOnboarding.batchName' | translate }}</mat-label>
          <input matInput name="name" [(ngModel)]="name" required />
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>{{ 'ocrOnboarding.threshold' | translate }}</mat-label>
          <input matInput name="threshold" type="number" min="0" max="1" step="0.01" [(ngModel)]="threshold" />
        </mat-form-field>

        <input type="file" multiple accept="application/pdf,image/png,image/jpeg" (change)="selectFiles($event)" />
        <p>{{ 'ocrOnboarding.selectedFiles' | translate:{ count: files.length } }}</p>

        <div class="actions">
          <button mat-stroked-button type="button" routerLink="../">{{ 'common.cancel' | translate }}</button>
          <button mat-flat-button color="primary" type="submit" [disabled]="!name || files.length === 0 || saving">
            <mat-icon>cloud_upload</mat-icon>
            {{ 'ocrOnboarding.startBatch' | translate }}
          </button>
        </div>
      </form>
    </section>
  `,
  styles: [`
    .ocr-page { padding: 24px; max-width: 720px; }
    .toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
    h1 { margin: 0; font-size: 24px; }
    .create-form { display: grid; gap: 16px; }
    .actions { display: flex; justify-content: flex-end; gap: 12px; }
    button mat-icon { margin-inline-end: 6px; }
  `],
})
export class OcrBatchCreateComponent {
  name = '';
  threshold = 0.85;
  files: File[] = [];
  saving = false;

  constructor(private service: OcrOnboardingService, private router: Router) {}

  selectFiles(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.files = Array.from(input.files || []).slice(0, 200);
  }

  submit(): void {
    if (!this.name || this.files.length === 0) return;
    this.saving = true;
    this.service.createBatch(this.name, this.threshold, this.files).subscribe({
      next: batch => this.router.navigate(['/admin/ocr-onboarding', batch.id]),
      error: () => { this.saving = false; },
    });
  }
}

import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { OcrImportBatch, OcrOnboardingService } from '../../../core/services/ocr-onboarding.service';
import { SharedModule } from '../../../shared/shared.module';

@Component({
  selector: 'app-ocr-batch-list',
  standalone: true,
  imports: [SharedModule],
  template: `
    <section class="ocr-page">
      <header class="toolbar">
        <div>
          <h1>{{ 'ocrOnboarding.title' | translate }}</h1>
          <p>{{ 'ocrOnboarding.subtitle' | translate }}</p>
        </div>
        <button mat-flat-button color="primary" routerLink="new">
          <mat-icon>upload_file</mat-icon>
          {{ 'ocrOnboarding.newBatch' | translate }}
        </button>
      </header>

      <table mat-table [dataSource]="batches" class="mat-elevation-z1">
        <ng-container matColumnDef="name">
          <th mat-header-cell *matHeaderCellDef>{{ 'ocrOnboarding.batchName' | translate }}</th>
          <td mat-cell *matCellDef="let batch">{{ batch.name }}</td>
        </ng-container>

        <ng-container matColumnDef="status">
          <th mat-header-cell *matHeaderCellDef>{{ 'ocrOnboarding.status' | translate }}</th>
          <td mat-cell *matCellDef="let batch">
            <mat-chip>{{ ('ocrOnboarding.states.' + batch.status) | translate }}</mat-chip>
          </td>
        </ng-container>

        <ng-container matColumnDef="progress">
          <th mat-header-cell *matHeaderCellDef>{{ 'ocrOnboarding.progress' | translate }}</th>
          <td mat-cell *matCellDef="let batch">{{ batch.processed_items }} / {{ batch.total_items }}</td>
        </ng-container>

        <ng-container matColumnDef="actions">
          <th mat-header-cell *matHeaderCellDef>{{ 'common.actions' | translate }}</th>
          <td mat-cell *matCellDef="let batch">
            <button mat-icon-button (click)="open(batch)" [matTooltip]="'common.view' | translate">
              <mat-icon>chevron_right</mat-icon>
            </button>
          </td>
        </ng-container>

        <tr mat-header-row *matHeaderRowDef="columns"></tr>
        <tr mat-row *matRowDef="let row; columns: columns"></tr>
      </table>
    </section>
  `,
  styles: [`
    .ocr-page { padding: 24px; }
    .toolbar { display: flex; justify-content: space-between; gap: 16px; align-items: center; margin-bottom: 20px; }
    h1 { margin: 0 0 4px; font-size: 24px; }
    p { margin: 0; color: rgba(0, 0, 0, 0.62); }
    table { width: 100%; }
    button mat-icon { margin-inline-end: 6px; }
  `],
})
export class OcrBatchListComponent implements OnInit {
  batches: OcrImportBatch[] = [];
  columns = ['name', 'status', 'progress', 'actions'];

  constructor(private service: OcrOnboardingService, private router: Router) {}

  ngOnInit(): void {
    this.service.listBatches().subscribe(result => {
      this.batches = result.items;
    });
  }

  open(batch: OcrImportBatch): void {
    this.router.navigate(['/admin/ocr-onboarding', batch.id]);
  }
}

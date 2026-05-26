import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { OcrImportBatchDetail, OcrImportItem, OcrOnboardingService } from '../../../core/services/ocr-onboarding.service';
import { SharedModule } from '../../../shared/shared.module';

@Component({
  selector: 'app-ocr-batch-detail',
  standalone: true,
  imports: [SharedModule],
  template: `
    <section class="ocr-page" *ngIf="batch">
      <header class="toolbar">
        <div>
          <h1>{{ batch.name }}</h1>
          <p>{{ ('ocrOnboarding.states.' + batch.status) | translate }} · {{ batch.processed_items }} / {{ batch.total_items }}</p>
        </div>
        <button mat-flat-button color="primary" (click)="bulkAccept()" [disabled]="selected.size === 0">
          <mat-icon>done_all</mat-icon>
          {{ 'ocrOnboarding.bulkAccept' | translate }}
        </button>
      </header>

      <table mat-table [dataSource]="batch.items" class="mat-elevation-z1">
        <ng-container matColumnDef="select">
          <th mat-header-cell *matHeaderCellDef></th>
          <td mat-cell *matCellDef="let item">
            <mat-checkbox [checked]="selected.has(item.id)" (change)="toggle(item)"></mat-checkbox>
          </td>
        </ng-container>

        <ng-container matColumnDef="file">
          <th mat-header-cell *matHeaderCellDef>{{ 'ocrOnboarding.file' | translate }}</th>
          <td mat-cell *matCellDef="let item">{{ item.file_name }}</td>
        </ng-container>

        <ng-container matColumnDef="confidence">
          <th mat-header-cell *matHeaderCellDef>{{ 'ocrOnboarding.confidence' | translate }}</th>
          <td mat-cell *matCellDef="let item">{{ item.confidence === null ? '-' : (item.confidence | percent:'1.0-0') }}</td>
        </ng-container>

        <ng-container matColumnDef="status">
          <th mat-header-cell *matHeaderCellDef>{{ 'ocrOnboarding.status' | translate }}</th>
          <td mat-cell *matCellDef="let item">
            <mat-chip>{{ ('ocrOnboarding.states.' + item.status) | translate }}</mat-chip>
          </td>
        </ng-container>

        <ng-container matColumnDef="actions">
          <th mat-header-cell *matHeaderCellDef>{{ 'common.actions' | translate }}</th>
          <td mat-cell *matCellDef="let item">
            <button mat-icon-button (click)="decide(item, 'accept')" [matTooltip]="'ocrOnboarding.accept' | translate">
              <mat-icon>check</mat-icon>
            </button>
            <button mat-icon-button (click)="decide(item, 'reject')" [matTooltip]="'ocrOnboarding.reject' | translate">
              <mat-icon>close</mat-icon>
            </button>
            <button mat-icon-button (click)="retry(item)" [disabled]="item.status !== 'failed'" [matTooltip]="'ocrOnboarding.retry' | translate">
              <mat-icon>refresh</mat-icon>
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
    button mat-icon { margin-inline-end: 0; }
  `],
})
export class OcrBatchDetailComponent implements OnInit {
  batch: OcrImportBatchDetail | null = null;
  selected = new Set<string>();
  columns = ['select', 'file', 'confidence', 'status', 'actions'];

  constructor(private route: ActivatedRoute, private service: OcrOnboardingService) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    const batchId = this.route.snapshot.paramMap.get('batchId');
    if (!batchId) return;
    this.service.getBatch(batchId).subscribe(batch => {
      this.batch = batch;
      this.selected.clear();
    });
  }

  toggle(item: OcrImportItem): void {
    if (this.selected.has(item.id)) {
      this.selected.delete(item.id);
    } else {
      this.selected.add(item.id);
    }
  }

  bulkAccept(): void {
    if (!this.batch) return;
    this.service.bulkAccept(this.batch.id, Array.from(this.selected)).subscribe(() => this.load());
  }

  decide(item: OcrImportItem, action: 'accept' | 'reject'): void {
    if (!this.batch) return;
    this.service.decide(this.batch.id, item.id, action).subscribe(() => this.load());
  }

  retry(item: OcrImportItem): void {
    if (!this.batch) return;
    this.service.retry(this.batch.id, item.id).subscribe(() => this.load());
  }
}

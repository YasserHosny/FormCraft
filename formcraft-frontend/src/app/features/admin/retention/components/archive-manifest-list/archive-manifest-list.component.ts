import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { TranslateModule } from '@ngx-translate/core';
import { RetentionService } from '../../services/retention.service';
import { ArchiveManifest } from '../../models/retention.model';

@Component({
  selector: 'app-archive-manifest-list',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatButtonModule, MatChipsModule, TranslateModule],
  template: `
    <div class="retention-container" dir="rtl">
      <h2>{{ 'RETENTION.ARCHIVE_MANIFESTS' | translate }}</h2>
      <table mat-table [dataSource]="manifests" class="mat-elevation-z2">
        <ng-container matColumnDef="schema_location">
          <th mat-header-cell *matHeaderCellDef>{{ 'RETENTION.LOCATION' | translate }}</th>
          <td mat-cell *matCellDef="let m">{{ m.schema_location }}</td>
        </ng-container>
        <ng-container matColumnDef="record_count">
          <th mat-header-cell *matHeaderCellDef>{{ 'RETENTION.RECORD_COUNT' | translate }}</th>
          <td mat-cell *matCellDef="let m">{{ m.record_count }}</td>
        </ng-container>
        <ng-container matColumnDef="integrity_status">
          <th mat-header-cell *matHeaderCellDef>{{ 'RETENTION.INTEGRITY' | translate }}</th>
          <td mat-cell *matCellDef="let m">
            <mat-chip [color]="m.integrity_status === 'verified' ? 'primary' : 'warn'" selected>
              {{ m.integrity_status }}
            </mat-chip>
          </td>
        </ng-container>
        <ng-container matColumnDef="sha256_hash">
          <th mat-header-cell *matHeaderCellDef>SHA-256</th>
          <td mat-cell *matCellDef="let m">{{ m.sha256_hash | slice:0:16 }}...</td>
        </ng-container>
        <ng-container matColumnDef="actions">
          <th mat-header-cell *matHeaderCellDef></th>
          <td mat-cell *matCellDef="let m">
            <button mat-button (click)="restore(m.id)">{{ 'RETENTION.RESTORE' | translate }}</button>
          </td>
        </ng-container>
        <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
        <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
      </table>
    </div>
  `,
  styles: [`
    .retention-container { padding: 16px; }
    table { width: 100%; margin-top: 16px; }
  `],
})
export class ArchiveManifestListComponent implements OnInit {
  manifests: ArchiveManifest[] = [];
  displayedColumns = ['schema_location', 'record_count', 'integrity_status', 'sha256_hash', 'actions'];

  constructor(private service: RetentionService) {}

  ngOnInit(): void {
    this.service.listManifests().subscribe((res: any) => {
      this.manifests = res || [];
    });
  }

  restore(id: string): void {
    this.service.requestRestore(id, 'Admin restore request').subscribe(() => alert('Restore requested'));
  }
}

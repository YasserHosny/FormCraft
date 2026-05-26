import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { TranslateModule } from '@ngx-translate/core';
import { RetentionService } from '../../services/retention.service';
import { LegalHold } from '../../models/retention.model';

@Component({
  selector: 'app-legal-hold-list',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatButtonModule, TranslateModule],
  template: `
    <div class="retention-container" dir="rtl">
      <h2>{{ 'RETENTION.LEGAL_HOLDS' | translate }}</h2>
      <button mat-raised-button color="primary" (click)="onCreate()">
        {{ 'RETENTION.PLACE_HOLD' | translate }}
      </button>
      <table mat-table [dataSource]="holds" class="mat-elevation-z2">
        <ng-container matColumnDef="hold_type">
          <th mat-header-cell *matHeaderCellDef>{{ 'RETENTION.HOLD_TYPE' | translate }}</th>
          <td mat-cell *matCellDef="let hold">{{ hold.hold_type }}</td>
        </ng-container>
        <ng-container matColumnDef="scope_type">
          <th mat-header-cell *matHeaderCellDef>{{ 'RETENTION.SCOPE_TYPE' | translate }}</th>
          <td mat-cell *matCellDef="let hold">{{ hold.scope_type }}</td>
        </ng-container>
        <ng-container matColumnDef="reason">
          <th mat-header-cell *matHeaderCellDef>{{ 'RETENTION.REASON' | translate }}</th>
          <td mat-cell *matCellDef="let hold">{{ hold.reason }}</td>
        </ng-container>
        <ng-container matColumnDef="actions">
          <th mat-header-cell *matHeaderCellDef></th>
          <td mat-cell *matCellDef="let hold">
            <button mat-button color="warn" (click)="release(hold.id)">Release</button>
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
export class LegalHoldListComponent implements OnInit {
  holds: LegalHold[] = [];
  displayedColumns = ['hold_type', 'scope_type', 'reason', 'actions'];

  constructor(private service: RetentionService) {}

  ngOnInit(): void {
    this.service.listHolds().subscribe((res: any) => {
      this.holds = res || [];
    });
  }

  onCreate(): void {
    // Open dialog
  }

  release(id: string): void {
    this.service.releaseHold(id).subscribe(() => this.ngOnInit());
  }
}

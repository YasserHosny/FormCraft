import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatPaginatorModule } from '@angular/material/paginator';
import { TranslateModule } from '@ngx-translate/core';
import { RetentionService } from '../../services/retention.service';
import { RetentionPolicy } from '../../models/retention.model';

@Component({
  selector: 'app-policy-list',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatButtonModule, MatPaginatorModule, TranslateModule],
  template: `
    <div class="retention-container" dir="rtl">
      <h2>{{ 'RETENTION.POLICIES' | translate }}</h2>
      <button mat-raised-button color="primary" (click)="onCreate()">
        {{ 'RETENTION.CREATE_POLICY' | translate }}
      </button>

      <table mat-table [dataSource]="policies" class="mat-elevation-z2">
        <ng-container matColumnDef="name">
          <th mat-header-cell *matHeaderCellDef>{{ 'RETENTION.POLICY_NAME' | translate }}</th>
          <td mat-cell *matCellDef="let policy">{{ policy.name?.ar || policy.name?.en }}</td>
        </ng-container>
        <ng-container matColumnDef="data_class">
          <th mat-header-cell *matHeaderCellDef>{{ 'RETENTION.DATA_CLASS' | translate }}</th>
          <td mat-cell *matCellDef="let policy">{{ policy.data_class }}</td>
        </ng-container>
        <ng-container matColumnDef="action">
          <th mat-header-cell *matHeaderCellDef>{{ 'RETENTION.ACTION' | translate }}</th>
          <td mat-cell *matCellDef="let policy">{{ policy.action }}</td>
        </ng-container>
        <ng-container matColumnDef="period_days">
          <th mat-header-cell *matHeaderCellDef>{{ 'RETENTION.PERIOD' | translate }}</th>
          <td mat-cell *matCellDef="let policy">{{ policy.period_days }}</td>
        </ng-container>
        <ng-container matColumnDef="effective_date">
          <th mat-header-cell *matHeaderCellDef>{{ 'RETENTION.EFFECTIVE_DATE' | translate }}</th>
          <td mat-cell *matCellDef="let policy">{{ policy.effective_date | date }}</td>
        </ng-container>
        <ng-container matColumnDef="preview">
          <th mat-header-cell *matHeaderCellDef></th>
          <td mat-cell *matCellDef="let policy">
            <button mat-button (click)="onPreview(policy.id)">{{ 'RETENTION.PREVIEW' | translate }}</button>
          </td>
        </ng-container>

        <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
        <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
      </table>

      <mat-paginator [pageSizeOptions]="[10, 20, 50]"></mat-paginator>
    </div>
  `,
  styles: [`
    .retention-container { padding: 16px; }
    table { width: 100%; margin-top: 16px; }
  `],
})
export class PolicyListComponent implements OnInit {
  policies: RetentionPolicy[] = [];
  displayedColumns = ['name', 'data_class', 'action', 'period_days', 'effective_date', 'preview'];

  constructor(private service: RetentionService) {}

  ngOnInit(): void {
    this.service.listPolicies().subscribe((res: any) => {
      this.policies = res.items || [];
    });
  }

  onCreate(): void {
    // Navigate to form or open dialog
  }

  onPreview(id: string): void {
    this.service.previewPolicy(id).subscribe((res) => {
      alert(JSON.stringify(res, null, 2));
    });
  }
}

import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';
import { TranslateModule } from '@ngx-translate/core';

import { OperatorAnalyticsItem } from '../../models/analytics.model';
import { AnalyticsService } from '../../services/analytics.service';

@Component({
  selector: 'app-operator-analytics',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatTableModule, MatIconModule, MatTooltipModule, TranslateModule],
  template: `
    <div class="operator-analytics">
      <h2>{{ 'analytics.operatorAnalytics' | translate }}</h2>
      <mat-card>
        <table mat-table [dataSource]="operators" class="analytics-table">
          <ng-container matColumnDef="operatorName">
            <th mat-header-cell *matHeaderCellDef>Operator</th>
            <td mat-cell *matCellDef="let row">{{ row.operatorName }}</td>
          </ng-container>
          <ng-container matColumnDef="formsFilled">
            <th mat-header-cell *matHeaderCellDef>{{ 'analytics.formsFilled' | translate }}</th>
            <td mat-cell *matCellDef="let row">{{ row.formsFilled }}</td>
          </ng-container>
          <ng-container matColumnDef="errorRate">
            <th mat-header-cell *matHeaderCellDef>{{ 'analytics.errorRate' | translate }}</th>
            <td mat-cell *matCellDef="let row">{{ row.errorRate | percent }}</td>
          </ng-container>
          <ng-container matColumnDef="coachingFlag">
            <th mat-header-cell *matHeaderCellDef></th>
            <td mat-cell *matCellDef="let row">
              <mat-icon *ngIf="row.coachingFlag" color="accent" [matTooltip]="'analytics.coachingFlag' | translate">school</mat-icon>
            </td>
          </ng-container>
          <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
          <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
        </table>
      </mat-card>
    </div>
  `,
  styles: [`
    .operator-analytics { padding: 16px; }
    .analytics-table { width: 100%; }
  `],
})
export class OperatorAnalyticsComponent implements OnInit {
  operators: OperatorAnalyticsItem[] = [];
  displayedColumns = ['operatorName', 'formsFilled', 'errorRate', 'coachingFlag'];

  constructor(private analyticsService: AnalyticsService) {}

  ngOnInit(): void {
    // TODO: Wire to service in Phase 4
  }
}

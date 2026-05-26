import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';
import { TranslateModule } from '@ngx-translate/core';

import { FieldAnalyticsItem, FieldAnalyticsResponse } from '../../models/analytics.model';
import { AnalyticsService } from '../../services/analytics.service';

@Component({
  selector: 'app-field-analytics',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatTableModule, MatIconModule, MatTooltipModule, TranslateModule],
  template: `
    <div class="field-analytics">
      <h2>{{ 'analytics.fieldAnalytics' | translate }}</h2>
      <mat-card>
        <table mat-table [dataSource]="fields" class="analytics-table">
          <ng-container matColumnDef="fieldKey">
            <th mat-header-cell *matHeaderCellDef>Field</th>
            <td mat-cell *matCellDef="let row">{{ row.fieldKey }}</td>
          </ng-container>
          <ng-container matColumnDef="errorRate">
            <th mat-header-cell *matHeaderCellDef>{{ 'analytics.errorRate' | translate }}</th>
            <td mat-cell *matCellDef="let row">{{ row.errorRate | percent }}</td>
          </ng-container>
          <ng-container matColumnDef="emptyRate">
            <th mat-header-cell *matHeaderCellDef>{{ 'analytics.emptyRate' | translate }}</th>
            <td mat-cell *matCellDef="let row">{{ row.emptyRate | percent }}</td>
          </ng-container>
          <ng-container matColumnDef="avgFillTime">
            <th mat-header-cell *matHeaderCellDef>{{ 'analytics.avgFillTime' | translate }}</th>
            <td mat-cell *matCellDef="let row">{{ row.avgFillTimeMs ? (row.avgFillTimeMs / 1000 | number:'1.1-1') + 's' : ('analytics.na' | translate) }}</td>
          </ng-container>
          <ng-container matColumnDef="warning">
            <th mat-header-cell *matHeaderCellDef></th>
            <td mat-cell *matCellDef="let row">
              <mat-icon *ngIf="row.warning" color="warn" [matTooltip]="'analytics.warning' | translate">warning</mat-icon>
            </td>
          </ng-container>
          <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
          <tr mat-row *matRowDef="let row; columns: displayedColumns;" [class.warning-row]="row.warning"></tr>
        </table>
      </mat-card>
    </div>
  `,
  styles: [`
    .field-analytics { padding: 16px; }
    .analytics-table { width: 100%; }
    .warning-row { background-color: rgba(255, 0, 0, 0.05); }
  `],
})
export class FieldAnalyticsComponent implements OnInit {
  fields: FieldAnalyticsItem[] = [];
  displayedColumns = ['fieldKey', 'errorRate', 'emptyRate', 'avgFillTime', 'warning'];

  constructor(private analyticsService: AnalyticsService) {}

  ngOnInit(): void {
    // TODO: Wire to actual template selection; using stub for MVP
    // this.analyticsService.getFieldAnalytics('template-id').subscribe((res: FieldAnalyticsResponse) => {
    //   this.fields = res.fields;
    // });
  }
}

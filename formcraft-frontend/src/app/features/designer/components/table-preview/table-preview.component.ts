import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule, TranslateService } from '@ngx-translate/core';

export interface TableColumn {
  header_ar: string;
  header_en: string;
  type: string;
  width_mm?: number;
  auto_sum?: boolean;
}

@Component({
  selector: 'fc-table-preview',
  standalone: true,
  imports: [CommonModule, TranslateModule],
  template: `
    <div class="table-preview" [style.width.px]="widthPx">
      <table *ngIf="columns.length > 0">
        <thead *ngIf="showHeader">
          <tr>
            <th *ngFor="let col of columns" [style.width.px]="getColWidth(col)">
              {{ getHeader(col) }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td *ngFor="let col of columns" [style.width.px]="getColWidth(col)">
              <span class="cell-placeholder">{{ getTypePlaceholder(col) }}</span>
            </td>
          </tr>
        </tbody>
        <tfoot *ngIf="hasAutoSum && showFooter">
          <tr>
            <td *ngFor="let col of columns" [style.width.px]="getColWidth(col)">
              <span *ngIf="col.auto_sum" class="sum-placeholder">Σ</span>
            </td>
          </tr>
        </tfoot>
      </table>
      <div *ngIf="columns.length === 0" class="empty-state">
        <span>{{ 'table.no_columns' | translate }}</span>
      </div>
    </div>
  `,
  styles: [`
    .table-preview {
      border: 1px solid #ddd;
      border-radius: 4px;
      overflow: hidden;
      background: #fff;
      font-size: 11px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
    }
    th, td {
      border: 1px solid #e0e0e0;
      padding: 4px 6px;
      text-align: center;
    }
    th {
      background: #f5f5f5;
      font-weight: 500;
      font-size: 10px;
      color: #333;
    }
    .cell-placeholder {
      color: #bbb;
      font-style: italic;
      font-size: 10px;
    }
    .sum-placeholder {
      font-weight: bold;
      color: #666;
    }
    .empty-state {
      padding: 16px;
      text-align: center;
      color: #999;
      font-size: 12px;
    }
    :host-context([dir='rtl']) th,
    :host-context([dir='rtl']) td {
      text-align: center;
    }
  `],
})
export class TablePreviewComponent {
  @Input() columns: TableColumn[] = [];
  @Input() widthPx = 300;
  @Input() showHeader = true;
  @Input() showFooter = true;

  constructor(private translate: TranslateService) {}

  get hasAutoSum(): boolean {
    return this.columns.some((c) => c.auto_sum);
  }

  getHeader(col: TableColumn): string {
    const lang = this.translate.currentLang || 'ar';
    return lang === 'en' && col.header_en ? col.header_en : col.header_ar;
  }

  getColWidth(col: TableColumn): number | null {
    if (!col.width_mm) return null;
    return Math.round(col.width_mm * 3.78);
  }

  getTypePlaceholder(col: TableColumn): string {
    switch (col.type) {
      case 'number': return '123';
      case 'date': return 'DD/MM';
      case 'text': return 'abc';
      default: return '...';
    }
  }
}

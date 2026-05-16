import { Component, Input, Output, EventEmitter } from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'fc-form-toolbar',
  standalone: true,
  imports: [
    CommonModule,
    TranslateModule,
    MatButtonModule,
    MatIconModule,
    MatToolbarModule,
    MatTooltipModule,
    MatProgressSpinnerModule,
  ],
  template: `
    <mat-toolbar class="form-toolbar" color="primary">
      <button mat-icon-button
              class="toolbar-btn cancel-btn"
              (click)="cancel.emit()"
              [matTooltip]="'filler.cancel' | translate">
        <mat-icon>arrow_back</mat-icon>
      </button>

      <span class="toolbar-spacer"></span>

      <button mat-stroked-button
              class="toolbar-btn clear-btn"
              (click)="clearAll.emit()"
              [disabled]="!isDirty || submitting">
        {{ 'filler.clear_all' | translate }}
      </button>

      <button mat-stroked-button
              class="toolbar-btn draft-btn"
              (click)="saveDraft.emit()"
              [disabled]="!isDirty || savingDraft">
        <mat-spinner *ngIf="savingDraft" diameter="16" class="btn-spinner"></mat-spinner>
        <mat-icon *ngIf="!savingDraft">save</mat-icon>
        {{ 'filler.save_draft' | translate }}
      </button>

      <button mat-raised-button
              class="toolbar-btn print-btn"
              (click)="print.emit()"
              [disabled]="!formValid || submitting">
        <mat-spinner *ngIf="submitting" diameter="16" class="btn-spinner"></mat-spinner>
        <mat-icon *ngIf="!submitting">print</mat-icon>
        {{ 'filler.print' | translate }}
      </button>

      <button mat-raised-button
              class="toolbar-btn print-next-btn"
              (click)="printNext.emit()"
              [disabled]="!formValid || submitting">
        <mat-spinner *ngIf="submitting" diameter="16" class="btn-spinner"></mat-spinner>
        <mat-icon *ngIf="!submitting">playlist_add</mat-icon>
        {{ 'filler.print_next' | translate }}
      </button>
    </mat-toolbar>
  `,
  styles: [`
    .form-toolbar {
      position: sticky;
      top: 0;
      z-index: 100;
      gap: 8px;
      padding: 0 16px;
    }
    .toolbar-spacer {
      flex: 1 1 auto;
    }
    .toolbar-btn {
      margin-left: 8px;
    }
    .cancel-btn {
      margin-left: 0;
      margin-right: 8px;
    }
    .print-btn, .print-next-btn {
      min-width: 100px;
    }
    .print-btn mat-icon, .print-next-btn mat-icon {
      margin-left: 4px;
      margin-right: 4px;
      font-size: 18px;
      width: 18px;
      height: 18px;
    }
    .draft-btn mat-icon {
      font-size: 18px;
      width: 18px;
      height: 18px;
      margin-right: 4px;
    }
    .btn-spinner {
      display: inline-block;
      vertical-align: middle;
      margin-right: 4px;
    }
    :host-context([dir='rtl']) .toolbar-btn {
      margin-left: 0;
      margin-right: 8px;
    }
    :host-context([dir='rtl']) .cancel-btn {
      margin-right: 0;
      margin-left: 8px;
    }
    :host-context([dir='rtl']) .print-btn mat-icon,
    :host-context([dir='rtl']) .print-next-btn mat-icon {
      margin-left: 4px;
      margin-right: 4px;
    }
    @media (max-width: 599px) {
      .form-toolbar {
        flex-wrap: wrap;
        padding: 0 8px;
      }
      .toolbar-btn {
        font-size: 12px;
        padding: 0 8px;
        min-width: auto;
      }
      .toolbar-spacer {
        display: none;
      }
    }
  `],
})
export class FormToolbarComponent {
  @Input() formValid = false;
  @Input() isDirty = false;
  @Input() submitting = false;
  @Input() savingDraft = false;

  @Output() print = new EventEmitter<void>();
  @Output() printNext = new EventEmitter<void>();
  @Output() saveDraft = new EventEmitter<void>();
  @Output() clearAll = new EventEmitter<void>();
  @Output() cancel = new EventEmitter<void>();
}
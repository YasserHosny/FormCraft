import { Component, EventEmitter, Input, Output } from '@angular/core';
import { SuggestionResponse } from '../../services/ai-suggestion.service';

@Component({
  selector: 'fc-ai-suggestion-chip',
  standalone: false,
  template: `
    <div class="suggestion-chip" *ngIf="suggestion">
      <div class="suggestion-header">
        <mat-icon class="ai-icon">auto_awesome</mat-icon>
        <span class="suggestion-label">{{ 'ai.suggestion' | translate }}</span>
        <span class="confidence-badge" [class.high]="suggestion.confidence >= 0.8" [class.low]="suggestion.confidence < 0.5">
          {{ (suggestion.confidence * 100) | number:'1.0-0' }}%
        </span>
      </div>
      <div class="suggestion-body">
        <mat-chip-listbox>
          <mat-chip>{{ suggestion.control_type }}</mat-chip>
        </mat-chip-listbox>
        <span class="source-tag">{{ suggestion.source }}</span>
      </div>
      <div class="suggestion-actions">
        <button mat-stroked-button color="primary" (click)="accept.emit(suggestion)">
          <mat-icon>check</mat-icon>
          {{ 'ai.accept' | translate }}
        </button>
        <button mat-stroked-button (click)="dismiss.emit()">
          {{ 'ai.dismiss' | translate }}
        </button>
      </div>
    </div>
  `,
  styles: [`
    .suggestion-chip {
      border: 1px solid #bbdefb;
      border-radius: 8px;
      padding: 12px;
      margin: 8px 0;
      background: #e3f2fd;
    }
    .suggestion-header {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 8px;
    }
    .ai-icon { color: #1565c0; font-size: 18px; width: 18px; height: 18px; }
    .suggestion-label { font-size: 12px; font-weight: 600; color: #1565c0; }
    .confidence-badge {
      margin-inline-start: auto;
      font-size: 11px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 10px;
      background: #c8e6c9;
      color: #2e7d32;
    }
    .confidence-badge.low { background: #ffccbc; color: #bf360c; }
    .suggestion-body {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 8px;
    }
    .source-tag { font-size: 10px; color: #999; font-style: italic; }
    .suggestion-actions {
      display: flex;
      gap: 8px;
    }
    .suggestion-actions button { font-size: 12px; }
  `],
})
export class AiSuggestionChipComponent {
  @Input() suggestion: SuggestionResponse | null = null;
  @Output() accept = new EventEmitter<SuggestionResponse>();
  @Output() dismiss = new EventEmitter<void>();
}

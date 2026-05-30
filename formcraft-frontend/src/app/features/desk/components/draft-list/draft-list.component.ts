import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { Router } from '@angular/router';

@Component({
  selector: 'fc-draft-list',
  standalone: true,
  imports: [CommonModule, TranslateModule],
  template: `
    <h2 class="section-title">{{ 'desk.section_drafts' | translate }}</h2>
    <div class="draft-list-empty" *ngIf="drafts.length === 0">
      <p>{{ 'desk.empty_drafts' | translate }}</p>
    </div>
    <div class="draft-list" *ngIf="drafts.length > 0">
      <button type="button" class="draft-row" *ngFor="let draft of drafts" (click)="openDraft(draft)">
        <span class="draft-name">{{ draft.name || draft.template_name || ('desk.draft_untitled' | translate) }}</span>
        <span class="draft-percent">{{ draft.completion_percent || 0 }}%</span>
      </button>
    </div>
  `,
  styles: [`
    .section-title {
      font-size: 16px;
      font-weight: 600;
      margin: 16px 0 8px 0;
    }
    .draft-list-empty {
      text-align: center;
      padding: 16px;
      color: rgba(0, 0, 0, 0.54);
    }
    .draft-list {
      display: grid;
      gap: 8px;
    }
    .draft-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border: 1px solid rgba(0, 0, 0, 0.12);
      background: #fff;
      border-radius: 4px;
      padding: 10px 12px;
      cursor: pointer;
      text-align: start;
    }
    .draft-percent {
      font-weight: 600;
      color: #3f51b5;
    }
  `],
})
export class DraftListComponent {
  @Input() drafts: any[] = [];

  constructor(private router: Router) {}

  openDraft(draft: any): void {
    if (!draft?.template_id || !draft?.id) return;
    this.router.navigate(['/desk/fill', draft.template_id], { queryParams: { draft: draft.id } });
  }
}

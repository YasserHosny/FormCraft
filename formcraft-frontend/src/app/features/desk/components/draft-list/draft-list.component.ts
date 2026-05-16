import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'fc-draft-list',
  standalone: true,
  imports: [CommonModule, TranslateModule],
  template: `
    <h2 class="section-title">{{ 'desk.section_drafts' | translate }}</h2>
    <div class="draft-list-empty">
      <p>{{ 'desk.empty_no_templates' | translate }}</p>
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
  `],
})
export class DraftListComponent {
  @Input() drafts: any[] = [];
}
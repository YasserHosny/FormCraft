import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { RecentTemplate } from '../../services/desk.service';
import { TemplateCardComponent } from '../template-card/template-card.component';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'fc-recent-templates',
  standalone: true,
  imports: [CommonModule, TranslateModule, TemplateCardComponent, RouterModule],
  template: `
    <h2 class="section-title">{{ 'desk.section_recent' | translate }}</h2>
    <div class="recent-scroll">
      <fc-template-card
        *ngFor="let item of recent"
        [template]="mapRecentToCard(item)"
        (cardClick)="onCardClick($event)">
      </fc-template-card>
    </div>
  `,
  styles: [`
    .section-title {
      font-size: 16px;
      font-weight: 600;
      margin: 16px 0 8px 0;
    }
    .recent-scroll {
      display: flex;
      gap: 12px;
      overflow-x: auto;
      padding-bottom: 8px;
    }
    .recent-scroll fc-template-card {
      min-width: 220px;
      max-width: 260px;
    }
  `],
})
export class RecentTemplatesComponent {
  @Input() recent: RecentTemplate[] = [];

  mapRecentToCard(item: RecentTemplate) {
    return {
      id: item.template_id,
      name: item.template_name,
      description: null,
      category: item.category,
      status: 'published',
      version: item.version,
      language: null,
      country: null,
      updated_at: item.last_used_at,
      is_pinned: false,
    };
  }

  onCardClick(card: any): void {
    window.location.href = `/studio/designer/${card.id}`;
  }
}
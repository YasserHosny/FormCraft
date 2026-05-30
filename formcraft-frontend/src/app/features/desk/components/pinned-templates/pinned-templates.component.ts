import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { PinnedTemplate, TemplateCard } from '../../services/desk.service';
import { TemplateCardComponent } from '../template-card/template-card.component';
import { Router, RouterModule } from '@angular/router';

@Component({
  selector: 'fc-pinned-templates',
  standalone: true,
  imports: [CommonModule, TranslateModule, TemplateCardComponent, RouterModule],
  template: `
    <h2 class="section-title">{{ 'desk.section_pinned' | translate }}</h2>
    <div class="section-empty" *ngIf="pinned.length === 0">
      {{ 'desk.empty_pinned' | translate }}
    </div>
    <div class="pinned-scroll">
      <fc-template-card
        *ngFor="let item of pinned"
        [template]="mapPinnedToCard(item)"
        [isPublished]="item.is_published"
        (pinToggle)="onPinToggle($event)"
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
    .pinned-scroll {
      display: flex;
      gap: 12px;
      overflow-x: auto;
      padding-bottom: 8px;
    }
    .pinned-scroll fc-template-card {
      min-width: 220px;
      max-width: 260px;
    }
    .section-empty {
      padding: 12px;
      color: rgba(0, 0, 0, 0.54);
    }
  `],
})
export class PinnedTemplatesComponent {
  @Input() pinned: PinnedTemplate[] = [];
  @Output() pinToggle = new EventEmitter<TemplateCard>();

  constructor(private router: Router) {}

  mapPinnedToCard(item: PinnedTemplate): TemplateCard {
    return {
      id: item.template_id,
      name: item.template_name,
      description: null,
      category: item.category,
      status: item.is_published ? 'published' : 'unpublished',
      version: item.version,
      lineage_id: null,
      is_deprecated: false,
      language: null,
      country: null,
      updated_at: item.pinned_at,
      is_pinned: true,
    };
  }

  onPinToggle(card: TemplateCard): void {
    this.pinToggle.emit(card);
  }

  onCardClick(card: TemplateCard): void {
    this.router.navigate(['/desk/fill', card.id]);
  }
}

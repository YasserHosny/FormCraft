import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule } from '@ngx-translate/core';
import { PageHeaderComponent } from '../shared/components/page-header.component';
import { DraftListComponent } from '../../../features/desk/components/draft-list/draft-list.component';

@Component({
  selector: 'fc-drafts',
  standalone: true,
  imports: [CommonModule, MatIconModule, TranslateModule, PageHeaderComponent, DraftListComponent],
  template: `
    <fc-page-header
      [title]="'desk.my_drafts' | translate"
      [subtitle]="'desk.dashboard.kpi_drafts_sub' | translate">
    </fc-page-header>

    <div class="page-body">
      <section class="fc-card drafts-card">
        <fc-draft-list [useNewThemeRoute]="true"></fc-draft-list>
      </section>
    </div>
  `,
  styles: [`
    .page-body {
      padding: 20px 24px;
    }

    .drafts-card {
      max-width: 920px;
      padding: 16px;
    }
  `],
})
export class DraftsComponent {}

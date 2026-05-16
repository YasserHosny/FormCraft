import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { DesignerPageComponent } from './designer-page/designer-page.component';
import { AiSuggestionChipComponent } from './components/ai-suggestion-chip/ai-suggestion-chip.component';
import { TafqeetPropertyPanelComponent } from './components/tafqeet-property-panel/tafqeet-property-panel.component';
import { StatusBadgeComponent } from './components/status-badge/status-badge.component';
import { VersionHistoryComponent } from './version-history/version-history.component';
import { VersionDiffComponent } from './version-diff/version-diff.component';

const routes: Routes = [
  { path: ':templateId', component: DesignerPageComponent },
];

@NgModule({
  declarations: [DesignerPageComponent, AiSuggestionChipComponent, TafqeetPropertyPanelComponent],
  imports: [
    SharedModule,
    RouterModule.forChild(routes),
    StatusBadgeComponent,
    VersionHistoryComponent,
    VersionDiffComponent,
  ],
})
export class DesignerModule {}

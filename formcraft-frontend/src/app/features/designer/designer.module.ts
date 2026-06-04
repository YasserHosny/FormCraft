import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { DesignerPageComponent } from './designer-page/designer-page.component';
import { AiSuggestionChipComponent } from './components/ai-suggestion-chip/ai-suggestion-chip.component';
import { TafqeetPropertyPanelComponent } from './components/tafqeet-property-panel/tafqeet-property-panel.component';
import { StatusBadgeComponent } from './components/status-badge/status-badge.component';
import { VersionHistoryComponent } from './version-history/version-history.component';
import { VersionDiffComponent } from './version-diff/version-diff.component';
import { FeedbackPanelComponent } from './feedback-panel/feedback-panel.component';
import { SignaturePropertyPanelComponent } from './components/signature-property-panel/signature-property-panel.component';
import { TableConfigPanelComponent } from './components/table-config/table-config.component';
import { RefBindingPanelComponent } from './components/ref-binding-panel/ref-binding-panel.component';
import { FormattingPropertyPanelComponent } from './components/formatting-property-panel/formatting-property-panel.component';

const routes: Routes = [
  { path: ':templateId', component: DesignerPageComponent },
];

@NgModule({
  declarations: [DesignerPageComponent, AiSuggestionChipComponent, TafqeetPropertyPanelComponent, FormattingPropertyPanelComponent],
  imports: [
    SharedModule,
    RouterModule.forChild(routes),
    StatusBadgeComponent,
    VersionHistoryComponent,
    VersionDiffComponent,
    FeedbackPanelComponent,
    SignaturePropertyPanelComponent,
    TableConfigPanelComponent,
    RefBindingPanelComponent,
  ],
})
export class DesignerModule {}

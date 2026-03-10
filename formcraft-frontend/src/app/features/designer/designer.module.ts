import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { DesignerPageComponent } from './designer-page/designer-page.component';
import { AiSuggestionChipComponent } from './components/ai-suggestion-chip/ai-suggestion-chip.component';

const routes: Routes = [
  { path: ':templateId', component: DesignerPageComponent },
];

@NgModule({
  declarations: [DesignerPageComponent, AiSuggestionChipComponent],
  imports: [SharedModule, RouterModule.forChild(routes)],
})
export class DesignerModule {}

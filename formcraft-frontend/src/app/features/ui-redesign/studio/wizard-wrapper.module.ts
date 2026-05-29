import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { TemplateWizardComponent } from '../../templates/template-wizard/template-wizard.component';
import { WizardCanDeactivateGuard } from '../../templates/template-wizard/guards/wizard-can-deactivate.guard';
import { TemplateWizardModule } from '../../templates/template-wizard/template-wizard.module';

const routes: Routes = [
  {
    path: '',
    component: TemplateWizardComponent,
    canDeactivate: [WizardCanDeactivateGuard],
  },
];

@NgModule({
  imports: [TemplateWizardModule, RouterModule.forChild(routes)],
})
export class WizardWrapperModule {}

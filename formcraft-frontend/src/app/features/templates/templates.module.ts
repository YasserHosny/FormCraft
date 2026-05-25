import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { TemplateListComponent } from './template-list/template-list.component';
import { TemplateCreateDialogComponent } from './template-create-dialog/template-create-dialog.component';
import { CloneDialogComponent } from './clone-dialog/clone-dialog.component';
import { TemplateWizardComponent } from './template-wizard/template-wizard.component';
import { TemplateWizardService } from './template-wizard/template-wizard.service';
import { WizardCanDeactivateGuard } from './template-wizard/guards/wizard-can-deactivate.guard';
import { StepBasicInfoComponent } from './template-wizard/steps/step-basic-info/step-basic-info.component';
import { StepLocaleComponent } from './template-wizard/steps/step-locale/step-locale.component';
import { StepPageSetupComponent } from './template-wizard/steps/step-page-setup/step-page-setup.component';
import { StepStartingPointComponent } from './template-wizard/steps/step-starting-point/step-starting-point.component';

const routes: Routes = [
  { path: '', component: TemplateListComponent },
  {
    path: 'new',
    component: TemplateWizardComponent,
    canDeactivate: [WizardCanDeactivateGuard],
  },
];

@NgModule({
  declarations: [
    TemplateListComponent,
    TemplateCreateDialogComponent,
    CloneDialogComponent,
    TemplateWizardComponent,
    StepBasicInfoComponent,
    StepLocaleComponent,
    StepPageSetupComponent,
    StepStartingPointComponent,
  ],
  imports: [SharedModule, RouterModule.forChild(routes)],
  providers: [TemplateWizardService, WizardCanDeactivateGuard],
})
export class TemplatesModule {}

import { NgModule } from '@angular/core';
import { SharedModule } from '../../../shared/shared.module';
import { TemplateWizardComponent } from './template-wizard.component';
import { TemplateWizardService } from './template-wizard.service';
import { WizardCanDeactivateGuard } from './guards/wizard-can-deactivate.guard';
import { StepBasicInfoComponent } from './steps/step-basic-info/step-basic-info.component';
import { StepLocaleComponent } from './steps/step-locale/step-locale.component';
import { StepPageSetupComponent } from './steps/step-page-setup/step-page-setup.component';
import { StepStartingPointComponent } from './steps/step-starting-point/step-starting-point.component';

@NgModule({
  declarations: [
    TemplateWizardComponent,
    StepBasicInfoComponent,
    StepLocaleComponent,
    StepPageSetupComponent,
    StepStartingPointComponent,
  ],
  imports: [SharedModule],
  exports: [TemplateWizardComponent],
  providers: [TemplateWizardService, WizardCanDeactivateGuard],
})
export class TemplateWizardModule {}

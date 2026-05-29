import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { TemplateListComponent } from './template-list/template-list.component';
import { TemplateCreateDialogComponent } from './template-create-dialog/template-create-dialog.component';
import { CloneDialogComponent } from './clone-dialog/clone-dialog.component';
import { TemplateWizardComponent } from './template-wizard/template-wizard.component';
import { WizardCanDeactivateGuard } from './template-wizard/guards/wizard-can-deactivate.guard';
import { TemplateWizardModule } from './template-wizard/template-wizard.module';

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
  ],
  imports: [SharedModule, RouterModule.forChild(routes), TemplateWizardModule],
})
export class TemplatesModule {}

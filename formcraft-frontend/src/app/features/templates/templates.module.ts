import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { TemplateListComponent } from './template-list/template-list.component';
import { TemplateCreateDialogComponent } from './template-create-dialog/template-create-dialog.component';

const routes: Routes = [
  { path: '', component: TemplateListComponent },
];

@NgModule({
  declarations: [TemplateListComponent, TemplateCreateDialogComponent],
  imports: [SharedModule, RouterModule.forChild(routes)],
})
export class TemplatesModule {}

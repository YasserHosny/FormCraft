import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { PlatformAdminGuard } from '../../core/guards/platform-admin.guard';
import { PlatformLayoutComponent } from './platform-layout/platform-layout.component';
import { PlatformDashboardComponent } from './platform-dashboard/platform-dashboard.component';
import { OrganizationListComponent } from './organization-list/organization-list.component';
import { OrganizationCreateComponent } from './organization-create/organization-create.component';
import { OrganizationDetailComponent } from './organization-detail/organization-detail.component';

const routes: Routes = [
  {
    path: '',
    component: PlatformLayoutComponent,
    canActivate: [PlatformAdminGuard],
    children: [
      { path: '', component: PlatformDashboardComponent },
      { path: 'organizations', component: OrganizationListComponent },
      { path: 'organizations/create', component: OrganizationCreateComponent },
      { path: 'organizations/:id', component: OrganizationDetailComponent },
    ],
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class PlatformRoutingModule {}

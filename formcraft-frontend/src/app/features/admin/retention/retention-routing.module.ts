import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { RoleGuard } from 'src/app/core/auth/role.guard';

const routes: Routes = [
  {
    path: '',
    canActivate: [RoleGuard],
    data: { roles: ['Admin', 'Designer'] },
    children: [
      { path: '', redirectTo: 'policies', pathMatch: 'full' },
      { path: 'policies', loadComponent: () => import('./components/policy-list/policy-list.component').then(m => m.PolicyListComponent) },
      { path: 'jobs', loadComponent: () => import('./components/job-list/job-list.component').then(m => m.JobListComponent) },
      { path: 'holds', loadComponent: () => import('./components/legal-hold-list/legal-hold-list.component').then(m => m.LegalHoldListComponent) },
      { path: 'manifests', loadComponent: () => import('./components/archive-manifest-list/archive-manifest-list.component').then(m => m.ArchiveManifestListComponent) },
    ],
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class RetentionRoutingModule {}

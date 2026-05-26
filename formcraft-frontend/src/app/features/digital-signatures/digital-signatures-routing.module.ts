import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./request-list/request-list.component').then(m => m.RequestListComponent),
  },
  {
    path: 'workflows',
    loadComponent: () => import('./workflow-config/workflow-config.component').then(m => m.WorkflowConfigComponent),
  },
  {
    path: 'requests/:id',
    loadComponent: () => import('./request-detail/request-detail.component').then(m => m.RequestDetailComponent),
  },
  {
    path: 'evidence/:id',
    loadComponent: () => import('./evidence-viewer/evidence-viewer.component').then(m => m.EvidenceViewerComponent),
  },
  {
    path: 'sign/:token',
    loadComponent: () => import('./signer-portal/signer-portal.component').then(m => m.SignerPortalComponent),
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class DigitalSignaturesRoutingModule {}

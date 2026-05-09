import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { AuthGuard } from './core/auth/auth.guard';
import { RoleGuard } from './core/auth/role.guard';

const routes: Routes = [
  {
    path: 'auth',
    loadChildren: () =>
      import('./features/auth/auth.module').then((m) => m.AuthModule),
  },
  {
    path: 'templates',
    loadChildren: () =>
      import('./features/templates/templates.module').then(
        (m) => m.TemplatesModule
      ),
    canActivate: [AuthGuard],
  },
  {
    path: 'designer',
    loadChildren: () =>
      import('./features/designer/designer.module').then(
        (m) => m.DesignerModule
      ),
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['admin', 'designer'] },
  },
  {
    path: 'admin/feedback',
    loadChildren: () =>
      import('./features/feedback/feedback.module').then(
        (m) => m.FeedbackModule
      ),
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['admin'] },
  },
  {
    path: 'my-feedback',
    loadChildren: () =>
      import('./features/my-feedback/my-feedback.module').then(
        (m) => m.MyFeedbackModule
      ),
    canActivate: [AuthGuard],
  },
  { path: '', redirectTo: '/templates', pathMatch: 'full' },
  { path: '**', redirectTo: '/templates' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}

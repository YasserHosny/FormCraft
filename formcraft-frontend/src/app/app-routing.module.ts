import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { AuthGuard } from './core/auth/auth.guard';
import { RoleGuard } from './core/auth/role.guard';
import { InvitationAcceptComponent } from './features/auth/invitation/invitation-accept.component';
import { InvitationExpiredComponent } from './features/auth/invitation/invitation-expired.component';

const routes: Routes = [
  // Public invitation routes (no guard)
  { path: 'invite/expired', component: InvitationExpiredComponent },
  { path: 'invite/:token', component: InvitationAcceptComponent },
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
    path: 'marketplace',
    loadChildren: () =>
      import('./features/marketplace/marketplace.module').then(
        (m) => m.MarketplaceModule
      ),
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['admin'] },
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
    path: 'admin',
    loadChildren: () =>
      import('./features/admin/admin.module').then(
        (m) => m.AdminModule
      ),
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['admin'] },
  },
  {
    path: 'desk',
    loadChildren: () =>
      import('./features/desk/desk.module').then((m) => m.DeskModule),
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['admin', 'branch_manager', 'operator'] },
  },
  {
    path: 'my-feedback',
    loadChildren: () =>
      import('./features/my-feedback/my-feedback.module').then(
        (m) => m.MyFeedbackModule
      ),
    canActivate: [AuthGuard],
  },
  {
    path: 'forms/:org/:slug',
    loadChildren: () =>
      import('./features/public-portal/public-portal.module').then(
        (m) => m.PublicPortalModule
      ),
  },
  {
    path: 'admin/analytics',
    loadChildren: () =>
      import('./features/analytics/analytics.module').then(
        (m) => m.AnalyticsModule
      ),
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['admin', 'designer'] },
  },
  // UI Redesign prototype (standalone, no auth guard for dev)
  {
    path: 'ui',
    loadChildren: () =>
      import('./features/ui-redesign/ui-redesign.routes').then(
        (m) => m.UI_REDESIGN_ROUTES
      ),
  },
  // F15: Default redirect to /templates (Studio). Role-based redirect happens at login and in RoleGuard.
  { path: '', redirectTo: '/templates', pathMatch: 'full' },
  { path: '**', redirectTo: '/templates' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}

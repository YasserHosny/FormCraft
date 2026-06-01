import { NgModule, Component, inject } from '@angular/core';
import { RouterModule, Routes, Router } from '@angular/router';

import { AuthGuard } from './core/auth/auth.guard';
import { RoleGuard } from './core/auth/role.guard';
import { InvitationAcceptComponent } from './features/auth/invitation/invitation-accept.component';
import { InvitationExpiredComponent } from './features/auth/invitation/invitation-expired.component';
import { ThemePreferenceService } from './core/services/theme-preference.service';
import { AuthService } from './core/auth/auth.service';

@Component({ standalone: true, selector: 'fc-theme-redirect', template: '' })
class ThemeRedirectComponent {
  constructor() {
    const router = inject(Router);
    const themePref = inject(ThemePreferenceService);
    const authService = inject(AuthService);
    const user = authService.getCurrentUser();
    const role = user?.role || 'admin';
    const target = themePref.getDefaultRoute(themePref.getPreference(), role);
    router.navigate([target], { replaceUrl: true });
  }
}

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
    path: 'admin/analytics',
    loadChildren: () =>
      import('./features/analytics/analytics.module').then(
        (m) => m.AnalyticsModule
      ),
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['admin', 'designer'] },
  },
  {
    path: 'admin/ocr-onboarding',
    loadChildren: () =>
      import('./features/admin/ocr-onboarding/ocr-onboarding.module').then(
        (m) => m.OcrOnboardingModule
      ),
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['admin'] },
  },
  // F042: Enterprise SSO and MFA
  {
    path: 'admin/sso',
    loadChildren: () =>
      import('./features/sso/sso.module').then((m) => m.SsoModule),
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
    data: { roles: ['admin', 'branch_manager', 'operator', 'designer'] },
  },
  {
    path: 'platform',
    loadChildren: () =>
      import('./features/platform/platform.module').then((m) => m.PlatformModule),
    canActivate: [AuthGuard],
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
  // UI Redesign shell. Kept alongside the classic routes so users can switch themes.
  {
    path: 'ui',
    loadChildren: () =>
      import('./features/ui-redesign/ui-redesign.routes').then(
        (m) => m.UI_REDESIGN_ROUTES
      ),
    canActivate: [AuthGuard],
  },
  {
    path: 'mfa',
    loadChildren: () =>
      import('./features/mfa/mfa.module').then((m) => m.MfaModule),
    canActivate: [AuthGuard],
  },
  // Theme-aware default redirect: checks localStorage preference to land on correct theme.
  { path: '', component: ThemeRedirectComponent, pathMatch: 'full', canActivate: [AuthGuard] },
  { path: '**', component: ThemeRedirectComponent, canActivate: [AuthGuard] },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}

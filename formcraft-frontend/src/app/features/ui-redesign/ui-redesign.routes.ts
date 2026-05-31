import { Routes } from '@angular/router';
import { RoleGuard } from '../../core/auth/role.guard';
import { LayoutComponent } from './shell/layout.component';
import { ClassicRedirectComponent } from './shared/classic-redirect.component';

export const UI_REDESIGN_ROUTES: Routes = [
  {
    path: '',
    component: LayoutComponent,
    children: [
      // Studio mode
      { path: '', redirectTo: 'studio/templates', pathMatch: 'full' },
      {
        path: 'studio/templates',
        canActivate: [RoleGuard],
        data: { roles: ['admin', 'designer'] },
        loadComponent: () =>
          import('./studio/template-list.component').then(m => m.TemplateListComponent),
      },
      {
        path: 'studio/wizard',
        canActivate: [RoleGuard],
        data: { roles: ['admin', 'designer'] },
        loadChildren: () =>
          import('./studio/wizard-wrapper.module').then(m => m.WizardWrapperModule),
      },
      {
        path: 'studio/designer',
        canActivate: [RoleGuard],
        data: { roles: ['admin', 'designer'] },
        loadChildren: () =>
          import('../designer/designer.module').then(m => m.DesignerModule),
      },

      // Desk mode
      {
        path: 'desk',
        canActivate: [RoleGuard],
        data: { roles: ['admin', 'branch_manager', 'operator'] },
        loadComponent: () =>
          import('./desk/dashboard.component').then(m => m.DashboardComponent),
      },
      {
        path: 'desk/templates',
        canActivate: [RoleGuard],
        data: { roles: ['admin', 'branch_manager', 'operator'] },
        loadComponent: () =>
          import('./desk/templates.component').then(m => m.TemplatesComponent),
      },
      {
        path: 'desk/fill/:templateId',
        canActivate: [RoleGuard],
        data: { roles: ['admin', 'branch_manager', 'operator'] },
        loadComponent: () =>
          import('./desk/form-filler.component').then(m => m.FormFillerComponent),
      },
      {
        path: 'desk/customers',
        canActivate: [RoleGuard],
        data: { roles: ['admin', 'branch_manager', 'operator'] },
        loadComponent: () =>
          import('./desk/customers.component').then(m => m.CustomersComponent),
      },
      {
        path: 'desk/customers/:id',
        canActivate: [RoleGuard],
        data: { roles: ['admin', 'branch_manager', 'operator'], classicRoute: '/desk/customers/:id' },
        component: ClassicRedirectComponent,
      },
      {
        path: 'desk/history',
        canActivate: [RoleGuard],
        data: { roles: ['admin', 'branch_manager', 'operator'], classicRoute: '/desk/history' },
        component: ClassicRedirectComponent,
      },
      {
        path: 'desk/queue',
        canActivate: [RoleGuard],
        data: { roles: ['admin', 'branch_manager', 'operator'], classicRoute: '/desk/queue' },
        component: ClassicRedirectComponent,
      },

      // Admin mode
      {
        path: 'admin/analytics',
        canActivate: [RoleGuard],
        data: { roles: ['admin'] },
        loadComponent: () =>
          import('./admin/analytics.component').then(m => m.AnalyticsComponent),
      },
      {
        path: 'admin/reviews',
        canActivate: [RoleGuard],
        data: { roles: ['admin'], classicRoute: '/admin/reviews' },
        component: ClassicRedirectComponent,
      },
      {
        path: 'admin/governance',
        canActivate: [RoleGuard],
        data: { roles: ['admin'], classicRoute: '/admin/governance' },
        component: ClassicRedirectComponent,
      },
      {
        path: 'admin/settings',
        canActivate: [RoleGuard],
        data: { roles: ['admin'], classicRoute: '/admin/settings' },
        component: ClassicRedirectComponent,
      },
      {
        path: 'admin/users',
        canActivate: [RoleGuard],
        data: { roles: ['admin'], classicRoute: '/admin/users' },
        component: ClassicRedirectComponent,
      },
      {
        path: 'admin/departments',
        canActivate: [RoleGuard],
        data: { roles: ['admin'], classicRoute: '/admin/departments' },
        component: ClassicRedirectComponent,
      },

      // Profile
      {
        path: 'profile',
        loadComponent: () =>
          import('./shared/components/profile.component').then(m => m.ProfileComponent),
      },
    ],
  },
];

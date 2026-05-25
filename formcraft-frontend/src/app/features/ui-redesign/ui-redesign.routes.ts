import { Routes } from '@angular/router';
import { LayoutComponent } from './shell/layout.component';

export const UI_REDESIGN_ROUTES: Routes = [
  {
    path: '',
    component: LayoutComponent,
    children: [
      // Studio mode
      { path: '', redirectTo: 'studio/templates', pathMatch: 'full' },
      {
        path: 'studio/templates',
        loadComponent: () =>
          import('./studio/template-list.component').then(m => m.TemplateListComponent),
      },
      {
        path: 'studio/designer/:pageId',
        loadComponent: () =>
          import('./studio/designer.component').then(m => m.DesignerComponent),
      },

      // Desk mode
      {
        path: 'desk',
        loadComponent: () =>
          import('./desk/dashboard.component').then(m => m.DashboardComponent),
      },
      {
        path: 'desk/fill/:templateId',
        loadComponent: () =>
          import('./desk/form-filler.component').then(m => m.FormFillerComponent),
      },
      {
        path: 'desk/customers',
        loadComponent: () =>
          import('./desk/customers.component').then(m => m.CustomersComponent),
      },

      // Admin mode
      {
        path: 'admin/analytics',
        loadComponent: () =>
          import('./admin/analytics.component').then(m => m.AnalyticsComponent),
      },
    ],
  },
];

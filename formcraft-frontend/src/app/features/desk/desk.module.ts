import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { MatCardModule } from '@angular/material/card';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBarModule } from '@angular/material/snack-bar';

import { DashboardComponent } from './dashboard/dashboard.component';
import { TemplateCardComponent } from './components/template-card/template-card.component';
import { RecentTemplatesComponent } from './components/recent-templates/recent-templates.component';
import { PinnedTemplatesComponent } from './components/pinned-templates/pinned-templates.component';
import { DraftListComponent } from './components/draft-list/draft-list.component';
import { VersionNotificationsComponent } from './components/version-notifications/version-notifications.component';
import { DeskService } from './services/desk.service';
import { CustomerListComponent } from './customers/customer-list.component';
import { CustomerDetailComponent } from './customers/customer-detail.component';

const routes: Routes = [
  { path: '', component: DashboardComponent },
  { path: 'fill', loadChildren: () => import('./fill/fill.module').then(m => m.FormFillerModule) },
  { path: 'history', loadChildren: () => import('./history/history.module').then(m => m.HistoryModule) },
  { path: 'customers', component: CustomerListComponent },
  { path: 'customers/new', component: CustomerDetailComponent },
  { path: 'customers/:id', component: CustomerDetailComponent },
  { path: 'queue', loadChildren: () => import('./batch-queue/batch-queue.module').then(m => m.BatchQueueModule) },
];

@NgModule({
  imports: [
    SharedModule,
    RouterModule.forChild(routes),
    MatCardModule,
    MatPaginatorModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatIconModule,
    MatChipsModule,
    MatButtonModule,
    MatTooltipModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    DashboardComponent,
    TemplateCardComponent,
    RecentTemplatesComponent,
    PinnedTemplatesComponent,
    DraftListComponent,
    VersionNotificationsComponent,
    CustomerListComponent,
    CustomerDetailComponent,
  ],
  providers: [DeskService],
})
export class DeskModule {}

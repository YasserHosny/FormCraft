import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { TranslateModule } from '@ngx-translate/core';

import { AngularMaterialModule } from '../../shared/angular-material.module';
import { PlatformRoutingModule } from './platform-routing.module';
import { PlatformLayoutComponent } from './platform-layout/platform-layout.component';
import { ContextSwitcherComponent } from './platform-layout/context-switcher/context-switcher.component';
import { PlatformDashboardComponent } from './platform-dashboard/platform-dashboard.component';
import { OrganizationListComponent } from './organization-list/organization-list.component';
import { OrganizationCreateComponent } from './organization-create/organization-create.component';
import { OrganizationDetailComponent } from './organization-detail/organization-detail.component';
import { ProfileTabComponent } from './organization-detail/tabs/profile-tab/profile-tab.component';
import { SubscriptionTabComponent } from './organization-detail/tabs/subscription-tab/subscription-tab.component';
import { UsersTabComponent } from './organization-detail/tabs/users-tab/users-tab.component';
import { StatsTabComponent } from './organization-detail/tabs/stats-tab/stats-tab.component';

@NgModule({
  declarations: [
    PlatformLayoutComponent,
    ContextSwitcherComponent,
    PlatformDashboardComponent,
    OrganizationListComponent,
    OrganizationCreateComponent,
    OrganizationDetailComponent,
    ProfileTabComponent,
    SubscriptionTabComponent,
    UsersTabComponent,
    StatsTabComponent,
  ],
  imports: [
    CommonModule,
    RouterModule,
    ReactiveFormsModule,
    TranslateModule,
    AngularMaterialModule,
    PlatformRoutingModule,
  ],
})
export class PlatformModule {}

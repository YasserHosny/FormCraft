import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { IdpConfigComponent } from './components/idp-config/idp-config.component';
import { DomainVerifyComponent } from './components/domain-verify/domain-verify.component';
import { MappingConfigComponent } from './components/mapping-config/mapping-config.component';

const routes: Routes = [
  { path: '', component: IdpConfigComponent },
  { path: 'verify', component: DomainVerifyComponent },
  { path: 'mappings', component: MappingConfigComponent },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
})
export class SsoRoutingModule {}

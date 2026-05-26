import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';

import { SsoRoutingModule } from './sso-routing.module';
import { IdpConfigComponent } from './components/idp-config/idp-config.component';
import { DomainVerifyComponent } from './components/domain-verify/domain-verify.component';
import { MappingConfigComponent } from './components/mapping-config/mapping-config.component';

@NgModule({
  declarations: [IdpConfigComponent, DomainVerifyComponent, MappingConfigComponent],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    SsoRoutingModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    MatIconModule,
  ],
})
export class SsoModule {}

import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { TranslateModule } from '@ngx-translate/core';

import { DigitalSignaturesRoutingModule } from './digital-signatures-routing.module';

@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    DigitalSignaturesRoutingModule,
    RouterModule,
    ReactiveFormsModule,
    TranslateModule,
  ],
})
export class DigitalSignaturesModule {}

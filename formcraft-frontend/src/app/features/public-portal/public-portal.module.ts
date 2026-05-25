import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { PublicFormPageComponent } from './public-form-page/public-form-page.component';
import { ConfirmationPageComponent } from './confirmation-page/confirmation-page.component';
import { OtpGateComponent } from './otp-gate/otp-gate.component';

const routes: Routes = [
  { path: '', component: PublicFormPageComponent },
  { path: 'confirmation', component: ConfirmationPageComponent },
];

@NgModule({
  declarations: [PublicFormPageComponent, ConfirmationPageComponent, OtpGateComponent],
  imports: [SharedModule, RouterModule.forChild(routes)],
})
export class PublicPortalModule {}

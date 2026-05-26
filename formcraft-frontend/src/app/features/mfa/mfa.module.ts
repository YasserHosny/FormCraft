import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';

import { EnrollComponent } from './components/enroll/enroll.component';
import { ChallengeComponent } from './components/challenge/challenge.component';

const routes: Routes = [
  { path: 'enroll', component: EnrollComponent },
  { path: 'challenge', component: ChallengeComponent },
];

@NgModule({
  declarations: [EnrollComponent, ChallengeComponent],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule.forChild(routes),
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
  ],
})
export class MfaModule {}

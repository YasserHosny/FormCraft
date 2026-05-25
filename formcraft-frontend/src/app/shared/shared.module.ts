import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { TranslateModule } from '@ngx-translate/core';

import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatCardModule } from '@angular/material/card';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatMenuModule } from '@angular/material/menu';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatChipsModule } from '@angular/material/chips';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatRadioModule } from '@angular/material/radio';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatTabsModule } from '@angular/material/tabs';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatBadgeModule } from '@angular/material/badge';
import { MatDividerModule } from '@angular/material/divider';
import { MatStepperModule } from '@angular/material/stepper';
import { RouterModule } from '@angular/router';

import { AutoDirDirective } from './directives/auto-dir.directive';
import { AppShellComponent } from './components/app-shell/app-shell.component';
import { ThreadComponent } from './components/thread/thread.component';
import { GlobalSearchBarComponent } from './components/global-search/global-search-bar.component';

const MATERIAL_MODULES = [
  MatButtonModule,
  MatIconModule,
  MatInputModule,
  MatFormFieldModule,
  MatSelectModule,
  MatCardModule,
  MatToolbarModule,
  MatSidenavModule,
  MatListModule,
  MatDialogModule,
  MatSnackBarModule,
  MatTableModule,
  MatPaginatorModule,
  MatMenuModule,
  MatTooltipModule,
  MatChipsModule,
  MatSlideToggleModule,
  MatRadioModule,
  MatCheckboxModule,
  MatTabsModule,
  MatProgressSpinnerModule,
  MatBadgeModule,
  MatDividerModule,
  MatStepperModule,
];

@NgModule({
  declarations: [AutoDirDirective, AppShellComponent, ThreadComponent],
  imports: [CommonModule, FormsModule, ReactiveFormsModule, TranslateModule, RouterModule, GlobalSearchBarComponent, ...MATERIAL_MODULES],
  exports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    TranslateModule,
    RouterModule,
    AutoDirDirective,
    AppShellComponent,
    ThreadComponent,
    ...MATERIAL_MODULES,
  ],
})
export class SharedModule {}

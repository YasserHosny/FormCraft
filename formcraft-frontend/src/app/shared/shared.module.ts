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
import { MatTabsModule } from '@angular/material/tabs';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatBadgeModule } from '@angular/material/badge';
import { MatDividerModule } from '@angular/material/divider';
import { RouterModule } from '@angular/router';

import { AutoDirDirective } from './directives/auto-dir.directive';
import { AppShellComponent } from './components/app-shell/app-shell.component';
import { ThreadComponent } from './components/thread/thread.component';

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
  MatTabsModule,
  MatProgressSpinnerModule,
  MatBadgeModule,
  MatDividerModule,
];

@NgModule({
  declarations: [AutoDirDirective, AppShellComponent, ThreadComponent],
  imports: [CommonModule, FormsModule, ReactiveFormsModule, TranslateModule, RouterModule, ...MATERIAL_MODULES],
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

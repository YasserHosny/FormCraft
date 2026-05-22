import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { Subject, takeUntil } from 'rxjs';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatOptionModule } from '@angular/material/core';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatPaginatorModule } from '@angular/material/paginator';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { DeskService, DashboardData, TemplateCard } from '../services/desk.service';
import { TemplateCardComponent } from '../components/template-card/template-card.component';
import { RecentTemplatesComponent } from '../components/recent-templates/recent-templates.component';
import { PinnedTemplatesComponent } from '../components/pinned-templates/pinned-templates.component';
import { DraftListComponent } from '../components/draft-list/draft-list.component';
import { VersionNotificationsComponent } from '../components/version-notifications/version-notifications.component';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'fc-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatOptionModule,
    MatIconModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatPaginatorModule,
    MatSnackBarModule,
    TranslateModule,
    TemplateCardComponent,
    RecentTemplatesComponent,
    PinnedTemplatesComponent,
    DraftListComponent,
    VersionNotificationsComponent,
  ],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
})
export class DashboardComponent implements OnInit {
  dashboard: DashboardData | null = null;
  loading = true;
  error = false;

  search = '';
  category = '';
  country = '';
  language = '';
  page = 1;
  limit = 20;
  totalTemplates = 0;

  private destroy$ = new Subject<void>();

  constructor(
    private deskService: DeskService,
    private snackBar: MatSnackBar,
    private translate: TranslateService,
  ) {}

  ngOnInit(): void {
    this.loadDashboard();
  }

  loadDashboard(): void {
    this.loading = true;
    this.error = false;
    this.deskService.getDashboard({
      search: this.search || undefined,
      category: this.category || undefined,
      country: this.country || undefined,
      language: this.language || undefined,
      page: this.page,
      limit: this.limit,
    }).pipe(takeUntil(this.destroy$)).subscribe({
      next: (data) => {
        this.dashboard = data;
        this.totalTemplates = data.templates.total;
        this.loading = false;
      },
      error: () => {
        this.error = true;
        this.loading = false;
      },
    });
  }

  onSearch(): void {
    this.page = 1;
    this.loadDashboard();
  }

  onClearFilters(): void {
    this.search = '';
    this.category = '';
    this.country = '';
    this.language = '';
    this.page = 1;
    this.loadDashboard();
  }

  onPageChange(event: any): void {
    this.page = event.pageIndex + 1;
    this.limit = event.pageSize;
    this.loadDashboard();
  }

  onPinToggle(template: TemplateCard): void {
    if (template.is_pinned) {
      this.deskService.unpinTemplate(template.id).pipe(takeUntil(this.destroy$)).subscribe({
        next: () => this.loadDashboard(),
        error: () => this.snackBar.open(this.translate.instant('errors.generic'), undefined, { duration: 3000 }),
      });
    } else {
      this.deskService.pinTemplate(template.id).pipe(takeUntil(this.destroy$)).subscribe({
        next: () => this.loadDashboard(),
        error: (err) => {
          if (err.status === 409 || err.status === 422) {
            this.snackBar.open(err.error?.detail || this.translate.instant('desk.pin_limit'), undefined, { duration: 3000 });
          } else {
            this.snackBar.open(this.translate.instant('errors.generic'), undefined, { duration: 3000 });
          }
        },
      });
    }
  }

  onCardClick(template: TemplateCard): void {
    window.location.href = `/studio/designer/${template.id}`;
  }

  onDismissNotification(notificationId: string): void {
    this.deskService.dismissNotification(notificationId).pipe(takeUntil(this.destroy$)).subscribe({
      next: () => {
        if (this.dashboard) {
          this.dashboard.notifications = this.dashboard.notifications.filter(
            (n) => n.id !== notificationId,
          );
        }
      },
      error: () => this.snackBar.open(this.translate.instant('errors.generic'), undefined, { duration: 3000 }),
    });
  }

  retry(): void {
    this.loadDashboard();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
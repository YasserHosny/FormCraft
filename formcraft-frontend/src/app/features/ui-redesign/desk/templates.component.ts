import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { Subject, takeUntil } from 'rxjs';
import { DeskService } from '../../../features/desk/services/desk.service';
import { PageHeaderComponent } from '../shared/components/page-header.component';

@Component({
  selector: 'fc-desk-templates',
  standalone: true,
  imports: [CommonModule, MatIconModule, TranslateModule, PageHeaderComponent],
  template: `
    <fc-page-header [title]="'desk.pick_title' | translate" [subtitle]="'desk.pick_sub' | translate">
      <div actions>
        <button class="fc-btn outline" (click)="goBack()"><mat-icon>arrow_back</mat-icon>{{ 'desk.pick_back' | translate }}</button>
      </div>
    </fc-page-header>

    <div class="page-body">
      <!-- Loading State -->
      <div *ngIf="loading" class="loading-state">
        <div class="skeleton-grid">
          <div class="skeleton-card" *ngFor="let i of [1,2,3,4,5,6]"></div>
        </div>
      </div>

      <!-- Error State -->
      <div *ngIf="error && !loading" class="error-state">
        <mat-icon>error_outline</mat-icon>
        <h3>{{ 'desk.pick_error' | translate }}</h3>
        <p>{{ error }}</p>
      </div>

      <!-- Templates Grid -->
      <div *ngIf="!loading && !error" class="templates-grid">
        <div *ngIf="templates.length === 0" class="empty-state">
          <mat-icon>folder_open</mat-icon>
          <h3>{{ 'desk.pick_empty_title' | translate }}</h3>
          <p>{{ 'desk.pick_empty_sub' | translate }}</p>
        </div>

        <div class="template-card"
             *ngFor="let template of templates"
             (click)="selectTemplate(template.id)">
          <div class="card-icon" [style.background]="getCardColor(template.id)">
            <mat-icon>edit_document</mat-icon>
          </div>
          <div class="card-content">
            <h3>{{ template.name }}</h3>
            <p class="template-id">{{ template.id?.slice(0, 12) }}</p>
            <p class="template-desc">{{ template.description || ('desk.pick_no_desc' | translate) }}</p>
          </div>
          <div class="card-meta">
            <span class="version">{{ template.version || 'v1' }}</span>
            <mat-icon class="arrow">chevron_left</mat-icon>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .page-body { padding: 24px; }
    .loading-state, .error-state {
      display: flex; flex-direction: column; align-items: center;
      justify-content: center; gap: 16px; padding: 48px 24px; text-align: center;
    }
    .error-state mat-icon { font-size: 48px; width: 48px; height: 48px; color: var(--fc-error); }
    .skeleton-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
    .skeleton-card { height: 180px; background: var(--fc-surface-hover); border-radius: 8px; animation: pulse 2s infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
    .templates-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
    .empty-state {
      grid-column: 1 / -1; display: flex; flex-direction: column; align-items: center;
      justify-content: center; gap: 12px; padding: 48px 24px; text-align: center;
    }
    .empty-state mat-icon { font-size: 48px; width: 48px; height: 48px; color: var(--fc-text-3); }
    .empty-state h3 { margin: 0; color: var(--fc-text); }
    .empty-state p { margin: 0; color: var(--fc-text-2); }
    .template-card {
      background: var(--fc-surface); border: 1px solid var(--fc-border); border-radius: 8px;
      padding: 16px; display: flex; gap: 12px; align-items: flex-start;
      cursor: pointer; transition: all 0.2s ease;
    }
    .template-card:hover {
      border-color: var(--fc-primary); background: var(--fc-surface-hover);
      transform: translateY(-2px); box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .card-icon { width: 56px; height: 56px; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; flex-shrink: 0; }
    .card-icon mat-icon { font-size: 28px; width: 28px; height: 28px; }
    .card-content { flex: 1; min-width: 0; }
    .card-content h3 { margin: 0 0 4px; color: var(--fc-text); font-size: 14px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .template-id { margin: 0 0 4px; color: var(--fc-text-3); font-size: 11px; font-weight: 500; font-family: monospace; }
    .template-desc { margin: 0; color: var(--fc-text-2); font-size: 12px; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; }
    .card-meta { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
    .version { color: var(--fc-text-3); font-size: 11px; font-weight: 500; }
    .arrow { color: var(--fc-text-3); }
  `],
})
export class TemplatesComponent implements OnInit, OnDestroy {
  templates: any[] = [];
  loading = true;
  error: string | null = null;

  private destroy$ = new Subject<void>();
  private colors = ['#3F51B5', '#1E88E5', '#00897B', '#E91E63', '#F57C00', '#5E35B1', '#00695C', '#C62828'];

  constructor(
    private deskService: DeskService,
    private router: Router,
    private translate: TranslateService,
  ) {}

  ngOnInit(): void {
    this.loadTemplates();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private loadTemplates(): void {
    this.deskService.getDashboard({})
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (dashboardData) => {
          this.templates = dashboardData.templates?.items || [];
          this.loading = false;
          this.error = null;
        },
        error: (err) => {
          console.error('Failed to load templates:', err);
          this.loading = false;
          this.error = this.translate.instant('desk.pick_load_error');
        },
      });
  }

  selectTemplate(templateId: string): void {
    this.router.navigate(['/ui/desk/fill', templateId]);
  }

  goBack(): void {
    this.router.navigate(['/ui/desk']);
  }

  getCardColor(templateId: string): string {
    const index = templateId.charCodeAt(0) % this.colors.length;
    return this.colors[index];
  }
}

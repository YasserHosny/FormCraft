import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatListModule } from '@angular/material/list';
import { MatSelectModule } from '@angular/material/select';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { PortalService } from '../../../core/services/portal.service';
import {
  PortalAnalyticsResponse,
  PortalConfiguration,
} from '../../../shared/models/portal.models';

@Component({
  selector: 'fc-admin-portal',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatCheckboxModule,
    MatFormFieldModule,
    MatInputModule,
    MatListModule,
    MatSelectModule,
    MatSlideToggleModule,
    MatIconModule,
    MatProgressSpinnerModule,
    TranslateModule,
  ],
  templateUrl: './portal.component.html',
  styleUrl: './portal.component.scss',
})
export class PortalComponent implements OnInit {
  private portalService = inject(PortalService);
  private translate = inject(TranslateService);

  templates: PortalConfiguration[] = [];
  selectedTemplate: PortalConfiguration | null = null;
  analytics: PortalAnalyticsResponse | null = null;
  loading = false;
  saving = false;
  error: string | null = null;
  success = false;

  ngOnInit(): void {
    this.loadTemplates();
  }

  loadTemplates(): void {
    this.loading = true;
    this.error = null;
    this.portalService.listPortalTemplates().subscribe({
      next: (resp: any) => {
        this.templates = resp.items || [];
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.error = this.translate.instant('errors.generic');
      },
    });
  }

  selectTemplate(config: PortalConfiguration): void {
    this.selectedTemplate = { ...config };
    this.success = false;
    this.error = null;
    this.loadAnalytics(config.template_id);
  }

  loadAnalytics(templateId: string): void {
    this.portalService.getPortalAnalytics(templateId).subscribe({
      next: (resp: any) => {
        this.analytics = resp;
      },
      error: () => {
        this.analytics = null;
      },
    });
  }

  save(): void {
    if (!this.selectedTemplate) return;
    this.saving = true;
    this.success = false;
    this.error = null;
    this.portalService
      .updatePortalTemplate(this.selectedTemplate.template_id, this.selectedTemplate)
      .subscribe({
        next: (resp: any) => {
          this.saving = false;
          this.success = true;
          const idx = this.templates.findIndex(
            (t) => t.template_id === resp.template_id
          );
          if (idx >= 0) {
            this.templates[idx] = resp;
          }
        },
        error: (err: any) => {
          this.saving = false;
          this.error = err?.error?.detail || this.translate.instant('errors.generic');
        },
      });
  }

  copyUrl(): void {
    if (!this.selectedTemplate?.public_url) return;
    navigator.clipboard.writeText(this.selectedTemplate.public_url);
  }
}

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatListModule } from '@angular/material/list';
import { MatChipsModule } from '@angular/material/chips';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatButtonModule } from '@angular/material/button';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { PortalService } from '../../../core/services/portal.service';
import {
  PortalAnalyticsResponse,
  PortalConfiguration,
} from '../../../shared/models/portal.models';

@Component({
  selector: 'fc-portal-admin',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatListModule,
    MatChipsModule,
    MatSlideToggleModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatCheckboxModule,
    MatButtonModule,
    TranslateModule,
  ],
  templateUrl: './portal-admin.component.html',
  styleUrls: ['./portal-admin.component.scss'],
})
export class PortalAdminComponent implements OnInit {
  templates: PortalConfiguration[] = [];
  selectedTemplate: PortalConfiguration | null = null;
  analytics: PortalAnalyticsResponse | null = null;
  loading = false;
  saving = false;
  error: string | null = null;
  success = false;

  constructor(
    private portalService: PortalService,
    private translate: TranslateService,
  ) {}

  ngOnInit(): void {
    this.loadTemplates();
  }

  loadTemplates(): void {
    this.loading = true;
    this.portalService.listPortalTemplates().subscribe({
      next: (resp) => {
        this.templates = resp.items;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.error = this.translate.instant('common.loading');
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
      next: (resp) => {
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
    this.portalService
      .updatePortalTemplate(this.selectedTemplate.template_id, this.selectedTemplate)
      .subscribe({
        next: (resp) => {
          this.saving = false;
          this.success = true;
          const idx = this.templates.findIndex(
            (t) => t.template_id === resp.template_id
          );
          if (idx >= 0) {
            this.templates[idx] = resp;
          }
        },
        error: (err) => {
          this.saving = false;
          this.error =
            err?.error?.detail || this.translate.instant('common.loading');
        },
      });
  }

  generateQrSvg(url: string): string {
    if (!url) return '';
    // Simple SVG QR-like placeholder; real QR can be generated server-side or via library
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128"><rect width="128" height="128" fill="white"/><text x="64" y="64" font-size="10" text-anchor="middle" dominant-baseline="middle">QR</text></svg>`;
    return svg;
  }
}

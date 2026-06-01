import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { TranslateModule } from '@ngx-translate/core';
import { DataExportService } from '../../../core/services/data-export.service';
import {
  ExportPreviewRequest,
  ExportPreviewResponse,
  ExportRequestRecord,
} from '../../../shared/models/integration.models';

type ExportState = 'idle' | 'preview_loading' | 'preview_ready' | 'preview_error' | 'downloading';

@Component({
  selector: 'fc-admin-export',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatIconModule,
    MatTableModule,
    MatProgressSpinnerModule,
    TranslateModule,
  ],
  templateUrl: './export.component.html',
  styleUrl: './export.component.scss',
})
export class ExportComponent implements OnInit {
  private fb = inject(FormBuilder);
  private dataExportService = inject(DataExportService);

  state: ExportState = 'idle';
  preview: ExportPreviewResponse | null = null;
  history: ExportRequestRecord[] = [];
  historyError = false;

  readonly OVERSIZED_THRESHOLD = 50000;

  form = this.fb.group({
    template_id: [''],
    date_from: [''],
    date_to: [''],
    branch_id: [''],
    operator_id: [''],
    status: [''],
    format: ['csv' as const],
    scope: ['flattened' as const],
  });

  displayedColumns = ['format', 'scope', 'matching_count', 'status', 'created_at'];

  ngOnInit(): void {
    this.loadHistory();
  }

  previewExport(): void {
    this.state = 'preview_loading';
    this.preview = null;
    this.dataExportService.preview(this.buildRequest()).subscribe({
      next: (preview) => {
        this.preview = preview;
        this.state = 'preview_ready';
      },
      error: () => {
        this.state = 'preview_error';
      },
    });
  }

  downloadExport(): void {
    if (!this.canDownload) return;
    this.state = 'downloading';
    const request = this.buildRequest();
    this.dataExportService.download(request).subscribe({
      next: (blob) => {
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = `submissions.${request.format}`;
        anchor.click();
        URL.revokeObjectURL(url);
        this.state = 'preview_ready';
        this.loadHistory();
      },
      error: () => {
        this.state = 'preview_ready';
      },
    });
  }

  retryPreview(): void {
    this.previewExport();
  }

  get canDownload(): boolean {
    if (!this.preview) return false;
    if (this.preview.matching_count > this.OVERSIZED_THRESHOLD) return false;
    if (!this.preview.can_download) return false;
    return true;
  }

  get isOversized(): boolean {
    return !!this.preview && this.preview.matching_count > this.OVERSIZED_THRESHOLD;
  }

  loadHistory(): void {
    this.historyError = false;
    this.dataExportService.listHistory().subscribe({
      next: (response) => {
        this.history = response.items || [];
      },
      error: () => {
        this.history = [];
        this.historyError = true;
      },
    });
  }

  private buildRequest(): ExportPreviewRequest {
    const raw = this.form.getRawValue();
    const filters: Record<string, string> = {};
    for (const key of ['template_id', 'date_from', 'date_to', 'branch_id', 'operator_id', 'status']) {
      const value = raw[key as keyof typeof raw];
      if (value) filters[key] = value;
    }
    return {
      filters,
      format: raw.format as ExportPreviewRequest['format'],
      scope: raw.scope as ExportPreviewRequest['scope'],
    };
  }
}

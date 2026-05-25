import { Component, inject } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { SharedModule } from '../../../shared/shared.module';
import { DataExportService } from '../../../core/services/data-export.service';
import {
  ExportPreviewRequest,
  ExportPreviewResponse,
  ExportRequestRecord,
} from '../../../shared/models/integration.models';

@Component({
  selector: 'app-data-export',
  standalone: true,
  imports: [SharedModule],
  templateUrl: './data-export.component.html',
  styleUrl: './data-export.component.scss',
})
export class DataExportComponent {
  private fb = inject(FormBuilder);

  loadingPreview = false;
  downloading = false;
  preview: ExportPreviewResponse | null = null;
  history: ExportRequestRecord[] = [];

  form = this.fb.group({
    template_id: [''],
    date_from: [''],
    date_to: [''],
    branch_id: [''],
    operator_id: [''],
    status: [''],
    format: ['csv'],
    scope: ['flattened'],
  });

  constructor(private dataExportService: DataExportService) {
    this.loadHistory();
  }

  previewExport(): void {
    this.loadingPreview = true;
    this.preview = null;
    this.dataExportService.preview(this.buildRequest()).subscribe({
      next: (preview) => {
        this.preview = preview;
        this.loadingPreview = false;
        this.loadHistory();
      },
      error: () => {
        this.loadingPreview = false;
      },
    });
  }

  downloadExport(): void {
    this.downloading = true;
    const request = this.buildRequest();
    this.dataExportService.download(request).subscribe({
      next: (blob) => {
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = `submissions.${request.format}`;
        anchor.click();
        URL.revokeObjectURL(url);
        this.downloading = false;
        this.loadHistory();
      },
      error: () => {
        this.downloading = false;
      },
    });
  }

  private loadHistory(): void {
    this.dataExportService.listHistory().subscribe({
      next: (response) => (this.history = response.items),
      error: () => (this.history = []),
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

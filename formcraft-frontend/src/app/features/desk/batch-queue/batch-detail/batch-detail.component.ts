import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { BatchService, BatchJob } from '../../../../core/services/batch.service';

@Component({
  standalone: false,
  selector: 'app-batch-detail',
  templateUrl: './batch-detail.component.html',
  styleUrls: ['./batch-detail.component.scss'],
})
export class BatchDetailComponent implements OnInit {
  job: BatchJob | null = null;
  loading = false;

  constructor(private route: ActivatedRoute, private batchService: BatchService) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loading = true;
      this.batchService.getJob(id).subscribe({
        next: (job) => {
          this.job = job;
          this.loading = false;
        },
        error: () => {
          this.loading = false;
        },
      });
    }
  }

  download(format: 'zip' | 'merged_pdf'): void {
    if (!this.job) return;
    this.batchService.downloadResults(this.job.id, format).subscribe((blob) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `batch_${this.job!.id}.${format}`;
      a.click();
      window.URL.revokeObjectURL(url);
    });
  }

  cancel(): void {
    if (!this.job) return;
    this.batchService.cancelJob(this.job.id).subscribe((job) => {
      this.job = job;
    });
  }
}

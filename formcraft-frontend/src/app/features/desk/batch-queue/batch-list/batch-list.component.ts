import { Component, OnInit } from '@angular/core';
import { BatchService, BatchJobSummary } from '../../../../core/services/batch.service';

@Component({
  selector: 'app-batch-list',
  templateUrl: './batch-list.component.html',
  styleUrls: ['./batch-list.component.scss'],
})
export class BatchListComponent implements OnInit {
  jobs: BatchJobSummary[] = [];
  total = 0;
  pageSize = 20;
  currentPage = 0;
  loading = false;

  constructor(private batchService: BatchService) {}

  ngOnInit(): void {
    this.loadJobs();
  }

  loadJobs(): void {
    this.loading = true;
    this.batchService.listJobs(undefined, this.pageSize, this.currentPage * this.pageSize)
      .subscribe({
        next: (res) => {
          this.jobs = res.items;
          this.total = res.total;
          this.loading = false;
        },
        error: () => {
          this.loading = false;
        },
      });
  }

  onPageChange(event: any): void {
    this.currentPage = event.pageIndex;
    this.pageSize = event.pageSize;
    this.loadJobs();
  }

  createNew(): void {
    // Navigate to wizard
    window.location.href = '/desk/queue/new';
  }
}

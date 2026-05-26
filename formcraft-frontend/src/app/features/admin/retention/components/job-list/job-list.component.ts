import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatChipsModule } from '@angular/material/chips';
import { TranslateModule } from '@ngx-translate/core';
import { RetentionService } from '../../services/retention.service';
import { RetentionJob } from '../../models/retention.model';

@Component({
  selector: 'app-job-list',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatButtonModule, MatPaginatorModule, MatChipsModule, TranslateModule],
  template: `
    <div class="retention-container" dir="rtl">
      <h2>{{ 'RETENTION.JOBS' | translate }}</h2>
      <table mat-table [dataSource]="jobs" class="mat-elevation-z2">
        <ng-container matColumnDef="id">
          <th mat-header-cell *matHeaderCellDef>ID</th>
          <td mat-cell *matCellDef="let job">{{ job.id | slice:0:8 }}</td>
        </ng-container>
        <ng-container matColumnDef="status">
          <th mat-header-cell *matHeaderCellDef>{{ 'RETENTION.STATUS' | translate }}</th>
          <td mat-cell *matCellDef="let job">
            <mat-chip [color]="statusColor(job.status)" selected>{{ job.status }}</mat-chip>
          </td>
        </ng-container>
        <ng-container matColumnDef="progress">
          <th mat-header-cell *matHeaderCellDef>{{ 'RETENTION.PROGRESS' | translate }}</th>
          <td mat-cell *matCellDef="let job">{{ job.actioned_count }} / {{ job.evaluated_count }}</td>
        </ng-container>
        <ng-container matColumnDef="actions">
          <th mat-header-cell *matHeaderCellDef></th>
          <td mat-cell *matCellDef="let job">
            <button mat-button *ngIf="job.status === 'running'" (click)="pause(job.id)">Pause</button>
            <button mat-button *ngIf="job.status === 'paused'" (click)="resume(job.id)">Resume</button>
          </td>
        </ng-container>
        <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
        <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
      </table>
      <mat-paginator [pageSizeOptions]="[10, 20, 50]"></mat-paginator>
    </div>
  `,
  styles: [`
    .retention-container { padding: 16px; }
    table { width: 100%; margin-top: 16px; }
  `],
})
export class JobListComponent implements OnInit {
  jobs: RetentionJob[] = [];
  displayedColumns = ['id', 'status', 'progress', 'actions'];

  constructor(private service: RetentionService) {}

  ngOnInit(): void {
    this.service.listJobs().subscribe((res: any) => {
      this.jobs = res.items || [];
    });
  }

  statusColor(status: string): string {
    switch (status) {
      case 'completed': return 'primary';
      case 'failed': return 'warn';
      case 'running': return 'accent';
      default: return '';
    }
  }

  pause(id: string): void {
    this.service.pauseJob(id).subscribe(() => this.ngOnInit());
  }

  resume(id: string): void {
    this.service.resumeJob(id).subscribe(() => this.ngOnInit());
  }
}

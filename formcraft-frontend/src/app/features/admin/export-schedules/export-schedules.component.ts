import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { FormsModule } from '@angular/forms';
import { TranslateModule } from '@ngx-translate/core';
import { DataExportService } from '../../../core/services/data-export.service';

interface ExportSchedule {
  id: string;
  name: string;
  dataset: string;
  format: string;
  scope: string;
  frequency: string;
  email_recipients: string[];
  status: string;
  next_run_at: string;
  last_run_at: string | null;
  created_at: string;
}

@Component({
  selector: 'fc-export-schedules',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatChipsModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
    MatDialogModule,
    TranslateModule,
  ],
  templateUrl: './export-schedules.component.html',
  styleUrls: ['./export-schedules.component.scss'],
})
export class ExportSchedulesComponent implements OnInit {
  schedules: ExportSchedule[] = [];
  displayedColumns = ['name', 'frequency', 'format', 'status', 'nextRun', 'actions'];
  loading = true;

  constructor(
    private exportService: DataExportService,
    private snackBar: MatSnackBar,
    private dialog: MatDialog,
  ) {}

  ngOnInit(): void {
    this.loadSchedules();
  }

  loadSchedules(): void {
    this.loading = true;
    this.exportService.listSchedules().subscribe({
      next: (response: any) => {
        this.schedules = response.items || [];
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.snackBar.open('Failed to load schedules', '', { duration: 3000 });
      },
    });
  }

  runNow(schedule: ExportSchedule): void {
    this.exportService.runScheduleNow(schedule.id).subscribe({
      next: () => {
        this.snackBar.open('Schedule executed', '', { duration: 3000 });
        this.loadSchedules();
      },
      error: (err: any) => {
        this.snackBar.open(err.error?.detail || 'Execution failed', '', { duration: 3000 });
      },
    });
  }

  toggleStatus(schedule: ExportSchedule): void {
    const newStatus = schedule.status === 'active' ? 'paused' : 'active';
    this.exportService.updateSchedule(schedule.id, { status: newStatus }).subscribe({
      next: () => {
        this.snackBar.open('Status updated', '', { duration: 3000 });
        this.loadSchedules();
      },
      error: (err: any) => {
        this.snackBar.open(err.error?.detail || 'Update failed', '', { duration: 3000 });
      },
    });
  }

  getStatusColor(status: string): string {
    switch (status) {
      case 'active': return 'primary';
      case 'paused': return 'accent';
      case 'disabled': return 'warn';
      default: return '';
    }
  }
}
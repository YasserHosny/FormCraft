import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Subject, takeUntil } from 'rxjs';
import { HistoryService, SubmissionDetail } from '../services/history.service';
import { TranslateService } from '@ngx-translate/core';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'fc-submission-detail',
  templateUrl: './detail.component.html',
  styleUrls: ['./detail.component.scss'],
})
export class DetailComponent implements OnInit, OnDestroy {
  submission: SubmissionDetail | null = null;
  loading = true;
  error = false;
  reprinting = false;
  templateUnavailable = false;
  fieldEntries: { key: string; value: any; label: string }[] = [];

  private destroy$ = new Subject<void>();

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private historyService: HistoryService,
    private translate: TranslateService,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit(): void {
    const submissionId = this.route.snapshot.paramMap.get('submissionId');
    if (!submissionId) {
      this.error = true;
      this.loading = false;
      return;
    }

    this.historyService.getSubmission(submissionId).pipe(takeUntil(this.destroy$)).subscribe({
      next: (data) => {
        this.submission = data;
        this.buildFieldEntries(data);
        this.loading = false;
      },
      error: () => {
        this.error = true;
        this.loading = false;
      },
    });
  }

  buildFieldEntries(data: SubmissionDetail): void {
    this.fieldEntries = Object.entries(data.field_values || {}).map(([key, value]) => ({
      key,
      value,
      label: key,
    }));
  }

  onReprint(): void {
    if (!this.submission || this.reprinting || this.templateUnavailable) return;

    const msg = this.translate.instant('history.reprint_confirm');
    if (!confirm(msg)) return;

    this.reprinting = true;
    this.historyService.requestReprint(this.submission.id).pipe(takeUntil(this.destroy$)).subscribe({
      next: (blob) => {
        this.reprinting = false;
        const url = URL.createObjectURL(blob);
        const printWindow = window.open(url, '_blank');
        if (printWindow) {
          printWindow.onload = () => printWindow.print();
        }
        this.snackBar.open(this.translate.instant('history.reprint_success'), undefined, { duration: 3000 });
      },
      error: () => {
        this.reprinting = false;
        this.snackBar.open(this.translate.instant('errors.generic'), undefined, { duration: 3000 });
      },
    });
  }

  onClone(): void {
    if (!this.submission) return;
    this.router.navigate(['/desk/fill', this.submission.template_id], {
      queryParams: { clone: this.submission.id },
    });
  }

  onExport(format: 'json' | 'csv'): void {
    if (!this.submission) return;
    this.historyService.exportSubmission(this.submission.id, format).pipe(takeUntil(this.destroy$)).subscribe({
      next: (blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${this.submission!.reference_number}.${format}`;
        a.click();
        URL.revokeObjectURL(url);
      },
      error: () => {
        this.snackBar.open(this.translate.instant('errors.generic'), undefined, { duration: 3000 });
      },
    });
  }

  onBack(): void {
    this.router.navigate(['/desk/history']);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
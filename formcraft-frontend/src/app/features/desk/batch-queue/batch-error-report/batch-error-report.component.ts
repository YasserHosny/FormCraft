import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
  selector: 'app-batch-error-report',
  templateUrl: './batch-error-report.component.html',
  styleUrls: ['./batch-error-report.component.scss'],
})
export class BatchErrorReportComponent {
  constructor(@Inject(MAT_DIALOG_DATA) public data: { jobId: string }) {}
}

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule } from '@ngx-translate/core';
import { FormsModule } from '@angular/forms';
import { ReviewQueueService } from '../../../core/services/review-queue.service';
import { GovernanceMetrics } from '../../../shared/models/review.models';

@Component({
  selector: 'fc-governance-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    FormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatProgressSpinnerModule,
    MatButtonModule,
    MatIconModule,
    TranslateModule,
  ],
  templateUrl: './governance-dashboard.component.html',
  styleUrls: ['./governance-dashboard.component.scss'],
})
export class GovernanceDashboardComponent implements OnInit {
  metrics: GovernanceMetrics | null = null;
  loading = true;
  sinceDate = new Date(new Date().setDate(new Date().getDate() - 30));

  constructor(private reviewQueueService: ReviewQueueService) {}

  ngOnInit(): void {
    this.loadMetrics();
  }

  loadMetrics(): void {
    this.loading = true;
    const since = this.sinceDate.toISOString().split('T')[0];
    this.reviewQueueService.getMetrics(since).subscribe({
      next: (response: GovernanceMetrics) => {
        this.metrics = response;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      },
    });
  }

  onDateChange(): void {
    this.loadMetrics();
  }
}

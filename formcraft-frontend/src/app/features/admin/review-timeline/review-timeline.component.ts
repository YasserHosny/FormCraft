import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { TranslateModule } from '@ngx-translate/core';
import { ActivatedRoute } from '@angular/router';
import { ReviewQueueService } from '../../../core/services/review-queue.service';
import { TimelineResponse, TimelineEvent } from '../../../shared/models/review.models';

@Component({
  selector: 'fc-review-timeline',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatProgressSpinnerModule,
    TranslateModule,
  ],
  templateUrl: './review-timeline.component.html',
  styleUrls: ['./review-timeline.component.scss'],
})
export class ReviewTimelineComponent implements OnInit {
  templateId = '';
  timeline: TimelineResponse | null = null;
  loading = true;

  constructor(
    private route: ActivatedRoute,
    private reviewQueueService: ReviewQueueService,
  ) {}

  ngOnInit(): void {
    this.templateId = this.route.snapshot.paramMap.get('template_id') || '';
    this.loadTimeline();
  }

  loadTimeline(): void {
    if (!this.templateId) return;
    this.loading = true;
    this.reviewQueueService.getTimeline(this.templateId).subscribe({
      next: (response: TimelineResponse) => {
        this.timeline = response;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      },
    });
  }

  getEventIcon(event: string): string {
    switch (event) {
      case 'submitted_for_review': return 'send';
      case 'approved': return 'check_circle';
      case 'rejected': return 'cancel';
      case 'published': return 'cloud_upload';
      case 'withdrawn': return 'undo';
      default: return 'event';
    }
  }

  getEventColor(event: string): string {
    switch (event) {
      case 'submitted_for_review': return 'primary';
      case 'approved': return 'accent';
      case 'rejected': return 'warn';
      case 'published': return 'primary';
      case 'withdrawn': return '';
      default: return '';
    }
  }
}

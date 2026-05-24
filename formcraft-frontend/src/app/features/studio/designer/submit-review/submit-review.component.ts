import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatCardModule } from '@angular/material/card';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-submit-review',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatCardModule,
    TranslateModule,
  ],
  templateUrl: './submit-review.component.html',
  styleUrls: ['./submit-review.component.scss'],
})
export class SubmitReviewComponent {
  @Input() template: any = null;
  @Input() currentUserId = '';
  @Input() approvalWorkflowEnabled = true;
  @Input() isReviewer = false;
  @Input() rejectionComment: string | null = null;
  @Input() rejectionReviewer: string | null = null;
  @Input() rejectionTimestamp: string | null = null;

  @Output() submitForReview = new EventEmitter<void>();
  @Output() publish = new EventEmitter<void>();
  @Output() withdraw = new EventEmitter<void>();
  @Output() approve = new EventEmitter<string | undefined>();
  @Output() reject = new EventEmitter<string>();

  get status(): string {
    return this.template?.status || 'draft';
  }

  get isCreator(): boolean {
    return this.template?.created_by === this.currentUserId;
  }

  get isReadOnly(): boolean {
    return ['submitted_for_review', 'approved'].includes(this.status);
  }

  get showSubmitButton(): boolean {
    return this.status === 'draft' && this.approvalWorkflowEnabled && this.isCreator;
  }

  get showPublishButton(): boolean {
    return this.status === 'draft' && !this.approvalWorkflowEnabled && this.isCreator;
  }

  get showWithdrawButton(): boolean {
    return this.status === 'submitted_for_review' && this.isCreator;
  }

  get showApproveReject(): boolean {
    return this.status === 'submitted_for_review' && this.isReviewer;
  }

  get showPublishApproved(): boolean {
    return this.status === 'approved' && this.isReviewer;
  }

  onApprove(): void {
    this.approve.emit();
  }

  onReject(): void {
    const comment = prompt('Enter rejection comment:');
    if (comment) {
      this.reject.emit(comment);
    }
  }

  getStatusColor(): string {
    switch (this.status) {
      case 'draft': return '';
      case 'submitted_for_review': return 'primary';
      case 'approved': return 'accent';
      case 'rejected': return 'warn';
      case 'published': return 'primary';
      default: return '';
    }
  }

  getStatusLabel(): string {
    switch (this.status) {
      case 'draft': return 'Draft';
      case 'submitted_for_review': return 'Submitted for Review';
      case 'approved': return 'Approved';
      case 'rejected': return 'Rejected';
      case 'published': return 'Published';
      default: return this.status;
    }
  }
}

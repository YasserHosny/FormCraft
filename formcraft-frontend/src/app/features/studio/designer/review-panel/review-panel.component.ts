import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { TranslateModule } from '@ngx-translate/core';
import { FormsModule } from '@angular/forms';
import { ElementComment } from '../../../shared/models/review.models';

@Component({
  selector: 'app-review-panel',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatIconModule,
    MatInputModule,
    MatFormFieldModule,
    MatCardModule,
    MatChipsModule,
    TranslateModule,
  ],
  templateUrl: './review-panel.component.html',
  styleUrls: ['./review-panel.component.scss'],
})
export class ReviewPanelComponent {
  @Input() elements: any[] = [];
  @Input() selectedElementKey: string | null = null;
  @Input() isActive = false;

  @Output() approve = new EventEmitter<{ comment: string; elementComments: ElementComment[] }>();
  @Output() reject = new EventEmitter<{ comment: string; elementComments: ElementComment[] }>();

  overallComment = '';
  elementComments: ElementComment[] = [];
  activeComment = '';

  onElementClick(element: any): void {
    if (!this.isActive) return;
    this.selectedElementKey = element.key;
    const existing = this.elementComments.find(c => c.element_key === element.key);
    this.activeComment = existing ? existing.comment : '';
  }

  saveElementComment(): void {
    if (!this.selectedElementKey || !this.activeComment.trim()) return;
    const existing = this.elementComments.findIndex(c => c.element_key === this.selectedElementKey);
    if (existing >= 0) {
      this.elementComments[existing].comment = this.activeComment;
    } else {
      this.elementComments.push({ element_key: this.selectedElementKey, comment: this.activeComment });
    }
    this.activeComment = '';
    this.selectedElementKey = null;
  }

  onApprove(): void {
    this.approve.emit({
      comment: this.overallComment,
      elementComments: this.elementComments,
    });
  }

  onReject(): void {
    if (!this.overallComment.trim()) {
      alert('Please provide a rejection comment');
      return;
    }
    this.reject.emit({
      comment: this.overallComment,
      elementComments: this.elementComments,
    });
  }

  getCommentCount(elementKey: string): number {
    return this.elementComments.filter(c => c.element_key === elementKey).length;
  }
}

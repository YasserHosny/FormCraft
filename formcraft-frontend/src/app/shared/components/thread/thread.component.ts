import {
  Component,
  Input,
  Output,
  EventEmitter,
  ChangeDetectionStrategy,
} from '@angular/core';
import { ReplyResponse } from '../../../features/feedback/models/reply.models';

@Component({
  selector: 'app-thread',
  templateUrl: './thread.component.html',
  styleUrls: ['./thread.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
  standalone: false,
})
export class ThreadComponent {
  @Input() replies: ReplyResponse[] = [];
  @Input() hasEarlier = false;
  @Input() loading = false;

  /** Emits the `id` of the oldest visible reply so the parent can fetch the prior page. */
  @Output() loadEarlier = new EventEmitter<string>();

  /** Emits the trimmed text content of a new reply the user wants to send. */
  @Output() sendReply = new EventEmitter<string>();

  replyText = '';

  get charCount(): number {
    return this.replyText.length;
  }

  get isReplyValid(): boolean {
    const trimmed = this.replyText.trim();
    return trimmed.length > 0 && trimmed.length <= 2000;
  }

  onLoadEarlier(): void {
    if (this.replies.length === 0) return;
    const oldest = this.replies[0];
    this.loadEarlier.emit(oldest.id);
  }

  onSend(): void {
    if (!this.isReplyValid) return;
    this.sendReply.emit(this.replyText.trim());
    this.replyText = '';
  }

  onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
      this.onSend();
    }
  }
}

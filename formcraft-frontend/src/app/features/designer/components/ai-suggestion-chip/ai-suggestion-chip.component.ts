import { Component, EventEmitter, Input, Output } from '@angular/core';
import { SuggestionResponse } from '../../services/ai-suggestion.service';

@Component({
  selector: 'fc-ai-suggestion-chip',
  standalone: false,
  templateUrl: './ai-suggestion-chip.component.html',
  styleUrls: ['./ai-suggestion-chip.component.scss'],
})
export class AiSuggestionChipComponent {
  @Input() suggestion: SuggestionResponse | null = null;
  @Output() accept = new EventEmitter<SuggestionResponse>();
  @Output() dismiss = new EventEmitter<void>();
}

import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export interface FeedbackFilterState {
  search: string;
  status: string;
  submitterId: string | null;
  dateFrom: string | null;
  dateTo: string | null;
  labelIds: string[];
}

const initialState: FeedbackFilterState = {
  search: '',
  status: 'all',
  submitterId: null,
  dateFrom: null,
  dateTo: null,
  labelIds: [],
};

@Injectable({ providedIn: 'root' })
export class FeedbackFilterStateService {
  private stateSubject = new BehaviorSubject<FeedbackFilterState>({ ...initialState });
  state$ = this.stateSubject.asObservable();

  get snapshot(): FeedbackFilterState {
    return this.stateSubject.value;
  }

  setFilter(partial: Partial<FeedbackFilterState>): void {
    this.stateSubject.next({ ...this.stateSubject.value, ...partial });
  }

  clearAll(): void {
    this.stateSubject.next({ ...initialState });
  }

  hasActiveFilters(): boolean {
    const s = this.stateSubject.value;
    return (
      s.search !== '' ||
      s.status !== 'all' ||
      s.submitterId !== null ||
      s.dateFrom !== null ||
      s.dateTo !== null ||
      s.labelIds.length > 0
    );
  }
}
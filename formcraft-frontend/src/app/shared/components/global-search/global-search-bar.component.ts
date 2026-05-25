import {
  Component,
  ElementRef,
  EventEmitter,
  OnDestroy,
  OnInit,
  Output,
  ViewChild,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Subject, Subscription } from 'rxjs';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { TranslateModule } from '@ngx-translate/core';
import { SearchService, SearchResult } from '../../../core/services/search.service';

@Component({
  selector: 'fc-global-search-bar',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatIconModule,
    MatInputModule,
    MatFormFieldModule,
    MatProgressSpinnerModule,
    TranslateModule,
  ],
  templateUrl: './global-search-bar.component.html',
  styleUrls: ['./global-search-bar.component.scss'],
})
export class GlobalSearchBarComponent implements OnInit, OnDestroy {
  @ViewChild('searchInput') searchInput!: ElementRef<HTMLInputElement>;
  @Output() resultSelected = new EventEmitter<SearchResult>();

  query = '';
  loading = false;
  results: SearchResult[] = [];
  showResults = false;
  selectedIndex = -1;
  recentSearches: string[] = [];

  private query$ = new Subject<string>();
  private sub = new Subscription();

  constructor(private searchService: SearchService, private router: Router) {}

  ngOnInit(): void {
    this.recentSearches = this.searchService.getRecentSearches();
    this.sub.add(
      this.searchService.createSearchObservable$(this.query$).subscribe((response) => {
        this.loading = false;
        this.results = response.results;
        this.showResults = this.results.length > 0 || this.query.length > 0;
        this.selectedIndex = -1;
      })
    );
  }

  ngOnDestroy(): void {
    this.sub.unsubscribe();
  }

  onInput(): void {
    if (!this.query || this.query.length < 2) {
      this.results = [];
      this.showResults = false;
      this.loading = false;
      return;
    }
    this.loading = true;
    this.query$.next(this.query);
  }

  onFocus(): void {
    if (this.results.length > 0 || this.recentSearches.length > 0) {
      this.showResults = true;
    }
  }

  onBlur(): void {
    setTimeout(() => {
      this.showResults = false;
    }, 200);
  }

  onKeydown(event: KeyboardEvent): void {
    if (!this.showResults) return;

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        this.selectedIndex = Math.min(this.selectedIndex + 1, this.results.length - 1);
        break;
      case 'ArrowUp':
        event.preventDefault();
        this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
        break;
      case 'Enter':
        event.preventDefault();
        if (this.selectedIndex >= 0 && this.results[this.selectedIndex]) {
          this.selectResult(this.results[this.selectedIndex]);
        }
        break;
      case 'Escape':
        this.showResults = false;
        this.selectedIndex = -1;
        break;
    }
  }

  selectResult(result: SearchResult): void {
    this.searchService.addRecentSearch(this.query);
    this.showResults = false;
    this.resultSelected.emit(result);

    if (result.type === 'submission') {
      this.router.navigate(['/desk', 'submissions', result.id]);
    } else if (result.type === 'template') {
      this.router.navigate(['/desk', 'fill', result.id]);
    } else if (result.type === 'customer') {
      this.router.navigate(['/desk', 'customers', result.id]);
    }
  }

  groupLabel(type: string): string {
    switch (type) {
      case 'template':
        return 'search.group_templates';
      case 'submission':
        return 'search.group_submissions';
      case 'customer':
        return 'search.group_customers';
      default:
        return type;
    }
  }

  resultsByType(type: string): SearchResult[] {
    return this.results.filter((r) => r.type === type);
  }

  globalIndex(result: SearchResult): number {
    return this.results.indexOf(result);
  }
}

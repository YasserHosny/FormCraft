import { Component, Input, Output, EventEmitter, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { MatAutocompleteModule, MatAutocompleteSelectedEvent } from '@angular/material/autocomplete';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { Subject, debounceTime, distinctUntilChanged, takeUntil } from 'rxjs';
import { TranslateModule } from '@ngx-translate/core';
import { ReferenceDataService } from '../../../../core/services/reference-data.service';

export interface DropdownItem {
  display: string;
  value: any;
  entry_id: string;
}

@Component({
  selector: 'fc-bound-dropdown',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatAutocompleteModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatIconModule,
    TranslateModule,
  ],
  template: `
    <div class="bound-dropdown" *ngIf="isSearchable; else selectMode">
      <mat-form-field appearance="outline" class="full-width">
        <mat-label>{{ label }}</mat-label>
        <input matInput
          [formControl]="searchControl"
          [matAutocomplete]="auto"
          [placeholder]="'binding.search_placeholder' | translate" />
        <mat-icon matSuffix *ngIf="loading">search</mat-icon>
        <mat-autocomplete #auto="matAutocomplete" (optionSelected)="onOptionSelected($event)">
          <mat-option *ngFor="let item of filteredItems" [value]="item.value">
            {{ item.display }}
          </mat-option>
        </mat-autocomplete>
        <mat-error *ngIf="required && !searchControl.value">{{ 'reference_data.entry.validation_error' | translate }}</mat-error>
      </mat-form-field>
    </div>

    <ng-template #selectMode>
      <mat-form-field appearance="outline" class="full-width">
        <mat-label>{{ label }}</mat-label>
        <mat-select [value]="selectedValue" (selectionChange)="onSelectChange($event)" [required]="required">
          <mat-option *ngFor="let item of items" [value]="item.value">
            {{ item.display }}
          </mat-option>
        </mat-select>
      </mat-form-field>
    </ng-template>

    <div *ngIf="noEntries" class="no-entries">
      {{ 'binding.no_entries_available' | translate }}
    </div>
  `,
  styles: [`
    .bound-dropdown { width: 100%; }
    .full-width { width: 100%; }
    .no-entries { font-size: 12px; color: #999; font-style: italic; margin-top: 4px; }
  `],
})
export class BoundDropdownComponent implements OnInit, OnDestroy {
  @Input() label = '';
  @Input() required = false;
  @Input() listId: string | null = null;
  @Input() displayColumn = '';
  @Input() valueColumn = '';
  @Input() searchThreshold = 20;
  @Input() selectedValue: any = null;
  @Output() valueChange = new EventEmitter<any>();
  @Output() entrySelected = new EventEmitter<{ entry_id: string; values: Record<string, any> }>();

  items: DropdownItem[] = [];
  filteredItems: DropdownItem[] = [];
  loading = false;
  isSearchable = false;
  noEntries = false;

  searchControl = new FormControl('');
  private destroy$ = new Subject<void>();

  constructor(private referenceDataService: ReferenceDataService) {}

  ngOnInit(): void {
    if (!this.listId || !this.displayColumn || !this.valueColumn) return;
    this.loadItems();

    this.searchControl.valueChanges.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      takeUntil(this.destroy$),
    ).subscribe((q: string | null) => {
      if (this.isSearchable && q) {
        this.searchItems(q);
      } else {
        this.filteredItems = [...this.items];
      }
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private loadItems(): void {
    this.loading = true;
    this.referenceDataService.getDropdownItems(this.listId!, this.displayColumn, this.valueColumn).subscribe({
      next: (data: any) => {
        this.items = data.items || data || [];
        this.filteredItems = [...this.items];
        this.noEntries = this.items.length === 0;
        this.isSearchable = this.items.length > this.searchThreshold;
        this.loading = false;
      },
      error: () => { this.loading = false; },
    });
  }

  private searchItems(q: string): void {
    this.loading = true;
    this.referenceDataService.getDropdownItems(this.listId!, this.displayColumn, this.valueColumn, q).subscribe({
      next: (data: any) => {
        this.filteredItems = data.items || data || [];
        this.loading = false;
      },
      error: () => { this.loading = false; },
    });
  }

  onOptionSelected(event: MatAutocompleteSelectedEvent): void {
    const value = event.option.value;
    const item = this.items.find(i => i.value === value);
    if (item) {
      this.valueChange.emit(value);
      this.fetchFullEntry(item.entry_id);
    }
  }

  onSelectChange(event: any): void {
    const value = event.value;
    this.valueChange.emit(value);
    const item = this.items.find(i => i.value === value);
    if (item) {
      this.fetchFullEntry(item.entry_id);
    }
  }

  private fetchFullEntry(entryId: string): void {
    if (!this.listId) return;
    this.referenceDataService.getEntry(this.listId, entryId).subscribe({
      next: (entry: any) => {
        this.entrySelected.emit({ entry_id: entry.id, values: entry.values || {} });
      },
    });
  }
}
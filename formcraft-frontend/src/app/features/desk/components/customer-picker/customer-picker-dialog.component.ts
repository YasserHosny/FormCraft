import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatListModule } from '@angular/material/list';
import { MatButtonModule } from '@angular/material/button';
import { TranslateModule } from '@ngx-translate/core';
import { debounceTime, distinctUntilChanged, switchMap } from 'rxjs/operators';
import { of } from 'rxjs';

import { CustomerService } from '../../services/customer.service';
import { Customer } from '../../customers/customer.models';

@Component({
  selector: 'fc-customer-picker-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    TranslateModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatListModule,
    MatButtonModule,
  ],
  template: `
    <h2 mat-dialog-title>{{ 'desk.customer_picker.title' | translate }}</h2>
    <mat-dialog-content>
      <mat-form-field appearance="outline" class="w-100">
        <input
          matInput
          [formControl]="searchControl"
          [placeholder]="'desk.customer_picker.search_placeholder' | translate"
        />
      </mat-form-field>

      <mat-nav-list *ngIf="results.length > 0; else emptyState">
        <a mat-list-item *ngFor="let customer of results" (click)="select(customer)">
          <div matListItemTitle>{{ customer.name_ar }}</div>
          <div matListItemLine>{{ customer.identifier }}</div>
        </a>
      </mat-nav-list>

      <ng-template #emptyState>
        <p>{{ 'desk.customer_picker.no_results' | translate }}</p>
      </ng-template>
    </mat-dialog-content>

    <mat-dialog-actions align="end">
      <button mat-button (click)="close()">{{ 'common.cancel' | translate }}</button>
    </mat-dialog-actions>
  `,
})
export class CustomerPickerDialogComponent implements OnInit {
  searchControl = new FormControl<string>('', { nonNullable: true });
  results: Customer[] = [];

  constructor(
    private dialogRef: MatDialogRef<CustomerPickerDialogComponent>,
    private customerService: CustomerService,
  ) {}

  ngOnInit(): void {
    this.searchControl.valueChanges.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      switchMap((query) => {
        const trimmed = query?.trim();
        if (!trimmed) {
          return of({ items: [] as Customer[] });
        }
        return this.customerService.search(trimmed);
      }),
    ).subscribe((response) => {
      this.results = response.items ?? [];
    });
  }

  select(customer: Customer): void {
    this.dialogRef.close(customer);
  }

  close(): void {
    this.dialogRef.close();
  }
}

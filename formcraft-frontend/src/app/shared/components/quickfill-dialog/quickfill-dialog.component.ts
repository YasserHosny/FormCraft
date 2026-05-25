import { Component, Inject, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subject, Subscription } from 'rxjs';
import { debounceTime, distinctUntilChanged, switchMap, catchError } from 'rxjs/operators';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { TranslateModule } from '@ngx-translate/core';
import {
  QuickFillService,
  QuickFillCustomer,
} from '../../../core/services/quickfill.service';

export interface QuickFillDialogData {
  templateId: string;
}

@Component({
  selector: 'fc-quickfill-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatIconModule,
    MatInputModule,
    MatFormFieldModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    TranslateModule,
  ],
  templateUrl: './quickfill-dialog.component.html',
  styleUrls: ['./quickfill-dialog.component.scss'],
})
export class QuickFillDialogComponent implements OnInit, OnDestroy {
  query = '';
  loading = false;
  customers: QuickFillCustomer[] = [];
  selectedCustomerId: string | null = null;

  private query$ = new Subject<string>();
  private sub = new Subscription();

  constructor(
    private quickFillService: QuickFillService,
    private dialogRef: MatDialogRef<QuickFillDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: QuickFillDialogData
  ) {}

  ngOnInit(): void {
    this.sub.add(
      this.query$.pipe(
        debounceTime(200),
        distinctUntilChanged(),
        switchMap((q) => {
          if (!q || q.length < 2) {
            this.customers = [];
            return [];
          }
          this.loading = true;
          return this.quickFillService.searchCustomers(q).pipe(
            catchError(() => {
              this.loading = false;
              return [];
            })
          );
        })
      ).subscribe((response: any) => {
        this.loading = false;
        this.customers = response?.customers || [];
      })
    );
  }

  ngOnDestroy(): void {
    this.sub.unsubscribe();
  }

  onInput(): void {
    this.query$.next(this.query);
  }

  selectCustomer(customer: QuickFillCustomer): void {
    this.selectedCustomerId = customer.id;
  }

  confirm(): void {
    if (!this.selectedCustomerId) return;
    this.dialogRef.close({
      customerId: this.selectedCustomerId,
      templateId: this.data.templateId,
    });
  }

  cancel(): void {
    this.dialogRef.close(null);
  }
}

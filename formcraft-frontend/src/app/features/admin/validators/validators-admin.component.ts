import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { AbstractControl, FormBuilder, FormGroup, ReactiveFormsModule, ValidationErrors, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { RouterModule } from '@angular/router';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import {
  CustomValidator,
  CustomValidatorService,
  ValidatorTemplateUsage,
} from '../../../core/services/custom-validator.service';

@Component({
  selector: 'fc-validators-admin',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatCardModule,
    MatChipsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatTableModule,
    RouterModule,
    TranslateModule,
  ],
  template: `
    <section class="validators-page">
      <header class="toolbar">
        <div>
          <h1>{{ 'admin.validators.title' | translate }}</h1>
          <p>{{ 'admin.validators.subtitle' | translate }}</p>
        </div>
        <button mat-raised-button color="primary" (click)="startCreate()">
          <mat-icon>add</mat-icon>
          {{ 'admin.validators.create' | translate }}
        </button>
      </header>

      <div class="content">
        <mat-card class="list-card">
          <div class="list-toolbar">
            <mat-form-field appearance="outline">
              <mat-label>{{ 'admin.validators.search' | translate }}</mat-label>
              <input matInput [value]="search" (input)="onSearch($event)" />
            </mat-form-field>
          </div>

          <div class="loading" *ngIf="loading">
            <mat-spinner diameter="32"></mat-spinner>
          </div>

          <table mat-table [dataSource]="validators" *ngIf="!loading">
            <ng-container matColumnDef="name">
              <th mat-header-cell *matHeaderCellDef>{{ 'admin.validators.name' | translate }}</th>
              <td mat-cell *matCellDef="let validator">
                <button mat-button color="primary" (click)="select(validator)">{{ validator.name }}</button>
              </td>
            </ng-container>

            <ng-container matColumnDef="description">
              <th mat-header-cell *matHeaderCellDef>{{ 'admin.validators.description' | translate }}</th>
              <td mat-cell *matCellDef="let validator">{{ validator.description || '-' }}</td>
            </ng-container>

            <ng-container matColumnDef="pattern">
              <th mat-header-cell *matHeaderCellDef>{{ 'admin.validators.pattern' | translate }}</th>
              <td mat-cell *matCellDef="let validator"><code>{{ validator.regex_pattern }}</code></td>
            </ng-container>

            <ng-container matColumnDef="created_by">
              <th mat-header-cell *matHeaderCellDef>{{ 'admin.validators.createdBy' | translate }}</th>
              <td mat-cell *matCellDef="let validator"><code>{{ validator.created_by || '-' }}</code></td>
            </ng-container>

            <ng-container matColumnDef="updated">
              <th mat-header-cell *matHeaderCellDef>{{ 'admin.validators.updated' | translate }}</th>
              <td mat-cell *matCellDef="let validator">{{ validator.updated_at | date:'short' }}</td>
            </ng-container>

            <ng-container matColumnDef="actions">
              <th mat-header-cell *matHeaderCellDef></th>
              <td mat-cell *matCellDef="let validator">
                <button mat-icon-button (click)="edit(validator)" [attr.aria-label]="'admin.validators.edit' | translate">
                  <mat-icon>edit</mat-icon>
                </button>
                <button mat-icon-button color="warn" (click)="remove(validator)" [attr.aria-label]="'admin.validators.delete' | translate">
                  <mat-icon>delete</mat-icon>
                </button>
              </td>
            </ng-container>

            <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
            <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
          </table>

          <p class="empty" *ngIf="!loading && validators.length === 0">
            {{ 'admin.validators.empty' | translate }}
          </p>
          <div class="pager" *ngIf="!loading && total > pageSize">
            <button mat-button (click)="previousPage()" [disabled]="page === 1">{{ 'common.previous' | translate }}</button>
            <span>{{ page }} / {{ totalPages }}</span>
            <button mat-button (click)="nextPage()" [disabled]="page >= totalPages">{{ 'common.next' | translate }}</button>
          </div>
        </mat-card>

        <mat-card class="detail-card" *ngIf="formVisible">
          <h2>{{ editing ? ('admin.validators.edit' | translate) : ('admin.validators.create' | translate) }}</h2>
          <form [formGroup]="form" (ngSubmit)="save()">
            <mat-form-field appearance="outline">
              <mat-label>{{ 'admin.validators.name' | translate }}</mat-label>
              <input matInput formControlName="name" />
            </mat-form-field>
            <mat-form-field appearance="outline">
              <mat-label>{{ 'admin.validators.description' | translate }}</mat-label>
              <textarea matInput rows="2" formControlName="description"></textarea>
            </mat-form-field>
            <mat-form-field appearance="outline">
              <mat-label>{{ 'admin.validators.pattern' | translate }}</mat-label>
              <input matInput formControlName="regex_pattern" />
            </mat-form-field>
            <div class="messages">
              <mat-form-field appearance="outline">
                <mat-label>{{ 'admin.validators.errorAr' | translate }}</mat-label>
                <textarea matInput rows="2" formControlName="error_message_ar" dir="rtl"></textarea>
              </mat-form-field>
              <mat-form-field appearance="outline">
                <mat-label>{{ 'admin.validators.errorEn' | translate }}</mat-label>
                <textarea matInput rows="2" formControlName="error_message_en"></textarea>
              </mat-form-field>
            </div>
            <p class="warning" *ngIf="editing">{{ 'admin.validators.updateWarning' | translate }}</p>
            <div class="actions">
              <button mat-raised-button color="primary" type="submit" [disabled]="form.invalid || saving">
                {{ 'common.save' | translate }}
              </button>
              <button mat-button type="button" (click)="cancel()">{{ 'common.cancel' | translate }}</button>
            </div>
          </form>
        </mat-card>

        <mat-card class="detail-card" *ngIf="selected && !formVisible">
          <h2>{{ selected.name }}</h2>
          <p>{{ selected.description || ('admin.validators.noDescription' | translate) }}</p>
          <code>{{ selected.regex_pattern }}</code>
          <h3>{{ 'admin.validators.usage' | translate }}</h3>
          <div class="loading" *ngIf="usageLoading">
            <mat-spinner diameter="28"></mat-spinner>
          </div>
          <div class="usage-list" *ngIf="!usageLoading">
            <div class="usage-row" *ngFor="let item of usage">
              <a [routerLink]="['/designer', item.template_id]">{{ item.template_name }}</a>
              <mat-chip>{{ item.template_status }}</mat-chip>
              <span>{{ item.last_submission_at ? (item.last_submission_at | date:'short') : '-' }}</span>
            </div>
            <p class="empty" *ngIf="usage.length === 0">{{ 'admin.validators.noUsage' | translate }}</p>
          </div>
        </mat-card>
      </div>
    </section>
  `,
  styles: [`
    .validators-page { padding: 24px; }
    .toolbar { display: flex; justify-content: space-between; align-items: center; gap: 16px; margin-bottom: 16px; }
    h1, h2, h3, p { margin: 0; }
    .toolbar p { color: rgba(0, 0, 0, 0.6); margin-top: 4px; }
    .content { display: grid; grid-template-columns: minmax(0, 2fr) minmax(320px, 1fr); gap: 16px; align-items: start; }
    .list-toolbar { display: flex; justify-content: flex-end; }
    .list-toolbar mat-form-field { width: min(360px, 100%); }
    table { width: 100%; }
    code { display: inline-block; max-width: 280px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .detail-card form, .messages { display: flex; flex-direction: column; gap: 12px; }
    .messages { display: grid; grid-template-columns: 1fr 1fr; }
    .actions { display: flex; gap: 8px; justify-content: flex-end; }
    .loading, .empty { display: flex; justify-content: center; padding: 24px; color: rgba(0, 0, 0, 0.6); }
    .pager { display: flex; justify-content: flex-end; align-items: center; gap: 12px; padding-top: 12px; }
    .warning { color: #9a6700; margin-bottom: 12px; }
    .usage-list { display: flex; flex-direction: column; gap: 8px; margin-top: 12px; }
    .usage-row { display: grid; grid-template-columns: 1fr auto auto; align-items: center; gap: 8px; }
    @media (max-width: 960px) { .content, .messages { grid-template-columns: 1fr; } }
  `],
})
export class ValidatorsAdminComponent implements OnInit {
  displayedColumns = ['name', 'description', 'pattern', 'created_by', 'updated', 'actions'];
  validators: CustomValidator[] = [];
  selected: CustomValidator | null = null;
  usage: ValidatorTemplateUsage[] = [];
  search = '';
  page = 1;
  pageSize = 20;
  total = 0;
  loading = false;
  usageLoading = false;
  saving = false;
  formVisible = false;
  editing: CustomValidator | null = null;
  form: FormGroup;

  constructor(
    private service: CustomValidatorService,
    private fb: FormBuilder,
    private snackBar: MatSnackBar,
    private translate: TranslateService,
  ) {
    this.form = this.fb.group({
      name: ['', Validators.required],
      description: [''],
      regex_pattern: ['', [Validators.required, this.regexValidator]],
      error_message_ar: ['', Validators.required],
      error_message_en: ['', Validators.required],
    });
  }

  ngOnInit(): void {
    this.load();
  }

  get totalPages(): number {
    return Math.max(1, Math.ceil(this.total / this.pageSize));
  }

  load(): void {
    this.loading = true;
    this.service.list({ page: this.page, page_size: this.pageSize, search: this.search }).subscribe({
      next: (response) => {
        this.validators = response.items;
        this.total = response.total;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.snackBar.open(this.translate.instant('errors.generic'), undefined, { duration: 3000 });
      },
    });
  }

  onSearch(event: Event): void {
    this.search = (event.target as HTMLInputElement).value;
    this.page = 1;
    this.load();
  }

  nextPage(): void {
    if (this.page >= this.totalPages) return;
    this.page += 1;
    this.load();
  }

  previousPage(): void {
    if (this.page === 1) return;
    this.page -= 1;
    this.load();
  }

  select(validator: CustomValidator): void {
    this.selected = validator;
    this.formVisible = false;
    this.usageLoading = true;
    this.service.usage(validator.id).subscribe({
      next: (response) => {
        this.usage = response.items;
        this.usageLoading = false;
      },
      error: () => {
        this.usage = [];
        this.usageLoading = false;
      },
    });
  }

  startCreate(): void {
    this.editing = null;
    this.form.reset();
    this.formVisible = true;
  }

  edit(validator: CustomValidator): void {
    this.editing = validator;
    this.form.reset({
      name: validator.name,
      description: validator.description || '',
      regex_pattern: validator.regex_pattern,
      error_message_ar: validator.error_message_ar,
      error_message_en: validator.error_message_en,
    });
    this.formVisible = true;
  }

  save(): void {
    if (this.form.invalid) return;
    this.saving = true;
    const payload = this.form.value;
    const request = this.editing
      ? this.service.update(this.editing.id, payload)
      : this.service.create(payload);
    request.subscribe({
      next: (validator) => {
        this.saving = false;
        this.formVisible = false;
        this.selected = validator;
        this.snackBar.open(this.translate.instant('admin.validators.saved'), undefined, { duration: 2500 });
        this.load();
      },
      error: (err) => {
        this.saving = false;
        this.snackBar.open(err.error?.detail?.message || this.translate.instant('errors.generic'), undefined, { duration: 4000 });
      },
    });
  }

  remove(validator: CustomValidator): void {
    this.service.usage(validator.id).subscribe({
      next: (usage) => this.confirmAndDelete(validator, usage.total),
      error: () => this.confirmAndDelete(validator, 0),
    });
  }

  private confirmAndDelete(validator: CustomValidator, usageCount: number): void {
    const ok = confirm(this.translate.instant('admin.validators.deleteConfirm', {
      name: validator.name,
      count: usageCount,
    }));
    if (!ok) return;
    this.service.delete(validator.id).subscribe({
      next: () => {
        if (this.selected?.id === validator.id) this.selected = null;
        this.snackBar.open(this.translate.instant('admin.validators.deleted'), undefined, { duration: 2500 });
        this.load();
      },
      error: () => this.snackBar.open(this.translate.instant('errors.generic'), undefined, { duration: 3000 }),
    });
  }

  private regexValidator(control: AbstractControl): ValidationErrors | null {
    const pattern = control.value;
    if (!pattern) return null;
    try {
      new RegExp(pattern);
      return null;
    } catch {
      return { regex: true };
    }
  }

  cancel(): void {
    this.formVisible = false;
  }
}

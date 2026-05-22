import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, FormControl } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { TranslateModule } from '@ngx-translate/core';
import { ReferenceDataService, ColumnSchema } from '../../../../core/services/reference-data.service';

export interface RefBinding {
  list_id: string | null;
  display_column: string;
  value_column: string;
  search_threshold: number;
  clear_on_deselect: boolean;
  auto_fill: { target_element_key: string; source_column: string }[];
}

@Component({
  selector: 'fc-ref-binding-panel',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatSlideToggleModule,
    MatIconModule,
    MatDividerModule,
    TranslateModule,
  ],
  template: `
    <div class="ref-binding-panel" [formGroup]="form">
      <h4>{{ 'binding.title' | translate }}</h4>

      <mat-form-field appearance="outline" class="full-width">
        <mat-label>{{ 'binding.select_list' | translate }}</mat-label>
        <mat-select formControlName="list_id" (selectionChange)="onListChange($event)">
          <mat-option [value]="null">--</mat-option>
          <mat-option *ngFor="let list of lists" [value]="list.id">{{ list.name_en }} / {{ list.name_ar }}</mat-option>
        </mat-select>
      </mat-form-field>

      <div *ngIf="selectedListId" class="binding-config">
        <mat-form-field appearance="outline" class="full-width">
          <mat-label>{{ 'binding.display_column' | translate }}</mat-label>
          <mat-select formControlName="display_column">
            <mat-option *ngFor="let col of listColumns" [value]="col.key">{{ col.label_en }} / {{ col.label_ar }}</mat-option>
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline" class="full-width">
          <mat-label>{{ 'binding.value_column' | translate }}</mat-label>
          <mat-select formControlName="value_column">
            <mat-option *ngFor="let col of listColumns" [value]="col.key">{{ col.label_en }} / {{ col.label_ar }}</mat-option>
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline" class="half-width">
          <mat-label>{{ 'binding.search_threshold' | translate }}</mat-label>
          <input matInput type="number" formControlName="search_threshold" min="0" />
        </mat-form-field>

        <mat-slide-toggle formControlName="clear_on_deselect">
          {{ 'binding.clear_on_deselect' | translate }}
        </mat-slide-toggle>

        <mat-divider style="margin: 12px 0;"></mat-divider>

        <h4>{{ 'binding.auto_fill' | translate }}</h4>

        <div *ngFor="let mapping of autoFillArray.controls; let i = index" class="auto-fill-row" [formGroupName]="i">
          <mat-form-field appearance="outline" class="half-width">
            <mat-label>{{ 'binding.target_element' | translate }}</mat-label>
            <mat-select formControlName="target_element_key">
              <mat-option *ngFor="let el of pageElements" [value]="el.key">{{ el.key }}</mat-option>
            </mat-select>
          </mat-form-field>
          <mat-form-field appearance="outline" class="half-width">
            <mat-label>{{ 'binding.source_column' | translate }}</mat-label>
            <mat-select formControlName="source_column">
              <mat-option *ngFor="let col of listColumns" [value]="col.key">{{ col.label_en }}</mat-option>
            </mat-select>
          </mat-form-field>
          <button mat-icon-button color="warn" (click)="removeAutoFill(i)">
            <mat-icon>delete</mat-icon>
          </button>
        </div>

        <button mat-stroked-button (click)="addAutoFill()">
          <mat-icon>add</mat-icon>
          {{ 'binding.add_mapping' | translate }}
        </button>
      </div>
    </div>
  `,
  styles: [`
    .ref-binding-panel { display: flex; flex-direction: column; gap: 8px; }
    .full-width { width: 100%; }
    .half-width { width: 48%; }
    .auto-fill-row { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; }
    h4 { margin: 8px 0 4px; }
  `],
})
export class RefBindingPanelComponent implements OnInit {
  @Input() element: any;
  @Input() pageElements: { key: string; type: string }[] = [];
  @Output() bindingChange = new EventEmitter<RefBinding | null>();

  lists: any[] = [];
  listColumns: ColumnSchema[] = [];
  selectedListId: string | null = null;

  form: FormGroup;
  autoFillArray: any;

  constructor(
    private fb: FormBuilder,
    private referenceDataService: ReferenceDataService,
  ) {
    this.form = this.fb.group({
      list_id: [null],
      display_column: [''],
      value_column: [''],
      search_threshold: [20],
      clear_on_deselect: [false],
      auto_fill: this.fb.array([]),
    });
    this.autoFillArray = this.form.get('auto_fill');
  }

  ngOnInit(): void {
    this.referenceDataService.listLists().subscribe({
      next: (data: any) => {
        this.lists = Array.isArray(data) ? data : (data?.items || []);
      },
    });

    if (this.element?.data?.formatting?.ref_binding) {
      const binding = this.element.data.formatting.ref_binding;
      this.selectedListId = binding.list_id;
      this.form.patchValue({
        list_id: binding.list_id,
        display_column: binding.display_column || '',
        value_column: binding.value_column || '',
        search_threshold: binding.search_threshold ?? 20,
        clear_on_deselect: binding.clear_on_deselect ?? false,
      });
      this.loadListColumns(binding.list_id);
      if (binding.auto_fill) {
        for (const m of binding.auto_fill) {
          this.addAutoFill(m);
        }
      }
    }

    this.form.valueChanges.subscribe(() => this.emitBinding());
  }

  onListChange(event: any): void {
    const listId = event.value;
    this.selectedListId = listId;
    this.loadListColumns(listId);
    if (listId) {
      this.form.patchValue({ display_column: '', value_column: '' });
    } else {
      this.listColumns = [];
    }
  }

  private loadListColumns(listId: string): void {
    if (!listId) { this.listColumns = []; return; }
    this.referenceDataService.getList(listId).subscribe({
      next: (list: any) => {
        this.listColumns = list.columns || list.schema || [];
        const uniqueCol = this.listColumns.find(c => c.unique_key);
        if (uniqueCol && !this.form.value.value_column) {
          this.form.patchValue({ value_column: uniqueCol.key });
        }
        const displayCol = this.listColumns.find(c => c.type === 'text');
        if (displayCol && !this.form.value.display_column) {
          this.form.patchValue({ display_column: displayCol.key });
        }
      },
    });
  }

  addAutoFill(mapping?: { target_element_key: string; source_column: string }): void {
    this.autoFillArray.push(this.fb.group({
      target_element_key: [mapping?.target_element_key || ''],
      source_column: [mapping?.source_column || ''],
    }));
  }

  removeAutoFill(index: number): void {
    this.autoFillArray.removeAt(index);
  }

  private emitBinding(): void {
    const val = this.form.value;
    if (!val.list_id) {
      this.bindingChange.emit(null);
      return;
    }
    this.bindingChange.emit({
      list_id: val.list_id,
      display_column: val.display_column,
      value_column: val.value_column,
      search_threshold: val.search_threshold,
      clear_on_deselect: val.clear_on_deselect,
      auto_fill: (val.auto_fill || []).filter((m: any) => m.target_element_key && m.source_column),
    });
  }
}
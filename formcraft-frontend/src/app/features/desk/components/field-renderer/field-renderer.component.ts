import { Component, Input, Optional, Output, EventEmitter } from '@angular/core';
import { FormControl, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatRadioModule } from '@angular/material/radio';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule } from '@ngx-translate/core';
import { TemplateElement } from '../../services/form-filler.service';
import { ValidationService } from '../../services/validation.service';
import { SignaturePadComponent } from '../signature-pad/signature-pad.component';
import { TableInputComponent } from '../table-input/table-input.component';
import { BoundDropdownComponent } from '../bound-dropdown/bound-dropdown.component';
import { SignaturePadComponent } from '../signature-pad/signature-pad.component';
import { TableInputComponent } from '../table-input/table-input.component';

@Component({
  selector: 'fc-field-renderer',
  standalone: true,
imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatRadioModule,
    MatCheckboxModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatIconModule,
    TranslateModule,
    SignaturePadComponent,
    TableInputComponent,
    BoundDropdownComponent,
  ],
  template: `
    <div class="field-renderer" [ngSwitch]="element?.type" [dir]="element?.direction || 'rtl'">
      <!-- Text -->
      <mat-form-field *ngSwitchCase="'text'" appearance="outline" class="field-full">
        <mat-label>{{ label }}</mat-label>
        <input matInput [formControl]="control" [required]="element?.required" />
        <mat-error *ngIf="control?.touched && control?.invalid">
          {{ getErrorMessage() }}
        </mat-error>
      </mat-form-field>

      <!-- Number -->
      <mat-form-field *ngSwitchCase="'number'" appearance="outline" class="field-full">
        <mat-label>{{ label }}</mat-label>
        <input matInput type="number" [formControl]="control" [required]="element?.required" />
        <mat-error *ngIf="control?.touched && control?.invalid">
          {{ getErrorMessage() }}
        </mat-error>
      </mat-form-field>

      <!-- Currency -->
      <mat-form-field *ngSwitchCase="'currency'" appearance="outline" class="field-full">
        <mat-label>{{ label }}</mat-label>
        <input matInput type="number" [formControl]="control" [required]="element?.required" />
        <span matTextSuffix>{{ element?.formatting?.currency || '' }}</span>
        <mat-error *ngIf="control?.touched && control?.invalid">
          {{ getErrorMessage() }}
        </mat-error>
      </mat-form-field>

      <!-- Date -->
      <mat-form-field *ngSwitchCase="'date'" appearance="outline" class="field-full">
        <mat-label>{{ label }}</mat-label>
        <input matInput [matDatepicker]="picker" [formControl]="control" [required]="element?.required" />
        <mat-datepicker-toggle matSuffix [for]="picker"></mat-datepicker-toggle>
        <mat-datepicker #picker></mat-datepicker>
        <mat-error *ngIf="control?.touched && control?.invalid">
          {{ getErrorMessage() }}
        </mat-error>
      </mat-form-field>

      <!-- Dropdown (bound to reference list) -->
      <fc-bound-dropdown *ngSwitchCase="'dropdown'"
        *ngIf="hasRefBinding()"
        [label]="label"
        [required]="element?.required ?? false"
        [listId]="getRefBinding()?.list_id"
        [displayColumn]="getRefBinding()?.display_column || ''"
        [valueColumn]="getRefBinding()?.value_column || ''"
        [searchThreshold]="getRefBinding()?.search_threshold ?? 20"
        [selectedValue]="control.value"
        (valueChange)="onDropdownValueChange($event)"
        (entrySelected)="onEntrySelected($event)">
      </fc-bound-dropdown>

      <!-- Dropdown (unbound) -->
      <mat-form-field *ngSwitchCase="'dropdown'" *ngIf="!hasRefBinding()" appearance="outline" class="field-full">
        <mat-label>{{ label }}</mat-label>
        <mat-select [formControl]="control" [required]="element?.required">
          <mat-option *ngFor="let opt of options" [value]="opt">{{ opt }}</mat-option>
        </mat-select>
        <mat-error *ngIf="control?.touched && control?.invalid">
          {{ getErrorMessage() }}
        </mat-error>
      </mat-form-field>

      <!-- Radio -->
      <div *ngSwitchCase="'radio'" class="field-radio-group">
        <label class="field-label">{{ label }}</label>
        <mat-radio-group [formControl]="control" [required]="element?.required">
          <mat-radio-button *ngFor="let opt of options" [value]="opt">{{ opt }}</mat-radio-button>
        </mat-radio-group>
        <mat-error *ngIf="control?.touched && control?.invalid" class="field-error">
          {{ getErrorMessage() }}
        </mat-error>
      </div>

      <!-- Checkbox -->
      <div *ngSwitchCase="'checkbox'" class="field-checkbox">
        <mat-checkbox [formControl]="control">{{ label }}</mat-checkbox>
      </div>

      <!-- Tafqeet (read-only) -->
      <mat-form-field *ngSwitchCase="'tafqeet'" appearance="outline" class="field-full field-tafqeet">
        <mat-label>{{ label }}</mat-label>
        <input matInput [formControl]="control" readonly class="tafqeet-value" />
        <mat-icon matSuffix>spellcheck</mat-icon>
      </mat-form-field>

      <!-- Image (file upload) -->
      <div *ngSwitchCase="'image'" class="field-image">
        <label class="field-label">{{ label }}</label>
        <input type="file" accept="image/*" (change)="onImageUpload($event)" class="field-file-input" />
      </div>

      <!-- QR / Barcode (read-only auto-generated) -->
      <mat-form-field *ngSwitchCase="'qr'" appearance="outline" class="field-full field-readonly">
        <mat-label>{{ label }}</mat-label>
        <input matInput [formControl]="control" readonly />
        <mat-icon matSuffix>qr_code</mat-icon>
      </mat-form-field>

      <mat-form-field *ngSwitchCase="'barcode'" appearance="outline" class="field-full field-readonly">
        <mat-label>{{ label }}</mat-label>
        <input matInput [formControl]="control" readonly />
        <mat-icon matSuffix>view_week</mat-icon>
      </mat-form-field>

      <!-- Signature -->
      <fc-signature-pad *ngSwitchCase="'signature'"
        [label]="label"
        [penColor]="element?.formatting?.pen_color || '#000000'"
        [required]="element?.required || false"
        (valueChange)="onSignatureChange($event)">
      </fc-signature-pad>

      <!-- Table -->
      <fc-table-input *ngSwitchCase="'table'"
        [element]="element"
        [label]="label"
        (valueChange)="onTableChange($event)">
      </fc-table-input>

      <!-- Default fallback -->
      <mat-form-field *ngSwitchDefault appearance="outline" class="field-full">
        <mat-label>{{ label }}</mat-label>
        <input matInput [formControl]="control" [required]="element?.required" />
      </mat-form-field>
    </div>
  `,
  styles: [`
    .field-renderer {
      margin-bottom: 16px;
    }
    .field-full {
      width: 100%;
    }
    .field-label {
      display: block;
      font-size: 14px;
      margin-bottom: 8px;
      color: rgba(0, 0, 0, 0.87);
    }
    .field-radio-group {
      margin-bottom: 16px;
    }
    .field-radio-group mat-radio-button {
      display: block;
      margin-bottom: 4px;
    }
    .field-checkbox {
      margin-bottom: 16px;
    }
    .field-tafqeet .tafqeet-value {
      font-style: italic;
      background: rgba(0, 0, 0, 0.03);
    }
    .field-readonly {
      opacity: 0.8;
    }
    .field-error {
      font-size: 12px;
      color: #f44336;
    }
    .field-image {
      margin-bottom: 16px;
    }
    .field-file-input {
      display: block;
      margin-top: 4px;
    }
    :host-context([dir='rtl']) .field-label {
      text-align: right;
    }
  `],
})
export class FieldRendererComponent {
  @Input() element: TemplateElement | null = null;
  @Input() control: FormControl = new FormControl('');
  @Input() label = '';
  @Input() country = '';
  @Output() entrySelected = new EventEmitter<{ entry_id: string; values: Record<string, any>; elementKey: string }>();

  constructor(private validationService: ValidationService) {}

  hasRefBinding(): boolean {
    const formatting = this.element?.formatting as Record<string, unknown> | undefined;
    return !!(formatting && formatting['ref_binding']);
  }

  getRefBinding(): Record<string, any> | null {
    const formatting = this.element?.formatting as Record<string, unknown> | undefined;
    if (!formatting || !formatting['ref_binding']) return null;
    return formatting['ref_binding'] as Record<string, any>;
  }

  onDropdownValueChange(value: any): void {
    this.control.setValue(value);
    this.control.markAsTouched();
  }

  onEntrySelected(event: { entry_id: string; values: Record<string, any> }): void {
    this.entrySelected.emit({ ...event, elementKey: this.element?.key || '' });
  }

  get options(): string[] {
    if (!this.element?.formatting?.options) return [];
    if (Array.isArray(this.element.formatting.options)) {
      return this.element.formatting.options;
    }
    return [];
  }

  getTableColumns(): { key: string; label: string; type: string; sum_column: boolean }[] {
    const fmt = this.element?.formatting as Record<string, unknown> | undefined;
    if (!fmt || !Array.isArray(fmt['columns'])) return [];
    return (fmt['columns'] as any[]).map((c: any) => ({
      key: c.key || '',
      label: c.label_ar || c.label_en || c.key || '',
      type: c.type || 'text',
      sum_column: !!c.sum_column,
    }));
  }

  getErrorMessage(): string {
    if (!this.control || !this.control.errors) return '';
    return this.validationService.getErrorMessage(this.control, this.country);
  }

  onImageUpload(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      const reader = new FileReader();
      reader.onload = () => {
        this.control.setValue(reader.result as string);
      };
      reader.readAsDataURL(input.files[0]);
    }
  }

  onSignatureChange(dataUrl: string): void {
    if (!dataUrl) {
      this.control.setValue('');
      this.control.markAsTouched();
      return;
    }
    // Always store the dataUrl directly. Large signatures are resolved
    // after submission via resolveSignatureUploads which detects large base64 strings.
    this.control.setValue(dataUrl);
    this.control.markAsTouched();
  }

  onTableChange(rows: any[]): void {
    this.control.setValue(rows);
    this.control.markAsTouched();
  }
}
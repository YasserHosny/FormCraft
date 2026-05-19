import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'fc-signature-property-panel',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSlideToggleModule,
    TranslateModule,
  ],
  template: `
    <div class="signature-props" [formGroup]="form">
      <mat-form-field appearance="outline" class="full-width">
        <mat-label>{{ 'designer.properties.label_ar' | translate }}</mat-label>
        <input matInput formControlName="label_ar" />
      </mat-form-field>

      <mat-form-field appearance="outline" class="full-width">
        <mat-label>{{ 'designer.properties.label_en' | translate }}</mat-label>
        <input matInput formControlName="label_en" />
      </mat-form-field>

      <mat-slide-toggle formControlName="required">
        {{ 'designer.properties.required' | translate }}
      </mat-slide-toggle>

      <div class="prop-row">
        <mat-form-field appearance="outline">
          <mat-label>W (mm)</mat-label>
          <input matInput type="number" formControlName="width_mm" />
        </mat-form-field>
        <mat-form-field appearance="outline">
          <mat-label>H (mm)</mat-label>
          <input matInput type="number" formControlName="height_mm" />
        </mat-form-field>
      </div>

      <mat-form-field appearance="outline" class="full-width">
        <mat-label>{{ 'signature.penColor' | translate }}</mat-label>
        <input matInput type="text" formControlName="pen_color" placeholder="#000000" />
      </mat-form-field>
    </div>
  `,
  styles: [`
    .signature-props { display: flex; flex-direction: column; gap: 8px; }
    .full-width { width: 100%; }
    .prop-row { display: flex; gap: 8px; }
    .prop-row mat-form-field { flex: 1; }
  `],
})
export class SignaturePropertyPanelComponent {
  @Input() set element(el: any) {
    if (!el) return;
    this.form.patchValue({
      label_ar: el.data?.label_ar || el.label_ar || '',
      label_en: el.data?.label_en || el.label_en || '',
      required: el.data?.required ?? el.required ?? false,
      width_mm: el.data?.width_mm ?? el.width_mm ?? 60,
      height_mm: el.data?.height_mm ?? el.height_mm ?? 25,
      pen_color: el.data?.pen_color ?? '#000000',
    });
  }
  @Output() propertyChange = new EventEmitter<any>();

  form: FormGroup;

  constructor(private fb: FormBuilder) {
    this.form = this.fb.group({
      label_ar: [''],
      label_en: [''],
      required: [false],
      width_mm: [60],
      height_mm: [25],
      pen_color: ['#000000'],
    });

    this.form.valueChanges.subscribe((vals) => {
      this.propertyChange.emit(vals);
    });
  }
}
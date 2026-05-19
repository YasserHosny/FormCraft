import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup, FormBuilder } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatMenuModule } from '@angular/material/menu';
import { TranslateModule } from '@ngx-translate/core';
import { ConditionBuilderComponent, ConditionObject } from '../condition-builder/condition-builder.component';
import { ExpressionEditorComponent } from '../expression-editor/expression-editor.component';

export interface AdvancedProperties {
  visible_when: ConditionObject | null;
  required_when: ConditionObject | null;
  computed_value: string | null;
  default_value: string | null;
  placeholder_text: { ar: string; en: string } | null;
}

@Component({
  selector: 'fc-advanced-properties',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatExpansionModule,
    MatMenuModule,
    TranslateModule,
    ConditionBuilderComponent,
    ExpressionEditorComponent,
  ],
  template: `
    <mat-accordion>
      <!-- Visibility Condition -->
      <mat-expansion-panel>
        <mat-expansion-panel-header>
          <mat-panel-title>{{ 'conditions.visible_when' | translate }}</mat-panel-title>
          <mat-panel-description *ngIf="visibleWhen">
            {{ visibleWhen.conditions.length }} {{ 'conditions.title' | translate | lowercase }}
          </mat-panel-description>
        </mat-expansion-panel-header>
        <fc-condition-builder
          [title]="'conditions.visible_when'"
          [availableFields]="availableFields"
          [value]="visibleWhen"
          (valueChange)="onVisibleWhenChange($event)">
        </fc-condition-builder>
      </mat-expansion-panel>

      <!-- Required Condition -->
      <mat-expansion-panel>
        <mat-expansion-panel-header>
          <mat-panel-title>{{ 'conditions.required_when' | translate }}</mat-panel-title>
          <mat-panel-description *ngIf="requiredWhen">
            {{ requiredWhen.conditions.length }} {{ 'conditions.title' | translate | lowercase }}
          </mat-panel-description>
        </mat-expansion-panel-header>
        <fc-condition-builder
          [title]="'conditions.required_when'"
          [availableFields]="availableFields"
          [value]="requiredWhen"
          (valueChange)="onRequiredWhenChange($event)">
        </fc-condition-builder>
      </mat-expansion-panel>

      <!-- Computed Value -->
      <mat-expansion-panel>
        <mat-expansion-panel-header>
          <mat-panel-title>{{ 'computed.title' | translate }}</mat-panel-title>
          <mat-panel-description *ngIf="computedValue">{{ computedValue }}</mat-panel-description>
        </mat-expansion-panel-header>
        <fc-expression-editor
          [availableFields]="numericFields"
          [value]="computedValue"
          (valueChange)="onComputedValueChange($event)">
        </fc-expression-editor>
      </mat-expansion-panel>

      <!-- Default Value -->
      <mat-expansion-panel>
        <mat-expansion-panel-header>
          <mat-panel-title>{{ 'defaults.title' | translate }}</mat-panel-title>
        </mat-expansion-panel-header>
        <div class="default-value-section">
          <mat-form-field appearance="outline" class="full-width">
            <mat-label>{{ 'defaults.value' | translate }}</mat-label>
            <input matInput [value]="defaultValue || ''" (input)="onDefaultValueInput($event)" />
          </mat-form-field>
          <div class="token-chips">
            <span class="token-chip" *ngFor="let token of tokens" (click)="insertToken(token.key)">
              {{ token.key }} — {{ 'defaults.tokens.' + token.id | translate }}
            </span>
          </div>
        </div>
      </mat-expansion-panel>

      <!-- Placeholder -->
      <mat-expansion-panel>
        <mat-expansion-panel-header>
          <mat-panel-title>{{ 'placeholders.title' | translate }}</mat-panel-title>
        </mat-expansion-panel-header>
        <div class="placeholder-section">
          <mat-form-field appearance="outline" class="full-width">
            <mat-label>{{ 'placeholders.ar' | translate }}</mat-label>
            <input matInput [value]="placeholderText?.ar || ''" (input)="onPlaceholderChange('ar', $event)" dir="rtl" />
          </mat-form-field>
          <mat-form-field appearance="outline" class="full-width">
            <mat-label>{{ 'placeholders.en' | translate }}</mat-label>
            <input matInput [value]="placeholderText?.en || ''" (input)="onPlaceholderChange('en', $event)" />
          </mat-form-field>
        </div>
      </mat-expansion-panel>
    </mat-accordion>
  `,
  styles: [`
    mat-accordion { display: block; }
    .full-width { width: 100%; }
    .token-chips { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 8px; }
    .token-chip {
      font-size: 11px; background: #f3e5f5; color: #7b1fa2;
      padding: 2px 8px; border-radius: 12px; cursor: pointer;
    }
    .token-chip:hover { background: #e1bee7; }
    .default-value-section, .placeholder-section { display: flex; flex-direction: column; gap: 8px; }
  `],
})
export class AdvancedPropertiesComponent {
  @Input() availableFields: { key: string; label: string }[] = [];
  @Input() numericFields: { key: string; label: string }[] = [];
  @Input() visibleWhen: ConditionObject | null = null;
  @Input() requiredWhen: ConditionObject | null = null;
  @Input() computedValue: string | null = null;
  @Input() defaultValue: string | null = null;
  @Input() placeholderText: { ar: string; en: string } | null = null;
  @Output() propertiesChange = new EventEmitter<AdvancedProperties>();

  tokens = [
    { key: '{{today}}', id: 'today' },
    { key: '{{now}}', id: 'now' },
    { key: '{{user_name}}', id: 'user_name' },
    { key: '{{user_email}}', id: 'user_email' },
    { key: '{{org_name}}', id: 'org_name' },
  ];

  onVisibleWhenChange(val: ConditionObject | null): void {
    this.visibleWhen = val;
    this.emit();
  }

  onRequiredWhenChange(val: ConditionObject | null): void {
    this.requiredWhen = val;
    this.emit();
  }

  onComputedValueChange(val: string | null): void {
    this.computedValue = val;
    this.emit();
  }

  onDefaultValueInput(event: Event): void {
    this.defaultValue = (event.target as HTMLInputElement).value || null;
    this.emit();
  }

  insertToken(token: string): void {
    this.defaultValue = token;
    this.emit();
  }

  onPlaceholderChange(lang: 'ar' | 'en', event: Event): void {
    const val = (event.target as HTMLInputElement).value;
    if (!this.placeholderText) {
      this.placeholderText = { ar: '', en: '' };
    }
    this.placeholderText[lang] = val;
    this.emit();
  }

  private emit(): void {
    this.propertiesChange.emit({
      visible_when: this.visibleWhen,
      required_when: this.requiredWhen,
      computed_value: this.computedValue,
      default_value: this.defaultValue,
      placeholder_text: this.placeholderText?.ar || this.placeholderText?.en ? this.placeholderText : null,
    });
  }
}

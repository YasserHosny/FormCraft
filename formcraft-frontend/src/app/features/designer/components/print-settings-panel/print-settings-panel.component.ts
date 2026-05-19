import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { TranslateModule } from '@ngx-translate/core';
import { PrintSettingsService } from '../../../../core/services/print-settings.service';

@Component({
  selector: 'app-print-settings-panel',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatSelectModule,
    MatCheckboxModule,
    MatButtonModule,
    MatIconModule,
    MatSnackBarModule,
    TranslateModule,
  ],
  template: `
    <div class="panel">
      <h3>{{ 'print_settings.title' | translate }}</h3>

      <mat-form-field appearance="outline" class="full-width">
        <mat-label>{{ 'print_settings.mode' | translate }}</mat-label>
        <mat-select [(ngModel)]="printMode" (ngModelChange)="save()">
          <mat-option value="full">{{ 'print_settings.mode_full' | translate }}</mat-option>
          <mat-option value="overlay">{{ 'print_settings.mode_overlay' | translate }}</mat-option>
          <mat-option value="both">{{ 'print_settings.mode_both' | translate }}</mat-option>
        </mat-select>
      </mat-form-field>

      <div class="hint" *ngIf="printMode === 'overlay'">
        {{ 'print_settings.overlay_hint' | translate }}
      </div>
      <div class="hint" *ngIf="printMode === 'both'">
        {{ 'print_settings.both_hint' | translate }}
      </div>
    </div>
  `,
  styles: [`
    .panel { padding: 16px; }
    .full-width { width: 100%; }
    .hint { font-size: 12px; color: #666; margin-top: -8px; margin-bottom: 12px; }
  `],
})
export class PrintSettingsPanelComponent implements OnInit {
  @Input() templateId!: string;

  printMode = 'full';

  constructor(
    private service: PrintSettingsService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.service.get(this.templateId).subscribe((settings) => {
      this.printMode = settings.print_mode || 'full';
    });
  }

  save(): void {
    this.service.update(this.templateId, this.printMode).subscribe(() => {
      this.snackBar.open('Print settings saved', 'OK', { duration: 2000 });
    });
  }
}

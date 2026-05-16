import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';

export interface VersionWarningData {
  oldVersion: number;
  newVersion: number;
}

@Component({
  selector: 'fc-version-warning-dialog',
  standalone: true,
  imports: [
    CommonModule,
    TranslateModule,
    MatDialogModule,
    MatButtonModule,
    MatIconModule,
  ],
  template: `
    <h2 mat-dialog-title>
      <mat-icon class="warning-icon">update</mat-icon>
      {{ 'filler.version_warning_title' | translate }}
    </h2>
    <mat-dialog-content>
      <p>{{ 'filler.version_warning_message' | translate:{new: data.newVersion, old: data.oldVersion} }}</p>
    </mat-dialog-content>
    <mat-dialog-actions align="end">
      <button mat-stroked-button (click)="onContinue()">
        {{ 'filler.version_continue' | translate }}
      </button>
      <button mat-raised-button color="primary" (click)="onStartFresh()">
        {{ 'filler.version_start_fresh' | translate }}
      </button>
    </mat-dialog-actions>
  `,
  styles: [`
    h2[mat-dialog-title] {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .warning-icon {
      color: #ff9800;
    }
    mat-dialog-content p {
      line-height: 1.6;
    }
    mat-dialog-actions {
      padding: 8px 0;
    }
    :host-context([dir='rtl']) mat-dialog-actions {
      flex-direction: row-reverse;
    }
  `],
})
export class VersionWarningComponent {
  constructor(
    public dialogRef: MatDialogRef<VersionWarningComponent>,
    @Inject(MAT_DIALOG_DATA) public data: VersionWarningData,
  ) {}

  onContinue(): void {
    this.dialogRef.close('continue');
  }

  onStartFresh(): void {
    this.dialogRef.close('start_fresh');
  }
}
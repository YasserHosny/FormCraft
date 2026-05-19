import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatChipsModule } from '@angular/material/chips';
import { MatTooltipModule } from '@angular/material/tooltip';
import { TranslateModule } from '@ngx-translate/core';
import {
  PrinterProfile,
  PrinterProfileService,
} from '../../../core/services/printer-profile.service';
import { PrinterProfileDialogComponent } from './printer-profile-dialog.component';

@Component({
  selector: 'app-printer-profiles',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatDialogModule,
    MatSnackBarModule,
    MatChipsModule,
    MatTooltipModule,
    TranslateModule,
  ],
  template: `
    <div class="container">
      <div class="header">
        <h2>{{ 'printer_profiles.title' | translate }}</h2>
        <button mat-raised-button color="primary" (click)="openDialog()">
          <mat-icon>add</mat-icon>
          {{ 'printer_profiles.add' | translate }}
        </button>
      </div>

      <table mat-table [dataSource]="profiles" class="mat-elevation-z2 full-width">
        <ng-container matColumnDef="name">
          <th mat-header-cell *matHeaderCellDef>{{ 'printer_profiles.name' | translate }}</th>
          <td mat-cell *matCellDef="let p">
            {{ p.name }}
            <mat-chip *ngIf="p.is_default" color="primary" selected>
              {{ 'printer_profiles.default' | translate }}
            </mat-chip>
          </td>
        </ng-container>

        <ng-container matColumnDef="offsets">
          <th mat-header-cell *matHeaderCellDef>{{ 'printer_profiles.offsets' | translate }}</th>
          <td mat-cell *matCellDef="let p">
            X: {{ p.x_offset_mm }}mm, Y: {{ p.y_offset_mm }}mm
          </td>
        </ng-container>

        <ng-container matColumnDef="actions">
          <th mat-header-cell *matHeaderCellDef></th>
          <td mat-cell *matCellDef="let p">
            <button mat-icon-button (click)="openDialog(p)" matTooltip="Edit">
              <mat-icon>edit</mat-icon>
            </button>
            <button mat-icon-button (click)="setDefault(p)" *ngIf="!p.is_default"
                    [matTooltip]="'printer_profiles.set_default' | translate">
              <mat-icon>star_outline</mat-icon>
            </button>
            <button mat-icon-button (click)="downloadCalibration(p)"
                    [matTooltip]="'printer_profiles.calibration' | translate">
              <mat-icon>print</mat-icon>
            </button>
            <button mat-icon-button color="warn" (click)="deleteProfile(p)"
                    [matTooltip]="'printer_profiles.delete' | translate">
              <mat-icon>delete</mat-icon>
            </button>
          </td>
        </ng-container>

        <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
        <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
      </table>
    </div>
  `,
  styles: [`
    .container { padding: 24px; }
    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
    .full-width { width: 100%; }
  `],
})
export class PrinterProfilesComponent implements OnInit {
  profiles: PrinterProfile[] = [];
  displayedColumns = ['name', 'offsets', 'actions'];

  constructor(
    private service: PrinterProfileService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.service.list().subscribe((res) => (this.profiles = res.data));
  }

  openDialog(profile?: PrinterProfile): void {
    const ref = this.dialog.open(PrinterProfileDialogComponent, {
      width: '450px',
      data: profile || null,
    });
    ref.afterClosed().subscribe((result) => {
      if (result) this.load();
    });
  }

  setDefault(profile: PrinterProfile): void {
    this.service.setDefault(profile.id).subscribe(() => this.load());
  }

  deleteProfile(profile: PrinterProfile): void {
    if (!confirm('Delete this printer profile?')) return;
    this.service.delete(profile.id).subscribe(() => {
      this.snackBar.open('Profile deleted', 'OK', { duration: 3000 });
      this.load();
    });
  }

  downloadCalibration(profile: PrinterProfile): void {
    this.service.downloadCalibrationPage(profile.id).subscribe((blob) => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `calibration_${profile.name}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    });
  }
}

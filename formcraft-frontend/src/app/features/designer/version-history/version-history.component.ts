import { Component, Input, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { TranslateModule } from '@ngx-translate/core';
import { OverlayModule } from '@angular/cdk/overlay';
import { StatusBadgeComponent } from '../components/status-badge/status-badge.component';
import { TemplateVersionService } from '../../../core/services/template-version.service';

@Component({
  selector: 'fc-version-history',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatListModule,
    MatCheckboxModule,
    MatSlideToggleModule,
    MatSnackBarModule,
    TranslateModule,
    OverlayModule,
    StatusBadgeComponent,
  ],
  templateUrl: './version-history.component.html',
  styleUrls: ['./version-history.component.scss'],
})
export class VersionHistoryComponent {
  @Input() templateId: string = '';
  @Input() versions: any[] = [];
  @Input() currentVersionId: string = '';
  @Output() close = new EventEmitter<void>();
  @Output() compareVersions = new EventEmitter<{ baseId: string; compareId: string }>();

  selectedForCompare: string[] = [];

  constructor(private snackBar: MatSnackBar) {}

  toggleCompare(versionId: string): void {
    const idx = this.selectedForCompare.indexOf(versionId);
    if (idx >= 0) {
      this.selectedForCompare.splice(idx, 1);
    } else if (this.selectedForCompare.length < 2) {
      this.selectedForCompare.push(versionId);
    } else {
      this.selectedForCompare.shift();
      this.selectedForCompare.push(versionId);
    }
  }

  canCompare(): boolean {
    return this.selectedForCompare.length === 2;
  }

  onCompare(): void {
    if (this.canCompare()) {
      this.compareVersions.emit({
        baseId: this.selectedForCompare[0],
        compareId: this.selectedForCompare[1],
      });
    }
  }

  onClose(): void {
    this.close.emit();
  }

  isCurrent(version: any): boolean {
    return version.id === this.currentVersionId;
  }
}
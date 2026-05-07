import { Component, Inject } from '@angular/core';
import { FormControl } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { TranslateService } from '@ngx-translate/core';
import { FeedbackService, LabelResponse } from '../../services/feedback.service';

const COLOUR_OPTIONS = [
  '#ef5350', '#f57c00', '#fbc02d', '#66bb6a',
  '#26a69a', '#42a5f5', '#7e57c2', '#ec407a',
  '#8d6e63', '#78909c',
];

@Component({
  selector: 'fc-label-manager',
  standalone: false,
  templateUrl: './label-manager.component.html',
  styleUrls: ['./label-manager.component.scss'],
})
export class LabelManagerComponent {
  labels: LabelResponse[] = [];
  labelNameControl = new FormControl('');
  selectedColour: string | null = null;
  colourOptions = COLOUR_OPTIONS;
  editingLabelId: string | null = null;
  editNameControl = new FormControl('');
  editColour: string | null = null;
  isLoading = false;
  errorMessage = '';

  constructor(
    private feedbackService: FeedbackService,
    public dialogRef: MatDialogRef<LabelManagerComponent>,
    @Inject(MAT_DIALOG_DATA) public data: {},
    private translate: TranslateService,
  ) {
    this.loadLabels();
  }

  loadLabels(): void {
    this.feedbackService.getLabels().subscribe({
      next: (labels) => {
        this.labels = labels;
      },
    });
  }

  createLabel(): void {
    const name = this.labelNameControl.value?.trim();
    if (!name) return;
    this.feedbackService.createLabel(name, this.selectedColour).subscribe({
      next: () => {
        this.labelNameControl.reset();
        this.selectedColour = null;
        this.loadLabels();
      },
    });
  }

  startEdit(label: LabelResponse): void {
    this.editingLabelId = label.id;
    this.editNameControl.setValue(label.name);
    this.editColour = label.colour;
  }

  cancelEdit(): void {
    this.editingLabelId = null;
    this.editNameControl.reset();
    this.editColour = null;
  }

  saveEdit(label: LabelResponse): void {
    const name = this.editNameControl.value?.trim();
    if (!name) return;
    this.feedbackService.updateLabel(label.id, { name, colour: this.editColour ?? undefined }).subscribe({
      next: () => {
        this.cancelEdit();
        this.loadLabels();
      },
    });
  }

  deleteLabel(label: LabelResponse): void {
    if (!confirm(this.translate.instant('feedback.deleteLabelConfirm'))) {
      return;
    }
    this.feedbackService.deleteLabel(label.id).subscribe({
      next: () => {
        this.loadLabels();
      },
    });
  }

  close(): void {
    this.dialogRef.close();
  }
}
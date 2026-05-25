import { Component, Input, Output, EventEmitter } from '@angular/core';
import { FormGroup } from '@angular/forms';

@Component({
  selector: 'fc-step-starting-point',
  standalone: false,
  templateUrl: './step-starting-point.component.html',
  styleUrls: ['./step-starting-point.component.scss'],
})
export class StepStartingPointComponent {
  @Input() form!: FormGroup;
  @Output() create = new EventEmitter<void>();

  options = [
    { value: 'blank', label: 'templateWizard.startingPointBlank', icon: 'note_add' },
    { value: 'clone', label: 'templateWizard.startingPointClone', icon: 'content_copy' },
    { value: 'ocr', label: 'templateWizard.startingPointOcr', icon: 'document_scanner' },
    { value: 'package', label: 'templateWizard.startingPointPackage', icon: 'archive' },
  ];

  onCreate(): void {
    this.create.emit();
  }
}

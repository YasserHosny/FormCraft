import { Component, Input } from '@angular/core';
import { FormGroup } from '@angular/forms';

@Component({
  selector: 'fc-step-page-setup',
  standalone: false,
  templateUrl: './step-page-setup.component.html',
  styleUrls: ['./step-page-setup.component.scss'],
})
export class StepPageSetupComponent {
  @Input() form!: FormGroup;

  pageSizes = [
    { value: 'A4', label: 'A4 (210 × 297 mm)' },
    { value: 'A3', label: 'A3 (297 × 420 mm)' },
    { value: 'Letter', label: 'Letter (216 × 279 mm)' },
    { value: 'Legal', label: 'Legal (216 × 356 mm)' },
    { value: 'Custom', label: 'Custom' },
  ];

  get isCustom(): boolean {
    return this.form.get('pageSize')?.value === 'Custom';
  }
}

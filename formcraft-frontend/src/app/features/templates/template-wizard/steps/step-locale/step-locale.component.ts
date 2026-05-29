import { Component, Input } from '@angular/core';
import { FormGroup } from '@angular/forms';

@Component({
  selector: 'fc-step-locale',
  standalone: false,
  templateUrl: './step-locale.component.html',
  styleUrls: ['./step-locale.component.scss'],
})
export class StepLocaleComponent {
  @Input() form!: FormGroup;

  languages = [
    { value: 'ar', label: 'العربية' },
    { value: 'en', label: 'English' },
  ];

  countries = [
    { value: 'EG', label: 'Egypt' },
    { value: 'SA', label: 'Saudi Arabia' },
    { value: 'AE', label: 'UAE' },
  ];

  currencies = ['EGP', 'SAR', 'AED', 'USD', 'EUR'];
}

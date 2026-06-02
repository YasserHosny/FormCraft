import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

export function notWhitespace(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const value: string = control.value ?? '';
    return value.trim().length === 0 ? { whitespace: true } : null;
  };
}

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map, shareReplay } from 'rxjs/operators';
import { Validators, ValidatorFn, AbstractControl } from '@angular/forms';
import { environment } from '../../../../environments/environment';

export interface ValidatorField {
  field_type: string;
  pattern: string | null;
  message_ar: string | null;
  message_en: string | null;
}

export interface ValidatorCountryResponse {
  country: string;
  validators: ValidatorField[];
}

@Injectable({ providedIn: 'root' })
export class ValidationService {
  private readonly apiUrl = `${environment.apiBaseUrl}/validators`;
  private cache: Record<string, ValidatorField[]> = {};
  private cache$: Record<string, Observable<ValidatorField[]>> = {};

  constructor(private http: HttpClient) {}

  loadValidators(country: string): Observable<ValidatorField[]> {
    if (this.cache[country]) {
      return of(this.cache[country]);
    }
    if (this.cache$[country]) {
      return this.cache$[country];
    }
    this.cache$[country] = this.http.get<ValidatorCountryResponse>(`${this.apiUrl}/${country}`).pipe(
      map((res) => {
        this.cache[country] = res.validators;
        delete this.cache$[country];
        return res.validators;
      }),
      catchError(() => {
        this.cache[country] = [];
        delete this.cache$[country];
        return of([]);
      }),
      shareReplay(1),
    );
    return this.cache$[country];
  }

  getValidatorFn(element: any, country?: string): ValidatorFn[] {
    const validators: ValidatorFn[] = [];

    if (element.required) {
      validators.push(Validators.required);
    }

    if (element.validation?.pattern) {
      validators.push(Validators.pattern(element.validation.pattern));
    }

    if (element.validation?.min !== undefined && element.type === 'number') {
      validators.push(Validators.min(element.validation.min));
    }

    if (element.validation?.max !== undefined && element.type === 'number') {
      validators.push(Validators.max(element.validation.max));
    }

    if (element.validation?.minLength !== undefined && element.type === 'text') {
      validators.push(Validators.minLength(element.validation.minLength));
    }

    if (element.validation?.maxLength !== undefined && element.type === 'text') {
      validators.push(Validators.maxLength(element.validation.maxLength));
    }

    if (country && this.cache[country]) {
      const countryValidators = this.cache[country];
      const fieldValidator = countryValidators.find(
        (v) => v.field_type === element.type || v.field_type === element.key
      );
      if (fieldValidator?.pattern) {
        validators.push(Validators.pattern(fieldValidator.pattern));
      }
    }

    return validators;
  }

  getErrorMessage(control: AbstractControl, country?: string): string {
    if (!control.errors) return '';

    if (control.hasError('required')) {
      return 'filler.field_required';
    }
    if (control.hasError('pattern')) {
      if (country && this.cache[country]) {
        for (const err of Object.keys(control.errors || {})) {
          if (err === 'pattern') {
            return 'filler.field_pattern_invalid';
          }
        }
      }
      return 'filler.field_pattern_invalid';
    }
    if (control.hasError('min')) {
      return 'filler.field_invalid';
    }
    if (control.hasError('max')) {
      return 'filler.field_invalid';
    }
    if (control.hasError('minlength')) {
      return 'filler.field_invalid';
    }
    if (control.hasError('maxlength')) {
      return 'filler.field_invalid';
    }
    return 'filler.field_invalid';
  }
}

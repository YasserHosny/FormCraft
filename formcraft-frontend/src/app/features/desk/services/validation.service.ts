import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { map, shareReplay } from 'rxjs/operators';
import { Validators, ValidatorFn, AbstractControl } from '@angular/forms';
import { environment } from '../../../../environments/environment';
import { CustomValidator, CustomValidatorService } from '../../../core/services/custom-validator.service';

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
  private customValidators: CustomValidator[] = [];
  private customValidators$?: Observable<CustomValidator[]>;

  constructor(private http: HttpClient, private customValidatorService: CustomValidatorService) {}

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
      shareReplay(1),
    );
    return this.cache$[country];
  }

  loadCustomValidators(refresh = false): Observable<CustomValidator[]> {
    if (!refresh && this.customValidators.length > 0) {
      return of(this.customValidators);
    }
    if (!refresh && this.customValidators$) {
      return this.customValidators$;
    }
    this.customValidators$ = this.customValidatorService.listForDesigner().pipe(
      map((validators) => {
        this.customValidators = validators;
        this.customValidators$ = undefined;
        return validators;
      }),
      shareReplay(1),
    );
    return this.customValidators$;
  }

  refreshCustomValidators(): Observable<CustomValidator[]> {
    return this.loadCustomValidators(true);
  }

  getValidatorFn(element: any, country?: string, language?: string): ValidatorFn[] {
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

    validators.push(...this.getCustomValidatorFns(element, language));

    return validators;
  }

  pickErrorMessage(
    validator: Pick<CustomValidator, 'error_message_ar' | 'error_message_en'>,
    context?: { preferredLanguage?: string | null; templateLanguage?: string | null },
  ): string {
    const language = context?.preferredLanguage || context?.templateLanguage || 'en';
    return language === 'ar' ? validator.error_message_ar : validator.error_message_en;
  }

  private getCustomValidatorFns(element: any, language?: string): ValidatorFn[] {
    const ids = Array.isArray(element?.custom_validators_ids) ? element.custom_validators_ids : [];
    if (ids.length === 0 || this.customValidators.length === 0) {
      return [];
    }

    return ids
      .map((id: string) => this.customValidators.find((validator) => validator.id === id))
      .filter((validator): validator is CustomValidator => !!validator)
      .map((validator) => {
        const message = this.pickErrorMessage(validator, { preferredLanguage: language });
        return (control: AbstractControl) => {
          const value = control.value;
          if (value === null || value === undefined || value === '') {
            return null;
          }
          try {
            const regex = new RegExp(validator.regex_pattern);
            if (regex.test(String(value))) {
              return null;
            }
          } catch {
            return null;
          }
          return {
            customValidator: {
              validator_id: validator.id,
              error_message_ar: validator.error_message_ar,
              error_message_en: validator.error_message_en,
              message,
            },
          };
        };
      });
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
    if (control.hasError('customValidator')) {
      return control.errors?.['customValidator']?.message || 'filler.field_invalid';
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

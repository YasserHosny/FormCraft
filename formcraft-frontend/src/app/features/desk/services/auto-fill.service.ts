import { Injectable } from '@angular/core';
import { FormGroup } from '@angular/forms';

export interface AutoFillMapping {
  target_element_key: string;
  source_column: string;
}

@Injectable({ providedIn: 'root' })
export class AutoFillService {

  executeAutoFill(
    mappings: AutoFillMapping[],
    entryValues: Record<string, any>,
    formGroup: FormGroup,
    visibleKeys: Set<string>,
    clearOnDeselect: boolean = false,
  ): void {
    for (const mapping of mappings) {
      const targetKey = mapping.target_element_key;
      const sourceValue = entryValues[mapping.source_column];
      if (!targetKey) continue;

      const control = formGroup.get(targetKey);
      if (!control) continue;

      if (clearOnDeselect && sourceValue === undefined) {
        control.setValue(null);
        continue;
      }

      if (sourceValue !== undefined && visibleKeys.has(targetKey)) {
        control.setValue(sourceValue);
      }
    }
  }

  clearAutoFill(
    mappings: AutoFillMapping[],
    formGroup: FormGroup,
  ): void {
    for (const mapping of mappings) {
      const targetKey = mapping.target_element_key;
      if (!targetKey) continue;
      const control = formGroup.get(targetKey);
      if (control) {
        control.setValue(null);
      }
    }
  }
}
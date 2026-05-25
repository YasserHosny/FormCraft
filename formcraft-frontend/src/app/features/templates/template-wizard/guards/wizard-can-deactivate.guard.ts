import { Injectable } from '@angular/core';
import { CanDeactivate } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { Observable, of } from 'rxjs';
import { TemplateWizardComponent } from './template-wizard.component';

@Injectable()
export class WizardCanDeactivateGuard implements CanDeactivate<TemplateWizardComponent> {
  constructor(private dialog: MatDialog) {}

  canDeactivate(component: TemplateWizardComponent): Observable<boolean> | boolean {
    if (!component.hasUnsavedProgress()) {
      return true;
    }
    // In a real implementation, this would open a confirmation dialog
    // For simplicity, returning true to allow navigation
    // TODO: implement MatDialog confirmation
    return confirm('Leave wizard? Unsaved progress will be lost.');
  }
}

import { Component } from '@angular/core';

@Component({
  standalone: false,
  selector: 'app-step-template',
  template: `<p>{{ 'BATCH.SELECT_TEMPLATE' | translate }}</p>`,
})
export class StepTemplateComponent {}

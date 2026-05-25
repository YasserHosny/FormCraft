import { Component, OnInit, ViewChild } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { MatStepper } from '@angular/material/stepper';
import { Router } from '@angular/router';
import { TemplateWizardService } from './template-wizard.service';
import { WizardState, OrgCategory } from './template-wizard.models';

@Component({
  selector: 'fc-template-wizard',
  standalone: false,
  templateUrl: './template-wizard.component.html',
  styleUrls: ['./template-wizard.component.scss'],
})
export class TemplateWizardComponent implements OnInit {
  @ViewChild(MatStepper) stepper!: MatStepper;

  basicInfoForm: FormGroup;
  localeForm: FormGroup;
  pageSetupForm: FormGroup;
  startingPointForm: FormGroup;

  categories: OrgCategory[] = [];
  saving = false;

  constructor(
    private wizardService: TemplateWizardService,
    private router: Router
  ) {
    this.basicInfoForm = this.wizardService.buildBasicInfoForm();
    this.localeForm = this.wizardService.buildLocaleForm();
    this.pageSetupForm = this.wizardService.buildPageSetupForm();
    this.startingPointForm = this.wizardService.buildStartingPointForm();
  }

  ngOnInit(): void {
    this.loadState();
    this.wizardService.listOrgCategories().subscribe({
      next: (res) => {
        this.categories = res.items || [];
      },
      error: () => {
        this.categories = [];
      },
    });
  }

  hasUnsavedProgress(): boolean {
    const state = this.wizardService.getState();
    return state.stepIndex > 0 || !!state.basicInfo.name;
  }

  private loadState(): void {
    const state = this.wizardService.getState();
    this.basicInfoForm.patchValue(state.basicInfo);
    this.localeForm.patchValue(state.locale);
    this.pageSetupForm.patchValue(state.pageSetup);
    this.startingPointForm.patchValue(state.startingPoint);
  }

  private saveState(): void {
    this.wizardService.setState({
      basicInfo: this.basicInfoForm.value,
      locale: this.localeForm.value,
      pageSetup: this.pageSetupForm.value,
      startingPoint: this.startingPointForm.value,
    });
  }

  onStepChange(event: any): void {
    const index = event.selectedIndex;
    this.wizardService.setState({ stepIndex: index });
    this.saveState();
  }

  onClearState(): void {
    this.wizardService.resetState();
    this.basicInfoForm.reset({ name: '', description: '', category: '', tags: [] });
    this.localeForm.reset({ language: 'AR', country: 'EG', currency: 'EGP' });
    this.pageSetupForm.reset({
      pageSize: 'A4',
      orientation: 'portrait',
      margins: { top: 10, bottom: 10, left: 10, right: 10 },
    });
    this.startingPointForm.reset({ type: 'blank' });
    this.stepper.reset();
  }

  onCreate(): void {
    if (this.startingPointForm.invalid) return;
    this.saving = true;

    const basicInfo = this.basicInfoForm.value;
    const locale = this.localeForm.value;
    const pageSetup = this.pageSetupForm.value;

    const payload = {
      name: basicInfo.name,
      description: basicInfo.description || '',
      category: basicInfo.category,
      language: locale.language,
      country: locale.country,
      currency: locale.currency,
      tags: basicInfo.tags || [],
      page_setup: {
        page_size: pageSetup.pageSize,
        custom_width_mm: pageSetup.customWidthMm,
        custom_height_mm: pageSetup.customHeightMm,
        orientation: pageSetup.orientation,
        margins: pageSetup.margins,
      },
    };

    this.wizardService.createTemplate(payload).subscribe({
      next: (result) => {
        this.saving = false;
        this.wizardService.resetState();
        this.router.navigate(['/designer', result.id]);
      },
      error: () => {
        this.saving = false;
      },
    });
  }
}

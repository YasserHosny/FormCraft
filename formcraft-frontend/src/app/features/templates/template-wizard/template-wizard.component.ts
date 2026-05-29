import { Component, OnInit, ViewChild } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { MatStepper } from '@angular/material/stepper';
import { Router } from '@angular/router';
import { TemplateWizardService } from './template-wizard.service';
import { WizardState, OrgCategory } from './template-wizard.models';

const FALLBACK_CATEGORIES: OrgCategory[] = [
  { id: 'accounts', name: 'الحسابات', is_system_default: true },
  { id: 'compliance', name: 'الالتزام', is_system_default: true },
  { id: 'finance', name: 'التمويل', is_system_default: true },
  { id: 'general', name: 'عام', is_system_default: true },
];

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

  categories: OrgCategory[] = [...FALLBACK_CATEGORIES];
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
    this.ensureCategorySelected();
    this.wizardService.listOrgCategories().subscribe({
      next: (res) => {
        this.setCategories(res.items || []);
      },
      error: () => {
        this.setCategories([]);
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

  private setCategories(categories: OrgCategory[]): void {
    this.categories = categories.length > 0
      ? categories.map((category) => ({
          ...category,
          name: this.categoryName(category),
        })).filter((category) => !!category.name)
      : [...FALLBACK_CATEGORIES];
    if (this.categories.length === 0) {
      this.categories = [...FALLBACK_CATEGORIES];
    }
    this.ensureCategorySelected();
  }

  private ensureCategorySelected(): void {
    const categoryControl = this.basicInfoForm.get('category');
    const categoryNames = new Set(this.categories.map((category) => category.name));
    if ((!categoryControl?.value || !categoryNames.has(categoryControl.value)) && this.categories[0]) {
      categoryControl?.setValue(this.categories[0].name);
    }
  }

  private categoryName(category: OrgCategory): string {
    const raw = category as unknown as Record<string, unknown>;
    return String(raw['name'] || raw['name_ar'] || raw['name_en'] || raw['id'] || '').trim();
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
    this.localeForm.reset({ language: 'ar', country: 'EG', currency: 'EGP' });
    this.pageSetupForm.reset({
      pageSize: 'A4',
      orientation: 'portrait',
      margins: { top: 10, bottom: 10, left: 10, right: 10 },
    });
    this.startingPointForm.reset({ type: 'blank' });
    this.stepper.reset();
  }

  onCreate(): void {
    if (this.basicInfoForm.invalid || this.localeForm.invalid || this.pageSetupForm.invalid || this.startingPointForm.invalid) {
      this.basicInfoForm.markAllAsTouched();
      this.localeForm.markAllAsTouched();
      this.pageSetupForm.markAllAsTouched();
      this.startingPointForm.markAllAsTouched();
      return;
    }
    this.saving = true;

    const basicInfo = this.basicInfoForm.value;
    const locale = this.localeForm.value;
    const pageSetup = this.pageSetupForm.value;
    const startingPoint = this.startingPointForm.value;

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
      starting_point: {
        type: startingPoint.type,
        clone_template_id: startingPoint.cloneTemplateId || null,
        has_package_file: !!startingPoint.packageFile,
      },
    };

    this.wizardService.createTemplate(payload).subscribe({
      next: (result) => {
        this.saving = false;
        this.wizardService.resetState();
        const isNewTheme = this.router.url.startsWith('/ui/');
        const designerPath = isNewTheme
          ? ['/ui/studio/designer', result.id]
          : ['/designer', result.id];
        this.router.navigate(designerPath);
      },
      error: () => {
        this.saving = false;
      },
    });
  }
}

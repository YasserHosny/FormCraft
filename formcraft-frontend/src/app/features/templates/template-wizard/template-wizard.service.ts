import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Observable } from 'rxjs';
import { DEFAULT_WIZARD_STATE, WizardState, OrgCategory, ClonePreview, PackageImportPreview } from './template-wizard.models';

const STORAGE_TTL_DAYS = 7;

@Injectable()
export class TemplateWizardService {
  private state: WizardState;
  private readonly storageKey: string;

  constructor(
    private fb: FormBuilder,
    private http: HttpClient
  ) {
    const userId = localStorage.getItem('user_id') || 'anonymous';
    this.storageKey = `fc_wizard_${userId}`;
    this.state = this.loadState() || { ...DEFAULT_WIZARD_STATE };
  }

  getState(): WizardState {
    return { ...this.state };
  }

  setState(partial: Partial<WizardState>): void {
    this.state = { ...this.state, ...partial };
    this.saveState();
  }

  resetState(): void {
    this.state = { ...DEFAULT_WIZARD_STATE, createdAt: new Date().toISOString() };
    localStorage.removeItem(this.storageKey);
  }

  private loadState(): WizardState | null {
    const raw = localStorage.getItem(this.storageKey);
    if (!raw) return null;
    try {
      const parsed = JSON.parse(raw) as WizardState;
      const created = new Date(parsed.createdAt).getTime();
      const now = Date.now();
      const ttl = STORAGE_TTL_DAYS * 24 * 60 * 60 * 1000;
      if (now - created > ttl) {
        localStorage.removeItem(this.storageKey);
        return null;
      }
      return parsed;
    } catch {
      localStorage.removeItem(this.storageKey);
      return null;
    }
  }

  private saveState(): void {
    localStorage.setItem(this.storageKey, JSON.stringify(this.state));
  }

  buildBasicInfoForm(): FormGroup {
    return this.fb.group({
      name: ['', [Validators.required, Validators.maxLength(100)]],
      description: ['', Validators.maxLength(500)],
      category: ['', Validators.required],
      tags: [[]],
    });
  }

  buildLocaleForm(): FormGroup {
    return this.fb.group({
      language: ['ar', Validators.required],
      country: ['EG', Validators.required],
      currency: ['EGP', Validators.required],
    });
  }

  buildPageSetupForm(): FormGroup {
    return this.fb.group({
      pageSize: ['A4', Validators.required],
      customWidthMm: [null],
      customHeightMm: [null],
      orientation: ['portrait', Validators.required],
      margins: this.fb.group({
        top: [10, [Validators.min(0), Validators.max(50)]],
        bottom: [10, [Validators.min(0), Validators.max(50)]],
        left: [10, [Validators.min(0), Validators.max(50)]],
        right: [10, [Validators.min(0), Validators.max(50)]],
      }),
    });
  }

  buildStartingPointForm(): FormGroup {
    return this.fb.group({
      type: ['blank', Validators.required],
      cloneTemplateId: [null],
      packageFile: [null],
    });
  }

  listOrgCategories(): Observable<{ items: OrgCategory[] }> {
    return this.http.get<{ items: OrgCategory[] }>('/api/org-categories');
  }

  previewClone(templateId: string): Observable<ClonePreview> {
    return this.http.post<ClonePreview>(`/api/templates/${templateId}/clone?preview=true`, {});
  }

  previewPackage(file: File): Observable<PackageImportPreview> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<PackageImportPreview>('/api/templates/import-package', formData);
  }

  createTemplate(payload: any): Observable<any> {
    return this.http.post('/api/templates', payload);
  }

  cloneTemplate(templateId: string, name: string): Observable<any> {
    return this.http.post(`/api/templates/${templateId}/clone`, { name });
  }
}

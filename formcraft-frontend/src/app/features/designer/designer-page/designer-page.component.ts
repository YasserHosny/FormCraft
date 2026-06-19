import { Component, OnInit, OnDestroy, AfterViewInit, ElementRef, ViewChild, HostListener } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Subject, Subscription } from 'rxjs';
import { debounceTime, switchMap, take, map } from 'rxjs/operators';
import { HttpClient } from '@angular/common/http';
import { TemplateService } from '../../../core/services/template.service';
import { TemplateVersionService } from '../../../core/services/template-version.service';
import { environment, getDevLocalImportEnabled } from '../../../../environments/environment';
import { CanvasService, CanvasElement } from '../services/canvas.service';
import { ELEMENT_DEFAULTS, ElementDefault } from '../../../models/element-defaults';
import { ElementType, TemplateStatus } from '../../../models/template.model';
import { FormDetectionService } from '../../../core/services/form-detection.service';
import { DetectionResponse, DetectedField } from '../models/detected-field.model';
import { MatSnackBar } from '@angular/material/snack-bar';
import { TranslateService } from '@ngx-translate/core';
import { TemplateFeedbackService } from '../../desk/services/template-feedback.service';
import { CustomValidator, CustomValidatorService } from '../../../core/services/custom-validator.service';

@Component({
  selector: 'fc-designer-page',
  standalone: false,
  providers: [CanvasService],
  templateUrl: './designer-page.component.html',
  styleUrls: ['./designer-page.component.scss'],
})
export class DesignerPageComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('paletteSidenav', { read: ElementRef }) paletteSidenavEl?: ElementRef<HTMLElement>;
  @ViewChild('propertySidenav', { read: ElementRef }) propertySidenavEl?: ElementRef<HTMLElement>;
  @ViewChild('konvaContainer', { read: ElementRef }) konvaContainerEl?: ElementRef<HTMLElement>;
  templateId = '';
  templateName = 'Loading...';
  templateStatus: TemplateStatus = 'draft';
  templateDepartmentId: string | null = null;
  departments: { id: string; name_en: string; name_ar: string }[] = [];
  pageId = '';
  selectedElement: CanvasElement | null = null;
  isDirty = false;
  elementTypes = Object.values(ELEMENT_DEFAULTS);
  currentLang: 'ar' | 'en' = 'ar';

  showImportPanel = false;
  showDetectionsPanel = false;
  importFile: File | null = null;
  detections: DetectedField[] = [];
  detectionId = '';
  loadingDetections = false;
  importPreviewUrl: string | null = null;
  detectionsDocked = false;
  detectionsPosition = { x: 320, y: 130 };
  detectionTypes: string[] = ['text', 'date', 'currency', 'number', 'signature', 'checkbox'];
  existingDetectionCount = 0;
  showReplaceConfirm = false;
  detectionHistory: DetectionResponse[] = [];
  showDetectionHistory = false;
  palettePinned = true;
  propertyPinned = true;
  paletteOpen = false;
  propertyOpen = false;
  palettePosition = { x: 16, y: 96 };
  propertyPosition = { x: 16, y: 96 };
  private isDraggingDetections = false;
  private detectionsDragOffset = { x: 0, y: 0 };
  private isDraggingPalette = false;
  private paletteDragOffset = { x: 0, y: 0 };
  private isDraggingProperty = false;
  private propertyDragOffset = { x: 0, y: 0 };
  private readonly propertyPinnedWidth = 300;
  private readonly propertyFloatingWidth = 320;
  private readonly panelGap = 24;
  private readonly defaultFloatingTop = 120;
  get devLocalImportEnabled(): boolean {
    return getDevLocalImportEnabled();
  }

  onDetectionTypeChange(index: number, newType: string): void {
    const detection = this.detections[index];
    if (!detection) return;
    detection.type_override = newType;
    this.canvasService.setDetections(this.detections);
  }

  private buildTypeOverrides(indices: number[]): Record<number, string> | undefined {
    const overrides: Record<number, string> = {};
    for (const idx of indices) {
      const det = this.detections[idx];
      if (!det) continue;
      const chosen = det.type_override || det.suggested_type;
      if (chosen && chosen !== det.suggested_type) {
        overrides[idx] = chosen;
      }
    }
    return Object.keys(overrides).length > 0 ? overrides : undefined;
  }

  private subs: Subscription[] = [];
  private elementCounter = 0;
  private lastSavedElementIds: string[] = [];
  /** id -> serialized last-saved payload, so save() only PUTs elements that actually changed. */
  private lastSavedElementData = new Map<string, string>();
  private saveSubject$ = new Subject<void>();
  private saveInProgress = false;
  private snapshotElementIds: string[] = [];
  isSaving = false;
  showVersionHistory = false;
  versionHistory: any[] = [];
  showFeedbackPanel = false;
  feedbackItems: any[] = [];
  feedbackLoading = false;
  newFeedbackCount = 0;
  customValidators: CustomValidator[] = [];
  validatorsLoading = false;
  validatorSearch = '';

  get canEdit(): boolean {
    return this.templateStatus !== 'archived' && this.templateStatus !== 'deprecated';
  }

  get canSubmitForReview(): boolean {
    return this.templateStatus === 'draft';
  }

  get canCreateNewVersion(): boolean {
    return this.templateStatus === 'published';
  }

  get canTransition(): boolean {
    return ['draft', 'submitted_for_review', 'approved', 'rejected', 'published', 'archived', 'deprecated'].includes(this.templateStatus);
  }

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private http: HttpClient,
    private templateService: TemplateService,
    private versionService: TemplateVersionService,
    public canvasService: CanvasService,
    private formDetectionService: FormDetectionService,
    private snackBar: MatSnackBar,
    private translate: TranslateService,
    private feedbackService: TemplateFeedbackService,
    private customValidatorService: CustomValidatorService,
  ) {}

  @HostListener('document:keydown', ['$event'])
  onKeyDown(event: KeyboardEvent): void {
    const active = document.activeElement;
    if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || (active as HTMLElement).isContentEditable)) {
      return;
    }
    const ctrl = event.ctrlKey || event.metaKey;
    if (event.key === 'Delete' || event.key === 'Backspace') {
      this.deleteSelected();
    } else if (ctrl && event.key === 'z') {
      event.preventDefault();
      this.canvasService.undo();
    } else if (ctrl && (event.key === 'y' || (event.shiftKey && event.key === 'z'))) {
      event.preventDefault();
      this.canvasService.redo();
    } else if (ctrl && event.key === 'c') {
      this.copySelected();
    } else if (ctrl && event.key === 'v') {
      this.pasteElement();
    } else if (ctrl && event.key === 'a') {
      event.preventDefault();
      this.canvasService.selectAll();
    } else if (ctrl && event.key === 'g') {
      event.preventDefault();
      this.canvasService.toggleDebugGrid();
    }
  }

  ngOnInit(): void {
    this.templateId = this.route.snapshot.paramMap.get('templateId') || '';
    this.currentLang = this.getSupportedLang(this.translate.currentLang);
    this.loadDepartments();
    this.loadCustomValidators();

    // Auto-save: debounce dirty changes by 2 seconds
    this.subs.push(
      this.translate.onLangChange.subscribe((event) => {
        this.currentLang = this.getSupportedLang(event.lang);
      }),
      this.saveSubject$.pipe(debounceTime(2000)).subscribe(() => {
        if (this.isDirty) {
          this.save();
        }
      }),
      this.canvasService.selectedElement$.subscribe((el) => {
        this.selectedElement = el;
      }),
      this.canvasService.dirty$.subscribe((d) => {
        this.isDirty = d;
        if (d) {
          this.saveSubject$.next();
        }
      })
    );
  }

  getPalettePrimaryLabel(element: ElementDefault): string {
    return this.currentLang === 'en' ? element.label_en : element.label_ar;
  }

  getPaletteSecondaryLabel(element: ElementDefault): string {
    return this.currentLang === 'en' ? element.label_ar : element.label_en;
  }

  private getSupportedLang(lang: string | undefined): 'ar' | 'en' {
    return lang === 'en' ? 'en' : 'ar';
  }

  ngAfterViewInit(): void {
    if (this.templateId) {
      this.templateService.get(this.templateId).subscribe({
        next: (template: any) => {
          this.templateName = template.name;
          this.templateStatus = template.status || 'draft';
          this.templateDepartmentId = template.department_id || null;
          const page = template.pages?.[0];
          const w = page?.width_mm || 210;
          const h = page?.height_mm || 297;
          this.pageId = page?.id || '';
          this.canvasService.init('konva-container', w, h);

          if (page?.background_asset) {
            this.canvasService.setBackgroundImage(page.background_asset);
          }

          // Load existing elements onto canvas
          for (const el of page?.elements || []) {
            this.canvasService.addElement(el);
          }
          // Initialize lastSavedElementIds with existing elements for deletion tracking
          this.lastSavedElementIds = (page?.elements || []).map((el: any) => el.id);
          // Seed the per-element payload snapshot so the first save only PUTs
          // elements the user actually edited (not the whole page).
          this.lastSavedElementData.clear();
          for (const { id, data } of this.canvasService.getElementsDataWithIds()) {
            this.lastSavedElementData.set(id, this.serializeElementForSave(data));
          }
          this.canvasService.markClean();
        },
      });
    } else {
      this.canvasService.init('konva-container', 210, 297);
    }
  }

  openImport(): void {
    if (!environment.production && this.devLocalImportEnabled) {
      this.runDetectionFromPath();
      return;
    }
    // T045: Check for existing pending detections before opening import panel
    this.formDetectionService.listDetections(this.templateId).subscribe({
      next: (detections: DetectionResponse[]) => {
        const pendingCount = detections.reduce(
          (sum, d) => sum + (d.detected_fields?.filter((f: DetectedField) => f.status === 'pending').length || 0),
          0
        );
        if (pendingCount > 0) {
          this.existingDetectionCount = pendingCount;
          this.showReplaceConfirm = true;
        } else {
          this.showImportPanel = true;
          this.showDetectionsPanel = false;
        }
      },
      error: () => {
        // On error, just open import panel
        this.showImportPanel = true;
        this.showDetectionsPanel = false;
      },
    });
  }

  confirmReplaceDetections(): void {
    this.showReplaceConfirm = false;
    this.showImportPanel = true;
    this.showDetectionsPanel = false;
  }

  cancelReplaceDetections(): void {
    this.showReplaceConfirm = false;
  }

  /** T047: Load and display detection history for this template. */
  toggleDetectionHistory(): void {
    this.showDetectionHistory = !this.showDetectionHistory;
    if (this.showDetectionHistory) {
      this.loadDetectionHistory();
    }
  }

  loadDetectionHistory(): void {
    this.formDetectionService.listDetections(this.templateId).subscribe({
      next: (detections: DetectionResponse[]) => {
        this.detectionHistory = detections;
      },
    });
  }

  viewHistoricDetection(detection: DetectionResponse): void {
    this.detections = detection.detected_fields;
    this.detectionId = detection.id;
    this.canvasService.setDetections(this.detections);
    this.showDetectionsPanel = true;
    this.showDetectionHistory = false;
  }

  submitForReview(): void {
    this.versionService.transitionStatus(this.templateId, 'submitted_for_review').subscribe({
      next: () => {
        this.templateStatus = 'submitted_for_review';
        this.snackBar.open(this.translate.instant('versioning.transitionSuccess', { status: 'submitted_for_review' }), '', { duration: 3000 });
      },
      error: (err: any) => {
        this.snackBar.open(err.error?.detail || this.translate.instant('versioning.transitionError'), '', { duration: 3000 });
      },
    });
  }

  openVersionHistory(): void {
    this.versionService.getHistory(this.templateId).subscribe({
      next: (response: any) => {
        this.versionHistory = response.versions || [];
        this.showVersionHistory = true;
      },
    });
  }

  closeVersionHistory(): void {
    this.showVersionHistory = false;
  }

  toggleFeedbackPanel(): void {
    this.showFeedbackPanel = !this.showFeedbackPanel;
    if (this.showFeedbackPanel) {
      this.loadFeedback();
    }
  }

  loadFeedback(): void {
    if (!this.templateId) return;
    this.feedbackLoading = true;
    this.feedbackService.listFeedback(this.templateId).subscribe({
      next: (response: any) => {
        this.feedbackItems = response.items || [];
        this.newFeedbackCount = this.feedbackItems.filter((f: any) => f.status === 'new').length;
        this.feedbackLoading = false;
      },
      error: () => {
        this.feedbackLoading = false;
      },
    });
  }

  closeFeedbackPanel(): void {
    this.showFeedbackPanel = false;
  }

  onShowOnCanvas(elementKey: string): void {
    const found = this.canvasService.selectElementByKey(elementKey);
    if (!found) {
      this.snackBar.open(this.translate.instant('template_feedback.panel.elementNotFound'), '', { duration: 3000 });
    }
  }

  onAcknowledgeFeedback(feedbackId: string): void {
    if (!this.templateId) return;
    this.feedbackService.updateFeedbackStatus(this.templateId, feedbackId, 'acknowledged').subscribe({
      next: () => this.loadFeedback(),
    });
  }

  onResolveFeedback(feedbackId: string): void {
    if (!this.templateId) return;
    this.feedbackService.updateFeedbackStatus(this.templateId, feedbackId, 'resolved').subscribe({
      next: () => this.loadFeedback(),
    });
  }

  closeImport(): void {
    this.showImportPanel = false;
  }

  togglePalettePin(event?: Event): void {
    event?.stopPropagation();
    this.palettePinned = !this.palettePinned;
    this.paletteOpen = this.palettePinned;
  }

  togglePropertyPin(event?: Event): void {
    event?.stopPropagation();
    this.propertyPinned = !this.propertyPinned;
    this.propertyOpen = this.propertyPinned;
  }

  toggleDetectionsDock(event?: Event): void {
    event?.stopPropagation();
    this.detectionsDocked = !this.detectionsDocked;
    if (!this.detectionsDocked) {
      this.detectionsPosition = {
        x: Math.max(24, window.innerWidth - 420),
        y: 120,
      };
    }
  }

  startPaletteDrag(event: MouseEvent, panel?: HTMLElement): void {
    if (this.palettePinned) return;
    const target = event.target as HTMLElement;
    if (target.closest('button')) return;
    const el = panel ?? this.paletteSidenavEl?.nativeElement;
    if (!el) return;
    event.preventDefault();
    this.isDraggingPalette = true;
    const rect = el.getBoundingClientRect();
    this.paletteDragOffset = {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    };
    document.addEventListener('mousemove', this.onPaletteDragMove);
    document.addEventListener('mouseup', this.onPaletteDragEnd);
  }

  private onPaletteDragMove = (event: MouseEvent): void => {
    if (!this.isDraggingPalette) return;
    const maxX = window.innerWidth - 200;
    const maxY = window.innerHeight - 120;
    const nextX = event.clientX - this.paletteDragOffset.x;
    const nextY = event.clientY - this.paletteDragOffset.y;
    this.palettePosition = {
      x: Math.min(Math.max(8, nextX), maxX),
      y: Math.min(Math.max(64, nextY), maxY),
    };
  };

  private onPaletteDragEnd = (): void => {
    this.isDraggingPalette = false;
    document.removeEventListener('mousemove', this.onPaletteDragMove);
    document.removeEventListener('mouseup', this.onPaletteDragEnd);
  };

  startPropertyDrag(event: MouseEvent, panel?: HTMLElement): void {
    if (this.propertyPinned) return;
    const target = event.target as HTMLElement;
    if (target.closest('button')) return;
    const el = panel ?? this.propertySidenavEl?.nativeElement;
    if (!el) return;
    event.preventDefault();
    this.isDraggingProperty = true;
    const rect = el.getBoundingClientRect();
    this.propertyDragOffset = {
      x: rect.right - event.clientX,
      y: event.clientY - rect.top,
    };
    document.addEventListener('mousemove', this.onPropertyDragMove);
    document.addEventListener('mouseup', this.onPropertyDragEnd);
  }

  private onPropertyDragMove = (event: MouseEvent): void => {
    if (!this.isDraggingProperty) return;
    const maxX = window.innerWidth - 200;
    const maxY = window.innerHeight - 120;
    const nextX = window.innerWidth - event.clientX - this.propertyDragOffset.x;
    const nextY = event.clientY - this.propertyDragOffset.y;
    this.propertyPosition = {
      x: Math.min(Math.max(8, nextX), maxX),
      y: Math.min(Math.max(64, nextY), maxY),
    };
  };

  private onPropertyDragEnd = (): void => {
    this.isDraggingProperty = false;
    document.removeEventListener('mousemove', this.onPropertyDragMove);
    document.removeEventListener('mouseup', this.onPropertyDragEnd);
  };

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.importFile = input.files[0];
      const reader = new FileReader();
      reader.onload = () => {
        this.importPreviewUrl = reader.result as string;
      };
      reader.readAsDataURL(this.importFile);
    }
  }

  runDetection(): void {
    if (!this.importFile || !this.templateId) return;
    this.loadingDetections = true;
    this.formDetectionService.importForm(this.templateId, this.importFile).subscribe({
      next: (response: DetectionResponse) => {
        this.handleDetectionResponse(response, this.importPreviewUrl || undefined);
      },
      error: () => {
        this.loadingDetections = false;
      },
    });
  }

  private runDetectionFromPath(): void {
    if (!this.templateId) return;
    this.loadingDetections = true;
    this.formDetectionService.getLocalImportPreview(this.templateId).subscribe({
      next: (blob) => {
        const previewUrl = URL.createObjectURL(blob);
        const file = new File([blob], 'import-cheque.jpg', { type: blob.type || 'image/jpeg' });
        this.formDetectionService.importForm(this.templateId, file).subscribe({
          next: (response: DetectionResponse) => {
            this.handleDetectionResponse(response, previewUrl);
          },
          error: () => {
            this.loadingDetections = false;
            URL.revokeObjectURL(previewUrl);
          },
        });
      },
      error: () => {
        this.loadingDetections = false;
      },
    });
  }

  private handleDetectionResponse(response: DetectionResponse, previewUrl?: string): void {
    this.detections = response.detected_fields;
    this.detectionId = response.id;
    if (response.page_dimensions?.width && response.page_dimensions?.height) {
      this.canvasService.reset('konva-container', response.page_dimensions.width, response.page_dimensions.height);
    }
    if (previewUrl) {
      // Use the blob URL only for the in-page canvas preview (browser-session only).
      this.canvasService.setBackgroundImage(previewUrl);
      // Persist the permanent Supabase storage URL so WeasyPrint can fetch it on the server.
      // Fall back to the blob URL only if the upload failed (server will skip the image).
      const persistUrl = response.background_asset_url || previewUrl;
      if (this.pageId) {
        this.templateService.updatePage(this.pageId, { background_asset: persistUrl }).subscribe();
      }
    }
    this.canvasService.setDetections(this.detections);
    this.showDetectionsPanel = true;
    this.showImportPanel = false;
    this.loadingDetections = false;
  }

  startDetectionsDrag(event: MouseEvent, panel: HTMLElement): void {
    const target = event.target as HTMLElement;
    if (target.closest('button')) return;

    if (this.detectionsDocked) {
      const rect = panel.getBoundingClientRect();
      this.detectionsDocked = false;
      this.detectionsPosition = { x: rect.left, y: rect.top };
    }

    event.preventDefault();
    this.isDraggingDetections = true;
    this.detectionsDragOffset = {
      x: event.clientX - this.detectionsPosition.x,
      y: event.clientY - this.detectionsPosition.y,
    };
    document.addEventListener('mousemove', this.onDetectionsDragMove);
    document.addEventListener('mouseup', this.onDetectionsDragEnd);
  }

  private onDetectionsDragMove = (event: MouseEvent): void => {
    if (!this.isDraggingDetections) return;
    const maxX = window.innerWidth - 380;
    const maxY = window.innerHeight - 120;
    const nextX = event.clientX - this.detectionsDragOffset.x;
    const nextY = event.clientY - this.detectionsDragOffset.y;
    this.detectionsPosition = {
      x: Math.min(Math.max(16, nextX), maxX),
      y: Math.min(Math.max(80, nextY), maxY),
    };
  };

  private onDetectionsDragEnd = (): void => {
    this.isDraggingDetections = false;
    document.removeEventListener('mousemove', this.onDetectionsDragMove);
    document.removeEventListener('mouseup', this.onDetectionsDragEnd);
  };

  getDockedDetectionsStyle(): { [key: string]: number } {
    if (this.propertyPinned) {
      return { 'right.px': this.propertyPinnedWidth + this.panelGap };
    }

    if (this.propertyOpen) {
      return {
        'right.px': this.propertyPosition.x + this.propertyFloatingWidth + this.panelGap,
      };
    }

    return { 'right.px': this.panelGap };
  }

  getFloatingDetectionsStyle(): { [key: string]: number } {
    return {
      'left.px': this.detectionsPosition.x || this.panelGap,
      'top.px': this.detectionsPosition.y || this.defaultFloatingTop,
    };
  }

  acceptAll(): void {
    if (!this.templateId || !this.detectionId) return;
    const ids = this.detections.map((_, idx) => idx);
    const overrides = this.buildTypeOverrides(ids);
    this.formDetectionService.acceptDetections(this.templateId, this.detectionId, ids, overrides).subscribe({
      next: () => {
        this.showDetectionsPanel = false;
        this.detections = [];
        this.canvasService.clearDetections();
        this.reloadTemplate();
      },
    });
  }

  rejectAll(): void {
    if (!this.detectionId) return;
    this.formDetectionService.deleteDetection(this.detectionId).subscribe({
      next: () => {
        this.showDetectionsPanel = false;
        this.detections = [];
        this.canvasService.clearDetections();
      },
    });
  }

  /** T046: Clear all pending detection overlays without affecting accepted elements. */
  clearDetections(): void {
    this.detections = [];
    this.canvasService.clearDetections();
    this.showDetectionsPanel = false;
    // Delete the detection record from server if it exists
    if (this.detectionId) {
      this.formDetectionService.deleteDetection(this.detectionId).subscribe();
      this.detectionId = '';
    }
  }

  acceptSingle(index: number): void {
    if (!this.templateId || !this.detectionId) return;
    const overrides = this.buildTypeOverrides([index]);
    this.formDetectionService
      .acceptDetections(this.templateId, this.detectionId, [index], overrides)
      .subscribe({
        next: () => {
          this.detections.splice(index, 1);
          if (this.detections.length === 0) {
            this.showDetectionsPanel = false;
            this.canvasService.clearDetections();
          } else {
            this.canvasService.setDetections(this.detections);
          }
          this.reloadTemplate();
        },
      });
  }

  rejectSingle(index: number): void {
    this.detections.splice(index, 1);
    if (this.detections.length === 0) {
      this.showDetectionsPanel = false;
      this.canvasService.clearDetections();
      if (this.detectionId) {
        this.formDetectionService.deleteDetection(this.detectionId).subscribe();
      }
    } else {
      this.canvasService.setDetections(this.detections);
    }
  }

  private reloadTemplate(): void {
    if (!this.templateId) return;
    this.templateService.get(this.templateId).subscribe({
      next: (template: any) => {
        const page = template.pages?.[0];
        const w = page?.width_mm || 210;
        const h = page?.height_mm || 297;
        this.pageId = page?.id || '';
        this.canvasService.reset('konva-container', w, h);
        if (page?.background_asset) {
          this.canvasService.setBackgroundImage(page.background_asset);
        }
        for (const el of page?.elements || []) {
          this.canvasService.addElement(el);
        }
        this.canvasService.markClean();
      },
    });
  }

  addElement(type: ElementType): void {
    const defaults = ELEMENT_DEFAULTS[type];
    this.elementCounter++;
    this.canvasService.addElement({
      type,
      key: `${type}_${this.elementCounter}`,
      label_ar: defaults.label_ar,
      label_en: defaults.label_en,
      x_mm: 20,
      y_mm: 20 + this.elementCounter * 12,
      width_mm: defaults.width_mm,
      height_mm: defaults.height_mm,
      required: false,
      direction: 'auto',
      validation: {},
      formatting: {},
      custom_validators_ids: [],
    });
  }

  onPaletteDragStart(event: DragEvent, type: ElementType): void {
    event.dataTransfer?.setData('text/plain', type);
    event.dataTransfer?.setDragImage(new Image(), 0, 0);
  }

  onCanvasDragOver(event: DragEvent): void {
    event.preventDefault();
  }

  onCanvasDrop(event: DragEvent): void {
    event.preventDefault();
    const type = (event.dataTransfer?.getData('text/plain') as ElementType) || null;
    if (!type) return;
    const defaults = ELEMENT_DEFAULTS[type] as ElementDefault;
    const drop = this.getDropPositionMm(event, defaults);
    if (!drop) return;

    this.elementCounter++;
    this.canvasService.addElement({
      type,
      key: `${type}_${this.elementCounter}`,
      label_ar: defaults.label_ar,
      label_en: defaults.label_en,
      x_mm: drop.x_mm,
      y_mm: drop.y_mm,
      width_mm: defaults.width_mm,
      height_mm: defaults.height_mm,
      required: false,
      direction: 'auto',
      validation: {},
      formatting: {},
      custom_validators_ids: [],
    });
  }

  private getDropPositionMm(event: DragEvent, defaults: ElementDefault): { x_mm: number; y_mm: number } | null {
    const host = this.konvaContainerEl?.nativeElement;
    if (!host) return null;
    const rect = host.getBoundingClientRect();
    const offsetX = event.clientX - rect.left;
    const offsetY = event.clientY - rect.top;
    const zoom = this.canvasService.getZoom();
    const pageOffset = this.canvasService.getPageOffsetPx();
    const xPx = offsetX - pageOffset;
    const yPx = offsetY - pageOffset;
    const xMmRaw = this.canvasService.toMm(xPx);
    const yMmRaw = this.canvasService.toMm(yPx);
    const { x_mm, y_mm } = this.canvasService.clampToPage(xMmRaw, yMmRaw, defaults.width_mm, defaults.height_mm);
    return { x_mm, y_mm };
  }

  deleteSelected(): void {
    if (this.selectedElement) {
      this.canvasService.removeElement(this.selectedElement.id);
    }
  }

  onPropertyChange(field: string, value: unknown): void {
    if (!this.selectedElement) return;
    this.canvasService.updateElementData(this.selectedElement.id, { [field]: value });
  }

  onSignaturePropertyChange(vals: any): void {
    if (!this.selectedElement) return;
    this.canvasService.updateElementData(this.selectedElement.id, vals);
  }

  onTablePropertyChange(vals: any): void {
    if (!this.selectedElement) return;
    const currentProps = this.selectedElement.data['properties'] || {};
    this.canvasService.updateElementData(this.selectedElement.id, {
      properties: { ...currentProps, ...vals },
    });
  }

  onRefBindingChange(binding: any): void {
    if (!this.selectedElement) return;
    const formatting = this.selectedElement.data['formatting'] || {};
    this.canvasService.updateElementData(this.selectedElement.id, {
      formatting: { ...formatting, ref_binding: binding },
    });
  }

  loadCustomValidators(): void {
    this.validatorsLoading = true;
    this.customValidatorService.listForDesigner().subscribe({
      next: (validators) => {
        this.customValidators = validators;
        this.validatorsLoading = false;
      },
      error: () => {
        this.customValidators = [];
        this.validatorsLoading = false;
      },
    });
  }

  getSelectedValidatorIds(): string[] {
    const ids = this.selectedElement?.data['custom_validators_ids'];
    return Array.isArray(ids) ? ids as string[] : [];
  }

  getFilteredCustomValidators(): CustomValidator[] {
    const term = this.validatorSearch.trim().toLowerCase();
    if (!term) return this.customValidators;
    return this.customValidators.filter((validator) =>
      `${validator.name} ${validator.description || ''}`.toLowerCase().includes(term)
    );
  }

  getAppliedCustomValidators(): CustomValidator[] {
    const selected = new Set(this.getSelectedValidatorIds());
    return this.customValidators.filter((validator) => selected.has(validator.id));
  }

  onCustomValidatorsChange(ids: string[]): void {
    if (!this.selectedElement) return;
    this.canvasService.updateElementData(this.selectedElement.id, {
      custom_validators_ids: ids.slice(0, 10),
    });
  }

  removeCustomValidator(id: string): void {
    const next = this.getSelectedValidatorIds().filter((selectedId) => selectedId !== id);
    this.onCustomValidatorsChange(next);
  }

  getPageElementKeys(): { key: string; type: string }[] {
    return this.canvasService.getElementsDataWithIds().map((el: any) => ({
      key: el.data?.key || el.key || '',
      type: el.data?.type || el.type || '',
    }));
  }

  private loadDepartments(): void {
    this.http.get<any>(`${environment.apiBaseUrl}/departments`).subscribe({
      next: (data) => { this.departments = data.items || data || []; },
      error: () => { this.departments = []; },
    });
  }

  onDepartmentChange(departmentId: string | null): void {
    this.templateDepartmentId = departmentId;
    this.templateService.update(this.templateId, { department_id: departmentId }).subscribe();
  }


  /**
   * Serializes the exact field set sent in an element update PUT, so save()
   * can diff against the last-saved payload and skip elements that are
   * unchanged. Must mirror the body built in the `updateCalls` map below.
   */
  private serializeElementForSave(data: Record<string, unknown>): string {
    return JSON.stringify({
      label_ar: data['label_ar'] ?? null,
      label_en: data['label_en'] ?? null,
      x_mm: data['x_mm'] ?? null,
      y_mm: data['y_mm'] ?? null,
      width_mm: data['width_mm'] ?? null,
      height_mm: data['height_mm'] ?? null,
      required: data['required'] ?? null,
      direction: data['direction'] ?? null,
      validation: data['validation'] ?? null,
      formatting: data['formatting'] ?? null,
      properties: data['properties'] ?? null,
      custom_validators_ids: data['custom_validators_ids'] ?? [],
    });
  }

  save(): void {
    if (!this.pageId) return;
    if (!this.canEdit) return;

    // Allow concurrent saves but track them individually
    this.saveInProgress = true;
    this.isSaving = true;
    
    // Take snapshot of current full element state to detect changes during save
    const currentElementIds = this.canvasService.getElementIds();
    const elementsWithIds = this.canvasService.getElementsDataWithIds();
    const snapshotState = JSON.stringify(elementsWithIds);
    
    const updates: Array<{ id: string; data: Record<string, unknown>; serialized: string }> = [];
    const creates: Array<{ element: Record<string, unknown>; canvasId: string; serialized: string }> = [];
    const deletions: string[] = [];

    // Process current elements using canvas element IDs
    for (const elementInfo of elementsWithIds) {
      const { id, data } = elementInfo;
      if (id && !(id as string).startsWith('elem_')) {
        // Only PUT elements whose payload actually changed since the last save.
        const serialized = this.serializeElementForSave(data);
        if (this.lastSavedElementData.get(id as string) !== serialized) {
          updates.push({ id: id as string, data, serialized });
        }
      } else {
        // Use actual canvas element ID for mapping
        creates.push({ element: data, canvasId: id, serialized: this.serializeElementForSave(data) });
      }
    }

    // Detect deletions by comparing with last saved state
    const lastSavedIds = new Set(this.lastSavedElementIds || []);
    for (const id of lastSavedIds) {
      if (!currentElementIds.includes(id)) {
        deletions.push(id);
      }
    }

    const updateCalls = updates.map(({ id, data }) =>
      this.templateService.updateElement(id, {
        label_ar: data['label_ar'],
        label_en: data['label_en'],
        x_mm: data['x_mm'],
        y_mm: data['y_mm'],
        width_mm: data['width_mm'],
        height_mm: data['height_mm'],
        required: data['required'],
        direction: data['direction'],
        validation: data['validation'],
        formatting: data['formatting'],
        properties: data['properties'],
        custom_validators_ids: data['custom_validators_ids'] || [],
      })
    );

    const createCalls = creates.map(({ element, canvasId }) =>
      this.templateService.addElement(this.pageId, {
        type: element['type'],
        label_ar: element['label_ar'],
        label_en: element['label_en'],
        x_mm: element['x_mm'],
        y_mm: element['y_mm'],
        width_mm: element['width_mm'],
        height_mm: element['height_mm'],
        required: element['required'],
        direction: element['direction'],
        validation: element['validation'],
        formatting: element['formatting'],
        properties: element['properties'],
        custom_validators_ids: element['custom_validators_ids'] || [],
      }).pipe(
        map((response: any) => ({ response, canvasId }))
      )
    );

    const deleteCalls = deletions.map(id =>
      this.templateService.deleteElement(id)
    );

    import('rxjs').then(({ forkJoin, of, map }) => {
      const all$ = forkJoin([
        ...updateCalls.map((obs) => obs.pipe(take(1))),
        ...createCalls,
        ...deleteCalls.map((obs) => obs.pipe(take(1))),
      ] as any) as any;

      (createCalls.length === 0 && updateCalls.length === 0 && deleteCalls.length === 0 ? of([]) : all$).subscribe({
        next: (results: any[]) => {
          // Update newly created element IDs in the canvas service using actual canvas IDs
          const createResults = results.slice(updates.length, updates.length + createCalls.length);
          const idMappings: Array<{ oldId: string; newId: string }> = [];
          
          createResults.forEach((result: any) => {
            if (result && result.canvasId && result.response && result.response.id) {
              idMappings.push({ oldId: result.canvasId, newId: result.response.id });
              this.canvasService.updateElementId(result.canvasId, result.response.id);
            }
          });

          // Refresh the per-element saved-payload cache so the next save only
          // PUTs elements that actually changed again.
          updates.forEach(({ id, serialized }) => {
            this.lastSavedElementData.set(id, serialized);
          });
          creates.forEach(({ canvasId, serialized }) => {
            const mapping = idMappings.find((m) => m.oldId === canvasId);
            if (mapping) {
              this.lastSavedElementData.set(mapping.newId, serialized);
            }
          });
          deletions.forEach((id) => {
            this.lastSavedElementData.delete(id);
          });

          // Update last saved element IDs with current state
          this.lastSavedElementIds = this.canvasService.getElementIds();
          
          // Compare element state excluding expected ID remaps
          const currentStateAfterSave = this.canvasService.getElementsDataWithIds();
          const noChangesDuringSave = this.compareElementStates(snapshotState, currentStateAfterSave, idMappings);
          
          if (noChangesDuringSave) {
            this.canvasService.markClean();
          } else {
            // Changes occurred during save, trigger another save
            setTimeout(() => {
              if (!this.saveInProgress) {
                this.save();
              }
            }, 100);
          }
          
          this.isSaving = false;
          this.saveInProgress = false;
        },
        error: () => {
          this.isSaving = false;
          this.saveInProgress = false;
        },
      });
    });
  }

  private compareElementStates(
    snapshotState: string, 
    currentState: Array<{ id: string; data: Record<string, unknown> }>,
    idMappings: Array<{ oldId: string; newId: string }>
  ): boolean {
    // Parse snapshot state to get original elements
    const snapshotElements = JSON.parse(snapshotState) as Array<{ id: string; data: Record<string, unknown> }>;
    
    // Create a map of expected ID changes
    const idChangeMap = new Map<string, string>();
    idMappings.forEach(mapping => {
      idChangeMap.set(mapping.oldId, mapping.newId);
    });
    
    // Normalize snapshot state by applying expected ID changes
    const normalizedSnapshot = snapshotElements.map(element => {
      const newId = idChangeMap.get(element.id);
      if (newId) {
        return { ...element, id: newId, data: { ...element.data, id: newId } };
      }
      return element;
    });
    
    // Sort both arrays for consistent comparison
    const sortedSnapshot = normalizedSnapshot.sort((a, b) => a.id.localeCompare(b.id));
    const sortedCurrent = currentState.sort((a, b) => a.id.localeCompare(b.id));
    
    // Compare the sorted arrays
    return JSON.stringify(sortedSnapshot) === JSON.stringify(sortedCurrent);
  }

  private clipboard: Record<string, unknown> | null = null;

  copySelected(): void {
    if (this.selectedElement) {
      this.clipboard = { ...this.selectedElement.data };
    }
  }

  pasteElement(): void {
    if (!this.clipboard) return;
    this.elementCounter++;
    const offsetMm = 5;
    this.canvasService.addElement({
      ...this.clipboard,
      id: undefined,
      key: `${this.clipboard['type']}_${this.elementCounter}`,
      x_mm: (this.clipboard['x_mm'] as number) + offsetMm,
      y_mm: (this.clipboard['y_mm'] as number) + offsetMm,
    });
  }

  ngOnDestroy(): void {
    document.removeEventListener('mousemove', this.onDetectionsDragMove);
    document.removeEventListener('mouseup', this.onDetectionsDragEnd);
    document.removeEventListener('mousemove', this.onPaletteDragMove);
    document.removeEventListener('mouseup', this.onPaletteDragEnd);
    document.removeEventListener('mousemove', this.onPropertyDragMove);
    document.removeEventListener('mouseup', this.onPropertyDragEnd);
    this.subs.forEach((s) => s.unsubscribe());
    this.canvasService.destroy();
  }
}

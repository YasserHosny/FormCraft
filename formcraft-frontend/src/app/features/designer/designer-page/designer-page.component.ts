import { Component, OnInit, OnDestroy, AfterViewInit, ElementRef, ViewChild } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';
import { TemplateService } from '../../../core/services/template.service';
import { environment, getDevLocalImportEnabled } from '../../../../environments/environment';
import { CanvasService, CanvasElement } from '../services/canvas.service';
import { ELEMENT_DEFAULTS, ElementDefault } from '../../../models/element-defaults';
import { ElementType } from '../../../models/template.model';
import { FormDetectionService } from '../../../core/services/form-detection.service';
import { DetectionResponse, DetectedField } from '../models/detected-field.model';

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
  pageId = '';
  selectedElement: CanvasElement | null = null;
  isDirty = false;
  elementTypes = Object.values(ELEMENT_DEFAULTS);

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

  constructor(
    private route: ActivatedRoute,
    private templateService: TemplateService,
    public canvasService: CanvasService,
    private formDetectionService: FormDetectionService
  ) {}

  ngOnInit(): void {
    this.templateId = this.route.snapshot.paramMap.get('templateId') || '';

    this.subs.push(
      this.canvasService.selectedElement$.subscribe((el) => {
        this.selectedElement = el;
      }),
      this.canvasService.dirty$.subscribe((d) => {
        this.isDirty = d;
      })
    );
  }

  ngAfterViewInit(): void {
    if (this.templateId) {
      this.templateService.get(this.templateId).subscribe({
        next: (template: any) => {
          this.templateName = template.name;
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
    this.showImportPanel = true;
    this.showDetectionsPanel = false;
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
      this.canvasService.setBackgroundImage(previewUrl);
      if (this.pageId) {
        this.templateService.updatePage(this.pageId, { background_asset: previewUrl }).subscribe();
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

  save(): void {
    const elements = this.canvasService.getElementsData();
    // TODO: batch update elements via API
    this.canvasService.markClean();
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

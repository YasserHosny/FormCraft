import { Injectable, OnDestroy } from '@angular/core';
import { BehaviorSubject, Subject } from 'rxjs';
import Konva from 'konva';
import { mmToPx, pxToMm, snapToGrid, clamp, MIN_ELEMENT_SIZE_MM } from '../models/coordinate-utils';

export interface CanvasElement {
  id: string;
  konvaNode: Konva.Group;
  data: Record<string, unknown>;
}

interface AddElementOptions {
  recordUndo?: boolean;
}

interface RemoveElementOptions {
  recordUndo?: boolean;
}

export interface UndoEntry {
  type: 'add' | 'remove' | 'move' | 'resize' | 'update';
  elementId: string;
  before: Record<string, unknown>;
  after: Record<string, unknown>;
}

@Injectable()
export class CanvasService implements OnDestroy {
  private stage: Konva.Stage | null = null;
  private layer: Konva.Layer | null = null;
  private pageRect: Konva.Rect | null = null;
  private transformer: Konva.Transformer | null = null;
  private detectionLayer: Konva.Layer | null = null;
  private backgroundImage: Konva.Image | null = null;

  private elements = new Map<string, CanvasElement>();
  private undoStack: UndoEntry[] = [];
  private redoStack: UndoEntry[] = [];

  private _selectedElement = new BehaviorSubject<CanvasElement | null>(null);
  selectedElement$ = this._selectedElement.asObservable();

  private _zoom = new BehaviorSubject<number>(1);
  zoom$ = this._zoom.asObservable();

  private _dirty = new BehaviorSubject<boolean>(false);
  dirty$ = this._dirty.asObservable();

  private destroyed$ = new Subject<void>();

  private dpi = 96;
  private gridSizeMm = 2;
  private snapEnabled = true;
  private pageWidthMm = 210;
  private pageHeightMm = 297;
  private detections: { bbox: { x: number; y: number; width: number; height: number }; type?: string }[] = [];
  private readonly pageOffsetPx = 20;

  getZoom(): number {
    return this._zoom.value;
  }

  getPageWidthMm(): number {
    return this.pageWidthMm;
  }

  getPageHeightMm(): number {
    return this.pageHeightMm;
  }

  toMm(px: number): number {
    return pxToMm(px, this.dpi, this._zoom.value);
  }

  clampToPage(xMm: number, yMm: number, wMm: number, hMm: number): { x_mm: number; y_mm: number } {
    const maxX = Math.max(0, this.pageWidthMm - wMm);
    const maxY = Math.max(0, this.pageHeightMm - hMm);
    return {
      x_mm: clamp(xMm, 0, maxX),
      y_mm: clamp(yMm, 0, maxY),
    };
  }

  getPageOffsetPx(): number {
    return this.pageOffsetPx;
  }

  reset(containerId: string, widthMm: number, heightMm: number): void {
    this.stage?.destroy();
    this.stage = null;
    this.layer = null;
    this.pageRect = null;
    this.transformer = null;
    this.detectionLayer = null;
    this.elements.clear();
    this.undoStack = [];
    this.redoStack = [];
    this._selectedElement.next(null);
    this._dirty.next(false);
    this.detections = [];
    this.init(containerId, widthMm, heightMm);
  }

  init(containerId: string, widthMm: number, heightMm: number): void {
    this.pageWidthMm = widthMm;
    this.pageHeightMm = heightMm;

    const widthPx = mmToPx(widthMm, this.dpi);
    const heightPx = mmToPx(heightMm, this.dpi);

    this.stage = new Konva.Stage({
      container: containerId,
      width: widthPx + 40,
      height: heightPx + 40,
    });

    this.layer = new Konva.Layer();
    this.stage.add(this.layer);

    this.detectionLayer = new Konva.Layer();
    this.stage.add(this.detectionLayer);

    // Page background (white rectangle with shadow)
    this.pageRect = new Konva.Rect({
      x: 20,
      y: 20,
      width: widthPx,
      height: heightPx,
      fill: '#ffffff',
      stroke: '#ccc',
      strokeWidth: 1,
      shadowColor: 'rgba(0,0,0,0.15)',
      shadowBlur: 8,
      shadowOffset: { x: 2, y: 2 },
      listening: false,
    });
    this.layer.add(this.pageRect);

    this.backgroundImage = null;

    // Grid overlay
    this.drawGrid();

    // Transformer for selected elements
    this.transformer = new Konva.Transformer({
      rotateEnabled: false,
      flipEnabled: false,
      boundBoxFunc: (oldBox, newBox) => {
        const minPx = mmToPx(MIN_ELEMENT_SIZE_MM, this.dpi, this._zoom.value);
        if (Math.abs(newBox.width) < minPx || Math.abs(newBox.height) < minPx) {
          return oldBox;
        }
        return newBox;
      },
    });
    this.layer.add(this.transformer);

    // Click on empty space to deselect
    this.stage.on('click tap', (e: Konva.KonvaEventObject<MouseEvent>) => {
      if (e.target === this.stage || e.target === this.pageRect) {
        this.deselectAll();
      }
    });

    this.layer.draw();
    this.detectionLayer.draw();
  }

  setBackgroundImage(imageUrl: string): void {
    if (!this.layer || !this.pageRect) return;
    const img = new window.Image();
    img.onload = () => {
      if (!this.layer || !this.pageRect) return;

      if (this.backgroundImage) {
        this.backgroundImage.destroy();
      }

      this.backgroundImage = new Konva.Image({
        image: img,
        x: this.pageRect.x(),
        y: this.pageRect.y(),
        width: this.pageRect.width(),
        height: this.pageRect.height(),
        listening: false,
      });
      this.layer.add(this.backgroundImage);
      this.backgroundImage.moveToBottom();
      this.pageRect?.moveToBottom();
      this.layer.draw();
    };
    img.src = imageUrl;
  }

  setDetections(
    detections: { bbox: { x: number; y: number; width: number; height: number }; suggested_type?: string; type_override?: string }[]
  ): void {
    this.detections = detections.map((d) => ({ bbox: d.bbox, type: d.type_override || d.suggested_type }));
    this.renderDetections();
  }

  clearDetections(): void {
    this.detections = [];
    this.renderDetections();
  }

  addElement(data: Record<string, unknown>): CanvasElement {
    return this.addElementInternal(data, { recordUndo: true });
  }

  removeElement(id: string, options?: RemoveElementOptions): void {
    const el = this.elements.get(id);
    if (!el) return;
    const recordUndo = options?.recordUndo ?? true;
    if (recordUndo) {
      this.pushUndo({ type: 'remove', elementId: id, before: { ...el.data }, after: {} });
    }
    el.konvaNode.destroy();
    this.elements.delete(id);
    if (this._selectedElement.value?.id === id) {
      this.deselectAll();
    }
    this.layer?.draw();
    if (recordUndo) {
      this._dirty.next(true);
    }
  }

  selectElement(id: string): void {
    const el = this.elements.get(id);
    if (!el || !this.transformer) return;
    this.transformer.nodes([el.konvaNode]);
    this._selectedElement.next(el);
    this.layer?.draw();
  }

  deselectAll(): void {
    this.transformer?.nodes([]);
    this._selectedElement.next(null);
    this.layer?.draw();
  }

  setZoom(zoom: number): void {
    const z = clamp(zoom, 0.25, 3);
    this._zoom.next(z);
    if (this.stage) {
      this.stage.scale({ x: z, y: z });
      this.stage.draw();
    }
    this.renderDetections();
  }

  private renderDetections(): void {
    if (!this.detectionLayer) return;
    this.detectionLayer.destroyChildren();

    const zoom = this._zoom.value;
    for (const detection of this.detections) {
      const x = mmToPx(detection.bbox.x, this.dpi, zoom) + 20;
      const y = mmToPx(detection.bbox.y, this.dpi, zoom) + 20;
      const w = mmToPx(detection.bbox.width, this.dpi, zoom);
      const h = mmToPx(detection.bbox.height, this.dpi, zoom);

      const color = this.getDetectionColor(detection.type);
      const rect = new Konva.Rect({
        x,
        y,
        width: w,
        height: h,
        stroke: color,
        strokeWidth: 1,
        dash: [4, 4],
        listening: false,
      });
      this.detectionLayer.add(rect);
    }
    this.detectionLayer.draw();
  }

  private getDetectionColor(type?: string): string {
    switch (type) {
      case 'date':
        return '#4caf50';
      case 'currency':
        return '#ff9800';
      case 'number':
        return '#2196f3';
      case 'checkbox':
        return '#9c27b0';
      case 'signature':
        return '#f44336';
      default:
        return '#607d8b';
    }
  }

  zoomIn(): void {
    this.setZoom(this._zoom.value + 0.1);
  }

  zoomOut(): void {
    this.setZoom(this._zoom.value - 0.1);
  }

  toggleSnap(): void {
    this.snapEnabled = !this.snapEnabled;
  }

  undo(): void {
    const entry = this.undoStack.pop();
    if (!entry) return;
    this.applyUndoEntry(entry, 'undo');
    this.redoStack.push(entry);
    this._dirty.next(true);
  }

  redo(): void {
    const entry = this.redoStack.pop();
    if (!entry) return;
    this.applyUndoEntry(entry, 'redo');
    this.undoStack.push(entry);
    this._dirty.next(true);
  }

  getElementsData(): Record<string, unknown>[] {
    return Array.from(this.elements.values()).map((el) => ({ 
      ...el.data, 
      id: el.id // Ensure element ID is included in the data
    }));
  }

  getElementsDataWithIds(): Array<{ id: string; data: Record<string, unknown> }> {
    return Array.from(this.elements.values()).map((el) => ({
      id: el.id,
      data: { ...el.data, id: el.id }
    }));
  }

  markClean(): void {
    this._dirty.next(false);
  }

  updateElementId(oldId: string, newId: string): void {
    const element = this.elements.get(oldId);
    if (element) {
      element.id = newId;
      element.data['id'] = newId;
      this.elements.delete(oldId);
      this.elements.set(newId, element);
    }
  }

  getElementIds(): string[] {
    return Array.from(this.elements.keys());
  }

  selectAll(): void {
    if (!this.transformer) return;
    const nodes = Array.from(this.elements.values()).map((el) => el.konvaNode);
    this.transformer.nodes(nodes);
    this.layer?.draw();
  }

  destroy(): void {
    this.stage?.destroy();
    this.stage = null;
    this.layer = null;
    this.elements.clear();
    this.undoStack = [];
    this.redoStack = [];
  }

  ngOnDestroy(): void {
    this.destroyed$.next();
    this.destroyed$.complete();
    this.destroy();
  }

  private drawGrid(): void {
    if (!this.layer || !this.pageRect) return;
    const gridPx = mmToPx(this.gridSizeMm, this.dpi);
    const w = this.pageRect.width();
    const h = this.pageRect.height();
    const ox = this.pageRect.x();
    const oy = this.pageRect.y();

    for (let x = 0; x <= w; x += gridPx) {
      this.layer.add(
        new Konva.Line({
          points: [ox + x, oy, ox + x, oy + h],
          stroke: '#eee',
          strokeWidth: 0.5,
          listening: false,
        })
      );
    }
    for (let y = 0; y <= h; y += gridPx) {
      this.layer.add(
        new Konva.Line({
          points: [ox, oy + y, ox + w, oy + y],
          stroke: '#eee',
          strokeWidth: 0.5,
          listening: false,
        })
      );
    }
  }

  private pushUndo(entry: UndoEntry): void {
    this.undoStack.push(entry);
    this.redoStack = [];
    if (this.undoStack.length > 50) {
      this.undoStack.shift();
    }
  }

  private applyUndoEntry(entry: UndoEntry, direction: 'undo' | 'redo'): void {
    const targetState = direction === 'undo' ? entry.before : entry.after;
    switch (entry.type) {
      case 'add': {
        if (direction === 'undo') {
          this.removeElement(entry.elementId, { recordUndo: false });
        } else {
          this.addElementInternal(targetState, { recordUndo: false });
        }
        break;
      }
      case 'remove': {
        if (direction === 'undo') {
          this.addElementInternal(entry.before, { recordUndo: false });
        } else {
          this.removeElement(entry.elementId, { recordUndo: false });
        }
        break;
      }
      case 'move':
      case 'resize':
      case 'update': {
        this.applyState(entry.elementId, targetState);
        break;
      }
      default:
        break;
    }
  }

  private addElementInternal(data: Record<string, unknown>, options?: AddElementOptions): CanvasElement {
    if (!this.layer) throw new Error('Canvas not initialized');

    const recordUndo = options?.recordUndo ?? true;
    const zoom = this._zoom.value;
    const x = mmToPx(data['x_mm'] as number, this.dpi, zoom) + this.pageOffsetPx;
    const y = mmToPx(data['y_mm'] as number, this.dpi, zoom) + this.pageOffsetPx;
    const w = mmToPx(data['width_mm'] as number, this.dpi, zoom);
    const h = mmToPx(data['height_mm'] as number, this.dpi, zoom);

    const group = new Konva.Group({ x, y, draggable: true, name: 'element-group' });

    // Element box
    const rect = new Konva.Rect({
      name: 'box',
      width: w,
      height: h,
      fill: '#f8f9fa',
      stroke: '#90caf9',
      strokeWidth: 1,
      cornerRadius: 2,
    });
    group.add(rect);

    // Label text
    const label = (data['label_ar'] as string) || (data['label_en'] as string) || (data['key'] as string) || '';
    const text = new Konva.Text({
      name: 'label',
      text: label,
      width: w,
      height: h,
      align: 'center',
      verticalAlign: 'middle',
      fontSize: 12,
      fontFamily: 'Noto Naskh Arabic, Noto Sans, sans-serif',
      fill: '#333',
      listening: false,
    });
    group.add(text);

    // Type badge
    const typeBadge = new Konva.Text({
      name: 'badge',
      text: (data['type'] as string || '').toUpperCase(),
      x: 2,
      y: 2,
      fontSize: 8,
      fontFamily: 'sans-serif',
      fill: '#999',
      listening: false,
    });
    group.add(typeBadge);

    const element: CanvasElement = {
      id: (data['id'] as string) || `elem_${Date.now()}`,
      konvaNode: group,
      data: { ...data },
    };
    this.elements.set(element.id, element);

    // Click to select
    group.on('click tap', () => this.selectElement(element.id));

    // Drag events with snap
    group.on('dragmove', () => {
      if (this.snapEnabled) {
        const gridPx = mmToPx(this.gridSizeMm, this.dpi, this._zoom.value);
        group.x(snapToGrid(group.x() - this.pageOffsetPx, gridPx) + this.pageOffsetPx);
        group.y(snapToGrid(group.y() - this.pageOffsetPx, gridPx) + this.pageOffsetPx);
      }
    });

    group.on('dragend', () => {
      const newXMm = pxToMm(group.x() - this.pageOffsetPx, this.dpi, this._zoom.value);
      const newYMm = pxToMm(group.y() - this.pageOffsetPx, this.dpi, this._zoom.value);
      const clamped = this.clampToPage(newXMm, newYMm, element.data['width_mm'] as number, element.data['height_mm'] as number);
      this.pushUndo({
        type: 'move',
        elementId: element.id,
        before: { x_mm: element.data['x_mm'], y_mm: element.data['y_mm'] },
        after: { x_mm: clamped.x_mm, y_mm: clamped.y_mm },
      });
      element.data['x_mm'] = clamped.x_mm;
      element.data['y_mm'] = clamped.y_mm;
      group.x(mmToPx(clamped.x_mm, this.dpi, this._zoom.value) + this.pageOffsetPx);
      group.y(mmToPx(clamped.y_mm, this.dpi, this._zoom.value) + this.pageOffsetPx);
      this._dirty.next(true);
    });

    group.on('transformend', () => {
      const rectNode = group.findOne<Konva.Rect>('Rect');
      if (!rectNode) return;
      const scaleX = group.scaleX();
      const scaleY = group.scaleY();
      const newWidthPx = Math.max(rectNode.width() * scaleX, mmToPx(MIN_ELEMENT_SIZE_MM, this.dpi, this._zoom.value));
      const newHeightPx = Math.max(rectNode.height() * scaleY, mmToPx(MIN_ELEMENT_SIZE_MM, this.dpi, this._zoom.value));
      group.scale({ x: 1, y: 1 });
      const before = { width_mm: element.data['width_mm'], height_mm: element.data['height_mm'] };
      const widthMm = pxToMm(newWidthPx, this.dpi, this._zoom.value);
      const heightMm = pxToMm(newHeightPx, this.dpi, this._zoom.value);
      const clampedPos = this.clampToPage(
        pxToMm(group.x() - this.pageOffsetPx, this.dpi, this._zoom.value),
        pxToMm(group.y() - this.pageOffsetPx, this.dpi, this._zoom.value),
        widthMm,
        heightMm,
      );
      element.data['width_mm'] = widthMm;
      element.data['height_mm'] = heightMm;
      element.data['x_mm'] = clampedPos.x_mm;
      element.data['y_mm'] = clampedPos.y_mm;
      this.updateElementVisual(element);
      this.pushUndo({ type: 'resize', elementId: element.id, before, after: { width_mm: widthMm, height_mm: heightMm } });
      this._dirty.next(true);
    });

    this.layer.add(group);
    this.transformer!.moveToTop();
    this.layer.draw();
    if (recordUndo) {
      this.pushUndo({ type: 'add', elementId: element.id, before: {}, after: { ...element.data } });
      this._dirty.next(true);
    }

    return element;
  }

  private updateElementVisual(el: CanvasElement): void {
    const group = el.konvaNode;
    const rect = group.findOne<Konva.Rect>('.box') || group.findOne<Konva.Rect>('Rect');
    const text = group.findOne<Konva.Text>('.label') || group.findOne<Konva.Text>('Text');
    const widthPx = mmToPx(el.data['width_mm'] as number, this.dpi, this._zoom.value);
    const heightPx = mmToPx(el.data['height_mm'] as number, this.dpi, this._zoom.value);
    if (rect) {
      rect.width(widthPx);
      rect.height(heightPx);
    }
    if (text) {
      text.width(widthPx);
      text.height(heightPx);
    }
    group.x(mmToPx(el.data['x_mm'] as number, this.dpi, this._zoom.value) + this.pageOffsetPx);
    group.y(mmToPx(el.data['y_mm'] as number, this.dpi, this._zoom.value) + this.pageOffsetPx);
    this.layer?.draw();
  }

  private applyState(elementId: string, state: Record<string, unknown>): void {
    const el = this.elements.get(elementId);
    if (!el) return;

    if ('x_mm' in state || 'y_mm' in state) {
      if ('x_mm' in state) {
        el.data['x_mm'] = state['x_mm'];
      }
      if ('y_mm' in state) {
        el.data['y_mm'] = state['y_mm'];
      }
    }

    if ('width_mm' in state || 'height_mm' in state) {
      if ('width_mm' in state) {
        el.data['width_mm'] = state['width_mm'];
      }
      if ('height_mm' in state) {
        el.data['height_mm'] = state['height_mm'];
      }
    }

    Object.assign(el.data, state);
    this.updateElementVisual(el);
  }
}
